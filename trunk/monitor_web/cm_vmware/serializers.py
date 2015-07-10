# encoding: utf-8
'''
Created on 2014年10月11日

@author: mhjlq1989@gmail.com
'''
from rest_framework import serializers
from models import VMwareHost
from models import VMwareInstance

class VMwareHostSerializer(serializers.ModelSerializer):
    class Meta:
        model = VMwareHost
        fields = ('host_ip', 'host_name', 'cpu', 'mem', 'created_at', 'updated_at')

class VMwareInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VMwareInstance
        fields = ('host_ip','host_name','instance_name','cpu','mem','power_state','up_time')