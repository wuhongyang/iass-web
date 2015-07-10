from django.db import models

class MisUmorg(models.Model):
    org_id = models.BigIntegerField(primary_key=True)
    org_name = models.CharField(max_length=50)
    parent_name = models.CharField(max_length=512)
    class Meta:
        managed = False
        db_table = 'mis_umorg'

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