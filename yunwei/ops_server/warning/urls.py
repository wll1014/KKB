# !/usr/bin/env python
# -*- coding:utf-8 -*-

from django.urls import path, re_path
from warning import views

urlpatterns = [
    re_path('^server_repaired/$', views.ServerRepairedWarning.as_view(),),
    re_path('^terminal_repaired/$', views.TerminalRepairedWarning.as_view(),),
    re_path('^server_unrepaired/$', views.ServerUnrepairedWarning.as_view(),),
    re_path('^terminal_unrepaired/$', views.TerminalUnrepairedWarning.as_view(),),
    re_path('^server_warning_pct/$', views.ServerWarningPercent.as_view(),),
    re_path('^terminal_warning_pct/$', views.TerminalWarningPercent.as_view(),),
    re_path('^server_dev_types/$', views.ServerWarningDevTypes.as_view(),),
    re_path('^terminal_dev_types/$', views.TerminalWarningDevTypes.as_view(),),
    re_path('^codes/$', views.WarningCodes.as_view(),),
    re_path('^thresholds/$', views.Thresholds.as_view(),),
    re_path('^thresholds/(?P<pk>\d+)/$', views.ThresholdsDetail.as_view(),),
    re_path('^sub_warning/$', views.SubWarning.as_view(),),
    re_path('^sub_warning/(?P<pk>\d+)/$', views.SubWarningDetail.as_view(),),
    re_path('^rules/$', views.Rules.as_view(),),
    re_path('^rules/(?P<pk>\d+)/$', views.RulesDetail.as_view(),),
    re_path('^export/$', views.ExportWarning.as_view(),),
    re_path('^ignore/$', views.IgnoreWarning.as_view(),),
]