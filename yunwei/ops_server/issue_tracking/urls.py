# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from django.urls import path, re_path, include
from django.conf.urls import url
from rest_framework.routers import SimpleRouter
from . import views

router = SimpleRouter()
router.register(r'issues', views.IssueTrackerView, basename='issues')

urlpatterns = [
    path('export/', views.IssueTrackerExportView.as_view(),),
    url('^', include(router.urls)),
]