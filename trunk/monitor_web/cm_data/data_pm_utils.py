import ConfigParser
import os
import collections
import time
import rrdtool
import sys
import socket
import xml.sax
import StringIO
from django.conf import settings

class PhysicalMachineData(object):
    metric_file = ''
    start_time = ''
    end_time = ''
    resolution = ''
    cf = ''
    metric = ''
    time_format = ''
    rrd_section = '1hour'

    def __init__(self):
        pass

    def rra_mapping(self, rrd_section):
        cp = ConfigParser.ConfigParser()
        conf_dir = os.path.dirname(__file__)
        conf_file = os.path.join(conf_dir, 'rra_api.conf')
        cp.read(conf_file)
        if rrd_section in cp.sections():
            self.rrd_section = rrd_section
            self.resolution = cp.get(rrd_section, "resolution")
            self.cf = cp.get(rrd_section, "cf")
            self.time_format = cp.get(rrd_section, "time_format")

    def get_data(self, target, metric, period):
        self.metric_file = settings.PHYSICAL_RRD_BASE_PATH + target + '/' + metric + '.rrd'
        if period == '1sec':
            self.start_time = 'end-10min'
        else:
            self.start_time = 'end-'+period
        self.end_time = 'now'
        self.rra_mapping(period)
        if not os.path.exists(self.metric_file):
                return 'Can\'t fetch the specific rrd data file , please check your params!'
        try:
            data = rrdtool.fetch(self.metric_file.encode("utf-8"), self.cf.encode("utf-8"), "--resolution", self.resolution.encode("utf-8"),
                                      "--start", self.start_time.encode("utf-8"), "--end", self.end_time.encode("utf-8"))

            instance_datas = collections.OrderedDict()
            instance_datas["time"] =[]
            instance_datas["value"] = []
            starttime = data[0][0]
            endtime = data[0][1]
            step = data[0][2]
            timelists = range(starttime + step, endtime + step, step)
            time_str_lists = []
            result_lists = []
            value = data[2]

            if len(value) == 1:
                # value length is one
                time_one = time.strftime(self.time_format, time.localtime(endtime))
                instance_datas["time"].append(time_one)
                value_one = (value[0][0] if value[0][0] is None else 0)
                instance_datas["value"].append(value_one)
                '''
                commented for cpu_uasge by lijun
                if self.metric == 'cpu_idle':
                    value_one = (value[0][0] if value[0][0] is None else 100)
                    instance_datas["value"].append(value_one)
                else:
                    value_one = (value[0][0] if value[0][0] is None else 0)
                    instance_datas["value"].append(value_one)
             '''
            else:
                flag = False  # flag is for reverse None data values filtering
                data_value = 0
                none_count = 0
                for i in range(len(value) - 1, -1, -1):
                    # comment: range(1,5,1) --> [1, 2, 3, 4]
                    if value[i][0] is None and flag is False:
                        none_count += 1
                        # if continuous None values more than five counts , set the flag to true
                        if none_count >= 5:
                            flag = True
                        continue
                    elif value[i][0] is None and flag is True:
                        # set the default value for None data
                        data_value = 0
                        '''commented for cpu_uasge by lijun
                        if metric == 'cpu_idle':
                            data_value = 100
                        else:
                            data_value = 0
                    '''
                    else:
                        flag = True
                        # summary data values: rra [sum]/[num], normal data values: rra [sum]
                        if len(value[i]) == 1:
                            data_value = value[i][0]
                        else:
                            data_value = value[i][0] / value[i][1]
                    time_time = time.localtime(timelists[i])
                    time_str_lists.append(time.strftime(self.time_format, time_time))
                    # modified by lijun 2015-1-16
                    if metric == 'bytes_in' or metric == 'bytes_out':
                        if isinstance(data_value,tuple):
                            data_value =(round(data_value[0]/1024,2), data_value[1])
                        else:
                            data_value = round(data_value/1024,2)

                    result_lists.append(data_value)
                # if [1sec] section selected , return the last date
                if self.rrd_section == '1sec':
                    instance_datas["time"].append(time_str_lists[0])
                    instance_datas["value"].append(result_lists[0])
                else:
                    time_str_lists.reverse()
                    result_lists.reverse()
                    instance_datas["time"] = time_str_lists
                    instance_datas["value"] = result_lists
            return instance_datas
        except Exception as err:
            raise err

    def get_host_info(self, host_address):
        ganglia_host = settings.GMOND_HOST
        ganglia_port = int(settings.GMOND_PORT)

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ganglia_host, ganglia_port))
            socket_file = s.makefile('r')
            data = socket_file.read().strip()

            parser = xml.sax.make_parser()
            handler = PhysicalMachineInfoHandler(host_address)
            parser.setContentHandler(handler)
            parser.parse(StringIO.StringIO(data))

            host_info = handler.metric
            boot_time = time.localtime(float(host_info['boottime']))
            #running_time = time.localtime(time.time()) - boot_time
            host_info['boottime'] = time.strftime('%Y-%m-%d %H:%M:%S',boot_time)
            #host_info['running_time'] = time.strftime('%m-%d %H:%M:%S',running_time)
            return host_info
        except Exception, err:
            raise err


class PhysicalMachineInfoHandler(xml.sax.ContentHandler):
    metric_attrs_tag = None
    metric = {}
    host_address = None
    flag = False
    metric_keys = ['os_name', 'os_release', 'mem_total', 'boottime', 'disk_total', 'machine_type', 'cpu_num',
                   'cpu_speed']

    def __init__(self, host_address):
        self.host_address = host_address

    def startDocument(self):
        print 'start xml document'

    def startElement(self, name, attrs):
        if name == 'HOST' and attrs['NAME'].encode('utf-8') == self.host_address:
            self.flag = True
        elif name == 'METRIC' and self.flag == True:
            if attrs['NAME'].encode('utf-8') in self.metric_keys:
                self.metric_attrs_tag = attrs['NAME']
                self.metric[attrs['NAME'].encode('utf-8')] = attrs['VAL'].encode('utf-8')

    def endElement(self, name):
        if name == 'HOST':
            self.flag = False
        elif name == 'METRIC' and self.metric_attrs_tag is not None:
            self.metric_attrs_tag = None

    def endDocument(self):
        print 'end xml document'



