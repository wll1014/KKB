# !/usr/bin/env python
# -*- coding:utf-8 -*-

from django.urls import path, re_path
from . import views


urlpatterns = [
    path('', views.OperationLogView.as_view(),),
    path('export/', views.ExportOpLog.as_view(),),
]