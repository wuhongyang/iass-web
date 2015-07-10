# coding:utf-8
from django.db import models
# Create your models here.

class CmUsertenant(models.Model):

    id = models.BigIntegerField(primary_key=True)
    username = models.CharField(max_length=64)
    tenantid = models.CharField(db_column='tenantId', max_length=256)  # Field name made lowercase.
    usertype = models.IntegerField(db_column='userType')  # Field name made lowercase.
    uid = models.CharField(max_length=64, blank=True)
    createtime = models.BigIntegerField(db_column='createTime', blank=True, null=True)  # Field name made lowercase.
    passstrenth = models.IntegerField(db_column='passStrenth', blank=True, null=True)  # Field name made lowercase.
    ccid = models.CharField(db_column='ccId', max_length=64, blank=True)  # Field name made lowercase.
    ccname = models.CharField(db_column='ccName', max_length=256, blank=True)  # Field name made lowercase.
    email = models.CharField(max_length=512, blank=True)
    description = models.CharField(max_length=512, blank=True)

    class Meta:
        managed = False
        db_table = 'CM_UserTenant'
        verbose_name = "cmuser"


class CmConfig(models.Model):

    id = models.BigIntegerField(primary_key=True)
    type = models.CharField(max_length=64)
    confkey = models.CharField(db_column='confKey', max_length=256)  # Field name made lowercase.
    confvalue = models.CharField(db_column='confValue', max_length=256)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'CM_Config'
        verbose_name = "cmuser"


class CmNovaQuotaUsages(models.Model):
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    id = models.IntegerField(primary_key=True)  # AutoField?
    project_id = models.CharField(max_length=255, blank=True)
    resource = models.CharField(max_length=255, blank=True)
    in_use = models.IntegerField()
    reserved = models.IntegerField()
    until_refresh = models.IntegerField(blank=True, null=True)
    deleted = models.IntegerField(blank=True, null=True)
    user_id = models.CharField(max_length=255, blank=True)

    class Meta:
        managed = False
        db_table = 'quota_usages'
        verbose_name = "novadb"


class CmNovaQuotas(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    project_id = models.CharField(max_length=255, blank=True)
    resource = models.CharField(max_length=255)
    hard_limit = models.IntegerField(blank=True, null=True)
    deleted = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'quotas'
        verbose_name = "novadb"


class CmUserInstaMapping(models.Model):
    fixed_ip = models.CharField(primary_key=True, max_length=39)
    floating_ip = models.CharField(max_length=39, blank=True)
    is_vm = models.IntegerField(blank=True, null=True)
    instance_name = models.CharField(max_length=255, blank=True)
    uuid = models.CharField(max_length=36, blank=True)
    os_type = models.CharField(max_length=255, blank=True)
    host_ip = models.CharField(max_length=39, blank=True, db_column='host_address')
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
        verbose_name = "mapdb"

class CmNovaHosts(models.Model):
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    id = models.IntegerField(primary_key=True)  # AutoField?
    service_id = models.IntegerField()
    cpus = models.IntegerField(db_column='vcpus')
    memory_mb = models.IntegerField()
    storage_gb = models.IntegerField(db_column='local_gb')
    vcpus_used = models.IntegerField()
    memory_mb_used = models.IntegerField()
    storage_gb_used = models.IntegerField(db_column='local_gb_used')
    hypervisor_type = models.TextField()
    hypervisor_version = models.IntegerField()
    cpu_info = models.TextField()
    disk_available_least = models.IntegerField(blank=True, null=True)
    free_ram_mb = models.IntegerField(blank=True, null=True)
    free_disk_gb = models.IntegerField(blank=True, null=True)
    current_workload = models.IntegerField(blank=True, null=True)
    vms = models.IntegerField(blank=True, null=True, db_column='running_vms')
    host_name = models.CharField(max_length=255, blank=True, db_column='hypervisor_hostname')
    deleted = models.IntegerField(blank=True, null=True)
    host_ip = models.CharField(max_length=39, blank=True)
    supported_instances = models.TextField(blank=True)
    pci_stats = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'compute_nodes'
        verbose_name = "novadb"


class MisUmorg(models.Model):
    org_id = models.BigIntegerField(primary_key=True)
    org_name = models.CharField(max_length=50)
    parent_name = models.CharField(max_length=512)
    class Meta:
        managed = False
        db_table = 'mis_umorg'
        verbose_name = 'mapdb'

class MisUmuser(models.Model):
    user_id = models.BigIntegerField(primary_key=True)
    org_id = models.BigIntegerField()
    parent_name = models.CharField(max_length=30)
    user_name = models.CharField(max_length=30)
    logon_id = models.CharField(max_length=30)
    email = models.CharField(max_length=50)
    office_phone = models.CharField(max_length=255)
    mobile = models.CharField(max_length=255)
    class Meta:
        managed = False
        db_table = 'mis_umuser'
        verbose_name = 'mapdb'

class WorkOrder(models.Model):
    id = models.BigIntegerField(primary_key=True)
    tickict_no = models.BigIntegerField()
    hostname = models.BigIntegerField()
    availability_zone = models.CharField(max_length=255)
    flavor_id = models.CharField(max_length=255)
    image_ref = models.CharField(max_length=512)
    min_count = models.CharField(max_length=255)
    user_id = models.BigIntegerField()
    user_name = models.CharField(max_length=30)
    org_id = models.BigIntegerField()
    org_name = models.CharField(max_length=30)
    parent_name = models.CharField(max_length=30)
    verify_status = models.IntegerField(blank=True, null=True)
    commit_time = models.DateTimeField(auto_now=True)
    class Meta:
        managed = False
        db_table = 'work_order'

class Device(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    model = models.CharField(max_length=255)
    classification = models.IntegerField()
    detail = models.CharField(max_length=512)
    purchase_time = models.DateTimeField(max_length=255)
    online_time = models.DateTimeField(max_length=255)
    host_ip = models.CharField(max_length=512)
    class Meta:
        managed = False
        db_table = 'device'

class FixedIps(models.Model):
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    id = models.IntegerField(primary_key=True)
    address = models.CharField(max_length=39, blank=True)
    network_id = models.IntegerField(blank=True, null=True)
    allocated = models.IntegerField(blank=True, null=True)
    leased = models.IntegerField(blank=True, null=True)
    reserved = models.IntegerField(blank=True, null=True)
    virtual_interface_id = models.IntegerField(blank=True, null=True)
    host = models.CharField(max_length=255, blank=True)
    instance_uuid = models.IntegerField(blank=True, null=True)
    #instance_uuid = models.ForeignKey('Instances', db_column='instance_uuid', blank=True, null=True)
    deleted = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'fixed_ips'
        verbose_name = "novadb"

class FloatingIps(models.Model):
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    id = models.IntegerField(primary_key=True)
    address = models.CharField(max_length=39, blank=True)
    fixed_ip_id = models.IntegerField(blank=True, null=True)
    project_id = models.CharField(max_length=255, blank=True)
    host = models.CharField(max_length=255, blank=True)
    auto_assigned = models.IntegerField(blank=True, null=True)
    pool = models.CharField(max_length=255, blank=True)
    interface = models.CharField(max_length=255, blank=True)
    deleted = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'floating_ips'
        verbose_name = "novadb"

class Instances(models.Model):
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    id = models.IntegerField(primary_key=True)
    internal_id = models.IntegerField(blank=True, null=True)
    user_id = models.CharField(max_length=255, blank=True)
    project_id = models.CharField(max_length=255, blank=True)
    image_ref = models.CharField(max_length=255, blank=True)
    kernel_id = models.CharField(max_length=255, blank=True)
    ramdisk_id = models.CharField(max_length=255, blank=True)
    launch_index = models.IntegerField(blank=True, null=True)
    key_name = models.CharField(max_length=255, blank=True)
    key_data = models.TextField(blank=True)
    power_state = models.IntegerField(blank=True, null=True)
    vm_state = models.CharField(max_length=255, blank=True)
    memory_mb = models.IntegerField(blank=True, null=True)
    vcpus = models.IntegerField(blank=True, null=True)
    hostname = models.CharField(max_length=255, blank=True)
    host = models.CharField(max_length=255, blank=True)
    user_data = models.TextField(blank=True)
    reservation_id = models.CharField(max_length=255, blank=True)
    scheduled_at = models.DateTimeField(blank=True, null=True)
    launched_at = models.DateTimeField(blank=True, null=True)
    terminated_at = models.DateTimeField(blank=True, null=True)
    display_name = models.CharField(max_length=255, blank=True)
    display_description = models.CharField(max_length=255, blank=True)
    availability_zone = models.CharField(max_length=255, blank=True)
    locked = models.IntegerField(blank=True, null=True)
    os_type = models.CharField(max_length=255, blank=True)
    launched_on = models.TextField(blank=True)
    instance_type_id = models.IntegerField(blank=True, null=True)
    vm_mode = models.CharField(max_length=255, blank=True)
    uuid = models.CharField(unique=True, max_length=36, blank=True)
    architecture = models.CharField(max_length=255, blank=True)
    root_device_name = models.CharField(max_length=255, blank=True)
    access_ip_v4 = models.CharField(max_length=39, blank=True)
    access_ip_v6 = models.CharField(max_length=39, blank=True)
    config_drive = models.CharField(max_length=255, blank=True)
    task_state = models.CharField(max_length=255, blank=True)
    default_ephemeral_device = models.CharField(max_length=255, blank=True)
    default_swap_device = models.CharField(max_length=255, blank=True)
    progress = models.IntegerField(blank=True, null=True)
    auto_disk_config = models.IntegerField(blank=True, null=True)
    shutdown_terminate = models.IntegerField(blank=True, null=True)
    disable_terminate = models.IntegerField(blank=True, null=True)
    root_gb = models.IntegerField(blank=True, null=True)
    ephemeral_gb = models.IntegerField(blank=True, null=True)
    cell_name = models.CharField(max_length=255, blank=True)
    node = models.CharField(max_length=255, blank=True)
    deleted = models.IntegerField(blank=True, null=True)
    locked_by = models.CharField(max_length=5, blank=True)
    cleaned = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'instances'
        verbose_name = "novadb"
