# !/usr/bin/env python
# -*- coding:utf-8 -*-

from django.urls import path, re_path
from diagnose import views

urlpatterns = [
    # 会议快照相关
    re_path(r'^snapshots/$', views.SnapShot.as_view(), ),
    re_path(r'^_snapshots/$', views.SnapShotList.as_view(), ),
    re_path(r'^snapshots/(?P<pk>\d+)/$', views.SnapShotTask.as_view(), ),
    re_path(r'^download/$', views.Download.as_view(), ),
    re_path(r'^apps/$', views.LogAppTypes.as_view(), ),
    # 链路检测相关
    path('createconf/', views.Link.as_view(), ),
    path('createconf/<int:task_id>/', views.LinkDetail.as_view(), ),
    path('createconf/<int:task_id>/call_ids/', views.LinkCallID.as_view(), ),
    path('createconf/<str:call_id>/methods/', views.LinkCallIDMethods.as_view(), ),
    path('createconf/<str:call_id>/primary/', views.LinkCallDetail.as_view(), ),
    path('createconf/<str:call_id>/all/', views.LinkCallAllMessages.as_view(), ),
    # 智能抓包相关
    re_path(r'tcpdump/quick_capture/$', views.QuickCaptureTask.as_view(), ),
    re_path(r'tcpdump/quick_capture/(?P<pk>\d+)/$', views.QuickCaptureTaskDetail.as_view(), ),
    # 自定义抓包相关
    re_path(r'tcpdump/custom_capture/$', views.CustomCaptureTask.as_view(), ),
    re_path(r'tcpdump/custom_capture/(?P<pk>\d+)/$', views.CustomCaptureTaskDetail.as_view(), ),
    re_path(r'tcpdump/custom_capture_items/$', views.CustomCaptureItem.as_view(), ),
    re_path(r'tcpdump/custom_capture_items/(?P<pk>\d+)/$', views.CustomCaptureItemDetail.as_view(), ),
    re_path(r'tcpdump/custom_capture_task/$', views.CustomCaptureTaskHandler.as_view(), ),
    re_path(
        r'tcpdump/(?P<machine_moid>[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12})/cards/$',
        views.MachineCards.as_view(),
    ),
    # 应用检测相关
    re_path(r'^check_apps/(?P<check_type>web|other|midware|platform)/$', views.AppsCheck.as_view(), ),
    re_path(r'^check_apps/$', views.AppsCheck.as_view(), ),
    re_path(r'^check_apps/export/$', views.AppsCheckExport.as_view(), ),
    re_path(r'^check_apps/(?P<check_type>web|other|midware|platform)/(?P<section>.*)/log/$',
            views.AppsCheckLog.as_view(), ),
    # 会议拓扑相关
    re_path(r'^topology/machine_rooms/$', views.ConfTopologyRooms.as_view(), ),
    re_path(r'^topology/confs/$', views.ConfTopologyRoomConfs.as_view(), ),
    re_path(r'^topology/confs/(?P<e164>\d{7})/$', views.ConfTopologyConfDetail.as_view(), ),
    # 终端诊断
    path('accounts/', views.TerminalAccountsSearch.as_view(), ),
    path('accounts/<str:e164>/', views.TerminalAccountInfo.as_view(), ),
    path('accounts/<str:e164>/terminals/', views.AccountTerminalsList.as_view(), ),
    path('accounts/<str:e164>/terminals/<str:terminal>/connect/', views.TerminalConnectInfo.as_view(), ),
    path('accounts/<str:e164>/terminals/<str:terminal>/status/', views.TerminalStatusInfo.as_view(), ),
    path('accounts/<str:e164>/terminals/<str:terminal>/statistic/', views.TerminalStatisticInfo.as_view(), ),
    path('accounts/<str:e164>/terminals/<str:terminal>/peripheral/', views.TerminalPeripheralInfo.as_view(), ),
    path('accounts/<str:e164>/terminals/<str:terminal>/crucial/', views.TerminalCrucialProcessesInfo.as_view(), ),
    path('accounts/<str:e164>/terminals/<str:terminal>/call/', views.TerminalCallRecordsInfo.as_view(), ),
]
