from django import forms

class RRDForm(forms.Form):
    #target = forms.IPAddressField(label='IP')
    monitor_type = forms.CharField(max_length=100,label='monitor_type')
    target = forms.CharField(max_length=100,required=False,label='target')
    metric = forms.CharField(max_length=100,label='metric')
    timestamp = forms.CharField(max_length=100,label='timestamp')
