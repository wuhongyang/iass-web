from rest_framework import serializers

class RRDData:
    def __init__(self,time,value):
        self.time = time
        self.value = value


class RRDDataSerializer(serializers.Serializer):
    time = serializers.FloatField()
    value = serializers.FloatField()
    
    def restore_object(self, attrs, instance=None):
        if instance is not None:
            instance.time = attrs.get('time', instance.time)
            instance.value = attrs.get('value', instance.value)
            return instance
        return RRDData(**attrs)

class RRDEchart:
    def __init__(self,time_list,value_list):
        self.time_list=time_list
        self.value_list=value_list


class RRDEchartSerializer(serializers.Serializer):
    time = serializers.FloatField()
    value = serializers.FloatField()

    def restore_object(self, attrs, instance=None):
        if instance is not None:
            instance.time = attrs.get('time', instance.time)
            instance.value = attrs.get('value', instance.value)
            return instance
        return RRDEchart(**attrs)

