# !/usr/bin/env python
# -*- coding:utf-8 -*-

from django.urls import path, re_path
from overview import views

urlpatterns = [
    # re_path('^closed_confs/$', views.ClosedConfs.as_view(),),
    re_path('^recreate_gis_map/$', views.RecreateGisMap.as_view(), name='recreate-gis-map'),
    re_path('^provinces/$', views.Province.as_view(), name='province'),
    re_path('^cities/$', views.City.as_view(), name='city'),
    re_path('^gis_config/$', views.GisConf.as_view(), name='gis-config'),
    re_path('^gis_config/(?P<pk>\d+)/$', views.GisConfDetail.as_view(), name='gis-config-detail'),
    re_path('^confs/$', views.Confs.as_view(), name='confs'),

    # gis配置页面添加终端相关
    re_path('^user_domain/$', views.UserDomain.as_view(), name='user-domain'),
    re_path('^(?P<user_domain_moid>\w{24})/user_info/$', views.UserInfo.as_view(), name='user-info'),
    re_path('^user_info/$', views.SearchUserInfo.as_view(), name='user-info'),
    re_path('^terminals/$', views.Terminal.as_view(), name='terminals'),
    re_path('^terminals/(?P<pk>\d+)/$', views.TerminalDetail.as_view(), name='terminals-detail'),

    # gis配置页面添加机房相关
    re_path('^luban_domains/$', views.LubanDomain.as_view(), name='luban-domain'),
    re_path('^(?P<domain_moid>[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12})/machine_room_info/$',
            views.LubanDomainMachineRoom.as_view(), name='luban-domain'),
    re_path('^machine_room_info/$', views.SearchLubanDomainMachineRoom.as_view(), name='search-machine-room-info'),
    re_path('^machine_rooms/$', views.MachineRoom.as_view(), name='machine-room'),
    re_path('^machine_rooms/(?P<pk>\d+)/$', views.MachineRoomDetail.as_view(), name='machine-room-detail'),

    # gis配置页面添加外设相关
    re_path('^over_peripheral_rooms/$', views.OverPeripheralRoom.as_view(), name='luban-machine-room'),
    re_path(
        '^(?P<machine_room_moid>[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12})/luban_peripheral_info/$',
        views.LubanPeripheral.as_view(), name='luban-peripheral'),
    re_path('^luban_peripheral_info/$', views.SearchLubanPeripheral.as_view(), name='search-lperipheral-info'),
    re_path('^peripherals/$', views.Peripheral.as_view(), name='peripherals'),
    re_path('^peripherals/(?P<pk>\d+)/$', views.PeripheralDetail.as_view(), name='peripherals-detail'),

    # 机房相关（树形列表用）
    re_path('^over_machine_rooms/$', views.OverMachinelRoom.as_view(), name='luban-machine-room-over-machine'),
    re_path(
        '^(?P<machine_room_moid>[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12})/luban_machine_info/$',
        views.LubanMachine.as_view(), name='luban-machine'),
    re_path('^luban_machine_info/$', views.SearchLubanMachine.as_view(), name='search-machine-info'),

    # gis连线相关
    re_path('^gis/links/$', views.GisLink.as_view(), name='links'),
    re_path('^gis/links/(?P<e164>\d{13})/$', views.TerminalInConfLink.as_view(), name='mt_in_conf_link'),
]
