import sys
import socket
import xml.sax
import StringIO
import time
import collections, time, ConfigParser, os
import datetime

time_format=''

def day_get(d):
    oneday = datetime.timedelta(days=1)
    day = d - oneday
    date_from = datetime.datetime(day.year, day.month, day.day, 0, 0, 0)
    date_to = datetime.datetime(day.year, day.month, day.day, 23, 59, 59)
    print '---'.join([str(date_from), str(date_to)])

def week_get(d):
    week_index=d.isoweekday()
    week_pace = datetime.timedelta(days=week_index-1)
    dayfrom = d - week_pace
    date_from = datetime.datetime(dayfrom.year, dayfrom.month, dayfrom.day, 0, 0, 0)
    date_to = datetime.datetime(d.year, d.month, d.day, d.hour, d.minute, d.second)
    print '---'.join([str(date_from), str(date_to)])

def month_get(d):
    date_from = datetime.datetime(d.year, d.month, 1, 0, 0, 0)
    date_to = datetime.datetime(d.year, d.month, d.day, d.hour, d.minute, d.second)
    print '---'.join([str(date_from), str(date_to)])

def quarter_get(d):
    month_index=d.month
    if month_index in (1,2,3):
        start_month=1
    elif month_index in (4,5,6):
        start_month=4
    elif month_index in (7,8,9):
        start_month=7
    elif month_index in (10,11,12):
        start_month=10
    date_from = datetime.datetime(d.year, start_month, 1, 0, 0, 0)
    date_to = datetime.datetime(d.year, d.month, d.day, d.hour, d.minute, d.second)
    print '---'.join([str(date_from), str(date_to)])
    return str(date_from), str(date_to)

def year_get(d):
    date_from = datetime.datetime(d.year, 1, 1, 0, 0, 0)
    date_to = datetime.datetime(d.year, d.month, d.day, d.hour, d.minute, d.second)
    print '---'.join([str(date_from), str(date_to)])


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


def aggr_avg_data(input_data):
    '''
    get average data value from list data

    '''
    # testdatas = [{"time": ["10-13 16:28", "10-13 16:29", "10-13 16:30"], "value":[11,22,33]},{"time":["10-13 16:28","10-13 16:29","10-13 16:30"],"value":[55,33,11]}]

    time_data = []
    value_data = []
    count=len(testdatas)
    # build time_data list
    for num in range(0,len(testdatas)):
        time_data.append(testdatas[num]['time'])
    for num in range(0,len(testdatas)):
        value_data.append(testdatas[num]['value'])

    result_data={'time': [], 'value': []}
    # remark the loop_tag to the default value 0, loop_tag is for ordered date comparasion
    loop_tag = [0 for loop in range(0, count)]
    for j in range(0, len(time_data[0])):
        ok_count = 1
        sum_value = value_data[0][j]
        cur_time = time.mktime(time.strptime(time_data[0][j],'%Y-%m-%d %H:%M'))
        for i in range(1,count):

            for k in range(loop_tag[i], len(time_data[i])):
                comp_time = time.mktime(time.strptime(time_data[i][k],'%Y-%m-%d %H:%M'))
                if float(cur_time) == float(comp_time):
                    ok_count += 1
                    loop_tag[i] = k
                    sum_value += value_data[i][k]
                    break
                elif float(cur_time) > float(comp_time):
                    continue
                else:
                    break
            # match every time value in the range list  then go on , or break
            if ok_count < i+1:
                break


        if ok_count == count:
            result_data['time'].append(time_data[0][j])
            result_data['value'].append(sum_value/count)

    if result_data['time'] == [] or result_data['value'] == []:
        result_data['data']='no legal data!'
    return result_data


class ChannelData(object):
    post_data = {"target": "", "metric": "", "timestamp": "", "monitor_type": ""}
    def __init__(self, **kwargs):
        for key in kwargs:
            if key in self.post_data.keys():
                self.post_data[key] = kwargs[key]
        self.post_data['monitor_type'] = ''

class VMData(ChannelData):
    # post_data = {"target": "", "metric": "", "timestamp": "", "monitor_type": ""}

    def __init__(self, **kwargs):
        super(VMData,self).__init__(**kwargs)
        self.post_data['monitor_type'] = 'vm'





if __name__ == '__main__':
    # #############################################################
    ganglia_host = '10.10.82.111'
    ganglia_port = 8657

    try:
        # list_a = [-1,0,1,-1,2,4]
        #
        # list_a.sort()
        # item_count= len(list_a)
        # print len(list_a)
        # i=0
        # for i in item_count-1:
        #     j=1
        #     for j in item_count-:
        #         a=(list_a[i],list_a[i+j])
        #
        #     i++
        #
        # print list_a
        d = datetime.datetime.now()
        day_get(d)
        week_get(d)
        month_get(d)
        start_time,end_time= quarter_get(d)
        print start_time,end_time
        year_get(d)

        # vm =VMData(target='target1',metric='metric1',timestamp='period1')
        # print vm.post_data
        # testdatas = [{"time": ["2014-10-13 16:28", "2014-10-13 16:29", "2014-10-13 16:30"], "value":[11,22,33]},
        #              {"time":["2014-10-13 16:29","2014-10-13 16:30","2014-10-13 16:31"],"value":[55,33,11]},
        #              {"time":["2014-10-13 16:29","2014-10-13 16:30","2014-10-13 16:31","2014-10-13 16:32",],"value":[55,55,11,20]},
        #               {"time":["2014-10-13 14:29","2014-10-14 16:30","2014-10-13 14:31"],"value":[55,33,11]},]
        #
        # xx=aggr_avg_data(testdatas)
        # print aggr_avg_data(testdatas)

        # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # s.connect((ganglia_host, ganglia_port))
        # file = s.makefile('r')
        # data = file.read().strip()
        # print data
        #
        # parser = xml.sax.make_parser()
        # handler = PhysicalMachineInfoHandler('10.10.82.111')
        # parser.setContentHandler(handler)
        # parser.parse(StringIO.StringIO(data))
        # print handler.metric

    except Exception, err:
        sys.exit(3)
