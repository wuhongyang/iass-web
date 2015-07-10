#/*******************************************************************************
#* Copyright (C) 2008 Novell, Inc. All rights reserved.
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
#* Authors: Brad Nicholes (bnicholes novell.com)
#******************************************************************************/
''' This plugin is meant to be a very simplistic example of how a gmetad plugin could be developed
    to analyze metric data as it is read from the various monitored system and produce some
    type of alerting system.  This plugin is probably not suitable for actual production use, but
    could be reworked to create a production alerting mechanism. 
    
    example gmetad.conf alert plugin configuration section:
    
    
    alert {
        sendmailpath "/usr/sbin/sendmail"
        toaddress "someone@somewhere.com"
        fromaddress "monitor@somewhere.com"
        # metric rule format <metric_name> <condition> <message>
        metricrule cpu_user "$val > 55" "CPU User metric has gone bezerk"
        metricrule load_one "$val > 0.5" "One minute load looks wacko"
    }
    '''

from Gmetad.gmetad_plugin import GmetadPlugin
from Gmetad.alert.alert_store import get_alert_store
from Gmetad.alert.alert_method import get_alert_method
from Gmetad.alert.methods.mail_method import MailMethod
import time
import traceback
import logging

alarm_method_mappings = {
    1:'mail',
    2:'phone',
    3:'log'
    }

alarm_level_mappings = {
    1:'warning',
    2:'critical' 
    }

def get_plugin():
    ''' All plugins are required to implement this method.  It is used as the factory
        function that instanciates a new plugin instance. '''
    # The plugin configuration ID that is passed in must match the section name 
    #  in the configuration file.
    return HealthPlugin('alert')

class HealthPlugin(GmetadPlugin):
    ''' This class implements the Health plugin that evaluates metrics and warns
        if out of bounds.'''

    STORE_IMP = 'storeimp'
    STORE_CFG = 'storecfg'

    _cfgDefaults = {
        STORE_IMP: "debug",
        STORE_CFG: "cfg"
    }

    def initConfDefaults(self):
        self.cfg = HealthPlugin._cfgDefaults

    def initConfHandlers(self):
        '''Init the handler array of configs'''
        self.cfgHandlers = {
            HealthPlugin.STORE_IMP: self._parseStoreImp,
            HealthPlugin.STORE_CFG: self._parseStoreCfg,
        }

    def _parseStoreImp(self, arg):
        ''' Parse the from address directive. '''
        v = arg.strip().strip('"')
        self.cfg[HealthPlugin.STORE_IMP] = v

    def _parseStoreCfg(self, arg):
        ''' Parse the from address directive. '''
        v = arg.strip().strip('"')
        self.cfg[HealthPlugin.STORE_CFG] = v

    def start(self):
        '''Called by the engine during initialization to get the plugin going.'''
        #print "Alert start called"
        pass
    
    def stop(self):
        '''Called by the engine during shutdown to allow the plugin to shutdown.'''
        #print "Alert stop called"
        pass

    def alert(self, level, host_ip, value, metric_rule, store):
        ''' Issue the alert on a host at specified level '''
        
        # Update the session info
        alertTime = int(time.time())
        session = store.getSession(metric_rule.id, host_ip)
        
        try:
            if session is None:
                store.newSession(metric_rule.id, host_ip, alertTime)
                session = store.getSession(metric_rule.id, host_ip)
            
            if session is None:
                logging.DEBUG("Something is wrong when new a session")
                return False
            
            # Check to guarantee the rule should not be hit too frequently
            if alertTime - session.lastAlert < session.INTERVAL:
                logging.info("AlertRule [%s] on metric [%s] alerts too frequently, pending ..." % (metric_rule.id, metric_rule.metricName))          
                return False
            elif alertTime - session.lastAlert >= session.MAX_IDLE:
                logging.info('AlertRule [%s] on metric [%s] on host [%s]'%(metric_rule.id, metric_rule.metricName, host_ip))
                store.renewSession(session.id, metric_rule.id, host_ip, alertTime)
                return False
            elif session.alertTimes <= metric_rule.alarmTimes:
                store.hitSession(session.id, metric_rule.id, host_ip, alertTime)
                return False
            
            # if session alarmTimes is beyond the threshold of rule's alarmTimes(setting), we alarm it, alert frequent alarmFrequency times
            if session.alertTimes > metric_rule.alarmTimes+metric_rule.alarmFrequency:
                #reset
                store.disable_HWRule(metric_rule.id, metric_rule.alarmProjectId, host_ip)
                store.renewSession(session.id, metric_rule.id, host_ip, alertTime)
                return False
            else:
                store.hitSession(session.id, metric_rule.id, host_ip, alertTime)
            
            contacts = store.getContacts(metric_rule.alarmProjectId)
        except Exception, e:
            print 'hello wrong1',e

        # Issue alert to every contact
        try:
            # alarm the last time and disable the rule
            temp = alarm_method_mappings[metric_rule.method]
            alarm_method = get_alert_method(temp)
            level_name = alarm_level_mappings[level]
            msg = metric_rule.getAlertMessage(time.ctime(alertTime), host_ip, level_name, metric_rule.metricName, value)
            sub = "Alert at level %s on host %s" % (level_name, host_ip)
            #if isinstance(alarm_method, MailMethod):
            #    pdb.set_trace()
            alarm_method.issueAlert(msg, sub, contacts)
            if session.alertTimes - metric_rule.alarmTimes == 1:
                store.storeAlertMsg(metric_rule, host_ip, sub, msg, alertTime)
        except Exception, e:
            print 'hello wrong!',e

        return True

    def notify(self, clusterNode):
        '''Called by the engine when the internal data source has changed.'''
        for hostNode in clusterNode:
            # Query a metricNode so that we can use it to generate a key
            for metricNode in hostNode:
                # Don't evaluate metrics that aren't numeric values.
                if metricNode.getAttr('type') in ['string', 'timestamp']:
                    continue
                try:
                    store = get_alert_store(self.cfg[HealthPlugin.STORE_IMP], self.cfg[HealthPlugin.STORE_CFG])
                    # get the host name
                    hostKey = hostNode.getAttr('name')
                    # get the metric of the host
                    metricRules = store.getHMRules(hostKey, metricNode.getAttr('name'), None)
                    for metricRule in metricRules:
                        # evalkey is metricNode.id:metricRule.metric , metricRule is the instance of AlertRule
                        evalKey = metricNode.generateKey([metricNode.id, metricRule.metricName])
                        # evalKey example: METRIC:load_one
                        evalNode = hostNode[evalKey]
                        if evalNode is None:
                            continue
                        if not metricRule.applyTo(hostKey):
                            continue

                        # If the Rule-check output Level > LEVEL_OK (LEVEL_WARNING/CRITICAL)
                        # then Issue the alert
                        value = metricNode.getAttr('val')
                        level = metricRule.check(value)
                        flag = False
                        if level > 0:
                            # return object of AlertSession
                            flag = self.alert(level, hostKey, value, metricRule, store)
                        
                            #logging.info('The Alert\'s flag is %s. True is run the alert, false means it\'s no need to alert or error occured when the function is running'%flag)

                except Exception, e:
                    print e
               #break
        #print "Alert notify called"
