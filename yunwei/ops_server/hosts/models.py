from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation


# Create your models here.

class MachineInfo(models.Model):
    class Meta:
        db_table = 'hosts_machine_info'

    name = models.CharField(max_length=128, unique=False, blank=True, verbose_name='主机名称')
    moid = models.CharField(max_length=64, unique=True, db_index=True, blank=True, null=True, verbose_name='主机moid')
    local_ip = models.CharField(max_length=15, unique=False, blank=True, verbose_name='本地扫描ip')
    machine_type = models.CharField(max_length=32, blank=True, verbose_name='主机类型')
    has_detail = models.SmallIntegerField(default=1, help_text='是否展示详情页，1：展示，0：不展示')
    cluster = models.CharField(max_length=32, blank=True, verbose_name='工作模式')
    room_name = models.CharField(max_length=128, blank=True, null=True, verbose_name='所属机房名称')
    room_moid = models.CharField(max_length=64, blank=True, null=True, verbose_name='所属机房moid')
    frame_name = models.CharField(max_length=128, blank=True, null=True, verbose_name='所属机框名称')
    frame_moid = models.CharField(max_length=64, blank=True, null=True, verbose_name='所属机框moid')
    frame_slot = models.CharField(max_length=32, blank=True, null=True, verbose_name='所属槽位')
    frame_type = models.CharField(max_length=32, blank=True, null=True, verbose_name='所属机框类型')
    domain_name = models.CharField(max_length=128, blank=True, null=True, verbose_name='所属域名称')
    domain_moid = models.CharField(max_length=64, blank=True, null=True, verbose_name='所属域moid')
    ip_list = models.CharField(max_length=2048, blank=True, verbose_name='所有ip信息')

    def __str__(self):
        return self.name


class MachineProfile(models.Model):
    class Meta:
        db_table = 'hosts_machine_profile'
        unique_together = ("moid", "object_id")

    moid = models.CharField(max_length=64, db_index=True, blank=True,
                            null=True, verbose_name='主机moid')
    name = models.CharField(max_length=128, blank=True, verbose_name='主机名称')
    local_ip = models.CharField(max_length=15, blank=True, verbose_name='本地扫描ip')
    machine_type = models.CharField(max_length=32, blank=True, verbose_name='主机类型')
    has_detail = models.SmallIntegerField(default=1, help_text='是否展示详情页，1：展示，0：不展示')
    cluster = models.CharField(max_length=32, blank=True, verbose_name='工作模式')
    frame_name = models.CharField(max_length=128, blank=True, null=True, verbose_name='所属机框名称')
    frame_moid = models.CharField(max_length=64, blank=True, null=True, verbose_name='所属机框moid')
    frame_slot = models.CharField(max_length=32, blank=True, null=True, verbose_name='所属槽位')
    frame_type = models.CharField(max_length=32, blank=True, null=True, verbose_name='所属机框类型')
    room_name = models.CharField(max_length=128, blank=True, null=True, verbose_name='所属机房名称')
    room_moid = models.CharField(max_length=64, blank=True, null=True, verbose_name='所属机房moid')
    domain_name = models.CharField(max_length=128, blank=True, null=True, verbose_name='所属域名称')
    domain_moid = models.CharField(max_length=64, blank=True, null=True, verbose_name='所属域moid')

    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class MachineGroup(models.Model):
    class Meta:
        db_table = 'hosts_group'
        unique_together = ("name", "room_moid")

    name = models.CharField(max_length=255, blank=True, verbose_name='分组名称')

    room_moid = models.CharField(max_length=64, blank=True, null=True, default=None, verbose_name='归属机房moid')
    machine = GenericRelation('MachineProfile')

    def __str__(self):
        return self.name
