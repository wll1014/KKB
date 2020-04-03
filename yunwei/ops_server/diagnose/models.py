from django.db import models


# Create your models here.

class SnapshotTaskModel(models.Model):
    class Meta:
        db_table = 'snapshot_task'

    filename = models.CharField(max_length=128, null=True, blank=True, default='', help_text='文件名')
    key = models.CharField(max_length=64, null=True, blank=True, default='', help_text='任务搜索的关键字')
    apps = models.CharField(max_length=64, null=True, blank=True, default='', help_text='任务搜索的应用名称')
    start_time = models.CharField(max_length=64, help_text='开始时间，timestamp格式')
    md5 = models.CharField(max_length=128, null=True, blank=True, default='', help_text='文件md5校验码')
    filesize = models.IntegerField(help_text='文件大小bytes', default=0)
    is_complete = models.SmallIntegerField(help_text='是否完成：0 未完成，1 完成，2 任务失败', default=0)
    pids = models.CharField(max_length=64, blank=True, help_text='此任务产生的进程号，多个由分号";"分割', default='')
    err_msg = models.CharField(max_length=512, blank=True, help_text='此任务产生的错误信息，多个由分号";"分割', default='')


class LinkCheckerModel(models.Model):
    task_id = models.AutoField(primary_key=True, help_text="任务ID")
    creator = models.CharField(max_length=128, help_text='任务创建人')
    link_type = models.SmallIntegerField(help_text='链路类型:1 会议链路;2 呼叫链路')
    mt_id = models.CharField(max_length=32, blank=True, default='', help_text='呼叫终端e164或终端ip')
    user = models.CharField(max_length=128, help_text='模拟创会用户名')
    start_time = models.CharField(max_length=64, blank=True, default='', help_text='任务开始时间,timestamp格式')
    end_time = models.CharField(max_length=64, blank=True, default='', help_text='任务结束时间,timestamp格式')
    conf_name = models.CharField(max_length=64, blank=True, default='', help_text='会议名称')
    conf_id = models.CharField(max_length=64, blank=True, default='', help_text='会议号码')
    conf_status = models.CharField(max_length=32, blank=True, default='', help_text='会议状态')
    conf_error = models.CharField(max_length=512, blank=True, default='', help_text='会议错误信息')
    is_complete = models.BooleanField(blank=True, default=0, help_text='任务是否完成:0 未完成;1 完成')
    need_del = models.BooleanField(blank=True, default=0, help_text='任务是否取消:0 未取消;1 取消')

    class Meta:
        db_table = 'diagnose_link'


class QuickCaptureTaskModel(models.Model):
    '''
    快捷抓包任务表
    '''

    class Meta:
        db_table = 'quick_capture_task'

    filename = models.CharField(max_length=128, null=True, blank=True, default='', help_text='文件名')
    conf_e164 = models.CharField(max_length=64, null=True, blank=True, default='', help_text='抓包的会议e164号码')
    mt_e164 = models.CharField(max_length=64, null=True, blank=True, default='', help_text='抓包的终端e164号码')
    start_time = models.CharField(max_length=64, help_text='开始时间，timestamp格式')
    # md5 = models.CharField(max_length=128, null=True, blank=True, default='', help_text='文件md5校验码')
    # filesize = models.IntegerField(help_text='文件大小bytes', default=0)
    is_complete = models.SmallIntegerField(help_text='是否完成：0 未完成，1 完成，2 任务失败', default=0)


class CustomCaptureTaskModel(models.Model):
    '''
    自定义抓包任务表
    '''

    class Meta:
        db_table = 'custom_capture_task'

    start_time = models.CharField(max_length=64, help_text='开始时间，timestamp格式')
    timeout = models.IntegerField(help_text='超时时间')
    filename = models.CharField(max_length=128, null=True, blank=True, default='', help_text='文件名')


class CustomCaptureItemsModel(models.Model):
    '''
    自定义抓包项目表
    '''

    class Meta:
        db_table = 'custom_capture_items'
        unique_together = ('moid', 'task')

    moid = models.CharField(max_length=64, help_text='项目moid')
    item_type = models.SmallIntegerField(help_text='1 服务器, 2 终端', default=1)
    dev_type = models.CharField(max_length=32, blank=True, help_text='设备类型', default='')
    card = models.CharField(max_length=32, blank=True, help_text='抓包网卡，如eth0、any"全部"')
    ports = models.CharField(max_length=256, blank=True, help_text='抓包端口，多个以","分开')
    protocol = models.CharField(max_length=16, blank=True, default='')
    task = models.ForeignKey(to=CustomCaptureTaskModel, on_delete=models.CASCADE, db_constraint=False)
    is_complete = models.SmallIntegerField(help_text='是否完成：0 未完成，1 完成，2 任务失败，3 初始任务', default=3)
