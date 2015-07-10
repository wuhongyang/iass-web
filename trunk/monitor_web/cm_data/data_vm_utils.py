from __future__ import division
import httplib, urllib, json
import models
from django.conf import settings
import time, ConfigParser, os
from django.http import Http404
'''
Created on 2014-9-28

@author: Lijun
'''

HOST_PORT = settings.DATACHANNEL_PORT
# TIME_FORMAT = {'1sec': '%m-%d %H:%M', '1hour': '%m-%d %H:%M', '1day': '%m-%d %H:%M', '1week': '%m-%d %H',
#                '1mon': '%Y-%m-%d', '1year': '%Y-%m-%d'}

def get_time_format(period):
        time_format = ''
        cp = ConfigParser.ConfigParser()
        conf_dir = os.path.dirname(__file__)
        conf_file = os.path.join(conf_dir, 'rra_api.conf')
        cp.read(conf_file)
        if period in cp.sections():
            time_format = cp.get(period, "time_format")
        return time_format

def get_data(host, post_data):
    http_method = 'POST'
    headers = {'Content-type': 'application/json'}
    request_uri = '/rrddata/?format=json'
    try:
        conn = httplib.HTTPConnection(host, HOST_PORT, timeout=30)
    except:
        # logging.error('can not access to $% : $% ', (host, HOST_PORT))
        raise
    conn.request(http_method, request_uri, json.dumps(post_data), headers)
    resp = conn.getresponse()
    result_data = eval(resp.read())
    conn.close()
    # result data should be dict or list type, and not string type
    if isinstance(result_data, str):
        # logging.error('response from %s : %s', host, HOST_PORT)
        # logging.error('error msg: %s', result_data)
        return None

    return result_data


def aggr_avg_data(input_data, time_format):
    '''
    get average data value from list data
    '''
    # testdatas = [{"time": ["10-13 16:28", "10-13 16:29", "10-13 16:30"], "value":[11,22,33]},{"time":["10-13 16:28","10-13 16:29","10-13 16:30"],"value":[55,33,11]}]
    if len(input_data) == 0:
        return 'Data set list is empty!'
    time_data = []
    value_data = []
    count=len(input_data)
    # build time_data list
    for num in range(0,len(input_data)):
        time_data.append(input_data[num]['time'])
    for num in range(0,len(input_data)):
        value_data.append(input_data[num]['value'])

    result_data={'time': [], 'value': []}
    # remark the loop_tag to the default value 0, loop_tag is for ordered date comparasion
    loop_tag = [0 for loop in range(0, count)]
    for j in range(0, len(time_data[0])):
        ok_count = 1
        sum_value = value_data[0][j][0]
        num_value = value_data[0][j][1]
        cur_time = time.mktime(time.strptime(time_data[0][j],time_format))
        for i in range(1,count):

            for k in range(loop_tag[i], len(time_data[i])):
                comp_time = time.mktime(time.strptime(time_data[i][k],time_format))
                if float(cur_time) == float(comp_time):
                    ok_count += 1
                    loop_tag[i] = k
                    sum_value += value_data[i][k][0]
                    num_value += value_data[i][k][1]
                    break
                elif float(cur_time) > float(comp_time):
                    continue
                else:
                    break
            # match every time value in the range list  then go on , or break
            if ok_count < i+1:
                break

        if ok_count == count:
            if num_value == 0:
                result_data['data']='no legal data!'
            else:
                result_data['time'].append(time_data[0][j])
                result_data['value'].append(round(sum_value/num_value, 2))

    if result_data['time'] == [] or result_data['value'] == []:
        result_data['data']='no legal data!'
    return result_data


class ChannelData(object):
    post_data = {"target": "", "metric": "", "timestamp": "", "monitor_type": ""}
    def __init__(self, **kwargs):
        for key in kwargs:
            if key in self.post_data.keys():
                self.post_data[key] = kwargs[key]
            '''
            commented for cpu_usage 2014-11-27
            # if key == 'metric' and kwargs[key] == 'cpu_usage':
            #     self.post_data[key] = 'cpu_idle'
          '''
        # self.post_data['monitor_type'] = ''

class VMData(ChannelData):

    def __init__(self, **kwargs):
        try:
            super(VMData,self).__init__(**kwargs)
            self.mapping = models.CmUserInstaMapping.objects.get(fixed_ip=self.post_data['target'])
        except models.CmUserInstaMapping.DoesNotExist:
            # logging.error('can not find correct hosts node!')
            raise Http404


class DepartData(ChannelData):

    def __init__(self, **kwargs):
        super(DepartData,self).__init__(**kwargs)
        self.hosts = models.CmUserInstaMapping.objects.filter(project_id=self.post_data["target"]).values('host_ip').distinct()
        if self.hosts.count() == 0:
            # logging.error('can not find correct hosts node!')
            raise Http404


class UserData(ChannelData):

    def __init__(self, **kwargs):
        super(UserData,self).__init__(**kwargs)
        self.hosts = models.CmUserInstaMapping.objects.filter(user_id=self.post_data['target']).values('host_ip').distinct()
        if self.hosts.count() == 0:
            # logging.error('can not find correct hosts node!')
            raise Http404

class PlatformData(ChannelData):

    def __init__(self, **kwargs):
        super(PlatformData,self).__init__(**kwargs)
        self.hosts = models.CmUserInstaMapping.objects.filter(is_vm=0).values('host_ip')
        if self.hosts.count() == 0:
            raise Http404
            # logging.error('can not find correct hosts node!')


class Visitor(object):
    def visit(self, node):
        meth_name = 'visit_'+ node.__class__.__name__
        meth = getattr(self, meth_name, None)
        if not meth:
            raise Http404
        return meth(node)


    def visit_aggr_data(self,node):
        rrd_data_list = []
        for host in node.hosts:
            rrd_data = get_data(host["host_ip"], node.post_data)
            # logging.info(node.post_data['metric'] +' rrd_data:'+ str(rrd_data))
            if rrd_data is not None:
                rrd_data_list.append(rrd_data)
        time_format=get_time_format(node.post_data['timestamp'])
        result_data =aggr_avg_data(rrd_data_list, time_format)
        '''commented for cpu_uasge by lijun
        if node.post_data['metric'] == 'cpu_idle':
             for i in range(0, len(result_data['value'])):
                    result_data['value'][i] = 100 - result_data['value'][i]
        else:
            pass
        '''
        return result_data

    def visit_VMData(self, node):
        result_data = get_data(node.mapping.host_ip, node.post_data)
        ''' commented for cpu_uasge by lijun
        if node.post_data['metric'] == 'cpu_idle':
             for i in range(0, len(result_data['value'])):
                    result_data['value'][i] = 100 - result_data['value'][i]
        else:
            pass
        '''
        return result_data


    def visit_DepartData(self, node):
        return self.visit_aggr_data(node)

    def visit_UserData(self, node):
        return self.visit_aggr_data(node)

    def visit_PlatformData(self, node):
         return self.visit_aggr_data(node)


