# !/usr/bin/env python
# -*- coding:utf-8 -*-

from django.urls import path, re_path
from . import views


urlpatterns = [
    path('', views.FAQRecord.as_view(),),
    path('<int:ids>/', views.FAQRecordDetail.as_view(),),
    path('classes/', views.FAQClass.as_view(),),
    path('classes/<int:ids>/', views.FAQClassDetail.as_view(),),
]