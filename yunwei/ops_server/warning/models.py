from django.db import models

# Create your models here.
from django.utils import timezone


class WarningCodeModel(models.Model):
    # 告警码表
    class Meta:
        db_table = 'warning_code'

    type = models.CharField(max_length=64, )
    code = models.SmallIntegerField(unique=True)
    name = models.CharField(max_length=128, )
    level = models.CharField(max_length=16, )
    description = models.CharField(max_length=128, blank=True, null=True, default='')
    suggestion = models.CharField(max_length=512, blank=True, null=True, default='')


class SubWarningCodeModel(models.Model):
    # 已订阅告警表
    class Meta:
        db_table = 'sub_warning_code'
        unique_together = ("user_id", "sub_code")

    domain_moid = models.CharField(max_length=40, null=True)
    user_id = models.CharField(max_length=40)
    sub_code = models.SmallIntegerField()


class ServerWarningRepairedModel(models.Model):
    # 服务器已修复告警
    class Meta:
        db_table = 'server_warning_repaired'

    device_moid = models.CharField(max_length=40)
    guid = models.CharField(max_length=40, default='')
    device_name = models.CharField(max_length=128, null=True, blank=True, default='')
    device_type = models.CharField(max_length=36, null=True, blank=True, default='')
    device_ip = models.CharField(max_length=128, null=True, blank=True, default='')
    machine_room_moid = models.CharField(max_length=40)
    machine_room_name = models.CharField(max_length=128, null=True, blank=True, default='')
    code = models.SmallIntegerField()
    level = models.CharField(max_length=16, )
    description = models.CharField(max_length=128, blank=True, null=True, default='')
    start_time = models.DateTimeField(default=timezone.now)
    resolve_time = models.DateTimeField(default=timezone.now)


class ServerWarningUnrepairedModel(models.Model):
    # 服务器未修复告警
    class Meta:
        db_table = 'server_warning_unrepaired'

    device_moid = models.CharField(max_length=40)
    guid = models.CharField(max_length=40, default='')
    device_name = models.CharField(max_length=128, null=True, blank=True, default='')
    device_type = models.CharField(max_length=36, null=True, blank=True, default='')
    device_ip = models.CharField(max_length=128, null=True, blank=True, default='')
    machine_room_moid = models.CharField(max_length=40)
    machine_room_name = models.CharField(max_length=128, null=True, blank=True, default='')
    code = models.SmallIntegerField()
    level = models.CharField(max_length=16, )
    description = models.CharField(max_length=128, blank=True, null=True, default='')
    start_time = models.DateTimeField(default=timezone.now)
    resolve_time = models.CharField(max_length=128, null=True, blank=True, default='')


class TerminalWarningRepairedModel(models.Model):
    # 终端已修复告警
    class Meta:
        db_table = 'terminal_warning_repaired'

    device_moid = models.CharField(max_length=40)
    device_name = models.CharField(max_length=128, null=True, blank=True, default='')
    device_type = models.CharField(max_length=36, null=True, blank=True, default='')
    device_ip = models.CharField(max_length=128, null=True, blank=True, default='')
    device_e164 = models.CharField(max_length=32, null=True, blank=True, default='')
    domain_name = models.CharField(max_length=128, null=True, blank=True, default='', help_text='用户域名称')
    domain_moid = models.CharField(max_length=40, help_text='用户域moid')
    code = models.SmallIntegerField()
    level = models.CharField(max_length=16, )
    description = models.CharField(max_length=128, blank=True, null=True, default='')
    start_time = models.DateTimeField(default=timezone.now)
    resolve_time = models.DateTimeField(default=timezone.now)


class TerminalWarningUnrepairedModel(models.Model):
    # 终端未修复告警
    class Meta:
        db_table = 'terminal_warning_unrepaired'

    device_moid = models.CharField(max_length=40)
    device_name = models.CharField(max_length=128, null=True, blank=True, default='')
    device_type = models.CharField(max_length=36, null=True, blank=True, default='')
    device_ip = models.CharField(max_length=128, null=True, blank=True, default='')
    device_e164 = models.CharField(max_length=32, null=True, blank=True, default='')
    domain_name = models.CharField(max_length=128, null=True, blank=True, default='', help_text='用户域名称')
    domain_moid = models.CharField(max_length=40, help_text='用户域moid')
    code = models.SmallIntegerField()
    level = models.CharField(max_length=16, )
    description = models.CharField(max_length=128, blank=True, null=True, default='')
    start_time = models.DateTimeField(default=timezone.now)
    resolve_time = models.CharField(max_length=128, null=True, blank=True, default='')


class WarningNotifyRuleModel(models.Model):
    class Meta:
        db_table = 'warning_notify_rule'

    name = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return self.name


class WarningNotifyUserModel(models.Model):
    class Meta:
        db_table = 'warning_notify_user'

    user_name = models.CharField(max_length=40)
    user_id = models.CharField(max_length=40)
    email = models.CharField(max_length=64)
    phone = models.CharField(max_length=64)
    rules = models.ManyToManyField(to=WarningNotifyRuleModel)

    def __str__(self):
        return self.user_name


class WarningNotifyWeChatModel(models.Model):
    class Meta:
        db_table = 'warning_notify_wechat'

    warning_notify_id = models.ForeignKey(
        to=WarningNotifyRuleModel,
        on_delete=models.CASCADE,
        db_constraint=False,
        db_column='warning_notify_id'
    )
    user_name = models.CharField(max_length=40)
    user_id = models.CharField(max_length=40)


class WarningNotifyEmailModel(models.Model):
    class Meta:
        db_table = 'warning_notify_email'

    warning_notify_id = models.ForeignKey(
        to=WarningNotifyRuleModel,
        on_delete=models.CASCADE,
        db_constraint=False,
        db_column='warning_notify_id'
    )
    user_name = models.CharField(max_length=40)
    user_id = models.CharField(max_length=40)


class WarningNotifyPhoneModel(models.Model):
    class Meta:
        db_table = 'warning_notify_phone'

    warning_notify_id = models.ForeignKey(
        to=WarningNotifyRuleModel,
        on_delete=models.CASCADE,
        db_constraint=False,
        db_column='warning_notify_id'
    )
    user_name = models.CharField(max_length=40)
    user_id = models.CharField(max_length=40)


class WarningNotifySubCodeModel(models.Model):
    class Meta:
        db_table = 'warning_notify_sub_code'
        unique_together = ("warning_notify_id", "sub_code")

    warning_notify_id = models.ForeignKey(
        to=WarningNotifyRuleModel,
        on_delete=models.CASCADE,
        db_constraint=False,
        db_column='warning_notify_id'
    )
    sub_code = models.SmallIntegerField()


class WarningThresholdModel(models.Model):
    class Meta:
        db_table = 'warning_threshold'

    cpu = models.SmallIntegerField(default=80, help_text='cpu使用率阈值-%')
    memory = models.SmallIntegerField(default=80, help_text='内存使用率阈值-%')
    disk = models.SmallIntegerField(default=80, help_text='分区使用率阈值-%')
    diskwritespeed = models.SmallIntegerField(default=2, help_text='磁盘写入速率阈值-M')
    rateofflow = models.SmallIntegerField(default=60, help_text='网口吞吐速率阈值-Mbps')
    diskage = models.SmallIntegerField(default=20, help_text='磁盘寿命使用率阈值-%')
    vmp = models.SmallIntegerField(default=20, help_text='合成器资源使用率阈值-%')
    mixer = models.SmallIntegerField(default=20, help_text='混音器资源使用率阈值-%')
    mp = models.SmallIntegerField(default=80, help_text='媒体端口授权使用率阈值-%')
    ap = models.SmallIntegerField(default=80, help_text='接入端口授权使用率阈值-%')
    video_num = models.SmallIntegerField(default=16, help_text='录像并发数量阈值-个')
    live_num = models.SmallIntegerField(default=3, help_text='直播会议并发数量阈值-个')
    viewer_num = models.SmallIntegerField(default=300, help_text='直播观看人数阈值-个')
    dcs_conf_num = models.SmallIntegerField(default=25, help_text='协作会议数量阈值-个')
    dcs_user_num = models.SmallIntegerField(default=25, help_text='协作人员数量阈值-个')
