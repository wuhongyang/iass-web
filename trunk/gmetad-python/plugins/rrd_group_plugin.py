# /*******************************************************************************
#* Portions Copyright (C) 2008 Novell, Inc. All rights reserved.
#*
#* Redistribution and use in source and binary forms, with or without
#* modification, are permitted provided that the following conditions are met:
#*
#*  - Redistributions of source code must retain the above copyright notice,
#*    this list of conditions and the following disclaimer.
#*
#*  - Redistributions in binary form must reproduce the above copyright notice,
#*    this list of conditions and the following disclaimer in the documentation
#*    and/or other materials provided with the distribution.
#*
#*  - Neither the name of Novell, Inc. nor the names of its
#*    contributors may be used to endorse or promote products derived from this
#*    software without specific prior written permission.
#*
#* THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS ``AS IS''
#* AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#* IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#* ARE DISCLAIMED. IN NO EVENT SHALL Novell, Inc. OR THE CONTRIBUTORS
#* BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#* CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
#* SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
#* INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
#* CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
#* ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
#* POSSIBILITY OF SUCH DAMAGE.
#*
#* Authors: Matt Ryan (mrayn novell.com)
#*                  Brad Nicholes (bnicholes novell.com)
#******************************************************************************/

import os
import rrdtool
import logging
import threading
import time
from random import randrange

from rrd_plugin import RRDPlugin
from Gmetad.rrd.rrd_store import get_rrd_store
from Gmetad.gmetad_config import getConfig, GmetadConfig


def get_plugin():
    ''' All plugins are required to implement this method.  It is used as the factory
        function that instanciates a new plugin instance. '''
    # The plugin configuration ID that is passed in must match the section name 
    #  in the configuration file.
    return RRDGroupPlugin('rrdgroup')


def getRandomInterval(midpoint, range=5):
    return randrange(max(midpoint - range, 0), midpoint + range)


class RRDGroupPlugin(RRDPlugin):
    ''' This class implements the RRD plugin that stores metric summary data to RRD files.
        It is derived from the RRDPlugin class.'''

    RRD_GROUPS = 'summary_groups'
    RRD_STORE_IMP = 'rrdstore_imp'
    RRD_STORE_CFG = 'rrdstore_cfg'

    def __init__(self, impid, cfgid=None):
        # bh: Load config via rrd_plugin
        RRDPlugin.__init__(self, 'RRD')

        # bh: Set the default value for config 'rrd_groups'
        self.cfg[RRDGroupPlugin.RRD_GROUPS] = []
        self.cfg[RRDGroupPlugin.RRD_STORE_IMP] = 'redis'
        #self.cfg[RRDGroupPlugin.RRD_STORE_CFG] = 'rrd-store'

        self.cfgHandlers[RRDGroupPlugin.RRD_GROUPS] = self._parseRrdGroups
        self.cfgHandlers[RRDGroupPlugin.RRD_STORE_IMP] = self._parseRrdStoreImp
        self.cfgHandlers[RRDGroupPlugin.RRD_STORE_CFG] = self._parseRrdStoreCfg

         # Parse the config of alarm method
        self._parseConfig(getConfig().getSection(impid))

        self.hostCache = {}

	if self.cfg.has_key(RRDGroupPlugin.RRD_STORE_CFG):
            self.store = get_rrd_store(self.cfg[RRDGroupPlugin.RRD_STORE_IMP], self.cfg[RRDGroupPlugin.RRD_STORE_CFG])
        else:
            self.store = get_rrd_store(self.cfg[RRDGroupPlugin.RRD_STORE_IMP])

    def _parseRrdGroups(self, args):
        ''' Parse the RRD groups directive. '''
        self.cfg[RRDGroupPlugin.RRD_GROUPS] = []
        for rrdgroup in args.split():
            self.cfg[RRDGroupPlugin.RRD_GROUPS].append(rrdgroup.strip().strip('"'))

    def _parseRrdStoreImp(self, arg):
        ''' Parse the Redis host. '''
        self.cfg[RRDGroupPlugin.RRD_STORE_IMP] = arg.strip().strip('"')

    def _parseRrdStoreCfg(self, arg):
        ''' Parse the Redis port. '''
        self.cfg[RRDGroupPlugin.RRD_STORE_CFG] = arg.strip().strip('"')

    def _getHostInfo(self, hostKey):
        ''' Get the host information from redis-server '''
        if not self.hostCache.has_key(hostKey):
            hostInfo = self.store.getHostInfo(hostKey)
            if hostInfo is None:
                return
            self.hostCache[hostKey] = hostInfo
        return self.hostCache[hostKey]

    def _updateGroupSummary(self, groupSummary, clusterNode):
        clusterUp = (clusterNode.getAttr('status') == 'up')
        for hostNode in clusterNode:
            hostKey = hostNode.getAttr('name')
            hostInfo = self._getHostInfo(hostKey)
            if not hostInfo:
                continue
            for group in self.cfg[RRDGroupPlugin.RRD_GROUPS]:
                if hostInfo.has_key(group):
                    summaryTime = int(time.time())
                    #self._updateGroupSummary(group, groupSummary, hostInfo, hostNode, clusterNode, int(time.time()))

                    if not hostInfo.has_key(group):
                        return
                    groupKey = hostInfo[group]

                    if not groupSummary.has_key(group):
                        groupSummary[group] = {}
                    if not groupSummary[group].has_key(groupKey):
                        groupSummary[group][groupKey] = {}
                        groupSummary[group][groupKey]['summary'] = {}
                        groupSummary[group][groupKey]['hosts_up'] = 0
                        groupSummary[group][groupKey]['hosts_down'] = 0

                    groupUp = (clusterNode.getAttr('status') == 'up')

                    reportedTime = summaryTime

                    if 'HOST' != hostNode.id:
                        return

                    reportedTime = int(hostNode.getAttr('reported'))
                    tn = int(hostNode.getAttr('tn'))

                    if hostNode.lastReportedTime == reportedTime:
                        tn = summaryTime - reportedTime
                        if tn < 0: tn = 0
                        hostNode.setAttr('tn', str(tn))
                    else:
                        hostNode.lastReportedTime = reportedTime

                    try:
                        if clusterUp and (int(hostNode.getAttr('tn')) < int(hostNode.getAttr('tmax')) * 4):
                            groupSummary[group][groupKey]['hosts_up'] += 1
                        else:
                            groupSummary[group][groupKey]['hosts_down'] += 1
                    except AttributeError:
                        pass
                    except KeyError:
                        pass

                    for metricNode in hostNode:
                        tn = int(metricNode.getAttr('tn'))

                        if metricNode.lastReportedTime == reportedTime:
                            tn = summaryTime - reportedTime
                            if tn < 0: tn = 0
                            metricNode.setAttr('tn', str(tn))

                        if metricNode.getAttr('type') in ['string', 'timestamp']:
                            continue

                        try:
                            summaryNode = groupSummary[group][groupKey]['summary'][str(metricNode)]
                            currSum = summaryNode.getAttr('sum')
                            summaryNode.incAttr('sum', float(metricNode.getAttr('val')))
                        except KeyError:
                            summaryNode = metricNode.summaryCopy(tag='METRICS')
                            summaryNode.setAttr('sum', float(metricNode.getAttr('val')))
                            summaryNode.setAttr('type', 'double')
                            groupSummary[group][groupKey]['summary'][str(summaryNode)] = summaryNode
                        summaryNode.incAttr('num', 1)

    def _updateGroupRRD(self, groupSummary, clusterNode, ds):
        groupRoot = '%s/GroupSummary' % self.cfg[RRDPlugin.RRD_ROOTDIR]
        self._checkDir(groupRoot)

        for group in groupSummary.keys():
            groupPath = '%s/%s' % (groupRoot, group)
            self._checkDir(groupPath)
            for groupKey in groupSummary[group].keys():
                groupKeyPath = '%s/%s' % (groupPath, groupKey)
                self._checkDir(groupKeyPath)
                for metricNode in groupSummary[group][groupKey]['summary'].itervalues():
                    rrdPath = '%s/%s.rrd' % (groupKeyPath, metricNode.getAttr('name'))
                    if not os.path.isfile(rrdPath):
                        self._createRRD(clusterNode, metricNode, rrdPath, ds.interval, True)
                    try:
                        self._updateRRD(clusterNode, metricNode, rrdPath, True)
                    except Exception:
                        pass

    def notify(self, clusterNode):
        '''Called by the engine when the internal data structure has changed.'''
        gmetadConfig = getConfig()
        try:
            if clusterNode.getAttr('status') == 'down':
                return
        except AttributeError:
            pass
        # Find the data source configuration entry that matches the cluster name
        for ds in gmetadConfig[GmetadConfig.DATA_SOURCE]:
            if ds.name == clusterNode.getAttr('name'):
                break
        if ds is None:
            logging.info('No matching data source for %s' % clusterNode.getAttr('name'))
            return

        if 'GRID' == clusterNode.id:
            # bh: We still do not process GRID here
            return

        if 'CLUSTER' == clusterNode.id:
            if len(self.cfg[RRDGroupPlugin.RRD_GROUPS]) == 0:
                # bh: No group is set so done
                return

            groupSummary = {}
            self._updateGroupSummary(groupSummary, clusterNode)
            self._updateGroupRRD(groupSummary, clusterNode, ds)

            #print "RRDSummary notify called"

