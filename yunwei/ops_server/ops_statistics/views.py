from django.shortcuts import render

# Create your views here.

import logging
import copy
import time
import jsonpath
import datetime
import os
import csv
import codecs
from math import ceil, floor
from common import global_func
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http.response import FileResponse, HttpResponse
from django.db import connections

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from common.keda_baseclass import KedaWarningBaseAPIView, MultiDeleteAPIView
from ops_statistics.models import PositionModel
from ops_statistics.statistics_serializer.statistics_serializer import PositionSerializers

from common.my_exception import OpsException
from common.my_elastic import es_client
from ops_statistics import query_func
from .dsl import es_ql
from ops.settings import MEDIA_ROOT

logger = logging.getLogger('ops.' + __name__)
info_logger = logging.getLogger('ops_info.' + __name__)


class HardWareResource(APIView):
    def get(self, request, *args, **kwargs):
        h_type = kwargs.get('type')

        metricset_name = {
            'cpu': 'cpu',
            'memory': 'memory',
            'network_in': 'network',
            'network_out': 'network',
            'disk': 'disk',
            'diskage': 'diskage',
        }

        start_time = request.query_params.get('start_time',
                                              str(es_client.get_start_time(time.time() * 1000 - 86400000)))
        end_time = request.query_params.get('end_time', str(es_client.get_end_time(time.time() * 1000)))
        interval = request.query_params.get('interval', es_client.get_interval_time(start_time, end_time, point=40))
        platform_moid = request.query_params.get('platform_moid', '')
        topN = int(request.query_params.get('topN', '5'))
        # 读取所有机器的moid
        try:
            with connections['luban'].cursor() as cursor:
                sql = '''
                select machine_moid,machine_name from machine_info where device_type='0'
                and machine_type not in %s
                '''
                # 去除jdb4000服务器
                params = [['jdb4000', ]]
                cursor.execute(sql, params=params)
                fetchall = cursor.fetchall()
        except Exception as e:
            err = str(e)
            logger.error(err)
            fetchall = []

        moids = [moid[0] for moid in fetchall]
        moid2name = {moid[0]: moid[1] for moid in fetchall}
        # moids = [
        #     '10ef2abe-6657-11e9-8da9-001e67e37d47',
        #     '3973d1e0-3576-11e9-9304-001e67e37d47',
        #     '50981888-6652-11e9-8da9-001e67e37d47'
        # ]

        data = {
            'start_time': start_time,
            'end_time': end_time,
            'interval': interval,
            'platform_moid': platform_moid,
            'topN': topN,
            'type': h_type,
            'info': []
        }

        if h_type in ('cpu', 'memory'):
            # 类型1，返回时间轴对应数据
            dsls = []
            # for moid in moids:
            for moid in fetchall:
                hardware_resource_dsl = copy.deepcopy(es_ql.cpu_memory)
                # 过滤主机条件
                hardware_resource_dsl['query']['bool']['must'].append(
                    {
                        'match_phrase': {
                            'beat.eqpid': moid[0]
                        }
                    }
                )
                # 时间条件
                hardware_resource_dsl['query']['bool']['filter']['range']['@timestamp']['gte'] = start_time
                hardware_resource_dsl['query']['bool']['filter']['range']['@timestamp']['lte'] = end_time
                hardware_resource_dsl['aggs']['2']['date_histogram']['extended_bounds']['min'] = int(start_time)
                hardware_resource_dsl['aggs']['2']['date_histogram']['extended_bounds']['max'] = int(end_time)
                hardware_resource_dsl['aggs']['2']['date_histogram']['interval'] = interval
                hardware_resource_dsl['query']['bool']['must'][0]['match']['metricset.name'] = metricset_name.get(
                    h_type)
                if h_type == 'cpu':
                    hardware_resource_dsl['aggs']['2']['aggs']['3'] = {
                        "avg": {
                            "field": "system.cpu.cores"
                        }
                    }
                if h_type == 'memory':
                    hardware_resource_dsl['aggs']['2']['aggs']['1']['avg']['field'] = 'system.memory.actual.used.pct'
                dsls.append(
                    hardware_resource_dsl
                )

            m_body = es_client.get_m_body(*dsls)
            logger.info(m_body)
            try:
                ret = es_client.msearch(body=m_body)
            except Exception as e:
                err = str(e)
                logger.error(err)
                response = global_func.get_response(0, error_msg=err)
                return Response(response)

            l_tmp = []
            for index, moid in enumerate(fetchall):
                if ret['responses'][index].get('aggregations') and ret['responses'][index]['aggregations']['2'][
                    'buckets']:
                    if h_type == 'cpu':
                        # cpu总使用率除以cpu核数
                        core_num = ret['responses'][index]['aggregations']['2']['buckets'][-1]['3']['value']
                        total_pct = ret['responses'][index]['aggregations']['2']['buckets'][-1]['3']['value']
                        if core_num and total_pct:
                            cpu_total_pct = total_pct / core_num
                        else:
                            cpu_total_pct = 0
                        l_tmp.append(
                            [index, moid[1], cpu_total_pct])
                    else:
                        l_tmp.append(
                            [index, moid[1], ret['responses'][index]['aggregations']['2']['buckets'][-1]['1']['value']])
                else:
                    l_tmp.append(
                        [index, moid[1], 0])

            # 根据最后一个值降序排序
            l_tmp.sort(key=lambda pct: pct[-1] if pct[-1] else 0, reverse=True)

            for index, value in enumerate(l_tmp):
                if index < topN:
                    i = value[0]
                    info = {
                        "name": value[1],
                        "description": value[1],
                        "data": []
                    }
                    if ret['responses'][i].get('aggregations'):
                        for bucket in ret['responses'][i]['aggregations']['2']['buckets']:
                            if h_type == 'cpu':
                                if bucket['1']['value'] and bucket['3']['value']:
                                    info['data'].append([bucket['key'], bucket['1']['value'] / bucket['3']['value']])
                                else:
                                    info['data'].append([bucket['key'], 0])
                            else:
                                info['data'].append(
                                    [bucket['key'], bucket['1']['value'] if bucket['1']['value'] else 0])

                    data['info'].append(info)
                else:
                    break

            response = global_func.get_response(data=data)

        elif h_type in ('network_in', 'network_out'):
            # moids = ['moooo-ooo-oooo-1234']
            # 类型1，数据处理方法区别
            dsls = []
            if h_type == 'network_in':
                es_ql.network['dsl']['aggs']['network_name']['aggs']['2'][
                    'aggs']['bytes']['max']['field'] = 'system.network.in.bytes'
            else:
                es_ql.network['dsl']['aggs']['network_name']['aggs']['2'][
                    'aggs']['bytes']['max']['field'] = 'system.network.out.bytes'

            for moid in fetchall:
                network_dsl = copy.deepcopy(es_ql.network)
                network_dsl['dsl']['query']['bool']['must'].append(
                    {"match_phrase": {"beat.eqpid": moid[0]}}
                )
                network_dsl['dsl']['query']['bool']['filter']['range']['@timestamp']['gte'] = start_time
                network_dsl['dsl']['query']['bool']['filter']['range']['@timestamp']['lte'] = end_time
                network_dsl['dsl']['aggs']['network_name']['aggs']['2']['date_histogram']['extended_bounds'][
                    'min'] = int(start_time)
                network_dsl['dsl']['aggs']['network_name']['aggs']['2']['date_histogram']['extended_bounds'][
                    'max'] = int(end_time)
                network_dsl['dsl']['aggs']['network_name']['aggs']['2']['date_histogram']['interval'] = interval
                dsls.append(network_dsl)

            m_body = es_client.get_index_header_m_body(*dsls)
            logger.info('multi search body: %s ' % m_body)
            try:
                ret = es_client.msearch(body=m_body)
            except Exception as e:
                logger.error(str(e))
                ret = None

            if ret:
                descs = []
                for moid in fetchall:
                    network_card_buckets = jsonpath.jsonpath(
                        ret['responses'][moids.index(moid[0])],
                        '$..aggregations.network_name.buckets'
                    )
                    if network_card_buckets:
                        for network_card_bucket in network_card_buckets[0]:
                            info = []
                            network_card_name = network_card_bucket['key']
                            desc = moid[1] + '+' + network_card_name
                            sub_buckets = network_card_bucket['2']['buckets']
                            keys = jsonpath.jsonpath(sub_buckets, '$..key')[1:]
                            normalized_values = jsonpath.jsonpath(sub_buckets, '$..normalized_value')

                            for index, key in enumerate(keys):
                                info.append({
                                    'timestamp': key,
                                    'value': normalized_values[index] if normalized_values[index] else 0}
                                )

                            descs.append({'desc': desc, 'info': info})
                # 根据网卡流量值排序
                descs.sort(key=lambda x: x['info'][-1]['value'] if x['info'][-1]['value'] else 0, reverse=True)

                for desc in descs[:topN]:
                    info = {
                        'name': desc['desc'],
                        'description': desc['desc'],
                        'data': [[info_dic['timestamp'], info_dic['value']] for info_dic in desc['info']]
                    }

                    data['info'].append(info)

            response = global_func.get_response(data=data)

        elif h_type in ('disk', 'diskage'):
            # 类型2，返回最新数据
            if h_type == 'diskage':
                diskage_dsl = es_ql.diskage
                dsls = [
                    diskage_dsl,
                ]
                m_body = es_client.get_index_header_m_body(*dsls)
                logger.debug(m_body)
                ret = es_client.msearch(body=m_body)

                if ret:
                    diskage_l = []
                    diskage_buckets = jsonpath.jsonpath(ret['responses'][dsls.index(diskage_dsl)], '$..buckets')
                    if diskage_buckets:
                        diskage_buckets = diskage_buckets[0]
                        for bucket in diskage_buckets:
                            machine_moid = bucket.get('key')
                            machine_name = moid2name.get(machine_moid) if moid2name.get(machine_moid) else '---'
                            diskage_jsonobj = jsonpath.jsonpath(bucket, '$..source.diskage')
                            if diskage_jsonobj:
                                diskages = diskage_jsonobj[0]
                            else:
                                diskages = []

                            for diskage in diskages:
                                name = diskage.get('dev')
                                used = diskage.get('age')
                                diskage_l.append(
                                    {
                                        'desc': machine_name + '+' + name,
                                        'used': used
                                    }
                                )
                    diskage_l.sort(key=lambda x: x['used'], reverse=True)
                    for diskage in diskage_l[:topN]:
                        diskage_info = {}
                        diskage_info['name'] = diskage['desc']
                        diskage_info['description'] = diskage['desc']
                        diskage_info['data'] = diskage['used']
                        data['info'].append(diskage_info)

            elif h_type == 'disk':
                disk_dsl = es_ql.disk_used
                moid_query = [{'match_phrase': {"beat.eqpid": moid}} for moid in moids]
                disk_dsl['dsl']['query']['bool']['should'] = moid_query
                disk_dsl['dsl']['query']['bool']['minimum_should_match'] = 1
                dsls = [
                    disk_dsl,
                ]

                m_body = es_client.get_index_header_m_body(*dsls)
                logger.debug(m_body)
                try:
                    ret = es_client.msearch(body=m_body)
                except Exception as e:
                    logger.error(str(e))
                    ret = {}
                if ret:
                    # 所有机器磁盘使用率列表
                    disk_l = []
                    disk_response = ret['responses'][dsls.index(disk_dsl)]
                    eqpid_buckets = jsonpath.jsonpath(disk_response, '$..eqpid.buckets')
                    eqpid_buckets = eqpid_buckets[0] if eqpid_buckets else []

                    for eqpid_bucket in eqpid_buckets:
                        machine_moid = eqpid_bucket.get('key', '')
                        machine_name = moid2name.get(machine_moid) if moid2name.get(machine_moid) else '---'
                        mount_point_buckets = jsonpath.jsonpath(eqpid_bucket, '$..mount_point.buckets')
                        mount_point_buckets = mount_point_buckets[0] if mount_point_buckets else []

                        for mount_point_bucket in mount_point_buckets:
                            mount_point = mount_point_bucket.get('key', '')
                            used_pct = jsonpath.jsonpath(mount_point_bucket, '$..pct')
                            used_pct = used_pct[0] if used_pct else 0
                            disk_l.append({
                                'desc': machine_name + '+' + mount_point,
                                'used': used_pct
                            })
                    disk_l.sort(key=lambda x: x['used'] if x['used'] else 0, reverse=True)
                    for disk in disk_l[:topN]:
                        disk_info = {}
                        disk_info['name'] = disk['desc']
                        disk_info['description'] = disk['desc']
                        disk_info['data'] = disk['used']
                        data['info'].append(disk_info)
            response = global_func.get_response(data=data)
        else:
            response = global_func.get_response(0, error_msg='error type')

        return Response(response)


class ConfResources(APIView):
    # 会议资源
    def get(self, request, *args, **kwargs):
        platform_moid = request.query_params.get('platform_moid', '')
        room_moid = request.query_params.get('room_moid', '')
        end_time = request.query_params.get('end_time', '')
        if end_time.isdigit():
            logger.debug(end_time)
            resource_info_data = query_func.get_now_resource_info(request, end_time)
            conf_convened_num_data = query_func.get_now_on_going_conf_info(request, end_time)
        else:
            resource_info_data = query_func.get_now_resource_info(request)
            conf_convened_num_data = query_func.get_now_on_going_conf_info(request)
        conf_type_info = query_func.get_conf_type(
            [on_going_conf_info.get('confE164') for on_going_conf_info in conf_convened_num_data]
        )
        # conf_type_info = {'0': ['6662455', '6662505', '6662529'], '1': ['6662456', '6662542', '6662550']}
        # resource_info_data = {
        #     "mooooooo-oooo-oooo-oooo-defaultmachi": {
        #         "remainder_port": 14,
        #         "machine_room_moid": "mooooooo-oooo-oooo-oooo-defaultmachi",
        #         "remainder_tra": 2,
        #         "total_port": 24
        #     },
        #     "mooooooo-oooo-oooo-oooo-defaultmach2": {
        #         "remainder_port": 14,
        #         "machine_room_moid": "mooooooo-oooo-oooo-oooo-defaultmach2",
        #         "remainder_tra": 1,
        #         "total_port": 24
        #     }
        # }
        conf_convened_num = {
            "name": "tra_conf_convened_num",
            "description": "传统会议已召开",
            "data": len(conf_type_info.get('0'))
        }
        port_conf_convened_num = {
            "name": "port_conf_convened_num",
            "description": "端口会议已召开",
            "data": len(conf_type_info.get('1'))
        }

        total_port = jsonpath.jsonpath(resource_info_data, '$..total_port')
        port_total_num = {
            "name": "total_port_num",
            "description": "端口总数",
            "data": sum(total_port) if total_port else 0
        }

        # es数据获取媒体上报内容，更换为redis获取
        # remainder_tra = jsonpath.jsonpath(resource_info_data, '$..remainder_tra')
        # conf_conveyable_num_1080_30 = {
        #     "name": "tra_conf_conveyable_num_1080_30",
        #     "description": "传统会议可召开1080P30会议",
        #     "data": sum(remainder_tra) if remainder_tra else 0
        # }
        now_support_conf_info = query_func.get_now_support_conf_info(request)
        conf_conveyable_num_1080_60_l = {
            "name": "tra_conf_conveyable_num_1080_60_l",
            "description": "传统会议可召开1080P60大方会议",
            "data": now_support_conf_info.get('1080p60_192', {}).get('support', 0)
        }
        conf_conveyable_num_1080_60_s = {
            "name": "tra_conf_conveyable_num_1080_60_s",
            "description": "传统会议可召开1080P60小方会议",
            "data": now_support_conf_info.get('1080p60_8', {}).get('support', 0)
        }
        conf_conveyable_num_1080_30_l = {
            "name": "tra_conf_conveyable_num_1080_30_l",
            "description": "传统会议可召开1080P30大方会议",
            "data": now_support_conf_info.get('1080p30_192', {}).get('support', 0)
        }
        conf_conveyable_num_1080_30_s = {
            "name": "tra_conf_conveyable_num_1080_30_s",
            "description": "传统会议可召开1080P30小方会议",
            "data": now_support_conf_info.get('1080p30_8', {}).get('support', 0)
        }
        conf_conveyable_num_720_60_l = {
            "name": "tra_conf_conveyable_num_720_60_l",
            "description": "传统会议可召开720P60大方会议",
            "data": now_support_conf_info.get('720p60_192', {}).get('support', 0)
        }
        conf_conveyable_num_720_60_s = {
            "name": "tra_conf_conveyable_num_720_60_s",
            "description": "传统会议可召开720P60小方会议",
            "data": now_support_conf_info.get('720p60_8', {}).get('support', 0)
        }
        conf_conveyable_num_720_30_l = {
            "name": "tra_conf_conveyable_num_720_30_l",
            "description": "传统会议可召开720P30大方会议",
            "data": now_support_conf_info.get('720p30_192', {}).get('support', 0)
        }
        conf_conveyable_num_720_30_s = {
            "name": "tra_conf_conveyable_num_720_30_s",
            "description": "传统会议可召开720P30小方会议",
            "data": now_support_conf_info.get('720p30_8', {}).get('support', 0)
        }
        remainder_port = jsonpath.jsonpath(resource_info_data, '$..remainder_port')
        port_num = {
            "name": "free_port_num",
            "description": "端口剩余数",
            "data": sum(remainder_port) if remainder_port else 0
        }
        data = {
            "platform_moid": platform_moid,
            "room_moid": room_moid,
            "info": [
                conf_convened_num,
                port_conf_convened_num,
                # conf_conveyable_num_1080_30,  # es数据获取媒体上报内容，更换为redis获取
                conf_conveyable_num_1080_60_l,
                conf_conveyable_num_1080_60_s,
                conf_conveyable_num_1080_30_l,
                conf_conveyable_num_1080_30_s,
                conf_conveyable_num_720_60_l,
                conf_conveyable_num_720_60_s,
                conf_conveyable_num_720_30_l,
                conf_conveyable_num_720_30_s,
                port_num,
                port_total_num,
            ]
        }

        response = global_func.get_response(data=data)
        return Response(response)


class P2PConfResources(APIView):
    def get(self, request, *args, **kwargs):
        platform_moid = request.query_params.get('platform_moid', '')
        room_moid = request.query_params.get('room_moid', '')
        end_time = request.query_params.get('end_time', '')
        if end_time.isdigit():
            ap_info = query_func.get_now_ap_info(request, end_time)
            dss_bandwidth_info = query_func.get_now_dss_bandwidth_info(request, end_time)
            p2p_conf_used_num = query_func.get_now_p2p_conf_info(request, end_time)
        else:
            ap_info = query_func.get_now_ap_info(request)
            dss_bandwidth_info = query_func.get_now_dss_bandwidth_info(request)
            p2p_conf_used_num = query_func.get_now_p2p_conf_info(request)

        # 点对点可召开总数（ap授权数/2 或 总带宽 / 4， 取较小的值）
        p2p_conf_total_num_from_ap = ap_info.get('total') / 2
        # 总带宽单位为kb
        p2p_conf_total_num_from_dss_bandwidth = dss_bandwidth_info.get('total') / 1024 / 4
        logger.info('ap: %s, bandwidth: %s' % (p2p_conf_total_num_from_ap, p2p_conf_total_num_from_dss_bandwidth))
        p2p_conf_total_num = min([p2p_conf_total_num_from_ap, p2p_conf_total_num_from_dss_bandwidth])
        p2p_conf_available = floor(p2p_conf_total_num - p2p_conf_used_num) if \
            floor(p2p_conf_total_num - p2p_conf_used_num) > 0 else 0

        p2p_conf_convened_num = {
            "name": "p2p_conf_convened_num",
            "description": "点对点会议已召开",
            "data": p2p_conf_used_num
        }
        p2p_conf_conveyable_num = {
            "name": "p2p_conf_conveyable_num",
            "description": "点对点会议可召开",
            "data": p2p_conf_available
        }
        data = {
            "platform_moid": platform_moid,
            "room_moid": room_moid,
            "info": [
                p2p_conf_convened_num,
                p2p_conf_conveyable_num,
            ]
        }

        response = global_func.get_response(data=data)
        return Response(response)


class ConfResourcesStatistics(APIView):
    # 会议资源统计图
    def get(self, request, *args, **kwargs):
        platform_moid = request.query_params.get('platform_moid', '')
        room_moid = request.query_params.get('room_moid', '')
        start_time = request.query_params.get('start_time',
                                              str(es_client.get_start_time(time.time() * 1000 - 86400000)))
        end_time = request.query_params.get('end_time', str(es_client.get_end_time(time.time() * 1000)))
        interval = request.query_params.get('interval', es_client.get_interval_time(start_time, end_time, point=40))

        port_resource = {
            "name": "conf_resource",
            "description": "端口会议资源",
            "data": []
        }
        conf_resource = {
            "name": "conf_resource",
            "description": "传统会议资源",
            "data": []
        }

        data = {
            "start_time": start_time,
            "end_time": end_time,
            "interval": interval,
            "platform_moid": platform_moid,
            "room_moid": room_moid,
            "info": [
                conf_resource,
                port_resource,
            ]
        }
        port_resource['data'], conf_resource['data'] = query_func.get_time_aggs_resource_info(request)

        response = global_func.get_response(data=data)
        return Response(response)


class CurrTerminal(APIView):
    # 终端在线统计
    def get(self, request, *args, **kwargs):
        start_time = request.query_params.get('start_time',
                                              str(es_client.get_start_time(time.time() * 1000 - 86400000)))
        end_time = request.query_params.get('end_time', str(es_client.get_end_time(time.time() * 1000)))
        interval = request.query_params.get('interval', es_client.get_interval_time(start_time, end_time, point=40))
        platform_moid = request.query_params.get('platform_moid', '')

        try:
            info_sip = {
                "name": "sip",
                "description": "SIP",
                "data": []
            }
            info_323 = {
                "name": "H.323",
                "description": "H.323",
                "data": []
            }
            data = {
                'start_time': start_time,
                'end_time': end_time,
                'interval': interval,
                'platform_moid': platform_moid,
                'info': [
                    info_323,
                    info_sip,
                ]
            }

            info_sip['data'], info_323['data'] = query_func.get_time_aggs_terminal_online_info(request)

            response = global_func.get_response(data=data)
        except Exception as e:
            err = str(e)
            logger.error(err)
            response = global_func.get_response(0, error_msg=err)
        return Response(response)


class CallingTerminal(APIView):
    # 终端呼叫统计
    def get(self, request, *args, **kwargs):
        start_time = request.query_params.get('start_time',
                                              str(es_client.get_start_time(time.time() * 1000 - 86400000)))
        end_time = request.query_params.get('end_time', str(es_client.get_end_time(time.time() * 1000)))
        interval = request.query_params.get('interval', es_client.get_interval_time(start_time, end_time, point=40))
        platform_moid = request.query_params.get('platform_moid', '')

        terminal_calling_info = {
            "name": "calling_terminals",
            "description": "终端呼叫数量",
            "data": []
        }
        data = {
            'start_time': start_time,
            'end_time': end_time,
            'interval': interval,
            'platform_moid': platform_moid,
            'info': [
                terminal_calling_info,
            ]
        }

        terminal_calling_info['data'] = query_func.get_time_aggs_terminal_calling_info(request)
        response = global_func.get_response(data=data)

        return Response(response)


class ConfTime(APIView):
    # 多点会议时长统计
    def get(self, request, *args, **kwargs):
        start_time = request.query_params.get('start_time',
                                              str(es_client.get_start_time(time.time() * 1000 - 86400000)))
        end_time = request.query_params.get('end_time', str(es_client.get_end_time(time.time() * 1000)))
        platform_moid = request.query_params.get('platform_moid', '')

        room_moid = request.query_params.get('room_moid', '')

        data = {
            'start_time': start_time,
            'end_time': end_time,
            'platform_moid': platform_moid,
            'room_moid': room_moid,
            'info': []
        }

        try:
            # 多点会议时长计算
            all_conf_time = query_func.get_all_conf_time_info(request)

            # 时长结果统计

            lte_20min_info = {
                "name": "lte_20min",
                "description": "<20分钟",
                "data": 0
            }
            min_20_60_info = {
                "name": "20-60min",
                "description": "20~60分钟",
                "data": 0
            }
            min_60_120_info = {
                "name": "60-120min",
                "description": "60~120分钟",
                "data": 0
            }
            min_120_240_info = {
                "name": "120-240min",
                "description": "120~240分钟",
                "data": 0
            }
            gt_240min_info = {
                "name": "gt_240min",
                "description": ">240分钟",
                "data": 0
            }
            for conf_time in all_conf_time:
                # 毫秒转为分钟
                conf_time_2_min = conf_time / 1000 / 60
                if conf_time_2_min <= 20:
                    lte_20min_info['data'] += 1
                elif conf_time_2_min <= 60:
                    min_20_60_info['data'] += 1
                elif conf_time_2_min <= 120:
                    min_60_120_info['data'] += 1
                elif conf_time_2_min <= 240:
                    min_120_240_info['data'] += 1
                else:
                    gt_240min_info['data'] += 1
            data['info'].append(gt_240min_info)
            data['info'].append(min_120_240_info)
            data['info'].append(min_60_120_info)
            data['info'].append(min_20_60_info)
            data['info'].append(lte_20min_info)

            response = global_func.get_response(data=data)
        except Exception as e:
            err = str(e)
            logger.error(err)
            response = global_func.get_response(0, error_msg=err)
        return Response(response)


class CurrConfNum(APIView):
    # 8.13调整，正在召开数据同class MediaConfNumStatistics
    def get(self, request, *args, **kwargs):
        start_time = request.query_params.get('start_time',
                                              str(es_client.get_start_time(time.time() * 1000 - 86400000)))
        end_time = request.query_params.get('end_time', str(es_client.get_end_time(time.time() * 1000)))
        interval = request.query_params.get('interval', es_client.get_interval_time(start_time, end_time, point=40))
        platform_moid = request.query_params.get('platform_moid', '')

        data = {
            "start_time": start_time,
            "end_time": end_time,
            "interval": interval,
            "platform_moid": platform_moid,
            "info": []
        }

        try:
            # 点对点正在召开会议数
            p2p_info = {
                "name": "p2p_conf",
                "description": "点对点会议",
                "data": []
            }

            p2p_conf_info_data = query_func.get_time_aggs_p2p_conf_info(request)
            p2p_info['data'] = p2p_conf_info_data

            data['info'].append(p2p_info)

            # 多点正在召开会议数
            conf_info = {
                "name": "conf",
                "description": "多点会议",
                "data": []
            }

            conf_info_data = query_func.get_time_aggs_conf_info(request)
            conf_info['data'] = conf_info_data

            data['info'].append(conf_info)
            response = global_func.get_response(data=data)
        except Exception as e:
            logger.error(str(e))
            response = global_func.get_response(0, error_msg=str(e))

        return Response(response)


class LiveConfNum(APIView):
    def get(self, request, *args, **kwargs):
        start_time = request.query_params.get('start_time',
                                              str(es_client.get_start_time(time.time() * 1000 - 86400000)))
        end_time = request.query_params.get('end_time', str(es_client.get_end_time(time.time() * 1000)))
        interval = request.query_params.get('interval', es_client.get_interval_time(start_time, end_time, point=40))
        platform_moid = request.query_params.get('platform_moid', '')
        live_conf_info, viewer_info = query_func.get_time_aggs_vrs_info(request)
        data = {
            "start_time": start_time,
            "end_time": end_time,
            "interval": interval,
            "platform_moid": platform_moid,
            "info": [
                live_conf_info,
                viewer_info
            ]
        }

        response = global_func.get_response(data=data)
        return Response(response)


class VrsResourcesStatistics(APIView):
    def get(self, request, *args, **kwargs):
        start_time = request.query_params.get('start_time',
                                              str(es_client.get_start_time(time.time() * 1000 - 86400000)))
        end_time = request.query_params.get('end_time', str(es_client.get_end_time(time.time() * 1000)))
        interval = request.query_params.get('interval', es_client.get_interval_time(start_time, end_time, point=40))
        platform_moid = request.query_params.get('platform_moid', '')
        try:
            video_room_resources_info, live_resources_info = query_func.get_time_aggs_vrs_resources_info(request)
        except Exception as e:
            logger.error(str(e))
            video_room_resources_info, live_resources_info = [], []
        data = {
            "start_time": start_time,
            "end_time": end_time,
            "interval": interval,
            "platform_moid": platform_moid,
            "info": [
                video_room_resources_info,
                live_resources_info,
            ]
        }
        response = global_func.get_response(data=data)
        return Response(response)


class AppointmentConf(APIView):
    def get(self, request, *args, **kwargs):
        platform_moid = request.query_params.get('platform_moid', '')
        # 预约会议数据
        appointment_conf_info = {
            "name": "appointment_confs",
            "description": "预约会议",
            "data": []
        }

        # 预约直播会议数据
        live_appointment_conf_info = {
            "name": "appointment_live_confs",
            "description": "预约直播会议",
            "data": []
        }
        data = {
            # "start_time": start_time,
            # "end_time": end_time,
            # "interval": interval,
            "platform_moid": platform_moid,
            "info": [
                appointment_conf_info,
                live_appointment_conf_info
            ]
        }

        appointment_conf_info['data'], live_appointment_conf_info['data'] = \
            query_func.get_appointment_conf_statistics_every_interval_min(request)

        response = global_func.get_response(data=data)
        return Response(response)


class TerminalResources(APIView):
    def get(self, request, *args, **kwargs):
        room_moid = request.query_params.get('room_moid', '')
        start_time = request.query_params.get('start_time',
                                              str(es_client.get_start_time(time.time() * 1000 - 86400000)))
        end_time = request.query_params.get('end_time', str(es_client.get_end_time(time.time() * 1000)))
        interval = request.query_params.get('interval', es_client.get_interval_time(start_time, end_time, point=40))
        platform_moid = request.query_params.get('platform_moid', '')

        online_mt_info = {
            "name": "online_mt",
            "description": "在线终端数量",
            "data": []
        }
        conf_mt_info = {
            "name": "conf_mt",
            "description": "与会终端数量",
            "data": []
        }
        data = {
            "start_time": start_time,
            "end_time": end_time,
            "interval": interval,
            "platform_moid": platform_moid,
            "room_moid": room_moid,
            "info": [
                online_mt_info,
                conf_mt_info,
            ]
        }

        online_mt_info['data'], conf_mt_info['data'] = query_func.get_time_aggs_terminal_online_in_meeting_info(request)
        response = global_func.get_response(data=data)

        return Response(response)


class TransmitResources(APIView):
    def get(self, request, *args, **kwargs):
        room_moid = request.query_params.get('room_moid', '')
        start_time = request.query_params.get('start_time',
                                              str(es_client.get_start_time(time.time() * 1000 - 86400000)))
        end_time = request.query_params.get('end_time', str(es_client.get_end_time(time.time() * 1000)))
        interval = request.query_params.get('interval', es_client.get_interval_time(start_time, end_time, point=40))
        platform_moid = request.query_params.get('platform_moid', '')

        bandwidth_info = {
            "name": "bandwidth",
            "description": "转发带宽",
            "data": []
        }

        data = {
            "start_time": start_time,
            "end_time": end_time,
            "interval": interval,
            "platform_moid": platform_moid,
            "room_moid": room_moid,
            "info": [
                bandwidth_info,
            ]
        }

        bandwidth_info_data = query_func.get_time_aggs_dss_bandwidth_info(request)
        bandwidth_info['data'] = bandwidth_info_data
        response = global_func.get_response(data=data)

        return Response(response)


class CompanyInfo(APIView):
    # 企业信息统计
    def get(self, request, *args, **kwargs):
        platform_moid = request.query_params.get('platform_moid', '')
        room_moid = request.query_params.get('room_moid', '')
        sql = '''
        SELECT used_flag,count(used_flag) as count FROM `user_domain` ud 
        LEFT JOIN `user_domain_machine` udm ON ud.user_domain_moid=udm.user_domain_moid 
        WHERE 1=1
        '''
        if platform_moid:
            sql += ' AND ud.platform_domain_moid="%s"' % platform_moid
        if room_moid:
            sql += ' AND udm.machine_room_moid="%s"' % room_moid

        sql += ' GROUP BY used_flag;'
        enable = 0
        disable = 0
        try:
            with connections['movision'].cursor() as cursor:
                cursor.execute(sql)
                fetchall = cursor.fetchall()
                if fetchall:
                    for one in fetchall:
                        if one[0] == 0:
                            disable += one[1]
                        elif one[0] == 1:
                            enable += one[1]
            enable_info = {
                'name': 'company_enable',
                'description': '在用企业',
                'data': enable
            }
            disable_info = {
                'name': 'company_disable',
                'description': '停用企业',
                'data': disable
            }
            data = {
                'platform_moid': platform_moid,
                'info': [enable_info, disable_info]
            }

            response = global_func.get_response(data=data)
        except Exception as e:
            err = str(e)
            logger.error(err)
            response = global_func.get_response(0, error_msg=err)
        return Response(response)


class TerminalInfo(APIView):
    # 终端信息统计
    def get(self, request, *args, **kwargs):
        room_moid = request.query_params.get('room_moid', '')
        platform_moid = request.query_params.get('platform_moid', '')

        user_domain_moid = request.query_params.get('user_domain_moid', '')
        sql = '''
        SELECT ui.`enable`, COUNT(`enable`) as count FROM user_info ui 
        LEFT JOIN user_domain ud on ui.user_domain_moid=ud.user_domain_moid 
        LEFT JOIN user_domain_machine udm on ud.user_domain_moid=udm.user_domain_moid 
        WHERE isdeleted = '0' and account_type != '9' and e164 is not null and 
        (device_type is null or device_type not in ('519','524','530','531')) and
        binded='0' and account is not NULL
        '''

        if platform_moid:
            sql += ' AND ud.platform_domain_moid="%s"' % platform_moid

        if user_domain_moid:
            sql += ' AND ui.user_domain_moid="%s"' % user_domain_moid

        if room_moid:
            sql += ' AND udm.machine_room_moid="%s"' % room_moid

        sql += ' GROUP BY ui.`enable`;'
        enable = 0
        disable = 0
        try:
            with connections['movision'].cursor() as cursor:
                cursor.execute(sql)
                fetchall = cursor.fetchall()
                if fetchall:
                    for one in fetchall:
                        if one[0] == 0:
                            disable += one[1]
                        elif one[0] == 1:
                            enable += one[1]
            enable_info = {
                'name': 'terminal_enable',
                'description': '在用帐号',
                'data': enable
            }
            disable_info = {
                'name': 'terminal_disable',
                'description': '停用帐号',
                'data': disable
            }
            data = {
                'platform_moid': platform_moid,
                'user_domain_moid': user_domain_moid,
                'info': [enable_info, disable_info]
            }

            response = global_func.get_response(data=data)
        except Exception as e:
            err = str(e)
            logger.error(err)
            response = global_func.get_response(0, error_msg=err)
        return Response(response)


class CreateConfTypeStatistics(APIView):
    # 创会数量统计
    def get(self, request, *args, **kwargs):
        room_moid = request.query_params.get('room_moid', '')
        start_time = request.query_params.get('start_time',
                                              str(es_client.get_start_time(time.time() * 1000 - 86400000)))
        end_time = request.query_params.get('end_time', str(es_client.get_end_time(time.time() * 1000)))
        interval = request.query_params.get('interval', es_client.get_interval_time(start_time, end_time, point=40))
        platform_moid = request.query_params.get('platform_moid', '')

        dsls = []
        create_conf_type_dsl = copy.deepcopy(es_ql.create_conf_type)

        dsls.append(create_conf_type_dsl)

        dsls = query_func.get_filter_dsl(request, dsls, excludes=['room_moid'])

        m_body = es_client.get_index_header_m_body(*dsls)
        logger.debug(m_body)

        try:
            ret = es_client.msearch(m_body)
        except Exception as e:
            err = str(e)
            logger.error(err)
            ret = None

        if ret:
            terminal_create_conf_info = {
                'name': 'terminal_create',
                'description': '终端创会',
                'data': []
            }
            cmc_create_conf_info = {
                'name': 'cmc_create',
                'description': '会控创会',
                'data': []
            }
            data = {
                "start_time": start_time,
                "end_time": end_time,
                "interval": interval,
                "platform_moid": platform_moid,
                "room_moid": room_moid,
                "info": [
                    terminal_create_conf_info,
                    cmc_create_conf_info
                ]
            }
            responses = ret['responses']
            create_conf_type_response = responses[dsls.index(create_conf_type_dsl)]
            create_conf_type_buckets = jsonpath.jsonpath(create_conf_type_response, '$..time.buckets')
            if create_conf_type_buckets:
                create_conf_type_buckets = create_conf_type_buckets[0]
                if room_moid:
                    in_room_meetingid = query_func.get_now_in_room_meetingid(request)
                    logger.debug(in_room_meetingid)
                else:
                    in_room_meetingid = None

                for bucket in create_conf_type_buckets:
                    timestamp = bucket.get('key')
                    cmc_create_count = 0
                    terminal_create_count = 0
                    create_conf_info = jsonpath.jsonpath(bucket, '$..requestorigin..key')
                    if create_conf_info:
                        meetingids = jsonpath.jsonpath(bucket, '$..meetingID.buckets[*].key')
                        meetingids = meetingids if meetingids else []

                        if in_room_meetingid is None:
                            meetingid_set = set(meetingids)
                        else:
                            # 过滤机房
                            # 机房下的meetingid 和 所有meetingid列表求交集
                            meetingid_set = set(in_room_meetingid) & set(meetingids)
                        meetingID_buckets = jsonpath.jsonpath(bucket, '$..meetingID.buckets')
                        meetingID_buckets = meetingID_buckets[0] if meetingID_buckets else []

                        for meetingID_bucket in meetingID_buckets:
                            if meetingID_bucket.get('key') in meetingid_set:
                                # 传入 room_moid 时，meetingid_set 为 此机房下的会议id集合
                                requestorigin_key = jsonpath.jsonpath(meetingID_bucket, '$..requestorigin..key')
                                requestorigin_key = requestorigin_key if requestorigin_key else []
                                # requestorigin:1：cmc创会，2：终端创会
                                cmc_create_count += requestorigin_key.count('1')
                                terminal_create_count += requestorigin_key.count('2')

                    cmc_create_conf_info['data'].append([timestamp, cmc_create_count])
                    terminal_create_conf_info['data'].append([timestamp, terminal_create_count])

            response = global_func.get_response(data=data)
        else:
            response = global_func.get_response(0, error_msg=err)
        return Response(response)


class CreateConfTypeDetail(APIView):
    # 创会数量列表
    def get(self, request, *args, **kwargs):
        room_moid = request.query_params.get('room_moid', '')
        start_time = request.query_params.get('start_time',
                                              str(es_client.get_start_time(time.time() * 1000 - 86400000)))
        end_time = request.query_params.get('end_time', str(es_client.get_end_time(time.time() * 1000)))
        platform_moid = request.query_params.get('platform_moid', '')

        key = request.query_params.get('key', '')
        count = request.query_params.get('count', '10')
        start = request.query_params.get('start', '0')

        data = {
            "start_time": start_time,
            "end_time": end_time,
            "platform_moid": platform_moid,
            "room_moid": room_moid,
            "key": key,
            "total": 0,
            "start": int(start) if start.isdigit() else 0,
            "count": int(count) if count.isdigit() else 0,
            "info": []
        }

        data['info'] = query_func.get_now_create_conf_type(request)
        data['total'] = len(data['info'])
        data['info'] = data['info'][int(start):int(start) + int(count)]
        response = global_func.get_response(data=data)

        return Response(response)


class CreateConfTypeDetailExport(APIView):
    def get(self, request, *args, **kwargs):
        start_time = request.query_params.get('start_time',
                                              str(es_client.get_start_time(time.time() * 1000 - 86400000)))
        end_time = request.query_params.get('end_time', str(es_client.get_end_time(time.time() * 1000)))

        start_time_as_string = global_func.format_timestamp(int(start_time) / 1000)
        end_time_as_string = global_func.format_timestamp(int(end_time) / 1000)
        media_path = os.path.join(MEDIA_ROOT, 'create_conf_type')
        file_name = '%s_%s_company_create_conf_type.csv' % (start_time_as_string, end_time_as_string)
        file_path = os.path.join(media_path, file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        data = [['企业名称', '终端创会数量', '会控创会数量']]
        jsonDataRead = query_func.get_now_create_conf_type(request)
        data.extend(
            [[jsonData.get('name'), jsonData.get('terminal_data'), jsonData.get('data')] for jsonData in jsonDataRead]
        )

        if jsonDataRead:
            try:
                with open(file_path, 'w', newline='', encoding='gbk') as f:
                    csv_writer = csv.writer(f)
                    csv_writer.writerows(data)
            except Exception as e:
                err = str(e)
                logger.error(err)
                return Response(status=500)

            logger.info("写入数据成功")
            # 读取csv数据
            conf_file = open(file_path, 'rb')
            logger.info(conf_file)
            response = FileResponse(conf_file)
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment;filename=%s' % file_name
            print(response['Content-Disposition'])
            # 发送至前端
            return response
        else:
            response = global_func.get_response(0, error_msg='文件不存在')
            return Response(response)


class CompanyConf(APIView):
    def get(self, request, *args, **kwargs):
        room_moid = request.query_params.get('room_moid', '')
        start_time = request.query_params.get('start_time',
                                              str(es_client.get_start_time(time.time() * 1000 - 86400000)))
        end_time = request.query_params.get('end_time', str(es_client.get_end_time(time.time() * 1000)))
        platform_moid = request.query_params.get('platform_moid', '')

        count = request.query_params.get('count', '10')
        start = request.query_params.get('start', '0')
        key = request.query_params.get('key', '')

        data = {
            "start_time": start_time,
            "end_time": end_time,
            "platform_moid": platform_moid,
            "room_moid": room_moid,
            "key": key,
            "total": 0,
            "start": int(start) if start.isdigit() else 0,
            "count": int(count) if count.isdigit() else 0,
            'info': []
        }

        data['info'] = query_func.get_now_company_conf(request)
        data['info'].sort(key=lambda x: x['data'], reverse=True)
        data['total'] = len(data['info'])
        data['info'] = data['info'][int(start):int(start) + int(count)]

        response = global_func.get_response(data=data)

        return Response(response)


class CompanyConfExport(APIView):
    def get(self, request, *args, **kwargs):
        start_time = request.query_params.get('start_time',
                                              str(es_client.get_start_time(time.time() * 1000 - 86400000)))
        end_time = request.query_params.get('end_time', str(es_client.get_end_time(time.time() * 1000)))

        start_time_as_string = global_func.format_timestamp(int(start_time) / 1000)
        end_time_as_string = global_func.format_timestamp(int(end_time) / 1000)
        media_path = os.path.join(MEDIA_ROOT, 'company_conf')
        file_name = '%s_%s_company_confs.csv' % (start_time_as_string, end_time_as_string)
        file_path = os.path.join(media_path, file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        data = [['企业名称', '会议数量']]
        jsonDataRead = query_func.get_now_company_conf(request)
        data.extend([[jsonData.get('description'), jsonData.get('data')] for jsonData in jsonDataRead])

        if jsonDataRead:
            try:
                with open(file_path, 'w', newline='', encoding='gbk') as f:
                    csv_writer = csv.writer(f)
                    csv_writer.writerows(data)
            except Exception as e:
                err = str(e)
                logger.error(err)
                return Response(status=500)

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


class CreateConfReq2AckTime(APIView):
    # 发起创会req至接到创会ack的时间间隔
    def get(self, request, *args, **kwargs):
        room_moid = request.query_params.get('room_moid', '')
        start_time = request.query_params.get('start_time',
                                              str(es_client.get_start_time(time.time() * 1000 - 86400000)))
        end_time = request.query_params.get('end_time', str(es_client.get_end_time(time.time() * 1000)))
        platform_moid = request.query_params.get('platform_moid', '')

        dsls = []
        create_conf_req2ack_time_dsl = copy.deepcopy(es_ql.create_conf_req2ack_time)

        dsls.append(create_conf_req2ack_time_dsl)
        dsls = query_func.get_filter_dsl(request=request, dsls=dsls, excludes=('room_moid',))

        m_body = es_client.get_index_header_m_body(*dsls)
        logger.debug(m_body)

        try:
            ret = es_client.msearch(m_body)
        except Exception as e:
            err = str(e)
            logger.error(err)
            ret = None

        if ret:
            try:
                info_lt_500ms = {
                    "name": "lt_500ms",
                    "description": "<500ms",
                    "data": 0,
                    "detail": []
                }
                info_500_1000ms = {
                    "name": "500ms-1s",
                    "description": "500ms-1s",
                    "data": 0,
                    "detail": []
                }
                info_gt_1s = {
                    "name": "gt_1s",
                    "description": ">1s",
                    "data": 0,
                    "detail": []
                }
                data = {
                    "start_time": start_time,
                    "end_time": end_time,
                    "platform_moid": platform_moid,
                    "room_moid": room_moid,
                    "info": [
                        info_lt_500ms,
                        info_500_1000ms,
                        info_gt_1s,
                    ]
                }

                create_conf_req2ack_time_response = ret['responses'][dsls.index(create_conf_req2ack_time_dsl)]
                meetingid_buckets = jsonpath.jsonpath(create_conf_req2ack_time_response, '$..meetingID.buckets')
                if meetingid_buckets:
                    meetingid_buckets = meetingid_buckets[0]
                    meetingids = jsonpath.jsonpath(meetingid_buckets, '$[*].key')
                    meetingids = meetingids if meetingids else []
                    if room_moid:
                        in_room_meetingid = query_func.get_now_in_room_meetingid(request)
                    else:
                        in_room_meetingid = None
                    if in_room_meetingid is None:
                        meetingid_set = set(meetingids)
                    else:
                        # 过滤机房
                        # 机房下的meetingid 和 所有meetingid列表求交集
                        meetingid_set = set(in_room_meetingid) & set(meetingids)

                    for meetingid_bucket in meetingid_buckets:
                        correlation_id_buckets = jsonpath.jsonpath(meetingid_bucket, '$..correlation_id.buckets')
                        meeting_info = jsonpath.jsonpath(meetingid_bucket, '$..source')
                        meeting_info_ack_num = jsonpath.jsonpath(meetingid_bucket, '$..source.type')
                        meeting_info_ack_num = meeting_info_ack_num.count('MAU_CM_CREATECONF_ACK') \
                            if isinstance(meeting_info_ack_num, list) else 0
                        meeting_info = meeting_info[0] if meeting_info else {}
                        if correlation_id_buckets:
                            correlation_id_buckets = correlation_id_buckets[0]
                            for correlation_id_bucket in correlation_id_buckets:
                                meetingid = meeting_info.get('meetingID', '')
                                if meetingid in meetingid_set:
                                    # 在过滤机房时，meetingid_set 为使用机房moid过滤后的结果
                                    if correlation_id_bucket.get('doc_count') >= 2 and meeting_info_ack_num:
                                        timestamp_buckets = jsonpath.jsonpath(correlation_id_bucket,
                                                                              '$..timestamp..key')
                                        create_conf_time = abs(timestamp_buckets[0] - timestamp_buckets[-1]) / 1000
                                        if meeting_info.get('type'):
                                            meeting_info.pop('type')
                                        if create_conf_time < 0.5:
                                            info_lt_500ms['data'] += 1
                                        elif create_conf_time < 1:
                                            info_500_1000ms['data'] += 1
                                        else:
                                            info_gt_1s['data'] += 1
                                            info_gt_1s['detail'].append(meeting_info)

                response = global_func.get_response(data=data)
            except Exception as e:
                err = str(e)
                logger.error(err)
                response = global_func.get_response(0, error_msg=err)
        else:
            response = global_func.get_response(0, error_code=10002)

        return Response(response)


class EquipmentUsage(APIView):
    """
    资产统计
    设备使用率  服务器和硬终端
    硬终端暂无法实现
    """

    def get(self, request, *args, **kwargs):
        parameters = request.query_params.dict()
        start_time = parameters.get("start_time")
        end_time = parameters.get("end_time")

        try:
            end_time = int(datetime.datetime.now().timestamp() * 1000) if end_time is None else int(end_time)
            start_time = int((datetime.datetime.now() - datetime.timedelta(
                days=1)).timestamp() * 1000) if start_time is None else int(start_time)
        except Exception:
            raise OpsException('30002')

        server_total_num = self.get_server_total_num()
        server_usage = self.get_server_usage_num(start_time, end_time)
        terminal_total_num = self.get_terminal_total_num()
        terminal_usage = self.get_terminal_usage_num(start_time, end_time)

        statistics = [{"name": "server", "description": "服务器设备统计", "data": [server_total_num, server_usage]},
                      {"name": "terminal", "description": "终端设备统计", "data": [terminal_total_num, terminal_usage]}]
        parameters['info'] = statistics
        return Response(global_func.get_response(data=parameters))

    def get_server_total_num(self):
        """
        获取服务器设备总数
        :return:
        """
        sql = """
                SELECT
                    machine_moid,machine_room_moid,machine_room_name
                FROM
                    machine_info
                """
        with connections['luban'].cursor() as cursor:
            params = []
            cursor.execute(sql, params)
            machine_info = cursor.fetchall()

        server_total_num = len(machine_info)
        return server_total_num

    def get_server_usage_num(self, start_time, end_time):
        """
        获取服务器运行总数
        :return:
        """
        server_run_num, _ = EquipmentRuntime.get_server_running_time(start_time, end_time)
        return server_run_num

    def get_terminal_total_num(self):
        """
        获取硬终端设备总数
        :return:
        """
        return 100

    def get_terminal_usage_num(self, start_time, end_time):
        """
        获取硬终端运行总数
        :return:
        """
        terminal_run_num, _ = EquipmentRuntime.get_terminal_running_time(start_time, end_time)
        return terminal_run_num


class EquipmentRuntime(APIView):
    """
    资产统计
    设备运行时长  服务器和硬终端
    硬终端暂无法实现
    """

    def get(self, request, *args, **kwargs):
        parameters = request.query_params.dict()
        start_time = parameters.get("start_time")
        end_time = parameters.get("end_time")

        try:
            end_time = int(datetime.datetime.now().timestamp() * 1000) if end_time is None else int(end_time)
            start_time = int((datetime.datetime.now() - datetime.timedelta(
                days=1)).timestamp() * 1000) if start_time is None else int(start_time)
        except Exception:
            raise OpsException('30002')

        server_num, server_online_time = self.get_server_running_time(start_time, end_time)
        server_ave_online_time = round(server_online_time/server_num, 2)

        terminal_num, terminal_online_time = self.get_terminal_running_time(start_time, end_time)
        terminal_ave_online_time = round(terminal_online_time / terminal_num, 2)

        statistics = [{"name": "server", "description": "服务器设备统计", "data": [server_online_time, server_ave_online_time]},
                      {"name": "terminal", "description": "终端设备统计", "data": [terminal_online_time, terminal_ave_online_time]}]
        parameters['info'] = statistics
        return Response(global_func.get_response(data=parameters))

    @staticmethod
    def get_server_running_time(start_time, end_time):
        """
        查询服务器运行时长  时间单位 分钟
        通过查询 metricbeat 上报的服务 uptime 信息确定服务器运行时长
        uptime 信息5分钟上报一次
        :return: tuple
        """
        dsl_ = {
            "size": 0,
            "query": {
                "bool": {
                    "filter": [
                        {
                            "range": {
                                "@timestamp": {
                                    "gte": "now-1d",
                                    "lte": "now"
                                }
                            }
                        },
                        {
                            "term": {
                                "metricset.module": "system"
                            }
                        },
                        {
                            "term": {
                                "metricset.name": "uptime"
                            }
                        }
                    ]
                }
            },
            "aggs": {
                "devmoid": {
                    "terms": {
                        "field": "beat.eqpid",
                        "size": 10000
                    }
                }
            }
        }
        dsl_['query']['bool']['filter'][0]['range']['@timestamp'] = {"gte": start_time, "lte": end_time}

        index = "metricbeat-*"
        try:
            server_info = es_client.search(index=index, body=dsl_)
        except Exception as err:
            logger.error(err.args)
            raise OpsException('10002')

        total_count = jsonpath.jsonpath(server_info, "$.hits.total")
        total_server_info = jsonpath.jsonpath(server_info, "$.aggregations.devmoid.buckets")

        total_count = 0 if total_count is False else total_count[0]
        total_server_info = [] if total_server_info is False else total_server_info[0]
        total_server_num = len(total_server_info)  # 服务器在线总数量
        total_online_time = total_count * 5  # 服务器在线总时长
        return total_server_num, total_online_time

    @staticmethod
    def get_terminal_running_time(start_time, end_time):
        """
        查询硬终端运行时长 时间单位 分钟
        :return: tuple
        """
        total_terminal_num = 100  # 硬终端在线总数量
        total_online_time = 100 * 24 * 60  # 硬终端在线总时长
        return total_terminal_num, total_online_time


class TerminalMeetingFreq(APIView):
    """
    终端参会次数统计
    user_domain_moid : 用户域过滤暂时无法实现
    """

    def get(self, request, *args, **kwargs):
        parameters = request.query_params.dict()
        start_time = parameters.get("start_time")
        end_time = parameters.get("end_time")
        key = parameters.get("key")
        user_domain_moid = parameters.get("user_domain_moid")
        start = parameters.get("start")
        count = parameters.get("count")

        try:
            start = 0 if start is None else int(start)
            count = 20 if count is None else int(count)
            end_time = int(datetime.datetime.now().timestamp() * 1000) if end_time is None else int(end_time)
            start_time = int((datetime.datetime.now() - datetime.timedelta(
                days=1)).timestamp() * 1000) if start_time is None else int(start_time)
        except Exception:
            raise OpsException('30002')

        total, info_data = self.get_termnal_meeting_times(start_time, end_time, user_domain_moid, key, start, count)
        parameters['info'] = info_data
        parameters['total'] = str(total)
        return Response(global_func.get_response(data=parameters))

    @staticmethod
    def get_termnal_meeting_times(start_time, end_time, user_domain_moid, key, start, count):
        """
        查询终端入会频率
        通过查询 EV_MCU_MT_ADD 确定终端入会频率
        :return: tuple
        """
        dsl_ = {
            "size": 0,
            "query": {
                "bool": {
                    "filter": [
                        {
                            "term": {
                                "source.eventid.keyword": "EV_MCU_MT_ADD"
                            }
                        }
                    ]
                }
            },
            "aggs": {
                "mtaccount": {
                    "terms": {
                        "field": "source.mtinfo.mtaccount.keyword",
                        "size": 10000,
                        "order": {
                            "confcount": "desc"
                        }
                    },
                    "aggs": {
                        "confcount": {
                            "cardinality": {
                                "field": "source.mtinfo.confe164.keyword"
                            }
                        },
                        "top1": {
                            "top_hits": {
                                "size": 1,
                                "_source": {
                                    "includes": "source.mtinfo.mtname"
                                }
                            }
                        }
                    }
                }
            }
        }
        dsl_['query']['bool']['filter'].append({"range": {"@timestamp": {"gte": start_time, "lte": end_time}}})
        if key is not None:
            dsl_['query']['bool']['filter'].append(
                {"wildcard": {"source.mtinfo.mtname.keyword": {"value": "*{}*".format(key)}}})

        index = "platform-nmscollector-*cmu*"
        try:
            info = es_client.search(index=index, body=dsl_)
        except Exception as err:
            logger.error(err.args)
            raise OpsException('10002')

        # keys = ['data', 'description', 'name']
        # description = "终端参会次数"
        # name = "terminal_meeting_freq"

        agg_data = jsonpath.jsonpath(info, "$.aggregations.mtaccount.buckets")[0]
        total = len(agg_data)
        use_data = agg_data[start: start+count]
        if len(use_data) == 0:
            return total, []

        meeting_times = jsonpath.jsonpath(use_data, "$.[*].confcount.value")
        meeting_mtname = jsonpath.jsonpath(use_data, "$.[*].top1.hits.hits..mtname")
        if meeting_times is False or meeting_mtname is False:
            return total, []
        data = [list(x) for x in zip(meeting_mtname, meeting_times)]
        return total, data


class TerminalMeetingFreqExport(APIView):
    """
    导出终端参会次数统计
    """

    def get(self, request, *args, **kwargs):

        response = TerminalMeetingFreq().get(request=request, **kwargs)
        response_stat = response.data["success"]
        if response_stat == 0:
            # 读数据失败
            return response
        response_data = response.data['data']['info']   # list
        if len(response_data) == 0:
            # 数据为空
            return Response(global_func.get_response(0, error_code=420, error_msg="数据为空"))
        else:
            # 数据不为空
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=terminal_meeting_frequence.csv'
            response.write(codecs.BOM_UTF8)
            writer = csv.writer(response)

            keys = ["终端名称", "参会次数"]
            writer.writerow([str(x) for x in keys])

            for item in response_data:
                writer.writerow([str(x) for x in item])
            return response


class TerminalMeetingTime(APIView):
    """
    终端参会时长统计
    暂无法实现
    user_domain_moid : 用户域过滤暂时无法实现
    """

    def get(self, request, *args, **kwargs):
        parameters = request.query_params.dict()
        start_time = parameters.get("start_time")
        end_time = parameters.get("end_time")
        key = parameters.get("key")
        user_domain_moid = parameters.get("user_domain_moid")
        start = parameters.get("start", 0)
        count = parameters.get("count", 20)

        try:
            start = 0 if start is None else int(start)
            count = 20 if count is None else int(count)
            end_time = int(datetime.datetime.now().timestamp() * 1000) if end_time is None else int(end_time)
            start_time = int((datetime.datetime.now() - datetime.timedelta(days=1)).timestamp() * 1000) if start_time is None else int(start_time)
        except Exception:
            raise OpsException('30002')

        total, info_data = self.get_termnal_meeting_time(start_time, end_time, user_domain_moid, key, start, count)
        parameters['info'] = info_data
        parameters['total'] = str(total)
        return Response(global_func.get_response(data=parameters))

    @staticmethod
    def get_termnal_meeting_time(start_time, end_time, user_domain_moid, key, start, count):
        """
        查询终端入会时长
        :return: tuple
        """
        # keys = ['data', 'description', 'name']
        # description = "终端参会时长"
        # name = "terminal_meeting_time"

        data = []
        total = 0

        return total, data


class TerminalMeetingTimeExport(APIView):
    """
    导出终端参会时长统计
    """

    def get(self, request, *args, **kwargs):

        response = TerminalMeetingTime().get(request=request, **kwargs)
        response_stat = response.data["success"]
        if response_stat == 0:
            # 读数据失败
            return response
        response_data = response.data['data']['info']   # list
        if len(response_data) == 0:
            # 数据为空
            return Response(global_func.get_response(0, error_code=420, error_msg="数据为空"))
        else:
            # 数据不为空
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=terminal_meeting_time.csv'
            response.write(codecs.BOM_UTF8)
            writer = csv.writer(response)

            keys = ["终端名称", "参会时长"]
            writer.writerow([str(x) for x in keys])

            for item in response_data:
                writer.writerow([str(x) for x in item])
            return response


class LaborTime(APIView):
    """
    节约工时统计
    暂无法实现
    """

    def get(self, request, *args, **kwargs):
        parameters = request.query_params.dict()
        last_days = parameters.get("last_days", 7)

        info_data = self.get_labor_time(last_days)
        parameters['info'] = info_data
        return Response(global_func.get_response(data=parameters))

    @staticmethod
    def get_labor_time(last_days):
        """
        查询节约工时
        :return: list
        """
        # keys = ['data', 'description', 'name']
        # description = "工时统计"
        # name = "labor_time"

        data = []

        return data


class Position(KedaWarningBaseAPIView, ListCreateAPIView, MultiDeleteAPIView):
    queryset = PositionModel.objects.all()
    serializer_class = PositionSerializers
    lookup_request_data = 'ids'


class PositionDetail(KedaWarningBaseAPIView, RetrieveUpdateDestroyAPIView):
    queryset = PositionModel.objects.all()
    serializer_class = PositionSerializers
