from django.db import models


# Create your models here.


class IssueTracker(models.Model):
    """
    问题追踪表
    """
    issue_status = [
        (1, '未处理'),
        (2, '处理中'),
        (3, '挂起'),
        (4, '已处理'),
    ]

    issue_priority = [
        (1, '低'),
        (2, '中'),
        (3, '高'),
        (4, '紧急'),
    ]

    id = models.AutoField(primary_key=True, help_text='问题编号')
    creat_time = models.DateTimeField(auto_now_add=True, help_text='记录创建时间')
    creator = models.CharField(max_length=64, help_text='记录创建人员')

    begin_time = models.DateTimeField(help_text='问题开始时间')
    close_time = models.DateTimeField(blank=True, null=True, help_text='问题关闭时间')
    tracers = models.CharField(max_length=128, help_text='问题跟踪人员')
    issue = models.CharField(max_length=128, help_text='问题名称')
    detail = models.CharField(blank=True, max_length=1024, default="", help_text='问题描述')
    status = models.SmallIntegerField(choices=issue_status, default=1, help_text='任务状态')
    priority = models.SmallIntegerField(choices=issue_priority, default=1, help_text='任务优先级')
    postscript = models.CharField(blank=True, max_length=1024, default="", help_text='备注')
    customer = models.CharField(blank=True, max_length=64, default="", help_text='客户名称')
    version = models.CharField(blank=True, max_length=32, default="", help_text='版本号')

    class Meta:
        indexes = [
            models.Index(fields=['-id', '-begin_time'], name='issue_tracker'),
        ]
        db_table = "issue_tracker"
