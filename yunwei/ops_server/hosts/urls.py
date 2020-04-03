#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

from django.urls import re_path
from hosts import views

urlpatterns = [
    re_path(r'^$', views.Hosts.as_view()),
    re_path(r'^logger/$', views.Logger.as_view()),
    re_path(r'^deploy_sync/$', views.DeploySync.as_view()),
    re_path(r'^groups/$', views.Group.as_view()),
    re_path(r'^domains/$', views.Domain.as_view()),
    re_path(r'^groups/(?P<group_id>\d+)/$', views.GroupDetail.as_view()),
    re_path(r'^groups/(?P<group_id>\d+)/members/$', views.GroupHandle.as_view()),
    re_path(r'^(?P<machine_moid>[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12})/$', views.HostDetail.as_view()),
    re_path(r'^(?P<machine_moid>[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12})/cpu_usage/$', views.CpuUsage.as_view()),
    re_path(r'^(?P<machine_moid>[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12})/cpu_usage/(?P<core_id>\d+)/$', views.CoreUsage.as_view()),
    re_path(r'^(?P<machine_moid>[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12})/memory_usage/$', views.MemoryUsage.as_view()),
    re_path(r'^(?P<machine_moid>[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12})/load_gauge/$', views.LoadGauge.as_view()),
    re_path(r'^(?P<machine_moid>[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12})/disk_usage/$', views.DiskUsage.as_view()),
    re_path(r'^(?P<machine_moid>[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12})/diskage/$', views.DiskAge.as_view()),
    re_path(r'^(?P<machine_moid>[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12})/network/$', views.NetTraffic.as_view()),
    re_path(r'^(?P<machine_moid>[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12})/uptime/$', views.Uptime.as_view()),
    re_path(r'^(?P<machine_moid>[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12})/top(?P<n>\d+)/memory/$', views.TopNMemory.as_view()),
    re_path(r'^(?P<machine_moid>[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12})/top(?P<n>\d+)/cpu/$', views.TopNCpu.as_view()),
    re_path(r'^(?P<machine_moid>[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12})/top(?P<n>\d+)/export/$', views.TopExport.as_view()),
]

