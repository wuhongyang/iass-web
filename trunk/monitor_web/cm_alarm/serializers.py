from rest_framework import serializers
from cm_alarm.models import CmAlarmGroup, CmAlarmUser, CmUserGroupMapping, CmAlarmHistory, CmMetric, CmAlarmRule, \
    CmAlarmProject, CmAlarmMapping,Mappings,CmAlarmHistoryMonth

'''
Created on 2014-9-28

@author: Administrator
'''


class CmAlarmGroupSerializer(serializers.Serializer):
    pk = serializers.Field()
    alarm_group_name = serializers.CharField(max_length=255)
    alarm_group_desc = serializers.CharField(max_length=512)

    def restore_object(self, attrs, instance=None):
        """
        Given a dictionary of deserialized field values, either update
        an existing model instance, or create a new model instance.
        """
        if instance:
            # Update existing instance
            instance.alarm_group_name = attrs.get('alarm_group_name', instance.alarm_group_name)
            instance.alarm_group_desc = attrs.get('alarm_group_desc', instance.alarm_group_desc)
            return instance

        # Create new instance
        return CmAlarmGroup(**attrs)


class CmAlarmUserSerializer(serializers.Serializer):
    pk = serializers.Field()
    alarm_user_name = serializers.CharField(max_length=255)
    email = serializers.CharField(max_length=255)
    phone = serializers.CharField(max_length=255)
    office_phone = serializers.CharField(max_length=255)
    remark = serializers.CharField(max_length=255)

    def restore_object(self, attrs, instance=None):
        if instance:
            # Update existing instance
            instance.pk = attrs.get('pk', instance.pk)
            instance.alarm_user_name = attrs.get('alarm_user_name', instance.alarm_user_name)
            instance.email = attrs.get('email', instance.email)
            instance.phone = attrs.get('phone', instance.phone)
            instance.office_phone = attrs.get('office_phone', instance.office_phone)
            instance.remark = attrs.get('remark', instance.remark)
            return instance
        # Create new instance
        return CmAlarmUser(**attrs)



class CmUserGroupMappingSerializer(serializers.Serializer):
    # pk = serializers.Field()
    alarm_user_id = serializers.IntegerField(required=True)
    alarm_group_id = serializers.IntegerField(required=True)
    alarm_group_name = serializers.CharField(max_length=255, allow_none=True)
    alarm_user_name = serializers.CharField(max_length=255, allow_none=True)
    alarm_config = serializers.IntegerField(blank=True)

    def restore_object(self, attrs, instance=None):
        if instance:
            # Update existing instance
            instance.alarm_group_name = attrs.get('alarm_group_name', instance.alarm_group_name)
            instance.alarm_user_name = attrs.get('alarm_user_name', instance.alarm_user_name)
            instance.alarm_config = attrs.get('alarm_config', instance.alarm_config)
            instance.alarm_group = attrs.get('alarm_group_id', instance.alarm_group_id)
            instance.alarm_group = attrs.get('alarm_user_id', instance.alarm_user_id)
            return instance

        # Create new instance
        return CmUserGroupMapping(**attrs)


class CmAlarmHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CmAlarmHistory
        fields = ('id','metric_desc','alarm_time','fixed_ip','alarm_group_names','alarm_content_summary','is_verify')
        read_only = True

class CmAlarmHistoryMonthSerializer(serializers.ModelSerializer):
    class Meta:
        model = CmAlarmHistoryMonth
        fields = ('alarm_time','count')
        read_only = True


class CmAlarmMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CmAlarmMapping


class CmAlarmProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = CmAlarmProject


class CmAlarmRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CmAlarmRule

class GetCmAlarmRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CmAlarmRule
        fields = ('id','alarm_times','metric_name','metric_desc','metric_id','alarm_project_name','comparison_operator','threshold','alarm_level','alarm_method','alarm_frequency')


class CmMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = CmMetric

class MappingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mappings
