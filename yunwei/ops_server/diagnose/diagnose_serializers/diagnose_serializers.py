#!/usr/bin/env python3
# coding: utf-8

__author__ = 'wanglei_sxcpx@kedacom.com'

import time
import logging
import copy
from django.utils import timezone
from rest_framework import serializers
from diagnose.models import SnapshotTaskModel, QuickCaptureTaskModel, CustomCaptureTaskModel, CustomCaptureItemsModel
from diagnose.models import LinkCheckerModel
from diagnose.query_func import get_luban_machines_info, get_mt_info

logger = logging.getLogger('ops.' + __name__)


class SnapShotSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = SnapshotTaskModel

    start_time_as_string = serializers.SerializerMethodField()

    def get_start_time_as_string(self, obj):
        return timezone.datetime.fromtimestamp(float(obj.start_time) / 1000)


class LinkSerializer(serializers.ModelSerializer):
    is_complete = serializers.SerializerMethodField()
    need_del = serializers.SerializerMethodField()

    class Meta:
        model = LinkCheckerModel
        fields = '__all__'

    def get_is_complete(self, obj):
        return int(obj.is_complete)

    def get_need_del(self, obj):
        return int(obj.need_del)


class QuickCaptureSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = QuickCaptureTaskModel

    start_time_as_string = serializers.SerializerMethodField()

    def get_start_time_as_string(self, obj):
        return timezone.datetime.fromtimestamp(float(obj.start_time) / 1000)


class CustomCaptureItemsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        # exclude = ('task',)
        model = CustomCaptureItemsModel

    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        moid = obj.moid
        item_type = obj.item_type
        if item_type == 1:
            machines_info = get_luban_machines_info([moid])
            name = machines_info.get(moid, {}).get('machine_name')
        else:
            mt_info = get_mt_info([moid])
            name = mt_info.get(moid, {}).get('name')
        return name


class CustomCaptureItemsRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        depth = 1
        # exclude = ('task',)
        model = CustomCaptureItemsModel


class CustomCaptureListSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = CustomCaptureTaskModel

    start_time_as_string = serializers.SerializerMethodField()

    def get_start_time_as_string(self, obj):
        return timezone.datetime.fromtimestamp(float(obj.start_time) / 1000)


class CustomCaptureRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = CustomCaptureTaskModel

    start_time_as_string = serializers.SerializerMethodField()

    def get_start_time_as_string(self, obj):
        return timezone.datetime.fromtimestamp(float(obj.start_time) / 1000)

    items = serializers.SerializerMethodField()

    def get_items(self, obj):
        return CustomCaptureItemsSerializer(obj.customcaptureitemsmodel_set.all(), many=True).data

    is_complete = serializers.SerializerMethodField()

    def get_is_complete(self, obj):
        '''
        任务是否完成 0：未完成，1：已完成, 2：抓包失败， 3：无子任务或全部子任务都未开始
        :param obj:
        :return:
        '''
        items = obj.customcaptureitemsmodel_set.all()
        if not items:
            is_complete = 3
        else:
            items_complete = [item.is_complete for item in items]
            if 2 in items_complete:
                is_complete = 2
            elif 0 in items_complete:
                is_complete = 0
            elif items_complete.count(3) == len(items_complete):
                is_complete = 3
            else:
                is_complete = 1
        return is_complete
