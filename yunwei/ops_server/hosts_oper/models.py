from django.db import models


# Create your models here.


class ScriptFiles(models.Model):
    """
    脚本管理表
    """
    file = models.FileField(upload_to='scripts/%Y/%m/%d/', verbose_name='脚本名称')
    filename = models.CharField(max_length=128, verbose_name='脚本名称')
    # size = models.IntegerField(verbose_name='脚本大小')
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name='上传日期')
    uploader = models.CharField(max_length=128, verbose_name='上传人员')
    postscript = models.CharField(max_length=64, blank=True, verbose_name='备注')

    class Meta:
        # 索引
        indexes = [
            models.Index(fields=['id', '-upload_time', 'file'], name='scripts'),
        ]
        # 表名
        db_table = "hosts_oper_scripts"


class RealTimeTasksModel(models.Model):
    '''
    即时任务
    '''

    class Meta:
        db_table = "real_time_tasks"

    task_name = models.CharField(max_length=64, verbose_name='任务名称', unique=True)
    script = models.ForeignKey(to=ScriptFiles, on_delete=models.CASCADE)
    script_params = models.CharField(max_length=512, default='', blank=True)
    operator = models.CharField(max_length=64, verbose_name='操作人员')
    begin_time = models.DateTimeField(auto_now_add=True, verbose_name='任务开始时间')
    duration = models.CharField(max_length=64, verbose_name='任务持续时间', default='0', blank=True)
    status = models.SmallIntegerField(verbose_name='任务状态，1：正在执行，2：执行成功，3：执行失败', default=1, blank=True)
    machines = models.CharField(max_length=2048, verbose_name='执行任务服务器moid，以","分开')
    stdout = models.TextField(verbose_name='任务正确输出', blank=True)
    stderr = models.TextField(verbose_name='任务错误输出', blank=True)
    results = models.TextField(verbose_name='任务结果', blank=True)


class CronTasksModel(models.Model):
    '''
    定时任务
    '''

    class Meta:
        db_table = "cron_tasks"

    task_name = models.CharField(max_length=64, verbose_name='任务名称', unique=True)
    script = models.ForeignKey(to=ScriptFiles, on_delete=models.CASCADE)
    script_params = models.CharField(max_length=512, default='', blank=True)
    operator = models.CharField(max_length=64, verbose_name='操作人员')
    last_modify_operator = models.CharField(max_length=64, verbose_name='最后修改人员')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='任务创建时间')
    cron_rule = models.CharField(max_length=2048, verbose_name='定时任务规则')
    last_modify_time = models.DateTimeField(auto_now_add=True, verbose_name='任务最后修改时间')
    status = models.SmallIntegerField(verbose_name='任务状态，1：正在执行，2：暂停执行，3：任务创建失败', default=1, blank=True)
    machines = models.CharField(max_length=2048, verbose_name='执行任务服务器moid，以","分开')
    results = models.TextField(verbose_name='任务结果', blank=True)


class DistributionFileModel(models.Model):
    """
    以供分发的文件表
    """

    class Meta:
        # 表名
        db_table = "distribution_file"

    file = models.FileField(upload_to='file_distribution/%Y/%m/%d/', verbose_name='文件名称')
    filename = models.CharField(max_length=256, verbose_name='文件名称')
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name='上传日期')
    uploader = models.CharField(max_length=128, verbose_name='上传人员')
    task = models.ForeignKey(to='DistributionTasksModel', on_delete=models.CASCADE)


class DistributionTasksModel(models.Model):
    """
    文件分发任务表
    """

    class Meta:
        # 表名
        db_table = "distribution_tasks"

    task_name = models.CharField(max_length=64, verbose_name='任务名称', unique=True)
    remote_path = models.CharField(max_length=128, verbose_name='分发文件的远端服务器路径', default='/opt/data/ops/distribution/')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='任务创建时间')
    operator = models.CharField(max_length=64, verbose_name='操作人员')
    machines = models.CharField(max_length=2048, verbose_name='执行任务服务器moid，以","分开')
    status = models.SmallIntegerField(verbose_name='任务状态，1：正在执行，2：执行成功，3：执行失败', default=1, blank=True)
    results = models.TextField(verbose_name='任务结果', blank=True, default='')
