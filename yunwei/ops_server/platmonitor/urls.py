#!/usr/bin/env python
# -*- coding:utf-8 -*-

from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.ConferencesInfoList.as_view(), ),
    path('summary-quality/', views.ConferencesQuality.as_view(), ),
    path('<str:conf_id>/extend/', views.ConferencesExtendInfo.as_view(), ),
    path('<str:conf_id>/mts/', views.ConfDevlist.as_view(), ),
    path('<str:conf_id>/mts/<str:mt_e164>/channel/', views.ConfDevChannel.as_view(), ),
    path('<str:conf_id>/mts/<str:mt_e164>/topology/', views.ConfDevTopology.as_view(), ),
    path('<str:conf_id>/mts/<str:mt_e164>/conf_info/', views.ConfDevInfo.as_view(), ),
    path('<str:conf_id>/mts/<str:mt_e164>/media_info/', views.ConfDevMediaInfo.as_view(), ),
    path('<str:conf_id>/mts/<str:mt_e164>/media_info/options/', views.ConfDevMediaInfoOptions.as_view(), ),
    path('<str:conf_id>/mts/<str:mt_e164>/switch/', views.ConfDevSwitchInfo.as_view(), ),
    path('<str:conf_id>/mts/<str:mt_e164>/call_ids/', views.ConfDevCallID.as_view(), ),
    path('<str:conf_id>/mts/<str:mt_e164>/<str:call_id>/methods/', views.ConfDevCallIDMethods.as_view(), ),
    path('<str:conf_id>/mts/<str:mt_e164>/<str:call_id>/primary/', views.ConfDevCallDetail.as_view(), ),
    path('<str:conf_id>/mts/<str:mt_e164>/<str:call_id>/all/', views.ConfDevCallAllMessages.as_view(), ),
    path('<str:conf_id>/mts/<str:mt_e164>/real_time_status/', views.RealTimeStatus.as_view(), ),
    re_path(r'^(?P<conf_id>\d{7})/actions/$', views.ConferencesActions.as_view(), ),
]
