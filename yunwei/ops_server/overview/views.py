from django.shortcuts import render

# Create your views here.

import logging
import copy
import time
import json
import jsonpath
import os

from django.db import connections
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, ListCreateAPIView, CreateAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from common.my_elastic import es_client
from common.pagination import ResultsSetPaginationOffset, ResultsDataSetPaginationOffset
from common import global_func
from common.my_exception import OpsException
from .dsl import es_ql
from .models import *
from common.keda_baseclass import KedaBaseAPIView, MultiDeleteAPIView, KedaWarningBaseAPIView
from .ops_serializer.ops_serializer import *
from ops.settings import BASE_DIR
from ops_statistics import query_func

logger = logging.getLogger('ops.' + __name__)


class Confs(APIView):
    def get(self, request, *args, **kwargs):
        platform_moid = request.query_params.get('platform_moid', '')
        start_time = request.query_params.get('start_time',
                                              str(es_client.get_start_time(time.time() * 1000 - 86400000)))
        end_time = request.query_params.get('end_time', str(es_client.get_end_time(time.time() * 1000)))

        # 已结束会议
        release_traditional_conf_count = 0
        release_port_conf_count = 0
        release_p2p_conf_count = 0
        try:
            release_traditional_conf_count = query_func.get_all_release_conf_count(request, end_time)
            # release_conf_list = query_func.get_now_release_conf_info(request, end_time)
            # release_conf_type = query_func.get_conf_type(release_conf_list)
            # logger.debug(release_conf_list)
            # 多点
            # 传统会议个数
            # release_traditional_conf_count = len(release_conf_type.get('0'))
            # release_traditional_conf_count = len(release_conf_list)
            # 端口会议个数
            # release_port_conf_count = len(release_conf_type.get('1'))
            release_port_conf_count = 0
            # 点对点
            ############
            release_p2p_conf_count = 0
        except Exception as e:
            err = str(e)
            logger.error(err)

        complete_conf_info = {
            "data": {
                "traditional_conf": release_traditional_conf_count,
                "port_conf": release_port_conf_count,
                "p2p_conf": release_p2p_conf_count
            },
            "name": "complete_conf",
            "description": "已结束会议数"
        }

        # 正在召开会议
        # 多点
        on_going_traditional_conf_count = 0
        on_going_port_conf_count = 0
        on_going_p2p_conf_count = 0
        # 供活跃会议使用
        active_conf_list = []
        try:
            on_going_conf_list = query_func.get_now_on_going_conf_info(request, end_time)
            # 供活跃会议使用
            active_conf_list = on_going_conf_list
            on_going_conf_list = [on_going_conf.get('confE164') if
                                  on_going_conf.get('confE164') else '' for on_going_conf in on_going_conf_list]
            on_going_conf_type = query_func.get_conf_type(on_going_conf_list)
            # 传统会议个数
            on_going_traditional_conf_count = len(on_going_conf_type.get('0'))
            # 端口会议个数
            on_going_port_conf_count = len(on_going_conf_type.get('1'))
            # 点对点
            ############
            on_going_p2p_conf_count = 0
        except Exception as e:
            err = str(e)
            logger.error(err)

        on_going_conf_info = {
            "data": {
                "traditional_conf": on_going_traditional_conf_count,
                "port_conf": on_going_port_conf_count,
                "p2p_conf": on_going_p2p_conf_count
            },
            "name": "on_going_conf",
            "description": "正在召开的会议数"
        }

        # 活跃会议
        active_traditional_conf_count = 0
        active_port_conf_count = 0
        active_p2p_conf_count = 0
        try:
            active_conf_list = [active_conf.get('confE164') for active_conf in active_conf_list if
                                active_conf.get('confE164') and active_conf.get('mtnum')
                                and int(active_conf.get('mtnum')) > 0]
            active_conf_type = query_func.get_conf_type(active_conf_list)
            # 传统会议个数
            active_traditional_conf_count = len(active_conf_type.get('0'))
            # 端口会议个数
            active_port_conf_count = len(active_conf_type.get('1'))
            # 点对点
            ############
            active_p2p_conf_count = 0
        except Exception as e:
            err = str(e)
            logger.error(err)

        active_conf_info = {
            "data": {
                "traditional_conf": active_traditional_conf_count,
                "port_conf": active_port_conf_count,
                "p2p_conf": active_p2p_conf_count
            },
            "name": "active_conf",
            "description": "活跃会议数"
        }
        data = {
            "start_time": start_time,
            "end_time": end_time,
            "platform_moid": platform_moid,
            'info': [
                complete_conf_info,
                active_conf_info,
                on_going_conf_info,
            ]
        }

        response = global_func.get_response(data=data)

        return Response(response)


class RecreateGisMap(APIView):
    def post(self, request, *args, **kwargs):
        base_map_json_path = os.path.join(BASE_DIR, 'overview', 'BoroughInfo.json')
        with open(base_map_json_path, 'r', encoding='utf8')as f:
            content = f.read()

        ret = json.loads(content)
        sqls = (
            'TRUNCATE TABLE %s' % (CityModel._meta.db_table),
            'TRUNCATE TABLE %s' % (ProvinceModel._meta.db_table),
        )
        connections['default'].close()
        with connections['default'].cursor() as cursor:
            for sql in sqls:
                cursor.execute(sql)
            for province in ret:
                ProvinceModel.objects.create(name=province)
                for city in ret[province]:
                    CityModel.objects.create(name=city, province=ProvinceModel.objects.filter(name=province).first())

        response = global_func.get_response()
        return Response(response)


class Province(KedaBaseAPIView, ListAPIView):
    queryset = ProvinceModel.objects.all()
    serializer_class = ProvinceSerializers


class City(KedaBaseAPIView, ListAPIView):
    queryset = CityModel.objects.all()
    serializer_class = CitySerializers
    # 关键字查询
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('province',)


class GisConf(KedaBaseAPIView, ListCreateAPIView, MultiDeleteAPIView):
    queryset = GisConfModel.objects.all()
    lookup_request_data = 'ids'

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method == 'GET':
            return GisConfGetSerializers
        elif self.request.method == 'POST':
            return GisConfPostSerializers
        else:
            return GisConfSerializers


class GisConfDetail(KedaBaseAPIView, RetrieveUpdateAPIView):
    queryset = GisConfModel.objects.all()

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method == 'GET':
            return GisConfGetSerializers
        else:
            return GisConfSerializers


class MachineRoomDetail(KedaBaseAPIView, RetrieveUpdateAPIView):
    queryset = GisMachineRoomModel.objects.all()
    serializer_class = GisMachineRoomSerializer


class TerminalDetail(KedaBaseAPIView, RetrieveUpdateAPIView):
    queryset = GisTerminalModel.objects.all()
    serializer_class = GisTerminalModelSerializer


class Terminal(KedaWarningBaseAPIView, ListCreateAPIView, MultiDeleteAPIView):
    queryset = GisTerminalModel.objects.all()
    serializer_class = GisTerminalModelSerializer
    lookup_request_data = 'ids'
    pagination_class = ResultsDataSetPaginationOffset


class PeripheralDetail(KedaBaseAPIView, RetrieveUpdateAPIView):
    queryset = GisPeripheralModel.objects.all()
    serializer_class = GisPeripheralSerializer


class Peripheral(KedaWarningBaseAPIView, ListCreateAPIView, MultiDeleteAPIView):
    queryset = GisPeripheralModel.objects.all()
    serializer_class = GisPeripheralSerializer
    lookup_request_data = 'ids'
    pagination_class = ResultsDataSetPaginationOffset


class LubanDomain(APIView):
    def get(self, request, *args, **kwargs):
        data = {}
        info_tmp_dic = {
            "domain_name": "",
            "domain_moid": "",
            "domain_type": "",
            "total": 0,
            "info": []  # 平台域下机房的数量
        }
        info = []
        try:
            connections['luban'].close()
            with connections['luban'].cursor() as cursor:
                sql = '''
                select * from domain_info
                where domain_status !=2
                '''
                cursor.execute(sql, )
                restlts = cursor.fetchall()
                counts_sql = '''
                SELECT domain_moid,COUNT(domain_moid) count FROM machine_room_info GROUP BY domain_moid
                '''
                cursor.execute(counts_sql)
                counts = cursor.fetchall()
                counts_dic = {count[0]: count[1] for count in counts}
                for restlt in restlts:
                    info_dic = copy.deepcopy(info_tmp_dic)
                    info_dic['domain_name'] = restlt[1]
                    # 域类型：0核心域，1平台域
                    info_dic['domain_type'] = restlt[2]
                    info_dic['domain_moid'] = restlt[3]
                    info_dic['total'] = counts_dic.get(restlt[3]) if counts_dic.get(restlt[3]) else 0
                    info.append(info_dic)
        except Exception as e:
            err = str(e)
            logger.error(err)
        data['info'] = info
        return Response(data=data)


class LubanDomainMachineRoom(APIView):
    def get(self, request, *args, **kwargs):
        domain_moid = kwargs.get('domain_moid')
        params = [domain_moid]
        sql = 'select * from machine_room_info'
        sql += ' where domain_moid=%s'
        connections['luban'].close()
        with connections['luban'].cursor() as cursor:
            cursor.execute(sql, params=params)
            machine_rooms = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            data = {
                "machine_room_moid": domain_moid if domain_moid else '',
                "info": [dict(zip(columns, row)) for row in machine_rooms],
            }
            response = global_func.get_response(data=data)
        return Response(response)


class SearchLubanDomainMachineRoom(APIView):
    def get(self, request, *args, **kwargs):
        key = request.query_params.get('key')
        if not key:
            response = global_func.get_response(0, error_msg='please send key word:\'key\'')
            return Response(response)
        data = {}

        info_tmp_dic = {
            "domain_name": "",
            "domain_moid": "",
            "info": []
        }

        connections['luban'].close()
        with connections['luban'].cursor() as cursor:
            sql = '''
            select mri.machine_room_moid from machine_room_info mri 
            '''
            query_key = '\'%' + key + '%\''
            sql += 'where mri.machine_room_name like ' + query_key
            cursor.execute(sql, )
            machine_room_moids = cursor.fetchall()
            if len(machine_room_moids):
                machine_room_moids_str = ','.join(('\'%s\'' % moid[0] for moid in machine_room_moids))
                sql = '''
                select di.domain_name,di.domain_moid,mri.* from machine_room_info mri LEFT JOIN domain_info di 
                on mri.domain_moid=di.domain_moid where mri.machine_room_moid in (%s)
                ''' % machine_room_moids_str

                cursor.execute(sql, )
                results = cursor.fetchall()
            else:
                results = []
            columns = [col[0] for col in cursor.description]
            info = []
            domain_moid = []
            for result in results:
                info_dic = copy.deepcopy(info_tmp_dic)
                if result[1] not in domain_moid:
                    domain_moid.append(result[1])
                    info_dic['domain_name'] = result[0]
                    info_dic['domain_moid'] = result[1]
                    info_dic['info'] = [dict(zip(columns[2:], result[2:]))]
                    info.append(info_dic)
                else:
                    info[domain_moid.index(result[1])]['info'].append(dict(zip(columns[2:], result[2:])))
        data['info'] = info
        response = global_func.get_response(data=data)
        return Response(response)


class MachineRoom(KedaWarningBaseAPIView, ListCreateAPIView, MultiDeleteAPIView):
    queryset = GisMachineRoomModel.objects.all()
    serializer_class = GisMachineRoomSerializer
    lookup_request_data = 'ids'
    pagination_class = ResultsDataSetPaginationOffset


class OverMachinelRoom(APIView):
    def get(self, request, *args, **kwargs):
        data = {
            'domain_moid': '',
        }
        info_tmp_dic = {
            "machine_room_name": "",
            "machine_room_moid": "",
            "total": 0,
            "info": []
        }
        info = []
        machine_room_sql = '''
        select machine_room_name,machine_room_moid from machine_room_info
        '''
        machine_room_count_sql = '''
        SELECT machine_room_moid,COUNT(machine_room_moid) count FROM machine_info GROUP BY machine_room_moid
        '''
        try:
            connections['luban'].close()
            with connections['luban'].cursor() as cursor:
                cursor.execute(machine_room_sql, )
                machine_rooms = cursor.fetchall()
                cursor.execute(machine_room_count_sql, )
                machine_room_counts = cursor.fetchall()
                machine_room_counts_dic = {
                    machine_room_count[0]: machine_room_count[1] for machine_room_count in machine_room_counts
                }
                for machine_room in machine_rooms:
                    info_dic = copy.deepcopy(info_tmp_dic)
                    info_dic['machine_room_name'] = machine_room[0]
                    info_dic['machine_room_moid'] = machine_room[1]
                    info_dic['total'] = machine_room_counts_dic.get(machine_room[1]) \
                        if machine_room_counts_dic.get(machine_room[1]) else 0
                    info.append(info_dic)
                data['info'] = info
                response = global_func.get_response(data=data)
        except Exception as e:
            err = str(e)
            logger.error(err)
            response = global_func.get_response(0, error_msg=err)

        return Response(response)


class LubanMachine(APIView):
    def get(self, request, *args, **kwargs):
        machine_room_moid = kwargs.get('machine_room_moid')
        start = int(request.query_params.get('start', '0'))
        count = int(request.query_params.get('count', '10'))
        # luban machine_info表中的 device_type ，为0则表示可以使用ansible控制的x86机器
        device_type = request.query_params.get('device_type', '')
        if device_type not in ['', '0', '1']:
            raise OpsException(code='10010')
        params = [machine_room_moid]
        connections['luban'].close()
        with connections['luban'].cursor() as cursor:
            sql = '''
            select sql_calc_found_rows
            mi.machine_name,mi.work_mode,mi.device_type,mi.default_getway,mi.machine_moid,mi.network_card_backup,
            mi.config_time,mi.machine_type,mi.BrdType,mi.id,mi.belong_slot,mi.client_version,mi.update_flag,
            mi.first_radar_flag,mi.cluster_id,mi.env_id,mi.belong_moid,mi.reboot_flag,mi.belong_frame_id,
            mi.copy_luban_service_flag,mi.mac_id,mi.machine_room_name,mi.BrdWorkMode,mi.machine_status,
            mi.machine_room_moid from machine_info mi 
            '''
            sql += ' where machine_room_moid=%s'

            if device_type:
                sql += ' and mi.device_type=%s'
                params.append(device_type)
            if start:
                sql += ' limit %s,%s' % (start, count)
            else:
                sql += ' limit %s' % count
            cursor.execute(sql, params=params)
            columns = [col[0] for col in cursor.description]
            fetchall = cursor.fetchall()
            # 查询总数
            total_sql = 'SELECT FOUND_ROWS()'
            cursor.execute(total_sql)
            total = cursor.fetchone()[0]
            data = {
                "machine_room_moid": machine_room_moid if machine_room_moid else '',
                "info": [dict(zip(columns, row)) for row in fetchall],
                'total': total,
                'start': start,
                'count': count,
            }
            response = global_func.get_response(data=data)
        return Response(response)


class SearchLubanMachine(APIView):
    def get(self, request, *args, **kwargs):
        key = request.query_params.get('key')
        if not key:
            raise OpsException(code='10010')
        # luban machine_info表中的 device_type ，为0则表示可以使用ansible控制的x86机器
        device_type = request.query_params.get('device_type', '')
        if device_type not in ['', '0', '1']:
            raise OpsException(code='10010')
        data = {}
        info_tmp_dic = {
            "machine_room_name": "",
            "machine_room_moid": "",
            "info": []
        }
        machine_moids_sql = '''
        select mi.machine_moid from machine_info mi 
        '''
        query_key = '\'%' + key + '%\''
        machine_moids_sql += ' where machine_type like ' + query_key
        machine_moids_sql += ' or machine_name like ' + query_key
        connections['luban'].close()
        with connections['luban'].cursor() as cursor:
            cursor.execute(machine_moids_sql, )
            machine_moids = cursor.fetchall()
            if len(machine_moids):
                sql = '''
                select mri.machine_room_name,mri.machine_room_moid,mi.machine_name,mi.work_mode,mi.device_type,
                mi.default_getway,mi.machine_moid,mi.network_card_backup,
                mi.config_time,mi.machine_type,mi.BrdType,mi.id,mi.belong_slot,mi.client_version,mi.update_flag,
                mi.first_radar_flag,mi.cluster_id,mi.env_id,mi.belong_moid,mi.reboot_flag,mi.belong_frame_id,
                mi.copy_luban_service_flag,mi.mac_id,mi.machine_room_name,mi.BrdWorkMode,mi.machine_status,
                mi.machine_room_moid from machine_room_info mri LEFT JOIN machine_info mi 
                on mri.machine_room_moid=mi.machine_room_moid where mi.machine_moid in %s
                '''
                params = [[machine_moid[0] for machine_moid in machine_moids]]
                if device_type:
                    sql += ' and mi.device_type=%s'
                    params.append(device_type)
                cursor.execute(sql, params)
                results = cursor.fetchall()
            else:
                results = []
            columns = [col[0] for col in cursor.description]
            info = []
            domain_moid = []
            for result in results:
                info_dic = copy.deepcopy(info_tmp_dic)
                if result[1] not in domain_moid:
                    domain_moid.append(result[1])
                    info_dic['machine_room_name'] = result[0]
                    info_dic['machine_room_moid'] = result[1]
                    info_dic['info'] = [dict(zip(columns[2:], result[2:]))]
                    info.append(info_dic)
                else:
                    info[domain_moid.index(result[1])]['info'].append(dict(zip(columns[2:], result[2:])))
        data['info'] = info
        response = global_func.get_response(data=data)
        return Response(response)


class OverPeripheralRoom(APIView):
    def get(self, request, *args, **kwargs):
        data = {
            'domain_moid': '',
        }
        info_tmp_dic = {
            "machine_room_name": "",
            "machine_room_moid": "",
            "total": 0,
            "info": []
        }
        info = []
        machine_room_sql = '''
        select machine_room_name,machine_room_moid from machine_room_info
        '''
        machine_room_count_sql = '''
        SELECT machine_room_moid,COUNT(machine_room_moid) count FROM peripheral_info GROUP BY machine_room_moid
        '''
        try:
            connections['luban'].close()
            with connections['luban'].cursor() as cursor:
                cursor.execute(machine_room_sql, )
                machine_rooms = cursor.fetchall()
                cursor.execute(machine_room_count_sql, )
                machine_room_counts = cursor.fetchall()
                machine_room_counts_dic = {
                    machine_room_count[0]: machine_room_count[1] for machine_room_count in machine_room_counts
                }
                for machine_room in machine_rooms:
                    info_dic = copy.deepcopy(info_tmp_dic)
                    info_dic['machine_room_name'] = machine_room[0]
                    info_dic['machine_room_moid'] = machine_room[1]
                    info_dic['total'] = machine_room_counts_dic.get(machine_room[1]) \
                        if machine_room_counts_dic.get(machine_room[1]) else 0
                    info.append(info_dic)
                data['info'] = info
                response = global_func.get_response(data=data)
        except Exception as e:
            err = str(e)
            logger.error(err)
            response = global_func.get_response(0, error_msg=err)
        return Response(response)


class LubanPeripheral(APIView):
    def get(self, request, *args, **kwargs):
        machine_room_moid = kwargs.get('machine_room_moid')
        params = [machine_room_moid]
        connections['luban'].close()
        with connections['luban'].cursor() as cursor:
            sql = 'select * from peripheral_info'
            sql += ' where machine_room_moid=%s'

            cursor.execute(sql, params=params)
            columns = [col[0] for col in cursor.description]
            fetchall = cursor.fetchall()

            data = {
                "machine_room_moid": machine_room_moid if machine_room_moid else '',
                "info": [dict(zip(columns, row)) for row in fetchall],
            }
            response = global_func.get_response(data=data)
        return Response(response)


class SearchLubanPeripheral(APIView):
    def get(self, request, *args, **kwargs):
        key = request.query_params.get('key')
        if not key:
            response = global_func.get_response(0, error_msg='please send key word:\'key\'')
            return Response(response)
        data = {}
        info_tmp_dic = {
            "machine_room_name": "",
            "machine_room_moid": "",
            "info": []
        }
        per_moids_sql = '''
        select pi.per_moid from peripheral_info pi 
        '''
        query_key = '\'%' + key + '%\''
        per_moids_sql += ' where per_type like ' + query_key
        per_moids_sql += ' or per_sub_type like ' + query_key
        connections['luban'].close()
        with connections['luban'].cursor() as cursor:
            cursor.execute(per_moids_sql, )
            per_moids = cursor.fetchall()
            if len(per_moids):
                per_moids_str = ','.join(('\'%s\'' % moid[0] for moid in per_moids))
                sql = '''
                select mri.machine_room_name,mri.machine_room_moid,pi.* from machine_room_info mri LEFT JOIN peripheral_info pi 
                on mri.machine_room_moid=pi.machine_room_moid where pi.per_moid in (%s)
                ''' % per_moids_str

                cursor.execute(sql, )
                results = cursor.fetchall()
            else:
                results = []
            columns = [col[0] for col in cursor.description]
            info = []
            domain_moid = []
            for result in results:
                info_dic = copy.deepcopy(info_tmp_dic)
                if result[1] not in domain_moid:
                    domain_moid.append(result[1])
                    info_dic['machine_room_name'] = result[0]
                    info_dic['machine_room_moid'] = result[1]
                    info_dic['info'] = [dict(zip(columns[2:], result[2:]))]
                    info.append(info_dic)
                else:
                    info[domain_moid.index(result[1])]['info'].append(dict(zip(columns[2:], result[2:])))
        data['info'] = info
        response = global_func.get_response(data=data)
        return Response(response)


class UserDomain(APIView):
    def get(self, request, *args, **kwargs):
        data = {
            'platform_moid': '',
        }
        info_tmp_dic = {
            "user_domain_name": "",
            "user_domain_moid": "",
            "total": 0,
            "info": []
        }
        info = []
        user_domain_sql_params = []
        user_domain_sql = '''
        SELECT ud.user_domain_moid, ud.user_domain_name, ud.platform_domain_moid,pd.platform_domain_name 
        FROM user_domain ud LEFT JOIN platform_domain pd on ud.platform_domain_moid=pd.platform_domain_moid WHERE 1=1
        '''
        platform_moid = request.query_params.get('platform_moid')
        user_domain_key = request.query_params.get('key')
        if platform_moid:
            data['platform_moid'] = platform_moid
            user_domain_sql += ' AND ud.platform_domain_moid=%s'
            user_domain_sql_params.append(platform_moid)

        if user_domain_key:
            data['key'] = user_domain_key
            user_domain_sql += ' AND ud.user_domain_name like \"%%{}%%\"'.format(user_domain_key)

        moid_counts_sql = '''
        SELECT user_domain_moid,COUNT(user_domain_moid) count FROM user_info GROUP BY user_domain_moid
        '''
        try:
            connections['movision'].close()
            with connections['movision'].cursor() as cursor:
                cursor.execute(user_domain_sql, params=user_domain_sql_params)
                user_domains = cursor.fetchall()
                cursor.execute(moid_counts_sql)
                moid_counts = cursor.fetchall()

                moid_counts_dic = {moid_count[0]: moid_count[1] for moid_count in moid_counts}
                for user_domain in user_domains:
                    info_dic = copy.deepcopy(info_tmp_dic)
                    info_dic['user_domain_name'] = user_domain[1]
                    info_dic['user_domain_moid'] = user_domain[0]
                    info_dic['platform_moid'] = user_domain[2]
                    info_dic['platform_name'] = user_domain[3]
                    info_dic['total'] = moid_counts_dic.get(user_domain[0]) if moid_counts_dic.get(user_domain[0]) \
                        else 0
                    info.append(info_dic)
            data['info'] = info

            response = global_func.get_response(data=data)
        except Exception as e:
            err = str(e)
            logger.error(err)
            response = global_func.get_response(0, error_msg=err)
        return Response(response)


class UserInfo(APIView):
    def get(self, request, *args, **kwargs):
        start = int(request.query_params.get('start', '0'))
        count = int(request.query_params.get('count', '10'))
        data = {
            'user_domain_moid': '',
            'user_domain_name': '',
            'total': 0,
            'start': start,
            'count': count,
            'info': []
        }

        user_domain_moid = kwargs.get('user_domain_moid')
        if user_domain_moid:
            try:
                connections['movision'].close()
                with connections['movision'].cursor() as cursor:
                    data['user_domain_moid'] = user_domain_moid
                    sql = '''
                    SELECT sql_calc_found_rows user_domain.user_domain_name,user_profile.name,user_info.* 
                    FROM user_info 
                    LEFT JOIN user_domain on user_info.user_domain_moid=user_domain.user_domain_moid
                    LEFT JOIN user_profile on user_info.moid=user_profile.moid
                    WHERE isdeleted = '0' and account_type != '9' and 
                    (device_type is null or device_type not in ('519','524','530','531')) and
                    binded='0' and account is not NULL and user_info.user_domain_moid=%s ORDER BY user_info.account
                    '''
                    if start:
                        sql += ' limit %s,%s' % (start, count)
                    else:
                        sql += ' limit %s' % count

                    cursor.execute(sql, [user_domain_moid])
                    columns = [col[0] for col in cursor.description]
                    result = cursor.fetchall()
                    if result:
                        data['user_domain_name'] = result[0][0]
                        data['info'] = [dict(zip(columns[1:], row[1:])) for row in result]

                        total_sql = 'SELECT FOUND_ROWS()'
                        cursor.execute(total_sql)
                        data['total'] = cursor.fetchone()[0]
            except Exception as e:
                logger.error(str(e))
                response = global_func.get_response(0, error_msg='mysql cannot connect')
                return Response(response)
        response = global_func.get_response(data=data)
        return Response(response)


class SearchUserInfo(APIView):
    '''
    通过关键字查询用户信息
    '''

    def get(self, request, *args, **kwargs):
        key = request.query_params.get('key')
        if not key:
            response = global_func.get_response(0, error_msg='please send key word:\'key\'')
            return Response(response)
        data = {}

        info_tmp_dic = {
            "user_domain_name": "",
            "user_domain_moid": "",
            "info": []
        }
        sql = '''
        select u.moid from user_info u left join user_profile up on up.moid=u.moid 
        where isdeleted = '0' and account_type != '9' and 
        (device_type is null or device_type not in ('519','524','530','531')) and
         binded='0' and account is not NULL 
        '''
        query_key = '\'%' + key + '%\''
        sql += ' and (up.name like ' + query_key
        sql += ' or up.full_py like ' + query_key
        sql += ' or u.account like ' + query_key
        sql += ' or u.email like ' + query_key
        sql += ' or u.e164 like ' + query_key
        sql += ' )'
        connections['movision'].close()
        with connections['movision'].cursor() as cursor:
            # 查询符合条件的用户moid
            cursor.execute(sql, )
            moids = cursor.fetchall()
            if len(moids):
                moids_str = ','.join(('\'%s\'' % moid[0] for moid in moids))
                sql = '''
                SELECT user_domain.user_domain_name,user_domain.user_domain_moid,user_profile.name,user_info.* 
                FROM user_info 
                LEFT JOIN user_domain on user_info.user_domain_moid=user_domain.user_domain_moid
                LEFT JOIN user_profile on user_info.moid=user_profile.moid
                WHERE user_info.moid in (%s) ORDER BY user_info.account
                ''' % moids_str
                # 查询用户moid为上条语句结果的用户信息，并分用户域整理数据
                cursor.execute(sql, )
                results = cursor.fetchall()
            else:
                results = []
            columns = [col[0] for col in cursor.description]

            info = []
            user_domain_moid = []
            for result in results:
                info_dic = copy.deepcopy(info_tmp_dic)
                if result[1] not in user_domain_moid:
                    user_domain_moid.append(result[1])
                    info_dic['user_domain_name'] = result[0]
                    info_dic['user_domain_moid'] = result[1]
                    info_dic['info'] = [dict(zip(columns[2:], result[2:]))]
                    info.append(info_dic)
                else:
                    info[user_domain_moid.index(result[1])]['info'].append(dict(zip(columns[2:], result[2:])))

        data['info'] = info
        response = global_func.get_response(data=data)
        return Response(response)


class GisLink(APIView):
    def get(self, request, *args, **kwargs):
        terminals = GisTerminalModel.objects.all()
        terminals_moid = [terminal.moid for terminal in terminals]
        machine_rooms = GisMachineRoomModel.objects.all()
        machine_rooms_moid_str = ','.join(('\'%s\'' % machine_room.moid for machine_room in machine_rooms))
        peripherals = GisPeripheralModel.objects.all()
        info = {
            "src_moid": "",
            "dest_moid": "",
            "status": 0,
            "detail": {}
        }
        data = {
            'info': []
        }

        manager_rooms = []
        all_used_rooms = []
        try:
            connections['luban'].close()
            with connections['luban'].cursor() as cursor:
                # 外设相关连线
                # 外设连接归属机房
                for peripheral in peripherals:
                    sql = '''
                    select machine_room_moid from peripheral_info where per_moid=%s
                    '''
                    per_moid = peripheral.moid
                    cursor.execute(sql, params=[per_moid])
                    machine_room_moid = cursor.fetchone()
                    info_tmp = copy.deepcopy(info)
                    info_tmp['src_moid'] = per_moid
                    if machine_room_moid:
                        info_tmp['dest_moid'] = machine_room_moid[0]
                        info_tmp['detail']['link_type'] = 2
                        data['info'].append(info_tmp)

                # 机房相关连线
                # 非管理机房连接管理机房
                if machine_rooms_moid_str:
                    manager_room_sql = '''
                    select machine_room_moid from machine_room_info where machine_room_type=1 and machine_num>0 and 
                    machine_room_moid in (%s)
                    ''' % machine_rooms_moid_str
                    all_used_room_sql = '''
                    select machine_room_moid from machine_room_info where machine_num>0 and machine_room_moid in (%s)
                    ''' % machine_rooms_moid_str

                    cursor.execute(manager_room_sql, )
                    manager_rooms = cursor.fetchall()
                    cursor.execute(all_used_room_sql, )
                    all_used_rooms = cursor.fetchall()

        except Exception as e:
            err = str(e)
            logger.error(err)

        for manager_room in manager_rooms:
            manager_room_moid = manager_room[0]
            for room_moid in all_used_rooms:
                if room_moid[0] != manager_room_moid:
                    info_tmp = copy.deepcopy(info)
                    info_tmp['src_moid'] = manager_room_moid
                    info_tmp['dest_moid'] = room_moid[0]
                    info_tmp['detail']['link_type'] = 1
                    data['info'].append(info_tmp)

        # 终端相关连线
        # 在会终端连注册机房
        in_meeting_terminals = []
        conf_mt_e164_info = query_func.get_now_in_meeting_mt_e164()
        for mt_e164_list in conf_mt_e164_info.values():
            in_meeting_terminals += mt_e164_list
        in_meeting_terminal_moids = []
        try:
            connections['movision'].close()
            with connections['movision'].cursor() as cursor:
                if in_meeting_terminals:
                    # for in_meeting_terminal in in_meeting_terminals:
                    sql = '''
                    SELECT uf.moid,udm.machine_room_moid,uf.e164,mr.machine_room_name,up.name FROM user_info uf 
                    LEFT JOIN user_domain_machine udm on uf.user_domain_moid=udm.user_domain_moid 
                    LEFT JOIN machine_room mr on mr.machine_room_moid=udm.machine_room_moid 
                    LEFT JOIN user_profile up on uf.moid=up.moid 
                    WHERE uf.e164 in %s
                    '''
                    # params = [in_meeting_terminal['mtaccount'], in_meeting_terminal['mtname']]
                    params = [in_meeting_terminals]
                    cursor.execute(sql, params=params)
                    user_moids = cursor.fetchall()

                    if user_moids:
                        for user_moid in user_moids:
                            in_meeting_terminal_moids.append({
                                'user_moid': user_moid[0],
                                'machine_room_moid': user_moid[1],
                                'mt_e164': user_moid[2],
                                'machine_room_name': user_moid[3],
                                'user_name': user_moid[4]
                            })

                for in_meeting_terminal_moid in in_meeting_terminal_moids:
                    if in_meeting_terminal_moid['user_moid'] in terminals_moid:
                        info_tmp = copy.deepcopy(info)
                        info_tmp['src_moid'] = in_meeting_terminal_moid['user_moid']
                        info_tmp['dest_moid'] = in_meeting_terminal_moid['machine_room_moid']
                        info_tmp['detail']['link_type'] = 0
                        info_tmp['detail']['mt_e164'] = in_meeting_terminal_moid['mt_e164']
                        info_tmp['detail']['machine_room_name'] = in_meeting_terminal_moid['machine_room_name']
                        info_tmp['detail']['user_name'] = in_meeting_terminal_moid['user_name']
                        for conf_e164 in conf_mt_e164_info:
                            if in_meeting_terminal_moid['mt_e164'] in conf_mt_e164_info[conf_e164]:
                                info_tmp['detail']['conf_e164'] = conf_e164
                                break
                        if not info_tmp['detail'].get('conf_e164'):
                            info_tmp['detail']['conf_e164'] = ''
                            logger.warning('未获取到%s的会议号码' % in_meeting_terminal_moid['mt_e164'])
                        data['info'].append(info_tmp)
        except Exception as e:
            err = str(e)
            logger.error(err)

        response = global_func.get_response(data=data)
        return Response(response)


class TerminalInConfLink(APIView):
    # 查询电子地图连线的会议上行的主视频、音频的丢包率、码率
    def get(self, request, *args, **kwargs):
        mt_e164 = kwargs.get('e164', '')
        conf_e164 = ''
        conf_name = ''
        conf_mt_e164_info = query_func.get_now_in_meeting_mt_e164()
        dsl = copy.deepcopy(es_ql.direct_up_video_audio_lost_rate_dsl)
        index = dsl.get('index')
        search_body = dsl.get('dsl')
        es_response = {}
        for conf_e164_key in conf_mt_e164_info:
            if mt_e164 in conf_mt_e164_info[conf_e164_key]:
                conf_e164_query = {"match_phrase": {"source.conf_e164": {"query": conf_e164_key}}}
                # 主叫为终端，被叫为会议，则为上行
                channer_query = {"match_phrase": {"source.context.channer.id": {"query": mt_e164}}}
                channee_query = {"match_phrase": {"source.context.chanee.id": {"query": conf_e164_key}}}
                conf_e164 = conf_e164_key
                conf_name = conf_mt_e164_info[conf_e164_key][0]
                search_body['query']['bool']['must'].append(conf_e164_query)
                search_body['query']['bool']['must'].append(channer_query)
                search_body['query']['bool']['must'].append(channee_query)
                logger.info(json.dumps(search_body))
                try:
                    es_response = es_client.search(index=index, body=search_body)
                    logger.info(json.dumps(es_response))
                except Exception as e:
                    logger.error(str(e))
                    response = global_func.get_response(0, error_code=10002)
                    return Response(response)
                else:
                    break
        if conf_e164:
            buckets = jsonpath.jsonpath(es_response, '$..chan_type.buckets')
            buckets = buckets[0] if buckets else []
            video_data = {}
            audio_data = {}
            data = {
                'conf_e164': conf_e164,
                'conf_name': conf_name,
                'mt_e164': mt_e164,
                'video': video_data,
                'audio': audio_data
            }
            for bucket in buckets:
                lost = jsonpath.jsonpath(bucket, '$..statis.rtp_lose.lose_percent.cur')
                # 丢包率，单位为%
                lost = lost[0] if lost else None
                rate = jsonpath.jsonpath(bucket, '$..statis.udp_pkt.bytes_rate.cur')
                # rate/1024*8，单位转换为kbps，保留2位小数
                rate = round(rate[0] / 1024 * 8, ndigits=2) if rate else None
                if bucket.get('key') == 'video':
                    video_data['lost'] = lost
                    video_data['rate'] = rate
                elif bucket.get('key') == 'audio':
                    audio_data['lost'] = lost
                    audio_data['rate'] = rate

            response = global_func.get_response(data=data)
            return Response(response)
        else:
            response = global_func.get_response(0, error_code=10404)
            return Response(response)
