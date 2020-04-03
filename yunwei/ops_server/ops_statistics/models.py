from django.db import models

# Create your models here.

class PositionModel(models.Model):
    class Meta:
        db_table = 'position'

    name = models.CharField(max_length=64, help_text='图表名称')
    description = models.CharField(max_length=64, help_text='图表描述')
    width = models.IntegerField(help_text='图表宽度')
    height = models.IntegerField(help_text='图表高度')
    x = models.IntegerField(help_text='图表坐标x')
    y = models.IntegerField(help_text='图表坐标y')
