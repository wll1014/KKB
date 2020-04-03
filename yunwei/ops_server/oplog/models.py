from django.db import models


# Create your models here.


class OperationLog(models.Model):
    """
    操作日志表
    """
    operation_type = [
        (1, '登录'),
        (2, '注销'),
        (3, '新增'),
        (4, '删除'),
        (5, '编辑'),
        (6, '上传'),
        (7, '其它'),
    ]

    operation_results = [
        (1, '成功'),
        (0, '失败'),
        (2, '未知'),
    ]

    username = models.CharField(max_length=128, verbose_name='用户名')
    time = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')
    ip = models.GenericIPAddressField(protocol='both', unpack_ipv4=True, verbose_name='IP地址')
    opertype = models.IntegerField(choices=operation_type, default=7, verbose_name='操作类型')
    operdesc = models.CharField(max_length=64, default='', blank=True, verbose_name='操作描述')
    operrest = models.IntegerField(choices=operation_results, default=2, verbose_name='操作结果')
    detail = models.TextField(blank=True, verbose_name='详情')

    class Meta:
        # 索引
        indexes = [
            models.Index(fields=['id', 'username', '-time'], name='oplog'),
        ]
        # 表名
        db_table = "oplog_log"
