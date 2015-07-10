"""
    cm_data.serializers
    ~~~~~~~~~~~~~
"""
from rest_framework import serializers
import models

class CmUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MisUmuser
        fields = ('user_id', 'user_name', 'logon_id', 'parent_name', 'email', 'office_phone', 'mobile')
        read_only = True

class CmOrgSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MisUmorg
        fields = ('org_id', 'org_name', 'parent_name')
        read_only = True

class CmNovaQuotaUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CmNovaQuotaUsages
        fields = ('resource', 'in_use')
        read_only = True


class CmNovaQuotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CmNovaQuotas
        fields = ('id', 'project_id', 'resource', 'hard_limit', 'deleted')
        read_only = True


class CmUserInstaMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CmUserInstaMapping
        fields = ('fixed_ip', 'instance_name', 'uuid', 'os_type', 'host_ip', 'host_name', 'user_name',
                  'rootfs_gb', 'storage_gb', 'memory_mb', 'vcpus', 'ecus_per_vcpu', 'az', 'project_id')
        read_only = True


class CmNovaHostsSerializer(serializers.ModelSerializer):
    ecus = serializers.SerializerMethodField('ecus_compute')
    vcpus = serializers.SerializerMethodField('vcpus_compute')
    ecus_used = serializers.SerializerMethodField('ecus_used_compute')

    def ecus_compute(self, cmnovahost):
        return cmnovahost.cpus * 4

    def vcpus_compute(self, cmnovahost):
        return cmnovahost.cpus * 4

    def ecus_used_compute(self, cmnovahost):
        return 0

    class Meta:
        model = models.CmNovaHosts
        fields = ('cpus', 'memory_mb', 'storage_gb', 'vcpus_used', 'memory_mb_used', 'storage_gb_used', 'hypervisor_type',
                  'hypervisor_version', 'cpu_info', 'vms', 'host_name', 'host_ip', 'ecus', 'vcpus', 'ecus_used')
        read_only = True

class WorkOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WorkOrder
        read_only = True

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Device
        fields = ('name', 'model', 'classification', 'detail', 'purchase_time', 'online_time','host_ip')