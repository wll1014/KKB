#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

from django.urls import re_path
from sidebar import views

urlpatterns = [
    re_path(r'^$', views.Sidebar.as_view()),
]

