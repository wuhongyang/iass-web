# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
# * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals

from django.db import models


class CmAlarmGroup(models.Model):
    alarm_group_name = models.CharField(max_length=255)
    alarm_group_desc = models.CharField(max_length=512)

    class Meta:
        managed = False
        db_table = 'cm_alarm_group'


class CmAlarmUser(models.Model):
    alarm_user_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=255,unique=True)
    office_phone = models.CharField(max_length=255)
    remark = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'cm_alarm_user'


class CmUserGroupMapping(models.Model):
    alarm_group_id = models.BigIntegerField()
    alarm_user_id = models.BigIntegerField()
    alarm_group_name = models.CharField(max_length=255, null=True)
    alarm_user_name = models.CharField(max_length=255, null=True)
    alarm_config = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cm_user_group_mapping'


class CmAlarmHistory(models.Model):
    # id = models.BigIntegerField(primary_key=True)
    alarm_rule_id = models.BigIntegerField()
    metric_name = models.CharField(max_length=255)
    metric_desc = models.CharField(max_length=255)
    alarm_time = models.DateTimeField(auto_now=True)
    alarm_content_summary = models.CharField(max_length=1000)
    alarm_content = models.TextField()
    alarm_group_ids = models.CharField(max_length=255)
    alarm_group_names = models.CharField(max_length=255)
    fixed_ip = models.CharField(max_length=255)
    is_verify = models.IntegerField(default=0)
    class Meta:
        managed = False
        db_table = 'cm_alarm_history'

class CmAlarmHistoryMonth(models.Model):
    count = models.BigIntegerField()
    alarm_time = models.CharField(max_length=100)
    class Meta:
        managed = False
        db_table = 'cm_alarm_history_month_count'


class CmAlarmMapping(models.Model):
    alarm_project_id = models.BigIntegerField()
    fixed_ip = models.CharField(max_length=39)
    is_vm = models.IntegerField(blank=True, null=True)
    alarm_group_ids = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'cm_alarm_mapping'


class CmAlarmProject(models.Model):

    alarm_project_name = models.CharField(max_length=255)
    alarm_project_desc = models.CharField(max_length=255,null=True,blank=True)
    alarm_group_ids = models.CharField(max_length=255)
    update_time = models.DateTimeField(auto_now=True)
    is_auto = models.IntegerField(default=0)
    class Meta:
        managed = False
        db_table = 'cm_alarm_project'


class CmAlarmRule(models.Model):
    # id = models.BigIntegerField(primary_key=True)
    alarm_times = models.IntegerField()
    metric_id = models.BigIntegerField()
    metric_name = models.CharField(max_length=255)
    metric_desc = models.CharField(max_length=255)
    alarm_project_id = models.BigIntegerField()
    alarm_project_name = models.CharField(max_length=255)
    disabled = models.IntegerField(default=0)
    alarm_frequency = models.IntegerField(default=0)
    alarm_method = models.IntegerField(blank=True, null=True)
    statistic = models.IntegerField(default=0)
    comparison_operator = models.CharField(max_length=255)
    threshold = models.CharField(max_length=64)
    alarm_level = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'cm_alarm_rule'


class CmMetric(models.Model):
    metric_name = models.CharField(max_length=255)
    metric_desc = models.CharField(max_length=255)
    metric_unit = models.CharField(max_length=45, null=True)
    class Meta:
        managed = False
        db_table = 'cm_metric'


class Mappings(models.Model):
    fixed_ip = models.CharField(primary_key=True, max_length=39)
    floating_ip = models.CharField(max_length=39, blank=True)
    is_vm = models.IntegerField(blank=True, null=True)
    instance_name = models.CharField(max_length=255, blank=True)
    uuid = models.CharField(max_length=36, blank=True)
    os_type = models.CharField(max_length=255, blank=True)
    host_address = models.CharField(max_length=39, blank=True)
    host_name = models.CharField(max_length=255, blank=True)
    user_id = models.CharField(max_length=64, blank=True)
    user_name = models.CharField(max_length=255, blank=True)
    rootfs_gb = models.IntegerField(blank=True, null=True, db_column='root_gb')
    storage_gb = models.IntegerField(blank=True, null=True, db_column='ephemeral_gb')
    memory_mb = models.IntegerField(blank=True, null=True)
    vcpus = models.IntegerField(blank=True, null=True)
    ecus_per_vcpu = models.IntegerField(blank=True, null=True)
    az = models.CharField(max_length=255, blank=True)
    project_id = models.CharField(max_length=64, blank=True)
    project_name = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mappings'

class CmAlarmDisabled(models.Model):
    alarm_rule_id = models.BigIntegerField()
    alarm_project_id = models.BigIntegerField()
    fixed_ip = models.CharField(max_length=255)
    expired = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'cm_alarm_disabled'

