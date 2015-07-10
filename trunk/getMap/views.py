# encoding: utf-8
'''
Created on 2014年10月11日

@author: mhjlq1989@gmail.com
'''
import utils
import json
from rest_framework.decorators import detail_route, list_route, link
from rest_framework import viewsets
from models import VMwareHost
from models import VMwareInstance
from serializers import VMwareHostSerializer
from serializers import VMwareInstanceSerializer
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from django.http import Http404
import models
import serializers
from pysphere import VIServer,VIProperty
from pysphere.vi_mor import VIMor, MORTypes


def change_time_format(value):
    '''
    this function used to change system uptime from second to a human readable format:
    (1Days 2Hours 3Minutes)
    :param value:
    :return: time_str
    '''
    if value > 0:
        sec = value % 60
        value = (value/60)
        minute = value % 60
        value = (value/60)
        hour = value % 24
        value = (value/24)
        time_str = str(value) + "Days " + str(hour) + "Hours " + str(minute) + "Minutes "
        if minute == 0 and hour == 0 and value == 0:
            time_str = time_str + str(sec) + "Second"
    else:
        time_str = ""
    return time_str


class VMwareHostViewSet(viewsets.ReadOnlyModelViewSet):
    
    lookup_field = 'host_ip'
    lookup_value_regex = '[^/]+'
    queryset = VMwareHost.objects.all()
    serializer_class = VMwareHostSerializer
    
    @list_route(['get'])
    def get_count(self, request):
        try:
            count = self.queryset.count()
            content = {'hosts': count}
            return Response(content)
        except VMwareHost.DoesNotExist:
            raise Http404
    
    @link()
    def metrics(self, request, host_ip):
        try:
            metric = request.GET.get('metric') or 'cpu_usage'
            period = request.GET.get('period') or '1week'
            hd = utils.HostData()
            content = hd.get_host_data(metric, period, {'host_ip': host_ip})
            return Response(content)
        except VMwareHost.DoesNotExist:
            raise Http404

    def retrieve(self, request, *args, **kwargs):
        host_ip_r = kwargs['host_ip']
        try:
            host_serializer = serializers.VMwareHostSerializer(self.queryset.get(host_ip=host_ip_r))
            instances_set = models.VMwareInstance.objects.filter(host_ip=host_serializer.data['host_ip'])
            instances_count = instances_set.count()
            mem_used = 0
            vcpus = 0
            ecu = 0
            for instance in instances_set:
                mem_used += int(instance.mem[0:len(instance.mem)-2])
                a = int(instance.cpu[0:instance.cpu.find("vcpu")])
                vcpus += a
                ecu += int(instance.cpu[instance.cpu.find("ecu")-1:instance.cpu.find("ecu")]) * a
            host_serializer.data['memory_used'] = str(mem_used/1024) + "GB"
            host_serializer.data['vcpus_used'] = vcpus
            host_serializer.data['ecus_used'] = ecu
            host_serializer.data['instances_count'] = instances_count

            server = VIServer()
            server.connect(host_serializer.data['host_ip'], 'root', 'P@ssw0rd')
            properties = ['capability.maxSupportedVMs',
                          'capability.maxSupportedVcpus',
                          'runtime.bootTime',
                          'runtime.powerState',
                          'summary.config.product.osType',
                          'summary.config.product.fullName',
                          'summary.config.product.licenseProductVersion',
                          'summary.config.product.licenseProductName',
                          'summary.config.product.instanceUuid',
                          'hardware.cpuPowerManagementInfo.hardwareSupport']
            results = server._retrieve_properties_traversal(property_names=properties, obj_type=MORTypes.HostSystem)
            for result in results:
                for p in result.PropSet:
                    if p.Name == 'hardware.cpuInfo.hz':
                        value = str(p.Val/(1024*1024*1024)) + " GHz"
                    elif p.Name == 'hardware.memorySize':
                        value = str(p.Val/(1024*1024)) + " MB"
                    elif p.Name == 'config.certificate':
                        value = str(p.Val)
                    elif p.Name == 'runtime.bootTime':
                        value = str(p.Val[0]) + "-" + str(p.Val[1]) + "-" + str(p.Val[2]) + " "
                        value = value + str(p.Val[3]) + ":" + str(p.Val[4])
                    else:
                        value = str(p.Val)
                    name = p.Name.split('.')[-1]
                    host_serializer.data[name] = value

            return Response(host_serializer.data)
        except VMwareHost.DoesNotExist:
            raise Http404

    def list(self, request, *args, **kwargs):
        try:
            host_serializer = serializers.VMwareHostSerializer(self.queryset, many=True)
            for hostEntry in host_serializer.data:
                instances_set = models.VMwareInstance.objects.filter(host_ip=hostEntry['host_ip'])
                instances_count = instances_set.count()
                hostEntry['instances_count'] = instances_count
                '''
                mem_used = 0
                vcpus = 0
                ecu = 0
                for instance in instances_set:
                    mem_used += int(instance.mem[0:len(instance.mem)-2])
                    a = int(instance.cpu[0:instance.cpu.find("vcpu")])
                    vcpus += a
                    ecu += int(instance.cpu[instance.cpu.find("ecu")-1:instance.cpu.find("ecu")]) * a
                hostEntry['memory_used'] = str(mem_used/1024) + "GB"
                hostEntry['vcpus_used'] = vcpus
                hostEntry['ecus_used'] = ecu

                server = VIServer()
                server.connect(hostEntry['host_ip'], 'root', 'P@ssw0rd')
                properties = ['capability.maxSupportedVMs',
                              'capability.maxSupportedVcpus',
                              'runtime.bootTime',
                              'runtime.powerState',
                              'summary.config.product.osType',
                              'summary.config.product.fullName',
                              'summary.config.product.licenseProductVersion',
                              'summary.config.product.licenseProductName',
                              'summary.config.product.instanceUuid',
                              'hardware.cpuPowerManagementInfo.hardwareSupport']
                results = server._retrieve_properties_traversal(property_names=properties, obj_type=MORTypes.HostSystem)
                for result in results:
                    for p in result.PropSet:
                        if p.Name == 'hardware.cpuInfo.hz':
                            value = str(p.Val/(1024*1024*1024)) + " GHz"
                        elif p.Name == 'hardware.memorySize':
                            value = str(p.Val/(1024*1024)) + " MB"
                        elif p.Name == 'config.certificate':
                            value = str(p.Val)
                        elif p.Name == 'runtime.bootTime':
                            value = str(p.Val[0]) + "-" + str(p.Val[1]) + "-" + str(p.Val[2]) + " "
                            value = value + str(p.Val[3]) + ":" + str(p.Val[4])
                        else:
                            value = str(p.Val)
                        name = p.Name.split('.')[-1]
                        hostEntry[name] = value
                '''
            return Response(host_serializer.data)
        except VMwareHost.DoesNotExist:
            raise Http404


class VMwareInstanceViewSet(viewsets.ReadOnlyModelViewSet):
    
    lookup_field = 'host_ip'
    lookup_value_regex = '[^/]+'
    queryset = VMwareInstance.objects.all()
    serializer_class = VMwareInstanceSerializer
    
    @link()
    def get_count(self, request, host_ip):
        try:
            data = self.queryset.filter(host_ip=host_ip)
            count = data.__len__()
            content = {'host_ip': host_ip, 'hosts': count}
            return Response(content)
        except VMwareInstance.DoesNotExist:
            raise Http404
    
    @link()
    def ins_list(self, request, host_ip):
        try:
            data = self.queryset.filter(host_ip=host_ip)
            content = self.serializer_class(data, many=True)
            for con in content.data:
                uptime = con['up_time']
                if uptime.strip() == '':
                    time_str = " "
                else:
                    time_str = change_time_format(int(uptime))
                con['up_time'] = time_str
            return Response(content.data)
        except VMwareInstance.DoesNotExist:
            raise Http404

    @link()
    def info(self, request, host_ip):
        try:
            instance_name = request.GET.get('ins_name') or None
            if instance_name is None:
                content = {'Error!': 'Instance name is None,You must specify instance name'}
                return Response(content)
            else:
                instance_serializer = serializers.VMwareInstanceSerializer(self.queryset.get(instance_name=instance_name))
                uptime = instance_serializer.data['up_time']
                if uptime.strip() == '':
                    time_str = " "
                else:
                    time_str = change_time_format(int(uptime))
                instance_serializer.data['up_time'] = time_str

                server = VIServer()
                server.connect(host_ip, 'root', 'P@ssw0rd')
                properties = ['name', 'runtime.maxCpuUsage', 'runtime.maxMemoryUsage', 'summary.config.vmPathName',
                              'runtime.suspendInterval', 'config.instanceUuid', 'config.locationId',
                              'summary.config.cpuReservation', 'config.guestFullName', 'config.version',
                              'guest.guestState', 'guest.hostName', 'guest.ipAddress',  'runtime.bootTime',
                              'runtime.connectionState']
                results = server._retrieve_properties_traversal(property_names=properties, obj_type=MORTypes.VirtualMachine)
                for result in results:
                    for p in result.PropSet:
                        if p.Name == 'name' and p.Val != instance_name:
                            break
                        pname = p.Name.split('.')[-1]
                        if p.Name != 'name':
                            pvalue = p.Val
                            instance_serializer.data[pname] = pvalue
                        if p.Name == 'runtime.bootTime':
                            v = p.Val
                            pvalue = str(v[0]) + '-' + str(v[1]) + '-' + str(v[2]) + ' ' + str(v[3]) + ':' + str(v[4])
                            instance_serializer.data[pname] = pvalue
            return Response(instance_serializer.data)
        except VMwareInstance.DoesNotExist:
            raise Http404

    @link()
    def metrics(self, request, host_ip):
        try:
            instance_name = request.GET.get('ins_name') or None
            if instance_name is None:
                content = {'Error!': 'Instance name is None,You must specify instance name'}
            else:
                metric = request.GET.get('metric') or 'cpu_usage'
                period = request.GET.get('period') or '1week'
                id = utils.InstanceData()
                content = id.get_instance_data(metric, period, {'instance_name': instance_name, 'host_ip': host_ip})
            return Response(content)
        except VMwareInstance.DoesNotExist:
            raise Http404