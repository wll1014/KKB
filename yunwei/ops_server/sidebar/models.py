from django.db import models

# Create your models here.

class ModelSidebar(models.Model):
    class Meta:
        db_table = 'sidebar'

    id = models.IntegerField(primary_key=True,verbose_name='菜单栏id',unique=True)
    title = models.CharField(max_length=64)
    url = models.CharField(max_length=128)
    icon = models.CharField(max_length=64, null=True)
    pid = models.ForeignKey(to='self', on_delete=models.CASCADE, null=True)

