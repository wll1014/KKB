#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

import logging
import json
import jsonpath
from rest_framework import serializers
from overview.models import *
from warning.models import ServerWarningUnrepairedModel, TerminalWarningUnrepairedModel
from django.db import connections
from overview import query_func
from common.my_elastic import es_client
from common.ip2gps.ip2gps import ip2gps

logger = logging.getLogger('ops.' + __name__)


class ProvinceSerializers(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = ProvinceModel


class CitySerializers(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = CityModel


class GisConfSerializers(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = GisConfModel


class GisConfPostSerializers(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = GisConfModel

    def validate(self, attrs):
        count = self.Meta.model.objects.all().count()
        if count > 0:
            raise serializers.ValidationError('已有配置，请修改现有配置')
        return attrs


class GisConfGetSerializers(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = GisConfModel
        depth = 1


class GisMachineRoomSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = GisMachineRoomModel

    coordinate = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    platform_moid = serializers.SerializerMethodField()
    platform_name = serializers.SerializerMethodField()
    machine_num = serializers.SerializerMethodField()

    def get_coordinate(self, obj):
        return obj.coordinate_str.split(',')

    def get_status(self, obj):
        # 查询机房下的所有机器moid
        try:
            with connections['luban'].cursor() as cursor:
                sql = '''
                SELECT machine_moid FROM `machine_info` WHERE machine_room_moid=%s
                '''
                params = [obj.moid]
                cursor.execute(sql, params)
                fetchall = cursor.fetchall()
                machine_moids = [machine_moid[0] for machine_moid in fetchall]
        except Exception:
            machine_moids = []
        # 未修复告警中存在这些moid，则状态为1（异常）
        is_warning = ServerWarningUnrepairedModel.objects.filter(device_moid__in=machine_moids).count()
        if is_warning:
            return 1
        return 0

    def get_platform_moid(self, obj):
        # 获取平台域moid
        try:
            with connections['luban'].cursor() as cursor:
                sql = '''
                SELECT di.domain_moid,di.domain_name 
                FROM `machine_room_info` mri 
                LEFT JOIN domain_info di 
                ON mri.domain_moid=di.domain_moid 
                WHERE machine_room_moid=%s
                '''
                params = [obj.moid]
                cursor.execute(sql, params)
                fetchone = cursor.fetchone()
                machine_num_sql = '''
                SELECT count(*) as machine_num FROM machine_info
                WHERE machine_room_moid=%s
                '''
                cursor.execute(machine_num_sql, params)
                machine_num_fetchone = cursor.fetchone()
                machine_num = machine_num_fetchone[0]
                self.machine_info = {
                    obj.moid: {'machine_num': machine_num, 'platform_moid': fetchone[0], 'platform_name': fetchone[1]}
                }
        except Exception:
            self.machine_info = {}
        return self.machine_info.get(obj.moid, {}).get('platform_moid', '')

    def get_platform_name(self, obj):
        # 获取平台域名称
        return self.machine_info.get(obj.moid, {}).get('platform_name', '')

    def get_machine_num(self, obj):
        # 获取机房内的机器数量
        return self.machine_info.get(obj.moid, {}).get('machine_num', '')


class GisTerminalModelSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = GisTerminalModel

    status = serializers.SerializerMethodField()
    user_domain_moid = serializers.SerializerMethodField()
    user_domain_name = serializers.SerializerMethodField()
    mtip = serializers.SerializerMethodField()
    mttype = serializers.SerializerMethodField()
    coordinate = serializers.SerializerMethodField()

    def get_status(self, obj):
        online_status = query_func.get_terminal_online_status(obj.moid)
        if online_status == 'EV_DEV_OFFLINE':
            return 2
        is_warning = TerminalWarningUnrepairedModel.objects.filter(device_moid=obj.moid).count()
        if is_warning:
            return 1
        return 0

    def get_user_domain_moid(self, obj):
        # 用户域moid
        try:
            with connections['movision'].cursor() as cursor:
                sql = '''
                SELECT ud.user_domain_moid,ud.user_domain_name,ui.e164 
                FROM user_info ui LEFT JOIN user_domain ud 
                ON ui.user_domain_moid=ud.user_domain_moid 
                WHERE moid=%s 
                '''
                params = [obj.moid]
                cursor.execute(sql, params)
                fetchone = cursor.fetchone()
                self.terminal_info = {
                    obj.moid: {'user_domain_moid': fetchone[0], 'user_domain_name': fetchone[1], 'e164': fetchone[2]}
                }
        except Exception as e:
            logger.error(str(e))
            self.terminal_info = {}
        return self.terminal_info.get(obj.moid, {}).get('user_domain_moid', '')

    def get_user_domain_name(self, obj):
        # 用户域名称
        return self.terminal_info.get(obj.moid, {}).get('user_domain_name', '')

    def get_mtip(self, obj):
        # 终端ip
        search_body = {"size": 1,
                       "_source": ["source.mt_info.netinfo.ip", "source.mt_info.netinfo.nat_ip", "source.devtype"],
                       "sort": [{"@timestamp": {"order": "desc"}}], "query": {"bool": {
                "must": [{"match_phrase": {"source.devid": {"query": obj.moid}}},
                         {"match_phrase": {"source.eventid": {"query": "EV_MT_INFO"}}},
                         {"range": {"@timestamp": {"gte": "now-30d/m"}}}]}}}
        logger.info('mtip_mttype search body: %s' % json.dumps(search_body))
        try:
            # 查询终端的ip和类型
            es_response = es_client.search(index='platform-*mt*', body=search_body)
            self.terminal_ip_type_info = {obj.moid: {
                'mtip': jsonpath.jsonpath(es_response, '$..netinfo.ip')[0]
                if jsonpath.jsonpath(es_response, '$..netinfo.ip') else '',
                'nat_ip': jsonpath.jsonpath(es_response, '$..netinfo.nat_ip')[0]
                if jsonpath.jsonpath(es_response, '$..netinfo.nat_ip') else '',
                'mttype': jsonpath.jsonpath(es_response, '$..devtype')[0]
                if jsonpath.jsonpath(es_response, '$..devtype') else '',
            }}
            logger.info(self.terminal_ip_type_info)
        except Exception as e:
            logger.error(str(e))
            self.terminal_ip_type_info = {}
        return self.terminal_ip_type_info.get(obj.moid, {}).get('nat_ip', '')

    def get_mttype(self, obj):
        # 终端设备类型
        return self.terminal_ip_type_info.get(obj.moid, {}).get('mttype', '')

    def get_coordinate(self, obj):
        # 获取地理坐标，优先级：手动填写 > ip转换 > 空
        if obj.coordinate_str:
            return obj.coordinate_str.split(',')
        else:
            default_coordinate = coordinate = ['']
            mtip = self.terminal_ip_type_info.get(obj.moid, {}).get('nat_ip', '')
            if mtip:
                coordinate = ip2gps(mtip)
                if not coordinate:
                    logger.warning('moid: %s, ip: %s can not to gps' % (obj.moid, mtip))
                    coordinate = default_coordinate
            return coordinate


class GisPeripheralSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = GisPeripheralModel

    coordinate = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    def get_coordinate(self, obj):
        return obj.coordinate_str.split(',')

    def get_status(self, obj):
        is_warning = ServerWarningUnrepairedModel.objects.filter(device_moid=obj.moid).count()
        if is_warning:
            return 1
        return 0
