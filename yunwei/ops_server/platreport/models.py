from django.db import models


# Create your models here.

class DailyReportModel(models.Model):
    # 日报
    class Meta:
        db_table = 'daily_report_data'
        unique_together = ('date', 'report_type')

    date = models.DateField()
    platform_moid = models.CharField(max_length=64, null=True, blank=True)
    platform_name = models.CharField(max_length=64, null=True, blank=True)
    report_type = models.CharField(max_length=64)
    report_data = models.TextField()

#
# class WeeklyReportModel(models.Model):
#     # 周报
#     date = models.DateField(auto_created=True)
#     platform_moid = models.CharField(max_length=64)
#     report_type = models.CharField(max_length=64)
#     data = models.TextField()
#
#
# class MonthlyReportModel(models.Model):
#     # 月报
#     date = models.DateField(auto_created=True)
#     platform_moid = models.CharField(max_length=64)
#     report_type = models.CharField(max_length=64)
#     data = models.TextField()
#
#
# class QuarterlyReportModel(models.Model):
#     # 季报
#     date = models.DateField(auto_created=True)
#     platform_moid = models.CharField(max_length=64)
#     report_type = models.CharField(max_length=64)
#     data = models.TextField()
#
#
# class SemiAnnualReportModel(models.Model):
#     # 半年报
#     date = models.DateField(auto_created=True)
#     platform_moid = models.CharField(max_length=64)
#     report_type = models.CharField(max_length=64)
#     data = models.TextField()
#
#
# class AnnualReportModel(models.Model):
#     # 年报
#     date = models.DateField(auto_created=True)
#     platform_moid = models.CharField(max_length=64)
#     report_type = models.CharField(max_length=64)
#     data = models.TextField()
