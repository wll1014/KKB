# !/usr/bin/env python
# -*- coding:utf-8 -*-


from django.urls import path, re_path
from . import views


urlpatterns = [
    path('', views.RecordView.as_view(),),
    path('<int:ids>/', views.RecordDetailView.as_view(),),
]


