#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

from django.urls import path, re_path
from platreport import views

urlpatterns = [
    re_path(r'^daily/(?P<date>\d{4}-\d{2}-\d{2})/$', views.DailyReport.as_view(), ),
    re_path(r'^daily/(?P<date>\d{4}-\d{2}-\d{2})/(?P<report_type>\w+)/$', views.DailyReportDetail.as_view(), ),
]
