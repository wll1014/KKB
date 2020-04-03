from django.db import models

# Create your models here.


class MaintenanceRecords(models.Model):
    """
    维护记录表
    """
    record_id = models.AutoField(primary_key=True, verbose_name='维护记录ID')
    creat_time = models.DateTimeField(auto_now_add=True, verbose_name='记录创建时间')
    creator = models.CharField(max_length=32, verbose_name='记录创建人')
    maintenance_time = models.DateTimeField(verbose_name='维护时间')
    maintainers = models.CharField(max_length=32, verbose_name='维护人')
    platform = models.CharField(max_length=32, verbose_name='所属平台')
    operating_models = models.CharField(max_length=32, verbose_name='操作模块')
    operations = models.CharField(max_length=500, verbose_name='维护明细')
    postscript = models.CharField(max_length=500, blank=True, verbose_name='备注')

    class Meta:
        # 索引
        indexes = [
            models.Index(fields=['record_id', '-maintenance_time', 'platform', 'operating_models'], name='maintenance'),
        ]
        # 表名
        db_table = "maintenance_records"
