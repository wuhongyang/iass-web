# encoding: utf-8
'''
Created on 2014年10月11日

@author: mhjlq1989@gmail.com
'''
from django.db import models

class VMwareHost(models.Model):
    
    host_ip = models.CharField(primary_key=True)
    host_name = models.CharField(null=True)
    cpu = models.CharField(null=True)
    mem = models.CharField(null=True)
    host_user = models.CharField(null=False)
    host_password = models.CharField(null=False)
    is_dirty = models.IntegerField(null=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    
    class Meta:
        managed = False
        db_table = 'vmware_host'

class VMwareInstance(models.Model):
    
    host_ip = models.CharField(primary_key=True)
    host_name = models.CharField(null=False, default='')
    instance_name = models.CharField(primary_key=True,default='')
    cpu = models.CharField(null=True)
    mem = models.CharField(null=True)
    power_state = models.CharField(null=True)
    up_time = models.CharField(null=True)
    
    class Meta:
        managed = False
        db_table = 'vmware_instance'