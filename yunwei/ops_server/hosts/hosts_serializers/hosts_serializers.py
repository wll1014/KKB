#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

import json
from hosts.models import *
from rest_framework import serializers
from warning.models import ServerWarningUnrepairedModel

class HostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineInfo
        exclude = ('ip_list','frame_moid',)

class HostSyncSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = MachineInfo


class HostDetailSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = MachineInfo

    # ip列表获取
    ip_list = serializers.SerializerMethodField()
    def get_ip_list(self,obj):
        return json.loads(obj.ip_list)

    # 分组名称获取
    group = serializers.SerializerMethodField()
    def get_group(self, obj):
        content_type_id = ContentType.objects.filter(app_label='hosts', model='machinegroup').first().id
        moid = obj.moid
        machine_profile_obj = MachineProfile.objects.filter(moid=moid, content_type_id=content_type_id).first()

        return machine_profile_obj.content_object.name

    # 主机是否告警获取
    status = serializers.SerializerMethodField()
    def get_status(self, obj):
        moid = obj.moid
        is_warning = ServerWarningUnrepairedModel.objects.filter(device_moid=moid).count()
        if is_warning:
            return 1
        return 0


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = MachineGroup


class MachineProfileSerializer(serializers.ModelSerializer):
    class Meta:
        # fields = '__all__'
        exclude = ('object_id', 'content_type')
        model = MachineProfile

    group = serializers.SerializerMethodField()
    def get_group(self, obj):
        return obj.content_object.name

    status = serializers.SerializerMethodField()
    def get_status(self, obj):
        moid = obj.moid
        is_warning = ServerWarningUnrepairedModel.objects.filter(device_moid=moid).count()
        if is_warning:
            return 1
        return 0
