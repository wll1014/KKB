# !/usr/bin/env python
# -*- coding:utf-8 -*-

from django.urls import path, re_path
from ops.settings import MEDIA_ROOT
from django.views.static import serve
from . import views


urlpatterns = [
    # 脚本管理相关
    path('scripts/', views.ScriptFileHandler.as_view(),),
    path('scripts/uploader/', views.ScriptUploader.as_view(), ),
    path('scripts/<int:ids>/', views.ScriptFileHandlerDetail.as_view(),),
    # 即时任务相关
    re_path('oper_tasks/real_time_tasks/$', views.RealTimeTasksList.as_view(),),
    re_path('oper_tasks/real_time_tasks/(?P<pk>\d+)/$', views.RealTimeTasksRetrieve.as_view(),),
    re_path('oper_tasks/real_time_task_operators/$', views.RealTimeTaskOperators.as_view(),),
    # 定时任务相关
    re_path('oper_tasks/cron_tasks/$', views.CronTasksList.as_view(), ),
    re_path('oper_tasks/cron_tasks/(?P<pk>\d+)/$', views.CronTasksRetrieve.as_view(), ),
    re_path('oper_tasks/cron_task_operators/$', views.CronTaskOperators.as_view(), ),
    re_path('oper_tasks/cron_task_last_modify_operators/$', views.CronTaskLastModifyOperators.as_view(), ),
    # 文件分发相关
    re_path('oper_tasks/distribution_files/$', views.DistributionFile.as_view(), ),
    re_path('oper_tasks/distribution_files/(?P<pk>\d+)/$', views.DistributionFileDetail.as_view(), ),
    re_path('oper_tasks/distribution_tasks/$', views.DistributionTasksList.as_view(), ),
    re_path('oper_tasks/distribution_tasks/(?P<pk>\d+)/$', views.DistributionTasksRetrieve.as_view(), ),
    re_path('oper_tasks/distribution_task_operators/$', views.DistributionTaskOperators.as_view(), ),
]
