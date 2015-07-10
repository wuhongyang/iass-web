# encoding: utf-8
'''
Created on 2014年10月13日

@author: mhjlq1989@gmail.com
'''
import httplib
import json
import logging
import urllib
import models
from django.conf import settings

HOST_PORT = settings.DATACHANNEL_PORT
HOST_IP = settings.VMWARE_DATACHANNEL_IP

def get_data(post_data):
    
    http_method = 'post'
    uri = '/rrddata/'
    headers = {'Content-Type': 'application/json'}
    try:
        conn = httplib.HTTPConnection(HOST_IP, HOST_PORT, timeout=30)
    except:
        logging.error("can not access to '$%:$%' " % (HOST_IP,HOST_PORT),)
        raise
    conn.request(http_method, uri, json.dumps(post_data), headers)
    resp = conn.getresponse()
    result = resp.read() or ''
    conn.close()
    
    return result

class InstanceData(object):
    
    def __init__(self):
        self.post_data={}
    
    def get_instance_data(self, metric, period, filter):
        '''
        @param filter: {'host_ip':'10.10.82.247', 'instance_name':'183441b0-c688-4aec-a830-4c02d04ed92d'}
        '''
        self.post_data['monitor_type'] = 'vmware'
        self.post_data['target'] = filter['host_ip'] + '_' + filter['instance_name']
        self.post_data['metric'] = metric
        self.post_data['timestamp'] = period        
        return get_data(self.post_data)

class HostData(object):
    
    def __init__(self):
        self.post_data={}
    
    def get_host_data(self, metric, period, filter):
        '''
        @param filter: {'host_ip':'10.10.82.247', 'instance_name':'183441b0-c688-4aec-a830-4c02d04ed92d'}
        '''
        if not isinstance(filter, dict):
            return
        
        self.post_data['monitor_type'] = 'vmware'
        self.post_data['target'] = filter['host_ip']
        self.post_data['metric'] = metric
        self.post_data['timestamp'] = period
        return get_data(self.post_data)

#print get_data("10.10.82.158", 8000, {'monitor_type':'vmware','target':'10.10.82.9','metric':'mem_usage','timestamp':'1week'})