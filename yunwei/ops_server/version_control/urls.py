#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from django.urls import path, re_path
from version_control import views

urlpatterns = [
    re_path(r'^(?P<file_type>platform|terminal|os)/$', views.PlatformVersionView.as_view(),),
    re_path(r'^(?P<file_type>platform|terminal|os)/(?P<id>\d+)/$', views.PlatformVersionDetailView.as_view(),),
]
