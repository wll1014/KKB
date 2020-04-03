from django.shortcuts import render, redirect

# Create your views here.
import logging
import json
import jsonpath
import os
import csv
import time
import requests
from lxml import etree
from django.db import connection, transaction, connections
from django.db.models import F, Q
from django.http.response import FileResponse
from django.contrib.contenttypes.models import ContentType
from rest_framework.views import APIView
from rest_framework.response import Response
from common import my_elastic, global_func
from common.my_elastic import es_client
import copy
from hosts.models import *
from hosts.hosts_serializers.hosts_serializers import *
from common.pagination import ResultsSetPaginationOffset
from ops.settings import NO_DETAIL_DEV_TYPES, MEDIA_ROOT
from hosts.dsl.es_ql import top_cpu_processes_dsl, top_mem_processes_dsl

logger = logging.getLogger('ops.' + __name__)


class Login(APIView):
    # 测试时获取ssoToken 使用
    def post(self, request, *args, **kwargs):
        try:
            auth_ip = global_func.get_conf('auth', 'ip')
            base_url = 'http://%s' % auth_ip
            url = base_url + '/apiCore/sso/userLogin'

            token = global_func.get_token(auth_ip)
            username = request.data.get('username')
            password = request.data.get('password')
            ret = requests.post(url, params={'userName': username, 'password': password, 'account_token': token})
            print(ret.text)

            xml = etree.fromstring(ret.text)
            ssoToken = xml.xpath('/userVO/token/text()')[0]
            return Response({'ssoToken': 'SSO_COOKIE_KEY=%s' % ssoToken})
        except Exception as e:
            logger.error(e)
            return Response({})


class DeploySync(APIView):
    # 同步部署数据
    def post(self, request, *args, **kwargs):
        try:
            luban_ip = global_func.get_conf('luban', 'ip')
            luban_port = global_func.get_conf('luban', 'port')
            url = 'http://%s:%s/luban/api/devices' % (luban_ip, luban_port)
            # url = 'http://127.0.0.1:9090/api/v1/ops/logger/' # 测试使用，获取多机房，多机器信息
            try:
                logger.info('sync luban(%s:%s) info' % (luban_ip, luban_port))
                ret = requests.get(url)
                logger.info('luban hosts info: %s' % ret.text)
                data = json.loads(ret.text)
            except Exception as e:
                logger.error(str(e))
                data = {'success': 0}
            if data.get('success'):
                # 存储主机分组内主机的moid
                with connections['luban'].cursor() as cursor:
                    frame_sql = '''
                    SELECT frame_moid,frame_type FROM frame_info;
                    '''
                    cursor.execute(frame_sql)
                    fetchall = cursor.fetchall()
                frame_moid2type = {fetch[0]:fetch[1] for fetch in fetchall}
                group_machine_l = list()
                # 存储数据校验的错误信息
                error_l = list()
                # 确认拿到luban数据后，清空本地数据库，按luban数据重新存储
                sql = 'TRUNCATE TABLE %s' % (MachineInfo._meta.db_table)
                cursor = connection.cursor()
                cursor.execute(sql)
                for device in data.get('devices'):
                    machine_moid = device.get('machine_moid')

                    group_machine_l.append(machine_moid)

                    machine_name = device.get('machine_name')
                    machine_type = device.get('machine_type')
                    has_detail = 1 if machine_type not in NO_DETAIL_DEV_TYPES else 0
                    cluster = device.get('cluster')
                    belong_frame = device.get('belong_frame')
                    frame_moid = device.get('belong_moid')
                    # 机框类型
                    frame_type = frame_moid2type.get(frame_moid)
                    # 机框槽位
                    frame_slot = device.get('belong_slot')
                    room_name = device.get('machine_room_name')
                    room_moid = device.get('machine_room_moid')
                    domain_name = device.get('domain_name')
                    domain_moid = device.get('domain_moid')
                    ip_list = device.get('ip_list', [])
                    local_ip = '0.0.0.0'
                    for ip in ip_list:
                        if ip.get('flag') == 1:
                            # flag 1 的为本地ip
                            local_ip = ip.get('ip')

                    # 存储获取到的主机信息
                    tmp_dict = dict()
                    tmp_dict.update(
                        {
                            'moid': machine_moid,
                            'name': machine_name,
                            'machine_type': machine_type,
                            'has_detail': has_detail,
                            'cluster': cluster,
                            'frame_name': belong_frame,
                            'frame_moid': frame_moid,
                            'frame_slot': frame_slot,
                            'frame_type': frame_type,
                            'room_name': room_name,
                            'room_moid': room_moid,
                            'domain_name': domain_name,
                            'domain_moid': domain_moid,
                            'ip_list': json.dumps(ip_list),
                            'local_ip': local_ip
                        }
                    )
                    hds = HostSyncSerializer(data=tmp_dict)
                    logger.info(json.dumps(tmp_dict))
                    if hds.is_valid():
                        hds.save()
                        try:
                            group_obj = MachineGroup.objects.get(name='未分组')
                        except MachineGroup.DoesNotExist as e:
                            logger.debug('未分组 group does not exist , create !' + str(e))
                            group_obj = MachineGroup.objects.create(name='未分组')
                        try:
                            # 更新主机信息概要表
                            obj = MachineProfile.objects.filter(moid=machine_moid)
                            if obj:
                                # 存在则更新
                                for machine_profile_obj in obj:
                                    machine_profile_obj.name = machine_name
                                    machine_profile_obj.moid = machine_moid
                                    machine_profile_obj.local_ip = local_ip
                                    machine_profile_obj.machine_type = machine_type
                                    machine_profile_obj.has_detail = has_detail
                                    machine_profile_obj.cluster = cluster
                                    machine_profile_obj.frame_name = belong_frame
                                    machine_profile_obj.frame_moid = frame_moid
                                    machine_profile_obj.frame_slot = frame_slot
                                    machine_profile_obj.frame_type = frame_type
                                    machine_profile_obj.room_name = room_name
                                    machine_profile_obj.room_moid = room_moid
                                    machine_profile_obj.domain_name = domain_name
                                    machine_profile_obj.domain_moid = domain_moid
                                    machine_profile_obj.save()
                            else:
                                # 不存在则创建
                                MachineProfile.objects.create(
                                    name=machine_name,
                                    moid=machine_moid,
                                    local_ip=local_ip,
                                    machine_type=machine_type,
                                    has_detail=has_detail,
                                    cluster=cluster,
                                    frame_name=belong_frame,
                                    frame_moid=frame_moid,
                                    frame_slot=frame_slot,
                                    frame_type=frame_type,
                                    room_name=room_name,
                                    room_moid=room_moid,
                                    domain_name=domain_name,
                                    domain_moid=domain_moid,
                                    content_object=group_obj,
                                )

                        except Exception as e:
                            logger.error(str(e) + 'create %s' % machine_moid)
                    else:
                        logger.error(json.dumps(hds.errors))
                        error_l.append(hds.errors)

                for obj in MachineProfile.objects.all():
                    if obj.moid not in group_machine_l:
                        obj.delete()
                        logger.info('delete old machine, moid is %s' % obj.moid)

                if error_l:
                    response = global_func.get_response(0, error_msg=error_l)
                    return Response(response)
                else:
                    response = global_func.get_response()
                    return Response(response)
            else:
                response = global_func.get_response(0, error_code=10004)
                return Response(response)
        except Exception as e:
            logger.error(str(e))
            response = global_func.get_response(0)
            return Response(response)


class Hosts(APIView):
    # 获取主机列表
    def get(self, request, *args, **kwargs):
        try:
            domain_moid = request.query_params.get('domain_moid')
            group_id = request.query_params.get('group_id')
            room_moid = request.query_params.get('room_moid')
            query = request.query_params.get('query')
            content = ContentType.objects.filter(app_label='hosts', model='machinegroup').first()
            if domain_moid:
                if group_id:
                    # 因为组是归属于机房的，所以有group_id的优先根据组id筛选
                    group = MachineGroup.objects.filter(id=group_id).first()
                    if group:
                        data = group.machine.filter(domain_moid=domain_moid)
                    else:
                        data = []
                elif room_moid:
                    # 根据机房moid筛选
                    data = MachineProfile.objects.filter(
                        room_moid=room_moid,
                        domain_moid=domain_moid,
                        content_type_id=content.id
                    )
                else:
                    # 只有domain_moid过滤条件
                    data = MachineProfile.objects.filter(
                        domain_moid=domain_moid,
                        content_type_id=content.id
                    )
            else:
                if group_id:
                    # 因为组是归属于机房的，所以有group_id的优先根据组id筛选
                    group = MachineGroup.objects.filter(id=group_id).first()
                    if group:
                        data = group.machine.all()
                    else:
                        data = []
                elif room_moid:
                    # 根据机房moid筛选
                    data = MachineProfile.objects.filter(
                        room_moid=room_moid,
                        content_type_id=content.id
                    )
                else:
                    # 无过滤条件返回全部信息
                    data = MachineProfile.objects.filter(
                        content_type_id=content.id
                    )

            if data and query:
                # 页面的查询过滤功能，基于上面moid筛选后的结果过滤
                data = data.filter(Q(name__contains=query) | Q(local_ip__contains=query))
            #
            # # 不返回jdb4000
            # data = data.filter(~Q(machine_type='jdb4000'))
            # 没有详情的数据排在后面
            data = data.order_by('-has_detail')
            pagination = ResultsSetPaginationOffset()
            # 根据ucd图，修改默认返回条数为19
            pagination.default_limit = 19
            pg_ret = pagination.paginate_queryset(queryset=data, request=request, view=self)
            hs = MachineProfileSerializer(instance=pg_ret, many=True)
            return pagination.get_paginated_response(data=hs.data)
        except Exception as e:
            logger.error(str(e))
            response = global_func.get_response(0, error_code=10005)
            return Response(response)


class HostDetail(APIView):
    # 获取主机详情
    def get(self, request, *args, **kwargs):
        machine_moid = kwargs.get('machine_moid')
        if machine_moid:
            try:
                machine_obj = MachineInfo.objects.filter(moid=machine_moid).first()
                if machine_obj:
                    hds = HostDetailSerializer(instance=machine_obj, many=False)
                    response = global_func.get_response(data=hds.data)
                    return Response(response)
                else:
                    response = global_func.get_response(data={})
                    return Response(response)
            except Exception as e:
                logger.error(str(e))
                response = global_func.get_response(0, error_code=10005)
                return Response(response)
        else:
            response = global_func.get_response(0, error_msg='机器moid有误')
            return Response(response)


class Group(APIView):
    # 主机分组
    def get(self, request, *args, **kwargs):
        try:
            domain_moid = request.query_params.get('domain_moid', '')
            info_l = []
            room_l = []
            room_d = {}
            domain_d = {}
            sql = '''
            SELECT mri.machine_room_moid,mri.machine_room_name,di.domain_moid,di.domain_name FROM machine_room_info mri
            LEFT JOIN domain_info di on mri.domain_moid=di.domain_moid
            '''
            # 机房moid去重后放入列表
            if domain_moid:
                sql += ' WHERE di.domain_moid=%s ORDER BY mri.id'
                params = [domain_moid]
            else:
                sql += '  ORDER BY mri.id'
                params = []
            try:
                with connections['luban'].cursor() as cursor:
                    cursor.execute(sql, params)
                    fetchall = cursor.fetchall()
                    room_l = [fetch[0] for fetch in fetchall]
                    room_d = {fetch[0]: fetch[1] for fetch in fetchall}
                    domain_d = {fetch[2]: fetch[3] for fetch in fetchall}
            except Exception as e:
                logger.error(str(e))
            if room_d:
                for room in room_l:
                    # 生成data列表
                    group_l = []
                    obj = MachineGroup.objects.all()
                    for group in obj:
                        if group.room_moid == room:
                            group_l.append(
                                {
                                    'name': group.name,
                                    'id': group.id,
                                    'count': len(group.machine.all()),
                                }
                            )

                    info = {
                        'room_moid': room,
                        # 'room_name': MachineInfo.objects.filter(room_moid=room).first().room_name,
                        'room_name': room_d.get(room),
                        'count': MachineInfo.objects.filter(room_moid=room).count(),
                        'group': group_l
                    }
                    info_l.append(info)
            data = {
                'info': info_l,
                'domain_moid': domain_moid,
                # 'domain_name': MachineProfile.objects.filter(domain_moid=domain_moid).first().domain_name,
                'domain_name': domain_d.get(domain_moid) if domain_d.get(domain_moid) else '',
            }
            response = global_func.get_response(data=data)
            return Response(response)

        except Exception as e:
            logger.error(e)
            response = global_func.get_response(0, error_code=10005)
            return Response(response)

    def post(self, request, *args, **kwargs):
        # 创建分组，需接收参数name,room_moid
        group_name = request.data.get('name')
        room_moid = request.data.get('room_moid')
        if group_name and room_moid:
            tmp_dict = dict()
            tmp_dict.update(
                {
                    'name': group_name,
                    'room_moid': room_moid,
                }
            )
            gs = GroupSerializer(data=tmp_dict)
            if gs.is_valid():
                gs.save()
                response = global_func.get_response()
            else:
                logger.error(str(gs.errors))
                if 'unique' in str(gs.errors):
                    response = global_func.get_response(0, error_code='10006')
                elif 'not be null' in str(gs.errors):
                    response = global_func.get_response(0, error_code='10007')
                else:
                    response = global_func.get_response(0, error_code='10005')
            return Response(response)
        else:
            response = global_func.get_response(0, error_code=10008)
            return Response(response)

    def delete(self, request, *args, **kwargs):
        try:
            # 获取待删除数据id的数组
            group_ids = request.data.get('ids')

            # 默认分组（name=未分组）不删除
            obj = MachineGroup.objects.filter(name='未分组')
            default_group_ids = list()

            for default_group in obj:
                default_group_ids.append(default_group.id)

            group_ids = list(set(group_ids).difference(set(default_group_ids)))

        except Exception as e:
            logger.error(str(e))
            response = global_func.get_response(0, error_code=10007)
            return Response(response)
        else:
            if not all([isinstance(x, int) for x in group_ids]):
                response = global_func.get_response(0, error_code=10007)
                return Response(response)

        # 执行删除
        try:
            with transaction.atomic():
                content = ContentType.objects.filter(app_label='hosts', model='machinegroup').first()
                no_group = MachineGroup.objects.get(name='未分组')
                # 主机移动至未分组
                MachineProfile.objects.filter(
                    content_type_id=content.id,
                    object_id__in=group_ids
                ).update(object_id=no_group.id)
                MachineGroup.objects.filter(id__in=group_ids).delete()
        except Exception as e:
            logger.error(str(e))
            response = global_func.get_response(0, error_code=10007)
            return Response(response)
        else:
            response = global_func.get_response()
            return Response(response)


class GroupDetail(APIView):
    def put(self, request, *args, **kwargs):
        # 修改分组名称
        try:
            name = request.data.get('name')
            group_id = kwargs.get('group_id')
            if not MachineGroup.objects.filter(pk=group_id).first().room_moid:
                response = global_func.get_response(0, error_code=10009)
            else:
                if name and group_id:
                    MachineGroup.objects.filter(pk=group_id).update(name=name)
                    response = global_func.get_response()
                else:
                    response = global_func.get_response(0, error_code=10007)
            return Response(response)

        except Exception as e:
            logger.error(str(e))
            response = global_func.get_response(0, error_code=10005)
            return Response(response)


class Domain(APIView):
    def get(self, request, *args, **kwargs):
        # 获取所有域的信息
        try:
            with connections['luban'].cursor() as cursor:
                sql = '''
                SELECT domain_name,domain_moid FROM domain_info 
                WHERE domain_status !=2
                ORDER BY domain_type DESC
                '''
                cursor.execute(sql)
                fetchall = cursor.fetchall()

            domain_info = [
                {
                    'domain_name': fetch[0],
                    'domain_moid': fetch[1]
                } for fetch in fetchall
            ]
            response = global_func.get_response(data=domain_info)
            return Response(response)
        except Exception as e:
            logger.error(str(e))
            response = global_func.get_response(0, error_code=10005)
            return Response(response)


class GroupHandle(APIView):
    # 对主机的分组操作
    def put(self, request, *args, **kwargs):
        try:
            group_id = kwargs.get('group_id')
            machine_moids = request.data.get('machine_moids')
            group = MachineGroup.objects.get(id=group_id)
            content = ContentType.objects.filter(app_label='hosts', model='machinegroup').first()
            for machine_moid in machine_moids:
                obj = MachineProfile.objects.filter(moid=machine_moid)
                machine = MachineInfo.objects.get(moid=machine_moid)
                for machine_profile_obj in obj:
                    if isinstance(machine_profile_obj.content_object, MachineGroup):
                        machine_profile_obj.object_id = group_id
                        machine_profile_obj.save()

            response = global_func.get_response()
            return Response(response)

        except Exception as e:
            logger.error(str(e))
            response = global_func.get_response(0, error_code=10005)
            return Response(response)


class CpuUsage(APIView):
    def get(self, request, *args, **kwargs):
        metricset_name = 'cpu'
        machine_moid = kwargs.get('machine_moid')
        start_time, end_time, interval = es_client.get_time_info(request)
        _query = [['match', {'metricset.name': metricset_name}], ['match_phrase', {'beat.eqpid': machine_moid}]]
        _filter = [['range', {'@timestamp': {"gte": start_time, "lte": end_time}}]]
        metric = []
        for field in es_client.fields_dic.get(metricset_name):
            metric.append([field.replace('.', '_'), 'avg', {'field': field}])

        _aggs = [
            {
                'bucket': ['by_time', 'date_histogram', {
                    "field": "@timestamp", "interval": interval,
                    "time_zone": "+08:00", "format": "yyyy-MM-dd HH:mm:ss", "min_doc_count": 0
                }],
                'metric': metric,
                'pipeline': [],
            }
        ]
        es_data = es_client.get_es_data(request, es_client, _query=_query, _filter=_filter, _aggs=_aggs, _size=0)

        data = {
            'machine_moid': machine_moid,
            'start_time': start_time,
            'end_time': end_time,
            'interval': interval
        }
        try:
            for field in es_client.fields_dic.get(metricset_name):
                data.update({
                    field: []
                })
                if hasattr(es_data, 'aggregations') and es_data.aggregations:
                    aggregations_f = getattr(es_data.aggregations, _aggs[0].get('bucket')[0])
                    for bucket in aggregations_f.buckets:
                        if hasattr(bucket, field.replace('.', '_')):
                            field_bucket_f = getattr(bucket, field.replace('.', '_'))
                            data.get(field).append([bucket.key, field_bucket_f.value])

            response = global_func.get_response(data=data)
            return Response(response)
        except Exception as e:
            logger.error(str(e))
            response = global_func.get_response(0, error_code=10002)
            return Response(response)


class CoreUsage(APIView):
    def get(self, request, *args, **kwargs):
        metricset_name = 'core'
        machine_moid = kwargs.get('machine_moid')
        core_id = kwargs.get('core_id')
        start_time, end_time, interval = es_client.get_time_info(request)
        _query = [
            ['match', {'metricset.name': metricset_name}],
            ['match_phrase', {'beat.eqpid': machine_moid}],
            ['match', {'system.core.id': core_id}],
        ]
        _filter = [['range', {'@timestamp': {"gte": start_time, "lte": end_time}}]]
        metric = []
        for field in es_client.fields_dic.get(metricset_name):
            metric.append([field.replace('.', '_'), 'avg', {'field': field}])

        _aggs = [
            {
                'bucket': ['by_time', 'date_histogram', {
                    "field": "@timestamp", "interval": interval,
                    "time_zone": "+08:00", "format": "yyyy-MM-dd HH:mm:ss", "min_doc_count": 0
                }],
                'metric': metric,
                'pipeline': []
            }
        ]
        es_data = es_client.get_es_data(request, es_client, _query=_query, _filter=_filter, _aggs=_aggs, _size=0)

        data = {
            'machine_moid': machine_moid,
            'start_time': start_time,
            'end_time': end_time,
            'interval': interval,
            'core_id': core_id,
        }
        for field in es_client.fields_dic.get(metricset_name):
            data.update({
                field: []
            })
            if hasattr(es_data, 'aggregations') and es_data.aggregations:
                aggregations_f = getattr(es_data.aggregations, _aggs[0].get('bucket')[0])
                for bucket in aggregations_f.buckets:
                    if hasattr(bucket, field.replace('.', '_')):
                        field_bucket_f = getattr(bucket, field.replace('.', '_'))
                        data.get(field).append([bucket.key, field_bucket_f.value])

        response = global_func.get_response(data=data)
        return Response(response)


class MemoryUsage(APIView):
    def get(self, request, *args, **kwargs):
        metricset_name = 'memory'
        machine_moid = kwargs.get('machine_moid')
        start_time, end_time, interval = es_client.get_time_info(request)
        _query = [['match', {'metricset.name': metricset_name}], ['match_phrase', {'beat.eqpid': machine_moid}]]
        _filter = [['range', {'@timestamp': {"gte": start_time, "lte": end_time}}]]
        metric = []
        for field in es_client.fields_dic.get(metricset_name):
            metric.append([field.replace('.', '_'), 'avg', {'field': field}])

        _aggs = [
            {
                'bucket': ['by_time', 'date_histogram', {
                    "field": "@timestamp", "interval": interval,
                    "time_zone": "+08:00", "format": "yyyy-MM-dd HH:mm:ss", "min_doc_count": 0
                }],
                'metric': metric,
                'pipeline': []
            }
        ]
        es_data = es_client.get_es_data(request, es_client, _query=_query, _filter=_filter, _aggs=_aggs, _size=0)

        data = {
            'machine_moid': machine_moid,
            'start_time': start_time,
            'end_time': end_time,
            'interval': interval,
        }
        for field in es_client.fields_dic.get(metricset_name):
            data.update({
                field: []
            })
            if hasattr(es_data, 'aggregations') and es_data.aggregations:
                aggregations_f = getattr(es_data.aggregations, _aggs[0].get('bucket')[0])
                for bucket in aggregations_f.buckets:
                    if hasattr(bucket, field.replace('.', '_')):
                        field_bucket_f = getattr(bucket, field.replace('.', '_'))
                        data.get(field).append([bucket.key, field_bucket_f.value])

        response = global_func.get_response(data=data)
        return Response(response)


class LoadGauge(APIView):
    def get(self, request, *args, **kwargs):
        metricset_name = 'load'
        machine_moid = kwargs.get('machine_moid')
        start_time, end_time, interval = es_client.get_time_info(request)
        _query = [['match', {'metricset.name': metricset_name}], ['match_phrase', {'beat.eqpid': machine_moid}]]
        _filter = [['range', {'@timestamp': {"gte": start_time, "lte": end_time}}]]
        metric = []
        for field in es_client.fields_dic.get(metricset_name):
            metric.append([field.replace('.', '_'), 'avg', {'field': field}])

        _aggs = [
            {
                'bucket': ['by_time', 'date_histogram', {
                    "field": "@timestamp", "interval": interval,
                    "time_zone": "+08:00", "format": "yyyy-MM-dd HH:mm:ss", "min_doc_count": 0
                }],
                'metric': metric,
                'pipeline': []
            }
        ]
        es_data = es_client.get_es_data(request, es_client, _query=_query, _filter=_filter, _aggs=_aggs, _size=0)

        data = {
            'machine_moid': machine_moid,
            'start_time': start_time,
            'end_time': end_time,
            'interval': interval,
        }
        try:
            for field in es_client.fields_dic.get(metricset_name):
                data.update({
                    field: []
                })
                if hasattr(es_data, 'aggregations') and es_data.aggregations:
                    aggregations_f = getattr(es_data.aggregations, _aggs[0].get('bucket')[0])
                    for bucket in aggregations_f.buckets:
                        if hasattr(bucket, field.replace('.', '_')):
                            field_bucket_f = getattr(bucket, field.replace('.', '_'))
                            data.get(field).append([bucket.key, field_bucket_f.value])

            response = global_func.get_response(data=data)
            return Response(response)

        except Exception as e:
            logger.error(str(e))
            response = global_func.get_response(0, error_code=10002)
            return Response(response)


class DiskIO(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'name': str(self.__class__)})


class DiskUsage(APIView):
    def get(self, request, *args, **kwargs):
        metricset_name = 'filesystem'
        machine_moid = kwargs.get('machine_moid')
        # 10分钟内
        start_time = (time.time() - 10 * 60) * 1000
        field_name = 'system.%s.mount_point' % metricset_name

        data = {
            'machine_moid': machine_moid,
        }

        if not request.query_params.get('partition'):
            _query_card = [
                ['match', {'metricset.name': metricset_name}],
                ['match_phrase', {'beat.eqpid': machine_moid}]
            ]

            _filter_card = [
                ['range', {'@timestamp': {"gte": start_time}}]
            ]

            metric_card = [['card', 'terms', {'field': field_name, 'size': 1000}]]

            _aggs_partition = [
                {
                    'bucket': [],
                    'metric': metric_card,
                    'pipeline': []
                }
            ]

            es_data_partition = es_client.get_es_data(request, es_client, _query=_query_card,
                                                      _filter=_filter_card, _aggs=_aggs_partition)

            # 获取到本机的所有分区挂载点名称
            partitions = []
            if hasattr(es_data_partition, 'aggregations') and es_data_partition.aggregations:
                for tag in es_data_partition.aggregations:
                    for bucket in tag.buckets:
                        partitions.append(bucket.key)

            data = copy.deepcopy(data)
            data.update(
                {
                    'partitions': partitions
                }
            )

            response = global_func.get_response(data=data)
            return Response(response)
        else:
            partition = request.query_params.get('partition')
            _query = [
                ['match', {'metricset.name': metricset_name}],
                ['match_phrase', {'beat.eqpid': machine_moid}],
                ['match', {field_name: partition}]
            ]

            _filter = [
                ['range', {'@timestamp': {"gte": start_time}}]
            ]

            _aggs = []
            _sort = '-@timestamp'
            _source = ["@timestamp", "system.filesystem"]
            es_data = es_client.get_es_data(request, es_client, _query, _filter, _aggs,
                                            _size=1, _sort=_sort, _source=_source)
            data = copy.deepcopy(data)
            if es_data:
                for hit in es_data:
                    data.update(
                        {
                            'partition': partition,
                            'free.bytes': hit.system.filesystem.free,
                            'total.bytes': hit.system.filesystem.total,
                            'used.bytes': hit.system.filesystem.used.bytes,
                            'used.pct': hit.system.filesystem.used.pct
                        }
                    )
            response = global_func.get_response(data=data)
            return Response(response)


class DiskAge(APIView):
    def get(self, request, *args, **kwargs):
        metricset_name = 'diskage'
        machine_moid = kwargs.get('machine_moid')
        # 5天内
        start_time = (time.time() - 5 * 60 * 60 * 24) * 1000
        drive = request.query_params.get('drive')

        diskage_eventid = 'EV_PFMINFO_DISK_AGE'

        data = {
            'machine_moid': machine_moid
        }

        if not drive:
            _query_drive = [
                ['match', {'source.eventid': diskage_eventid}],
                ['match_phrase', {'beat.eqpid': machine_moid}]
            ]

            _filter_drive = [
                ['range', {'@timestamp': {"gte": start_time}}]
            ]

            metric_drive = [['drive', 'terms', {'field': 'source.diskage.dev.keyword', 'size': 1000}]]

            _aggs_drive = [
                {
                    'bucket': [],
                    'metric': metric_drive,
                    'pipeline': []
                }
            ]

            es_data_drive = es_client.get_es_data(request, es_client, _query=_query_drive, _size=0,
                                                  _filter=_filter_drive, _aggs=_aggs_drive, index='machine-*')

            # 获取到本机的所有盘符名称
            drives = []
            if hasattr(es_data_drive, 'aggregations') and es_data_drive.aggregations:
                for tag in es_data_drive.aggregations:
                    for bucket in tag.buckets:
                        drives.append(bucket.key)

            data = copy.deepcopy(data)
            data.update(
                {
                    'drives': drives
                }
            )

            response = global_func.get_response(data=data)
            return Response(response)
        else:
            _query = [
                ['match', {'source.eventid': diskage_eventid}],
                ['match_phrase', {'beat.eqpid': machine_moid}],
                ['match', {'source.diskage.dev': drive}],
            ]

            _filter = [
                ['range', {'@timestamp': {"gte": start_time}}]
            ]
            metric = []

            _aggs = [
                {
                    'bucket': [],
                    'metric': metric,
                    'pipeline': []
                }
            ]

            _sort = '-@timestamp'

            _source = ['@timestamp', 'source.diskage']

            es_data = es_client.get_es_data(request, es_client, _query=_query, index='machine-*',
                                            _filter=_filter, _aggs=_aggs, _sort=_sort, _source=_source, _size=1)

            data = copy.deepcopy(data)

            for field in es_client.fields_dic.get(metricset_name):
                data.update({
                    field: -1,
                    'drive': drive,
                })
                if es_data:
                    for hit in es_data:
                        # field 默认为-1， 如获取到则覆盖变量，sort保证最后一个为最新值
                        diskage_list = hit.source.diskage
                        for diskage in diskage_list:
                            if diskage.dev == drive:
                                data[field] = diskage.age / 100

            response = global_func.get_response(data=data)
            return Response(response)


class NetTraffic(APIView):
    def get(self, request, *args, **kwargs):
        metricset_name = 'network'
        machine_moid = kwargs.get('machine_moid')
        start_time, end_time, interval = es_client.get_time_info(request)
        field_name = 'system.%s.name' % metricset_name

        data = {
            'machine_moid': machine_moid,
        }

        if not request.query_params.get('card'):

            _query_card = [
                ['match', {'metricset.name': metricset_name}],
                ['match_phrase', {'beat.eqpid': machine_moid}]
            ]

            _filter_card = [
                ['range', {'@timestamp': {"gte": start_time}}]
            ]

            metric_card = [['card', 'terms', {'field': field_name, 'size': 1000}]]

            _aggs_card = [
                {
                    'bucket': [],
                    'metric': metric_card,
                    'pipeline': []
                }
            ]

            es_data_card = es_client.get_es_data(request, es_client, _query=_query_card,
                                                 _filter=_filter_card, _aggs=_aggs_card)

            # 获取到本机的所有网卡名称
            cards = []
            if hasattr(es_data_card, 'aggregations') and es_data_card.aggregations:
                for tag in es_data_card.aggregations:
                    for bucket in tag.buckets:
                        cards.append(bucket.key)

            data = copy.deepcopy(data)
            data.update(
                {
                    'cards': cards
                }
            )
            response = global_func.get_response(data=data)
            return Response(response)

        else:
            card = request.query_params.get('card')
            _query = [
                ['match', {'metricset.name': metricset_name}],
                ['match_phrase', {'beat.eqpid': machine_moid}],
                ['match', {'system.network.name': card}]
            ]

            _filter = [
                ['range', {'@timestamp': {"gte": start_time, "lte": end_time}}]
            ]

            data = copy.deepcopy(data)
            data.update(
                {
                    'start_time': start_time,
                    'end_time': end_time,
                    'interval': interval,
                    'card': card,
                }
            )
            for field in es_client.fields_dic.get(metricset_name):
                data.update(
                    {
                        field: []
                    }
                )
                metric = [['in_bytes', 'max', {"field": field}]]

                _aggs = [
                    {
                        'bucket': ['by_time', 'date_histogram', {
                            "field": "@timestamp", "interval": interval,
                            "time_zone": "+08:00", "format": "yyyy-MM-dd HH:mm:ss", "min_doc_count": 0
                        }],
                        'metric': metric,
                        'pipeline': [['bytes_deriv', 'derivative', {"buckets_path": "in_bytes",
                                                                    "unit": interval}]]
                    }
                ]
                es_data = es_client.get_es_data(request, es_client, _query, _filter, _aggs, _size=0)
                if hasattr(es_data, 'aggregations') and es_data.aggregations:
                    for tag in es_data.aggregations:
                        for bucket in tag.buckets:
                            if hasattr(bucket, 'bytes_deriv'):
                                data[field].append([bucket.key, bucket.bytes_deriv.normalized_value])

            response = global_func.get_response(data=data)
            return Response(response)


class Uptime(APIView):
    def get(self, request, *args, **kwargs):
        metricset_name = 'uptime'
        machine_moid = kwargs.get('machine_moid')
        # 10分钟内
        start_time = (time.time() - 10 * 60) * 1000

        _query = [
            ['match', {'metricset.name': metricset_name}],
            ['match_phrase', {'beat.eqpid': machine_moid}]
        ]

        _filter = [
            ['range', {'@timestamp': {"gte": start_time}}]
        ]
        metric = []

        _aggs = [
            {
                'bucket': [],
                'metric': metric,
                'pipeline': []
            }
        ]

        _sort = '-@timestamp'

        _source = ['@timestamp', 'system']

        es_data = es_client.get_es_data(request, es_client, _query=_query,
                                        _filter=_filter, _aggs=_aggs, _sort=_sort, _source=_source, _size=1)

        data = {
            'machine_moid': machine_moid
        }

        for field in es_client.fields_dic.get(metricset_name):
            data.update({
                field: -1
            })
            if es_data:
                for hit in es_data:
                    # field 默认为-1， 如获取到则覆盖变量，sort保证第一个为最新值
                    data[field] = hit.system.uptime.duration.ms

        response = global_func.get_response(data=data)
        return Response(response)


class TopNMemory(APIView):
    def get(self, request, *args, **kwargs):
        machine_moid = kwargs.get('machine_moid')
        start_time, end_time, interval = es_client.get_time_info(request)
        n = kwargs.get('n')
        data = {
            'machine_moid': machine_moid,
            'topN': []
        }
        base_dsl = copy.deepcopy(top_mem_processes_dsl)
        index = base_dsl.get('index', '')
        dsl = base_dsl.get('dsl', {})
        dsl['query']['bool']['must'].append(
            {'match_phrase': {'beat.eqpid': machine_moid}}
        )
        dsl['query']['bool']['filter'].append(
            {"range": {"@timestamp": {"gte": start_time, "lte": end_time}}}
        )
        dsl['aggs']['pid']['terms']['size'] = n
        logger.info(dsl)

        try:
            es_response = es_client.search(index=index, body=dsl)
        except Exception as e:
            logger.error(str(e))
            response = global_func.get_response(0, error_code=10002)
            return Response(response)
        buckets = jsonpath.jsonpath(es_response, '$..aggregations.pid.buckets')
        if buckets:
            buckets = buckets[0]
            for bucket in buckets:
                avg_memory_pct_value = bucket.get('avg_mem_pct', {}).get('value', 0)
                process_name = jsonpath.jsonpath(bucket, '$..system.process.name')[0]
                data.get('topN').append([process_name, avg_memory_pct_value])

        response = global_func.get_response(data=data)

        return Response(response)


class TopNCpu(APIView):
    def get(self, request, *args, **kwargs):
        machine_moid = kwargs.get('machine_moid')
        n = kwargs.get('n')
        start_time, end_time, interval = es_client.get_time_info(request)
        data = {
            'machine_moid': machine_moid,
            'topN': []
        }
        base_dsl = copy.deepcopy(top_cpu_processes_dsl)
        index = base_dsl.get('index', '')
        dsl = base_dsl.get('dsl', {})
        dsl['query']['bool']['must'].append(
            {'match_phrase': {'beat.eqpid': machine_moid}}
        )
        dsl['query']['bool']['filter'].append(
            {"range": {"@timestamp": {"gte": start_time, "lte": end_time}}}
        )
        dsl['aggs']['pid']['terms']['size'] = n
        logger.info(dsl)

        try:
            es_response = es_client.search(index=index, body=dsl)
        except Exception as e:
            logger.error(str(e))
            response = global_func.get_response(0, error_code=10002)
            return Response(response)
        buckets = jsonpath.jsonpath(es_response, '$..aggregations.pid.buckets')
        if buckets:
            buckets = buckets[0]
            for bucket in buckets:
                avg_cpu_pct_value = bucket.get('avg_cpu_pct', {}).get('value', 0)
                process_name = jsonpath.jsonpath(bucket, '$..system.process.name')[0]
                data.get('topN').append([process_name, avg_cpu_pct_value])

        response = global_func.get_response(data=data)

        return Response(response)


class TopExport(APIView):
    def get(self, request, *args, **kwargs):
        host_info = HostDetail().get(request, *args, **kwargs)
        host_name = host_info.data.get('data', {}).get('name', '')
        host_local_ip = host_info.data.get('data', {}).get('local_ip', '')
        top_cpu_processes = TopNCpu().get(request, *args, **kwargs)
        top_cpu_processes_data = top_cpu_processes.data.get('data', {}).get('topN', [])
        top_mem_processes = TopNMemory().get(request, *args, **kwargs)
        top_mem_processes_data = top_mem_processes.data.get('data', {}).get('topN', [])
        n = kwargs.get('n', 10)
        n = min([int(n), len(top_mem_processes_data), len(top_cpu_processes_data)])

        start_time = request.query_params.get('start_time',
                                              str(es_client.get_start_time(time.time() * 1000 - 86400000)))
        end_time = request.query_params.get('end_time', str(es_client.get_end_time(time.time() * 1000)))

        start_time_as_string = global_func.format_timestamp(int(start_time) / 1000)
        end_time_as_string = global_func.format_timestamp(int(end_time) / 1000)
        media_path = os.path.join(MEDIA_ROOT, 'top_cpu_mem_processes')
        file_name = '%s_%s_top_cpu_mem_processes.csv' % (start_time_as_string, end_time_as_string)
        file_path = os.path.join(media_path, file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if top_mem_processes_data or top_cpu_processes_data:
            data = [['服务器名称', '服务器本地ip', '应用名称', 'CPU占用率', '应用名称', 'MEM占用率']]
            data.extend(
                [[host_name, host_local_ip, top_cpu_processes_data[index][0],
                  '{}%'.format(top_cpu_processes_data[index][1] * 100),
                  top_mem_processes_data[index][0],
                  '{}%'.format(top_mem_processes_data[index][1] * 100)] for index in range(int(n))]
            )
            try:
                with open(file_path, 'w', newline='', encoding='gbk') as f:
                    csv_writer = csv.writer(f)
                    csv_writer.writerows(data)
            except Exception as e:
                err = str(e)
                logger.error(err)
                response = global_func.get_response(0, error_msg=err)
                return Response(response)
            logger.info("写入数据成功")
            # 读取csv数据
            conf_file = open(file_path, 'rb')
            logger.info(conf_file)
            response = FileResponse(conf_file)
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment;filename=%s' % file_name
            # 发送至前端
            return response
        else:
            response = global_func.get_response(0, error_msg='文件不存在')
            return Response(response)


class Logger(APIView):
    def post(self, request, *args, **kwargs):
        logger.debug(request.data)
        response = global_func.get_response()
        return Response(response)

    def get(self, request, *args, **kwargs):
        logger.debug(request.data)
        response = global_func.get_response()
        return Response(response)


class ShowIndex(APIView):
    def get(self, request, *args, **kwargs):
        return redirect('/ops/static/index.html')


class Check(APIView):
    def get(self, request, *args, **kwargs):
        response = global_func.get_response()
        return Response(response)


class IsLogin(APIView):
    def get(self, request, *args, **kwargs):
        sso_auth = request.META.get('ssoAuth', {})
        sso_auth.update({'url': '/portalCore/'})
        response = global_func.get_response(data=sso_auth)
        return Response(response)


class Logout(APIView):
    def post(self, request, *args, **kwargs):
        portalcore_login_uri = '/portalCore/login'
        logout_uri = 'apiCore/sso/userLogout'
        sso_ip = global_func.get_conf('auth', 'ip')
        sso_port = global_func.get_conf('auth', 'port')
        url = 'http://%s:%s/%s' % (sso_ip, sso_port, logout_uri)
        username = request.META.get('ssoAuth', {}).get('name', 'administrator')
        # username = 'bsjg'
        ssoToken = request.COOKIES.get('SSO_COOKIE_KEY')
        # ssoToken = '8ef47027-7af2-4908-b7a6-6c3f4095c70a'
        if ssoToken:
            try:
                account_token = global_func.get_token(sso_ip, sso_port)
                ret = requests.post(url=url, params={'userName': username,
                                                     'ssoToken': ssoToken,
                                                     'account_token': account_token
                                                     })
                if ret.status_code == 200:
                    response = global_func.get_response(data={'url': portalcore_login_uri})
                    return Response(response)
                else:
                    response = global_func.get_response(0, error_msg=ret.text)
                    return Response(response)

            except Exception as e:
                err = str(e)
                logger.error(err)
                response = global_func.get_response(0, error_msg='%s 请求失败' % url)
                return Response(response)
        else:
            response = global_func.get_response(0, error_msg='cookie: SSO_COOKIE_KEY 不存在')
            return Response(response)
