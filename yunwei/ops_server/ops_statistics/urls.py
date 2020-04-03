# !/usr/bin/env python
# -*- coding:utf-8 -*-

from django.urls import path, re_path
from ops_statistics import views, nginx_statistics_views

urlpatterns = [
    re_path(r'^media_resources/$', views.ConfResourcesStatistics.as_view(), ),
    re_path(r'^conf_resources/$', views.ConfResources.as_view(), ),
    re_path(r'^p2p_conf_resources/$', views.P2PConfResources.as_view(), ),
    re_path(r'^h_transmit_resources/$', views.TransmitResources.as_view(), ),
    re_path(r'^terminal_resources/$', views.TerminalResources.as_view(), ),
    re_path(r'^conf_time/$', views.ConfTime.as_view(), ),
    re_path(r'^calling_terminals/$', views.CallingTerminal.as_view(), ),
    re_path(r'^curr_terminals/$', views.CurrTerminal.as_view(), ),
    re_path(r'^curr_confs/$', views.CurrConfNum.as_view(), ),
    re_path(r'^vrs/$', views.LiveConfNum.as_view(), ),
    re_path(r'^vrs_resources/$', views.VrsResourcesStatistics.as_view(), ),
    re_path(r'^appointment/$', views.AppointmentConf.as_view(), ),
    re_path(r'^company_info/$', views.CompanyInfo.as_view(), ),
    re_path(r'^terminal_info/$', views.TerminalInfo.as_view(), ),
    re_path(r'^create_conf_type/$', views.CreateConfTypeStatistics.as_view(), ),
    re_path(r'^create_conf_type_detail/$', views.CreateConfTypeDetail.as_view(), ),
    re_path(r'^create_conf_type_export/$', views.CreateConfTypeDetailExport.as_view(), ),
    re_path(r'^company_conf/$', views.CompanyConf.as_view(), ),
    re_path(r'^company_conf_export/$', views.CompanyConfExport.as_view(), ),
    re_path(r'^create_conf_time/$', views.CreateConfReq2AckTime.as_view(), ),
    re_path(r'^img_position/$', views.Position.as_view(), ),
    re_path(r'^img_position/(?P<pk>\d+)/$', views.PositionDetail.as_view(), ),
    re_path(r'^(?P<type>cpu|memory|network_in|network_out|disk|diskage)/$', views.HardWareResource.as_view(), ),
    path('equipment_usage/', views.EquipmentUsage.as_view(), ),
    path('equipment_online/', views.EquipmentRuntime.as_view(), ),
    path('terminal_meeting_time/', views.TerminalMeetingTime.as_view(), ),
    path('terminal_meeting_time_export/', views.TerminalMeetingTimeExport.as_view(), ),
    path('terminal_meeting_freq/', views.TerminalMeetingFreq.as_view(), ),
    path('terminal_meeting_freq_export/', views.TerminalMeetingFreqExport.as_view(), ),
    path('labor_time/', views.LaborTime.as_view(), ),
]

# web请求统计url
web_requests_urlpatterns = [
    re_path(r'^requests/outline/$', nginx_statistics_views.OutLine.as_view(), name='outline'),
    re_path(r'^requests/traffic/$', nginx_statistics_views.RequestTraffic.as_view(), name='traffic'),
    re_path(r'^requests/pv/$', nginx_statistics_views.PV.as_view(), name='pv'),
    re_path(r'^requests/ip/$', nginx_statistics_views.IP.as_view(), name='ip'),
    re_path(r'^requests/slow_responses/$', nginx_statistics_views.SlowResponses.as_view(), name='slow_responses'),
    re_path(r'^requests/urls/$', nginx_statistics_views.URLs.as_view(), name='urls'),
    re_path(r'^requests/clients_pct/$', nginx_statistics_views.ClientsPct.as_view(), name='clients_pct'),
    re_path(r'^requests/clients/$', nginx_statistics_views.Clients.as_view(), name='clients'),
    re_path(r'^requests/status_code/$', nginx_statistics_views.StatusCode.as_view(), name='status_code'),
    re_path(r'^requests/errors/$', nginx_statistics_views.Errors.as_view(), name='errors'),
    re_path(r'^requests/methods/$', nginx_statistics_views.Methods.as_view(), name='methods'),
    re_path(r'^requests/modules/$', nginx_statistics_views.Modules.as_view(), name='modules'),
    re_path(r'^requests/detail/$', nginx_statistics_views.Detail.as_view(), name='detail'),
    re_path(r'^requests/export/$', nginx_statistics_views.Export.as_view(), name='export'),
]

urlpatterns += web_requests_urlpatterns
