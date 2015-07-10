'''
Created on 2014-9-25

@author: Administrator
'''
from django.db import models
from django.forms import ModelForm
from cm_alarm.models import CmAlarmGroupUser, CmAlarmGroup


class CmAlarmGroupUserForm(ModelForm):
    class Meta:
        model = CmAlarmGroupUser


# def __init__(self, *args, **kwargs):
#         #group_id = kwargs.pop('alarm_group_id','')
#         group_id = args[0]['alarm_group_id']
#         super(CmAlarmGroupUserForm, self).__init__(*args, **kwargs)
# #       self.fields['alarm_group']= forms.ModelChoiceField(queryset=CmAlarmGroup.objects.filter(pk=group_id))
#         self.fields['alarm_group'].queryset=CmAlarmGroup.objects.filter(pk=group_id)
#         print "xxx"

class CmAlarmGroupForm(ModelForm):
    class Meta:
        model = CmAlarmGroup