from django.db import models
from django.core.validators import MaxValueValidator

# Create your models here.


class FAQClassifications(models.Model):
    """
    问题分类表
    """
    id = models.AutoField(primary_key=True, verbose_name='分类ID')
    name = models.CharField(max_length=32, unique=True, verbose_name='分类名')

    class Meta:
        indexes = [
            models.Index(fields=['id'], name='faq_classifications'),
        ]
        db_table = "faq_classifications"


class FAQRecords(models.Model):
    """
    FAQ记录表
    """
    record_id = models.AutoField(primary_key=True, verbose_name='FAQ记录ID')
    creat_time = models.DateTimeField(auto_now_add=True, verbose_name='记录创建时间')
    creator = models.CharField(max_length=32, verbose_name='记录创建人')
    classification = models.ForeignKey(FAQClassifications, on_delete=models.PROTECT, related_name='classification',
                                       verbose_name='分类')
    question = models.CharField(max_length=128, verbose_name='faq问题')
    answer = models.CharField(max_length=1024, verbose_name='faq答案')

    class Meta:
        unique_together = (('classification', 'question'),)
        indexes = [
            models.Index(fields=['record_id'], name='faq_records'),
        ]
        db_table = "faq_records"
