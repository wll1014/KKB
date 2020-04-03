#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

import os
import logging
import json
import time
import datetime
import math
import copy

import jsonpath
from django.utils import timezone
from django.db import connections

from ops_statistics.dsl import es_ql
from platmonitor.dsl import es_query
from common.my_elastic import es_client, ESIndex
from common.my_redis import redis_client
from common.global_func import get_now_near_30min, get_timestamp_near_30min, get_timestamp_near_15min, \
    get_now_near_15min
from common.my_exception import OpsException
from ops.settings import BASE_DIR

logger = logging.getLogger('ops.' + __name__)


def get_user_domain_name():
    # 获取用户域moid和用户域名称
    try:
        with connections['movision'].cursor() as cursor:
            sql = '''
            SELECT user_domain_moid,user_domain_name FROM user_domain;
            '''
            params = []
            cursor.execute(sql, params)
            fetchall = cursor.fetchall()
        user_domain_dic = {}
        for one in fetchall:
            user_domain_dic[one[0]] = one[1]
    except Exception as e:
        err = str(e)
        logger.error(err)
        user_domain_dic = {}

    return user_domain_dic


def get_now_on_going_conf_info(request, deadline=None):
    '''
    获取当前会议列表的会议号、终端数量
    :param deadline: 获取截止time的最新状态
    :return: 当前会议列表的会议号、终端数量 [{"confE164":"4440011","mtnum":"0"}]
    '''
    dsl = copy.deepcopy(es_ql.now_conf_statistics)
    if deadline:
        # 获取time之前的数据,优化取值时间区间
        dsl['dsl']['query']['bool'].update(
            {'filter': {'range': {'@timestamp': {'lte': deadline, 'gte': int(deadline) - 15 * 60 * 1000}}}}
        )
    else:
        dsl['dsl']['query']['bool'].update(
            {'filter': {'range': {'@timestamp': {'lte': 'now', 'gte': 'now-15m/m'}}}}
        )
    dsls = [dsl]
    dsls = get_filter_dsl(request, dsls, excludes=['start_time', 'end_time', 'interval'], from_mq=True)
    m_body = es_client.get_index_header_m_body(*dsls)
    logger.debug(m_body)
    try:
        conf_response = es_client.msearch(m_body)['responses'][0]
    except Exception as e:
        err = str(e)
        logger.error(err)
        conf_response = {}

    confdatainfo = []
    if conf_response:
        confdatainfo_jsonobj = jsonpath.jsonpath(conf_response, '$..confdatainfo')
        if confdatainfo_jsonobj:
            for confdatainfo_bucket in confdatainfo_jsonobj:
                confdatainfo += confdatainfo_bucket

    return confdatainfo


def get_time_aggs_conf_info(request):
    '''
    获取正在召开多点会议数量的时间聚合结果
    :param request: Django请求对象，用于获取传参platform_moid,room_moid,start_time,end_time,interval
    :return: 正在召开多点会议数量的时间聚合结果
    '''
    dsl = copy.deepcopy(es_ql.conf_statistics)
    dsls = [dsl]
    dsls = get_filter_dsl(request, dsls, from_mq=True)
    m_body = es_client.get_index_header_m_body(*dsls)
    logger.debug(m_body)
    try:
        conf_response = es_client.msearch(m_body)['responses'][0]
    except Exception as e:
        err = str(e)
        logger.error(err)
        conf_response = {}
    conf_info_data = []
    last_confdatainfo_length = 0
    if conf_response:
        conf_timestamp_buckets = jsonpath.jsonpath(conf_response, '$..aggregations.time.buckets')
        if conf_timestamp_buckets:
            conf_timestamp_buckets = conf_timestamp_buckets[0]
            for index, bucket in enumerate(conf_timestamp_buckets):
                if index == 0:
                    continue
                timestamp = jsonpath.jsonpath(bucket, '$.key')[0]
                confdatainfo_length = jsonpath.jsonpath(bucket, '$..value')
                if index >= len(conf_timestamp_buckets) - 2:
                    if index == len(conf_timestamp_buckets) - 2:
                        last_confdatainfo_length = jsonpath.jsonpath(bucket, '$..value')
                    if index == len(conf_timestamp_buckets) - 1 and len(
                            confdatainfo_length if confdatainfo_length else []) != last_confdatainfo_length:
                        logger.debug('重用倒数第二份数据')
                        confdatainfo_length = last_confdatainfo_length

                conf_info_data.append([timestamp, int(sum(confdatainfo_length)) if confdatainfo_length else None])

    return conf_info_data


def get_time_aggs_p2p_conf_info(request, need_total=False):
    '''
    获取正在召开点对点会议数量的时间聚合结果
    :param request: Django请求对象，用于获取传参platform_moid,room_moid,start_time,end_time,interval
    :return: 正在召开点对点会议数量的时间聚合结果
    '''
    server_type = request.query_params.get('server_type', '0')
    dsl = copy.deepcopy(es_ql.p2p_conf_statistics)
    # dsl['dsl']['query']['bool']['should'][1]['bool']['must'].append(
    #     {
    #         "match": {
    #             "source.ap_info.server_type": server_type
    #         }
    #     }
    # )
    dsls = [dsl]
    dsls = get_filter_dsl(request, dsls)
    m_body = es_client.get_index_header_m_body(*dsls)
    logger.debug(m_body)
    try:
        p2p_response = es_client.msearch(m_body)['responses'][0]
    except Exception as e:
        err = str(e)
        logger.error(err)
        p2p_response = {}

    p2p_info_data = []
    # 倒数第二个数据的 桶大小
    last_but_one_bucket_length = 0
    last_p2p_used = []
    last_p2p_total = []
    if p2p_response:
        p2p_timestamp_buckets = jsonpath.jsonpath(p2p_response, '$..aggregations.time.buckets')
        if p2p_timestamp_buckets:
            p2p_timestamp_buckets = p2p_timestamp_buckets[0]
            for index, bucket in enumerate(p2p_timestamp_buckets):
                if index == 0:
                    continue
                timestamp = jsonpath.jsonpath(bucket, '$.key')[0]
                p2p_used = jsonpath.jsonpath(bucket, '$..confmtcount.value')
                p2p_total = jsonpath.jsonpath(bucket, '$..ap_info.total')

                if index >= len(p2p_timestamp_buckets) - 2:
                    # 最后两个桶
                    logger.debug(bucket)
                    logger.debug(len(bucket.get('pas').get('buckets')))
                    if index == len(p2p_timestamp_buckets) - 2:
                        # 倒数第二个桶
                        last_but_one_bucket_length = len(p2p_used) if p2p_used else 0
                        logger.debug(last_but_one_bucket_length)
                        last_p2p_used = jsonpath.jsonpath(bucket, '$..confmtcount.value')
                        last_p2p_total = jsonpath.jsonpath(bucket, '$..ap_info.total')

                    if index == len(p2p_timestamp_buckets) - 1 and len(
                            bucket.get('pas').get('buckets')) != last_but_one_bucket_length:
                        # 倒数第一个桶
                        logger.debug('重用倒数第二份数据')
                        p2p_used = last_p2p_used
                        p2p_total = last_p2p_total

                p2p_used = (sum(p2p_used) / 2) if p2p_used else None
                p2p_total = (sum(p2p_total) / 2) if p2p_total else None
                if need_total:
                    # 需要返回ap计算的p2p会议总数
                    p2p_info_data.append([timestamp, p2p_used, p2p_total])
                else:
                    p2p_info_data.append([timestamp, p2p_used])

    return p2p_info_data


def get_time_aggs_terminal_online_in_meeting_info(request):
    '''
    终端在线、与会数量
    :param request:
    :return:
    '''
    dsl = copy.deepcopy(es_ql.terminals_statistics)
    dsls = [dsl]
    dsls = get_filter_dsl(request, dsls)
    m_body = es_client.get_index_header_m_body(*dsls)
    logger.debug(m_body)
    try:
        terminal_online_in_meeting_response = es_client.msearch(m_body)['responses'][0]
    except Exception as e:
        err = str(e)
        logger.error(err)
        terminal_online_in_meeting_response = {}

    terminal_curonline_count_data = []
    terminal_callingcount_count_data = []

    if terminal_online_in_meeting_response:
        time_buckets = jsonpath.jsonpath(terminal_online_in_meeting_response, '$..aggregations.time.buckets')[0]
        for time_bucket in time_buckets:
            timestamp = jsonpath.jsonpath(time_bucket, '$.key')[0]
            # 在线终端
            curonline_count = jsonpath.jsonpath(time_bucket, '$..curonlinecount.value')
            curonline_count = sum(curonline_count) if curonline_count else None
            # 与会终端
            callingcount_count = jsonpath.jsonpath(time_bucket, '$..callingcount.value')
            callingcount_count = sum(callingcount_count) if callingcount_count else None
            terminal_curonline_count_data.append([timestamp, curonline_count])
            terminal_callingcount_count_data.append([timestamp, callingcount_count])

    return terminal_curonline_count_data, terminal_callingcount_count_data


def get_time_aggs_terminal_calling_info(request):
    '''

    :param request:
    :return:
    '''
    dsl = copy.deepcopy(es_ql.calling_terminal)
    dsls = [dsl]
    dsls = get_filter_dsl(request, dsls)
    m_body = es_client.get_index_header_m_body(*dsls)
    logger.debug(m_body)
    try:
        calling_terminal_response = es_client.msearch(m_body)['responses'][0]
    except Exception as e:
        err = str(e)
        logger.error(err)
        calling_terminal_response = {}

    calling_terminal_data = []
    # 倒数第二个 桶大小
    last_but_one_bucket_length = 0
    last_callingcount = []
    if calling_terminal_response:
        time_buckets = jsonpath.jsonpath(calling_terminal_response, '$..aggregations.time.buckets')
        if time_buckets:
            time_buckets = time_buckets[0]
            for index, time_bucket in enumerate(time_buckets):
                if index == 0:
                    continue
                timestamp = jsonpath.jsonpath(time_bucket, '$.key')[0]
                callingcount = jsonpath.jsonpath(time_bucket, '$..callingcount.value')

                if index >= len(time_buckets) - 2:
                    # 最后两个桶
                    if index == len(time_buckets) - 2:
                        # 倒数第二个桶
                        last_callingcount = jsonpath.jsonpath(time_bucket, '$..callingcount.value')
                        last_but_one_bucket_length = len(last_callingcount) if last_callingcount else 0
                        logger.debug('last_but_one_bucket_length: %s' % last_but_one_bucket_length)
                    if index == len(time_buckets) - 1 and len(
                            callingcount if callingcount else []) != last_but_one_bucket_length:
                        # 倒数第一个桶
                        logger.debug('重用倒数第二份数据')
                        callingcount = last_callingcount if last_callingcount else []

                callingcount = sum(callingcount) if callingcount else None
                calling_terminal_data.append([timestamp, callingcount])

    return calling_terminal_data


def get_time_aggs_terminal_online_info(request):
    '''

    :param request:
    :return:
    '''
    dsl = copy.deepcopy(es_ql.curr_terminal)
    dsls = [dsl]
    dsls = get_filter_dsl(request, dsls)
    m_body = es_client.get_index_header_m_body(*dsls)
    logger.debug(m_body)
    try:
        terminal_online_response = es_client.msearch(m_body)['responses'][0]
    except Exception as e:
        err = str(e)
        logger.error(err)
        terminal_online_response = {}

    sip_terminal_online_data = []
    h323_terminal_online_data = []
    # 倒数第二个数据的 桶大小
    last_but_one_bucket_length = 0
    last_sip_count = 0
    last_h323_count = 0
    if terminal_online_response:
        terminal_online_buckets = jsonpath.jsonpath(terminal_online_response, '$..aggregations.time.buckets')
        if terminal_online_buckets:
            terminal_online_buckets = terminal_online_buckets[0]
            for index, bucket in enumerate(terminal_online_buckets):
                # 第一组数据可能不完整（不是全部逻辑服务器上报的数据）
                if index == 0:
                    continue
                timestamp = jsonpath.jsonpath(bucket, '$.key')[0]
                sip_count = jsonpath.jsonpath(bucket, '$..sip.value')
                h323_count = jsonpath.jsonpath(bucket, '$..h323.value')
                # 最后两个桶
                if index >= len(terminal_online_buckets) - 2:
                    if index == len(terminal_online_buckets) - 2:
                        # 倒数第二个桶
                        last_but_one_bucket_length = len(sip_count) if sip_count else 0
                        logger.debug('last_but_one_bucket_length: %s' % last_but_one_bucket_length)
                        last_sip_count = jsonpath.jsonpath(bucket, '$..sip.value')
                        last_h323_count = jsonpath.jsonpath(bucket, '$..h323.value')
                    if index == len(terminal_online_buckets) - 1 and len(
                            sip_count if sip_count else []) != last_but_one_bucket_length:
                        # 倒数第一个桶
                        logger.debug('重用倒数第二份数据')
                        sip_count = last_sip_count
                        h323_count = last_h323_count

                sip_terminal_online_data.append([timestamp, sum(sip_count) if sip_count else 0])
                h323_terminal_online_data.append([timestamp, sum(h323_count) if h323_count else 0])

    return sip_terminal_online_data, h323_terminal_online_data


def get_filter_dsl(request, dsls, excludes=None, includes=None, from_mq=False, delay_filter_time=True):
    '''
    获取添加过滤条件的dsl
    :param delay_filter_time: 是否将使用date_histogram函数的query filter过滤时间向前后延迟一个interval时间，延迟可使时间聚合的数据完整
    :param request: Django请求对象，用于获取通用传参platform_moid,room_moid,start_time,end_time,interval
    :param dsls: dsl列表
    :param excludes: 排除列表
    :param includes: 包含列表
    :param from_mq: dsl是否查询mq的消息，mq消息与nms消息过滤机房的字段不同
    :return: 更新后的dsls
    '''

    # 用于挑选过滤项,只对includes、excludes其中一个生效，优先includes
    filter_items = ('platform_moid', 'room_moid', 'start_time', 'end_time', 'interval')
    filter_list = []
    if includes:
        # 传入indclues
        for include in includes:
            if include in filter_items:
                filter_list.append(include)
    elif excludes:
        # 传入excludes
        filter_list = list(filter_items)
        for exclude in excludes:
            if exclude in filter_items:
                filter_list.remove(exclude)
    else:
        filter_list = list(filter_items)

    platform_moid = request.query_params.get('platform_moid', '')
    room_moid = request.query_params.get('room_moid', '')
    start_time = request.query_params.get('start_time', str(es_client.get_start_time(time.time() * 1000 - 86400000)))
    end_time = request.query_params.get('end_time', str(es_client.get_end_time(time.time() * 1000)))
    interval = request.query_params.get('interval', es_client.get_interval_time(start_time, end_time, point=40))
    if isinstance(interval, str):
        # 间隔时间仅支持ms单位
        if interval.isdigit():
            interval = interval + 'ms'
        if len(interval.split('ms')) != 2 or not interval[0].isdigit():
            # 不是以ms结尾的，按默认间隔时间处理
            interval = es_client.get_interval_time(start_time, end_time, point=40)
    for dsl in dsls:
        if platform_moid and 'platform_moid' in filter_list:
            if dsl['dsl']['query']['bool'].get('must'):
                dsl['dsl']['query']['bool']['must'].append({
                    "match_phrase": {
                        "beat.platform_moid": platform_moid
                    }
                })
            else:
                dsl['dsl']['query']['bool']['must'] = [{
                    "match_phrase": {
                        "beat.platform_moid": platform_moid
                    }
                }]
        if room_moid and 'room_moid' in filter_list:
            if from_mq:
                if dsl['dsl']['query']['bool'].get('must'):
                    dsl['dsl']['query']['bool']['must'].append({
                        "match_phrase": {
                            "source.roommoid": room_moid
                        }
                    })
                else:
                    dsl['dsl']['query']['bool']['must'] = [{
                        "match_phrase": {
                            "source.roommoid": room_moid
                        }
                    }]
            else:
                if dsl['dsl']['query']['bool'].get('must'):
                    dsl['dsl']['query']['bool']['must'].append({
                        "match_phrase": {
                            "beat.roomid": room_moid
                        }
                    })
                else:
                    dsl['dsl']['query']['bool']['must'] = [{
                        "match_phrase": {
                            "beat.roomid": room_moid
                        }
                    }]
        if 'start_time' in filter_list:
            if dsl['dsl']['query']['bool'].get('filter'):
                dsl['dsl']['query']['bool']['filter']['range']['@timestamp']['gte'] = start_time
            if dsl['dsl'].get('aggs') and dsl['dsl']['aggs'].get('time'):
                dsl['dsl']['aggs']['time']['date_histogram']['extended_bounds']['min'] = int(start_time)
                if dsl['dsl']['query']['bool'].get('filter') and delay_filter_time:
                    # 如果为时间曲线，筛选的开始时间向前增加筛选一个间隔时间的长度
                    dsl['dsl']['query']['bool']['filter']['range']['@timestamp']['gte'] = str(
                        int(start_time) - int(interval.split('ms')[0]))
        if 'end_time' in filter_list:
            if dsl['dsl']['query']['bool'].get('filter'):
                dsl['dsl']['query']['bool']['filter']['range']['@timestamp']['lte'] = end_time
            if dsl['dsl'].get('aggs') and dsl['dsl']['aggs'].get('time'):
                dsl['dsl']['aggs']['time']['date_histogram']['extended_bounds']['max'] = int(end_time)
                if dsl['dsl']['query']['bool'].get('filter') and delay_filter_time:
                    # 如果为时间曲线，筛选的结束时间向后增加筛选一个间隔时间的长度
                    dsl['dsl']['query']['bool']['filter']['range']['@timestamp']['lte'] = str(
                        int(end_time) + int(interval.split('ms')[0]))
        if 'interval' in filter_list:
            if dsl['dsl']['aggs'].get('time'):
                dsl['dsl']['aggs']['time']['date_histogram']['interval'] = interval
    try:
        logger.debug(json.dumps(dsls))
    except Exception as e:
        logger.debug(dsls)
        err = str(e)
        logger.error(err)
    return dsls


def get_now_dss_bandwidth_info(request, deadline=None):
    '''

    :param request:
    :param deadline:
    :return:
    '''
    dsl = copy.deepcopy(es_ql.now_bandwidth)
    if deadline:
        min5 = 5 * 60 * 1000
        # 获取time之前的数据
        dsl['dsl']['query']['bool'].update(
            {'filter': {'range': {'@timestamp': {'lte': deadline, 'gte': int(deadline) - min5}}}}
        )
    dsls = [dsl]
    dsls = get_filter_dsl(request, dsls, excludes=['start_time', 'end_time', 'interval'])
    m_body = es_client.get_index_header_m_body(*dsls)
    logger.debug(m_body)

    try:
        dss_bandwidth_response = es_client.msearch(m_body)['responses'][0]
    except Exception as e:
        err = str(e)
        logger.error(err)
        dss_bandwidth_response = {}

    dss_bandwidth_info = {
        'total': 0,
        'used': 0
    }
    if dss_bandwidth_response:
        dss_bandwidth_total = jsonpath.jsonpath(dss_bandwidth_response, '$..bandwidth.total')
        dss_bandwidth_total = sum(dss_bandwidth_total) if isinstance(dss_bandwidth_total, list) else 0
        dss_bandwidth_used = jsonpath.jsonpath(dss_bandwidth_response, '$..bandwidth.used')
        dss_bandwidth_used = sum(dss_bandwidth_used) if isinstance(dss_bandwidth_used, list) else 0

        dss_bandwidth_info['total'] += dss_bandwidth_total
        dss_bandwidth_info['used'] += dss_bandwidth_used

    return dss_bandwidth_info


def get_time_aggs_dss_bandwidth_info(request):
    '''
    获取dss转发带宽的时间聚合结果
    :param request:
    :return: dss转发带宽的时间聚合结果
    '''
    dsl = copy.deepcopy(es_ql.dss_bandwidth)
    dsls = [dsl]
    dsls = get_filter_dsl(request, dsls)
    m_body = es_client.get_index_header_m_body(*dsls)
    logger.debug(m_body)

    try:
        dss_bandwidth_response = es_client.msearch(m_body)['responses'][0]
    except Exception as e:
        err = str(e)
        logger.error(err)
        dss_bandwidth_response = {}

    dss_bandwidth_info_data = []
    if dss_bandwidth_response:
        dss_bandwidth_time_buckets = jsonpath.jsonpath(dss_bandwidth_response, '$..time.buckets')
        if dss_bandwidth_time_buckets:
            dss_bandwidth_time_buckets = dss_bandwidth_time_buckets[0]
            for dss_bandwidth_time_bucket in dss_bandwidth_time_buckets:
                timestamp = jsonpath.jsonpath(dss_bandwidth_time_bucket, '$.key')[0]
                devid_buckets = jsonpath.jsonpath(dss_bandwidth_time_bucket, '$..devid.buckets')[0]
                bandwidth_total = None
                bandwidth_used = None

                bandwidth_total_jsonobj = jsonpath.jsonpath(devid_buckets, '$..bandwidth_total.value')
                bandwidth_used_jsonobj = jsonpath.jsonpath(devid_buckets, '$..bandwidth_used.value')

                if bandwidth_total_jsonobj:
                    bandwidth_total = sum(bandwidth_total_jsonobj)
                if bandwidth_used_jsonobj:
                    bandwidth_used = sum(bandwidth_used_jsonobj)

                dss_bandwidth_info_data.append([timestamp, bandwidth_total, bandwidth_used])

    return dss_bandwidth_info_data


def get_now_release_conf_info(request, deadline=None):
    '''
    获取已结束的会议列表的会议号
    :param deadline: 获取截止time的最新状态
    :return: ["4440011","4440012"]
    '''
    dsl = copy.deepcopy(es_ql.now_release_conf_statistics)
    if deadline:
        # 获取time之前的数据
        dsl['dsl']['query']['bool'].update(
            {'filter': {'range': {'@timestamp': {'lte': deadline}}}}
        )
    dsls = [dsl]
    dsls = get_filter_dsl(request, dsls, excludes=['start_time', 'end_time', 'interval'])
    m_body = es_client.get_index_header_m_body(*dsls)
    logger.debug(m_body)

    try:
        release_conf_response = es_client.msearch(m_body)['responses'][0]
    except Exception as e:
        err = str(e)
        logger.error(err)
        release_conf_response = {}

    release_conf_e164_list = []
    if release_conf_response:
        release_conf_jsonobj = jsonpath.jsonpath(release_conf_response, '$..confe164.buckets')
        if release_conf_jsonobj:
            for buckets in release_conf_jsonobj:
                try:
                    e164 = buckets[0].get('key')
                    release_conf_e164_list.append(e164)
                except Exception as e:
                    err = str(e)
                    logger.warning(err)
    return release_conf_e164_list


def get_all_release_conf_count(request, deadline=None):
    '''
    获取已结束会议的个数
    :param request:
    :param deadline:
    :return:
    '''
    conf_count = 0
    dsl = copy.deepcopy(es_ql.all_release_conf_count)
    if deadline:
        # 获取time之前的数据
        dsl['dsl']['query']['bool'].update(
            {'filter': {'range': {'@timestamp': {'lte': deadline}}}}
        )
    dsls = [dsl]
    dsls = get_filter_dsl(request, dsls, excludes=['start_time', 'end_time', 'interval'])
    m_body = es_client.get_index_header_m_body(*dsls)
    logger.debug(m_body)

    try:
        release_conf_response = es_client.msearch(m_body)['responses'][0]
    except Exception as e:
        err = str(e)
        logger.error(err)
        release_conf_response = {}

    if release_conf_response:
        conf_count = jsonpath.jsonpath(release_conf_response, '$.aggregations.conf_count.value')
        if conf_count:
            conf_count = conf_count[0]

    return conf_count


def get_conf_type(confe164_list):
    '''

    :param confe164_list:
    :return:
    '''
    # 构建查询语句中 e164 “或”关系的字符串
    if not isinstance(confe164_list, list):
        confe164_list = []
    confe164_list_str = ' || '.join(confe164_list)

    dsl = {
        'index': ESIndex.NMSCmuIndex.value,
        'dsl': {
            "size": 0,
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "source.eventid": "EV_MCU_CONF_CREATE"
                            }
                        },
                        {
                            "match": {
                                "source.confinfo.confe164": confe164_list_str
                            }
                        }
                    ]
                }
            },
            "aggs": {
                "confe164": {
                    "terms": {
                        "field": "source.confinfo.confe164.keyword",
                        "size": 10000
                    },
                    "aggs": {
                        "top": {
                            "top_hits": {
                                "sort": {
                                    "@timestamp": {
                                        "order": "desc"
                                    }
                                },
                                "size": 1,
                                "_source": [
                                    "source.confinfo.conftype"
                                ]
                            }
                        }
                    }
                }
            }
        }
    }
    dsls = [dsl]
    m_body = es_client.get_index_header_m_body(*dsls)
    logger.debug(m_body)
    try:
        conf_type_response = es_client.msearch(m_body)['responses'][0]
    except Exception as e:
        err = str(e)
        logger.error(err)
        conf_type_response = {}

    # 0：传统会议，1：端口会议
    conf_type_dict = {'0': [], '1': []}
    if conf_type_response:
        confe164_buckets = jsonpath.jsonpath(conf_type_response, '$..confe164.buckets')
        if confe164_buckets:
            confe164_buckets = confe164_buckets[0]

            for bucket in confe164_buckets:
                e164 = bucket.get('key')
                conftype_jsonobj = jsonpath.jsonpath(bucket, '$..conftype')
                if conftype_jsonobj:
                    conftype = conftype_jsonobj[0]
                    if conftype == 0:
                        # es查询结果为去重的会议号结果，在 confe164_list 获得原始数量，加入列表
                        conf_type_dict['0'].extend([e164] * confe164_list.count(e164))
                    elif conftype == 1:
                        conf_type_dict['1'].extend([e164] * confe164_list.count(e164))
            for confe164 in confe164_list:
                if confe164 not in conf_type_dict['0'] + conf_type_dict['1']:
                    conf_type_dict['0'].append(confe164)

    return conf_type_dict


def get_all_create_conf_time_info(request, deadline=None):
    '''
    获取所有会议的开始时间
    :param request:
    :param deadline:
    :return: 会议id对应的会议e164号码和会议开始时间的时间戳
    {"21": {"e164": "4440011", "timestamp": 1565755336308}, "23": {"e164": "4440012", "timestamp": 1565755358981}}
    '''
    dsl = copy.deepcopy(es_ql.all_create_conf_time_statistics)
    if deadline:
        # 获取time之前的数据
        dsl['dsl']['query']['bool'].update(
            {'filter': {'range': {'@timestamp': {'lte': deadline}}}}
        )
        dsls = [dsl]
        dsls = get_filter_dsl(request, dsls, excludes=['start_time', 'end_time', 'interval', 'room_moid'])
    else:
        dsls = [dsl]
        dsls = get_filter_dsl(request, dsls, excludes=['room_moid'])
    m_body = es_client.get_index_header_m_body(*dsls)
    logger.debug(m_body)

    try:
        create_conf_time_response = es_client.msearch(m_body)['responses'][0]
    except Exception as e:
        err = str(e)
        logger.error(err)
        create_conf_time_response = {}

    create_conf_time_dict = {}
    if create_conf_time_response:
        meetingid_buckets_jsonobj = jsonpath.jsonpath(create_conf_time_response, '$..meetingID.buckets')
        if meetingid_buckets_jsonobj:
            meetingid_buckets = meetingid_buckets_jsonobj[0]
            for meetingid_bucket in meetingid_buckets:
                meetingid = meetingid_bucket.get('key')
                e164 = ''
                timestamp = 0
                e164_buckets_jsonobj = jsonpath.jsonpath(meetingid_bucket, '$..confE164.buckets')
                if e164_buckets_jsonobj:
                    e164_buckets = e164_buckets_jsonobj[0]
                    e164 = e164_buckets[0].get('key')
                timestamp_buckets_jsonobj = jsonpath.jsonpath(meetingid_bucket, '$..timestamp.buckets')
                if timestamp_buckets_jsonobj:
                    timestamp_buckets = timestamp_buckets_jsonobj[0]
                    timestamp = timestamp_buckets[0].get('key')
                create_conf_time_dict[meetingid] = {'e164': e164, 'timestamp': timestamp}

    return create_conf_time_dict


def get_all_conf_time_info(request, deadline=None):
    '''
    获取 get_all_create_conf_time_info 函数取到创建会议的会议时长
    :param request:
    :param deadline:
    :return:
    '''
    room_moid = request.query_params.get('room_moid', '')

    create_conf_time_info = get_all_create_conf_time_info(request, deadline)
    meetingid_list = create_conf_time_info.keys()

    if room_moid:
        meetingids = get_now_in_room_meetingid(request)
        meetingid_set = set(meetingids) & set(meetingid_list)
    else:
        meetingid_set = set(meetingid_list)

    # 构建查询语句中 meetingID “或”关系的字符串
    meetingid_str = ' || '.join(meetingid_set)

    dsl = {
        'index': ESIndex.MQWatcherIndex.value,
        'dsl': {
            "size": 0,
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "source.type": "MAU_CM_RELEASECONF_NTF"
                            }
                        },
                        {
                            "match": {
                                "source.meetingID": meetingid_str
                            }
                        }
                    ]
                }
            },
            "aggs": {
                "meetingID": {
                    "terms": {
                        "field": "source.meetingID.keyword",
                        "size": 100000
                    },
                    "aggs": {
                        "timestamp": {
                            "max": {
                                "field": "@timestamp"
                            }
                        },
                        "confE164": {
                            "terms": {
                                "field": "source.confE164.keyword"
                            }
                        }
                    }
                }
            }
        }
    }
    if deadline:
        # 获取time之前的数据
        dsl['dsl']['query']['bool'].update(
            {'filter': {'range': {'@timestamp': {'lte': deadline}}}}
        )
    dsls = [dsl]
    dsls = get_filter_dsl(request, dsls, excludes=['start_time', 'end_time', 'interval', 'room_moid'])
    m_body = es_client.get_index_header_m_body(*dsls)
    logger.debug(m_body)

    try:
        release_conf_time_response = es_client.msearch(m_body)['responses'][0]
    except Exception as e:
        err = str(e)
        logger.error(err)
        release_conf_time_response = {}

    release_conf_time_dict = {}
    if release_conf_time_response:
        meetingid_buckets_jsonobj = jsonpath.jsonpath(release_conf_time_response, '$..meetingID.buckets')
        if meetingid_buckets_jsonobj:
            meetingid_buckets = meetingid_buckets_jsonobj[0]
            for meetingid_bucket in meetingid_buckets:
                meetingid = meetingid_bucket.get('key')
                e164 = ''
                timestamp = 0
                e164_buckets_jsonobj = jsonpath.jsonpath(meetingid_bucket, '$..confE164.buckets')
                if e164_buckets_jsonobj:
                    e164_buckets = e164_buckets_jsonobj[0]
                    e164 = e164_buckets[0].get('key')
                timestamp_buckets_jsonobj = jsonpath.jsonpath(meetingid_bucket, '$..timestamp.value')
                if timestamp_buckets_jsonobj:
                    timestamp = timestamp_buckets_jsonobj[0]
                release_conf_time_dict[meetingid] = {'e164': e164, 'timestamp': timestamp}

    conf_time_l = []
    logger.info(release_conf_time_dict)
    for create_conf_meetingid in meetingid_set:
        create_conf_time = create_conf_time_info[create_conf_meetingid].get('timestamp')
        if create_conf_meetingid in release_conf_time_dict:
            # 已结束会议
            release_conf_time = release_conf_time_dict[create_conf_meetingid].get('timestamp')
        else:
            # 未结束会议
            release_conf_time = time.time() * 1000
        conf_time = release_conf_time - create_conf_time
        conf_time_l.append(conf_time)

    return conf_time_l


def get_now_resource_info(request, deadline=None):
    '''
    {
        "mooooooo-oooo-oooo-oooo-defaultmachi": {
            "remainder_port": 14,
            "machine_room_moid": "mooooooo-oooo-oooo-oooo-defaultmachi",
            "remainder_tra": 2,
            "total_port": 24,
            "used_tra": 1
        },
        "mooooooo-oooo-oooo-oooo-defaultmach2": {
            "remainder_port": 1,
            "machine_room_moid": "mooooooo-oooo-oooo-oooo-defaultmach2",
            "remainder_tra": 2,
            "total_port": 12,
            "used_tra": 1
        }
    }
    :param request:
    :param deadline:
    :return:
    '''
    platform_moid = request.query_params.get('platform_moid', '')
    room_moid = request.query_params.get('room_moid', '')
    dsl = copy.deepcopy(es_ql.now_mediamaster_resource)
    if deadline:
        # 获取time之前的数据
        dsl['dsl']['query']['bool'].update(
            {'filter': {'range': {'@timestamp': {'lte': deadline}}}}
        )
    dsls = [dsl]
    should1 = {
        "bool": {
            "must": [
                {
                    "match": {
                        "source.eventid": "EV_MACHINE_ROOM_RES_INFO"
                    }
                }
            ],
            "boost": 1
        }
    }

    should2 = {
        "bool": {
            "must": [
                {
                    "match": {
                        "source.type": "MCU_MAU_CONFLIST_NTF"
                    }
                }
            ],
            "boost": 2
        }
    }
    if platform_moid:
        should1['bool']['must'].append(
            {
                "match_phrase": {
                    "beat.platform_moid": platform_moid
                }
            }
        )
        should2['bool']['must'].append(
            {
                "match_phrase": {
                    "beat.platform_moid": platform_moid
                }
            }
        )

    if room_moid:
        should1['bool']['must'].append(
            {
                "match_phrase": {
                    "source.roomid": room_moid
                }
            }
        )
        should2['bool']['must'].append(
            {
                "match_phrase": {
                    "source.roommoid": room_moid
                }
            }
        )
    dsl['dsl']['query']['bool']['should'].append(should1)
    dsl['dsl']['query']['bool']['should'].append(should2)

    m_body = es_client.get_index_header_m_body(*dsls)
    logger.debug(m_body)

    try:
        resource_response = es_client.msearch(m_body)['responses'][0]
    except Exception as e:
        err = str(e)
        logger.error(err)
        resource_response = {}

    resource_info = {}
    used_tra = 0
    if resource_response:
        roomid_buckets = jsonpath.jsonpath(resource_response, '$..roomid.buckets')
        if roomid_buckets:
            roomid_buckets = roomid_buckets[0]
            for roomid_bucket in roomid_buckets:
                room_res_info = jsonpath.jsonpath(roomid_bucket, '$..room_res_info')
                if room_res_info:
                    room_res_info = room_res_info[0]
                    machine_room_moid = room_res_info.get('machine_room_moid')
                    resource_info[machine_room_moid] = room_res_info
                    cmu_top_buckets = jsonpath.jsonpath(resource_response, '$..cmumoid.buckets')
                    if cmu_top_buckets:
                        cmu_top_buckets = cmu_top_buckets[0]
                        for cmu_top_bucket in cmu_top_buckets:
                            roommoid = jsonpath.jsonpath(cmu_top_bucket, '$..roommoid')
                            if roommoid:
                                roommoid = roommoid[0]
                                confE164_list = jsonpath.jsonpath(cmu_top_bucket, '$..confE164')
                                used_tra += len(get_conf_type(confE164_list).get('0'))
                                if resource_info.get(roommoid):
                                    resource_info[roommoid]['used_tra'] = used_tra

    return resource_info


def get_avg(l):
    '''
    传入数字组成的列表，返回平均数
    :param l: 数字组成的列表
    :return: 平均数
    '''
    try:
        return sum(l) / len(l)
    except Exception as e:
        err = str(e)
        logger.error(err)
    return 0.0


def get_time_aggs_resource_info(request):
    start_time = request.query_params.get('start_time', str(es_client.get_start_time(time.time() * 1000 - 86400000)))
    platform_moid = request.query_params.get('platform_moid', '')
    room_moid = request.query_params.get('room_moid', '')
    # 获取在start_time之前的最新数据
    now_timestamp = datetime.datetime.now().timestamp() * 1000
    resource_info = get_now_resource_info(request, deadline=start_time)

    # 上一次端口总数
    last_total_port = get_avg(jsonpath.jsonpath(resource_info, '$..total_port'))
    # 上一次端口剩余数
    last_free_port = get_avg(jsonpath.jsonpath(resource_info, '$..remainder_port'))

    # 上一次传统会议已召开数
    last_used_tra = len(get_now_on_going_conf_info(request, deadline=start_time))
    # 上一次传统会议剩余数
    last_free_tra = get_avg(jsonpath.jsonpath(resource_info, '$..remainder_tra'))

    dsl = copy.deepcopy(es_ql.mediamaster_resource)

    should1 = {
        "bool": {
            "must": [
                {
                    "match": {
                        "source.eventid": "EV_MACHINE_ROOM_RES_INFO"
                    }
                }
            ],
            "boost": 1
        }
    }

    should2 = {
        "bool": {
            "must": [
                {
                    "match": {
                        "source.type": "MCU_MAU_CONFLIST_NTF"
                    }
                },

            ],
            "boost": 2
        }
    }

    if platform_moid:
        should1['bool']['must'].append(
            {
                "match_phrase": {
                    "beat.platform_moid": platform_moid
                }
            }
        )
        should2['bool']['must'].append(
            {
                "match_phrase": {
                    "beat.platform_moid": platform_moid
                }
            }
        )

    if room_moid:
        should1['bool']['must'].append(
            {
                "match_phrase": {
                    "source.roomid": room_moid
                }
            }
        )
        should2['bool']['must'].append(
            {
                "match_phrase": {
                    "source.roommoid": room_moid
                }
            }
        )
    dsl['dsl']['query']['bool']['should'].append(should1)
    dsl['dsl']['query']['bool']['should'].append(should2)
    dsls = [dsl]
    dsls = get_filter_dsl(request, dsls, excludes=['platform_moid', 'room_moid'])

    m_body = es_client.get_index_header_m_body(*dsls)
    logger.debug(m_body)
    try:
        resource_response = es_client.msearch(m_body)['responses'][0]
    except Exception as e:
        err = str(e)
        logger.error(err)
        resource_response = {}

    port_resource_data = []
    conf_resource_data = []
    if resource_response:
        time_buckets = jsonpath.jsonpath(resource_response, '$..time.buckets')
        if time_buckets:
            time_buckets = time_buckets[0]
            all_confE164_list = jsonpath.jsonpath(time_buckets, '$..confE164')
            all_confE164_list = list(set(all_confE164_list)) if all_confE164_list else []
            # 根据所有的e164号码，查询传统会议e164号码列表
            all_tra_list = get_conf_type(all_confE164_list).get('0')
            for time_bucket in time_buckets:
                timestamp = time_bucket.get('key')
                if jsonpath.jsonpath(time_bucket, '$..source.room_res_info'):
                    room_res_info = jsonpath.jsonpath(time_bucket, '$..source.room_res_info')[0]
                    last_total_port = room_res_info.get('total_port')
                    last_free_port = room_res_info.get('remainder_port')
                    last_free_tra = room_res_info.get('remainder_tra')
                if jsonpath.jsonpath(time_bucket, '$..confE164'):
                    confE164_list = jsonpath.jsonpath(time_bucket, '$..confE164')
                    # 所有传统会议e164号码 和 当前循环中的 e164号码 求交集 则为当前的传统会议
                    last_used_tra = len(set(all_tra_list) & set(confE164_list))
                else:
                    if jsonpath.jsonpath(time_bucket, '$..source.type') and \
                            jsonpath.jsonpath(time_bucket, '$..source.type')[0] == 'MCU_MAU_CONFLIST_NTF':
                        last_used_tra = 0
                    else:
                        last_used_tra = last_used_tra
                if timestamp > now_timestamp:
                    last_free_port = last_total_port
                    last_used_tra = 0
                port_resource_data.append([timestamp, last_total_port, last_total_port - last_free_port])
                conf_resource_data.append([timestamp, last_used_tra + last_free_tra, last_used_tra])

    return port_resource_data, conf_resource_data


def get_now_ap_info(request, deadline=None):
    # 服务器类型，0：非国密， 1：国密
    server_type = request.query_params.get('server_type', '0')
    dsl = copy.deepcopy(es_ql.now_ap)
    dsl['dsl']['query']['bool']['must'].append(
        {
            "match": {
                "source.ap_info.server_type": server_type
            }
        }
    )
    if deadline:
        # 获取time之前的数据
        dsl['dsl']['query']['bool'].update(
            {'filter': {'range': {'@timestamp': {'lte': deadline}}}}
        )
    dsls = [dsl]
    dsls = get_filter_dsl(request, dsls, excludes=['start_time', 'end_time', 'interval'])
    m_body = es_client.get_index_header_m_body(*dsls)
    logger.debug(m_body)
    try:
        ap_response = es_client.msearch(m_body)['responses'][0]
    except Exception as e:
        err = str(e)
        logger.error(err)
        ap_response = {}

    ap_info = {
        'total': 0,
        'used': 0
    }
    if ap_response:
        ap_total = jsonpath.jsonpath(ap_response, '$..ap_info.total')
        ap_used = jsonpath.jsonpath(ap_response, '$..ap_info.used')
        if ap_total:
            ap_info['total'] += sum(ap_total)
        if ap_used:
            ap_info['used'] += sum(ap_used)

    return ap_info


def get_now_p2p_conf_info(request, deadline=None):
    # 拉点对点会议列表后计算 点对点会议数量
    # params = {
    #     'conf_type': 2,
    #     'conf_status': 1,
    #     'start': '0',
    #     'count': '0',
    # }
    # if deadline:
    #     params.update({'start_time': deadline})
    # try:
    #     stat, result = es_query.P2PConfList(**params).get_conference()  # 会议详情列表
    #     logger.info(stat)
    #     logger.info(result)
    # except Exception as err:
    #     logger.error(err)
    # else:
    #     p2p_conf_count = len(result) if stat else 0

    # 点对点会议终端数计算 点对点会议数量
    dsl = copy.deepcopy(es_ql.now_p2p_conf)
    if deadline:
        # 获取time之前的数据
        dsl['dsl']['query']['bool'].update(
            {'filter': {'range': {'@timestamp': {'lte': deadline}}}}
        )
    dsls = [dsl]
    dsls = get_filter_dsl(request, dsls, excludes=['start_time', 'end_time', 'interval'])
    m_body = es_client.get_index_header_m_body(*dsls)
    logger.debug(m_body)
    try:
        p2p_conf_response = es_client.msearch(m_body)['responses'][0]
    except Exception as e:
        err = str(e)
        logger.error(err)
        p2p_conf_response = {}

    confmtcount = 0
    if p2p_conf_response:
        dev_moid_buckets = jsonpath.jsonpath(p2p_conf_response, '$..dev_moid.buckets')
        if dev_moid_buckets:
            dev_moid_buckets = dev_moid_buckets[0]
            for dev_moid_bucket in dev_moid_buckets:
                timestamp = jsonpath.jsonpath(dev_moid_bucket, '$..sort')
                if timestamp:
                    if jsonpath.jsonpath(dev_moid_bucket, '$..confmtcount'):
                        confmtcount += sum(jsonpath.jsonpath(dev_moid_bucket, '$..confmtcount'))
    # confmtcount:点对点会议终端数，一半则为点对点会议数
    p2p_conf_count = confmtcount / 2
    return p2p_conf_count


def get_now_in_meeting_mt_e164():
    '''
    redis中读取正在召开会议的所有终端号码
    :return: 终端号码list
    '''
    script_path = os.path.join(BASE_DIR, 'lua', 'get_conf_mt_e164.lua')
    with open(script_path, 'r', encoding='utf-8')as f:
        script_content = f.read()

    in_meeting_terminals = {}
    try:
        get_conf_mt_e164 = redis_client.register_script(script_content)
        conf_mt_e164_info = get_conf_mt_e164()
        in_meeting_terminals = json.loads(conf_mt_e164_info.decode('utf-8'))
        logger.info(in_meeting_terminals)
    except Exception as e:
        err = str(e)
        logger.error(err)
    return in_meeting_terminals


def get_now_company_conf(request):
    '''
    企业创会数量列表
    :param request:
    :return:
    '''
    room_moid = request.query_params.get('room_moid', '')
    key = request.query_params.get('key', '')
    dsl = copy.deepcopy(es_ql.company_conf_statistics)
    dsls = [dsl]
    dsls = get_filter_dsl(request, dsls, excludes=('room_moid',))

    m_body = es_client.get_index_header_m_body(*dsls)
    logger.debug(m_body)
    try:
        company_conf_response = es_client.msearch(m_body)['responses'][0]
    except Exception as e:
        err = str(e)
        logger.error(err)
        company_conf_response = {}

    company_conf_data_info = []
    company_conf_buckets = jsonpath.jsonpath(company_conf_response, '$..confinfo.buckets')
    if company_conf_buckets:
        company_conf_buckets = company_conf_buckets[0]

        user_domain_dic = get_user_domain_name()
        if room_moid:
            in_room_meetingid = get_now_in_room_meetingid(request)
        else:
            in_room_meetingid = None
        for index, bucket in enumerate(company_conf_buckets):
            user_domain_moid = bucket.get('key')
            user_domain_name = user_domain_dic.get(user_domain_moid) \
                if user_domain_dic.get(user_domain_moid) else '--'
            meetingids = jsonpath.jsonpath(bucket, '$..meetingID..key')
            meetingids = meetingids if meetingids else []
            if in_room_meetingid is None:
                meetingid_set = set(meetingids)
            else:
                # 过滤机房
                # 机房下的meetingid 和 所有meetingid列表求交集
                meetingid_set = set(in_room_meetingid) & set(meetingids)
            logger.debug(meetingids)
            logger.debug(in_room_meetingid)
            logger.debug(meetingid_set)
            if key:
                if key in user_domain_name:
                    data = {
                        'description': user_domain_name,
                        'name': bucket.get('key'),
                        'data': len(meetingid_set)
                    }
                    logger.info(data)
                    if data['data'] > 0:
                        company_conf_data_info.append(data)
            else:
                data = {
                    'description': user_domain_name,
                    'name': bucket.get('key'),
                    'data': len(meetingid_set)
                }
                logger.info(data)
                if data['data'] > 0:
                    company_conf_data_info.append(data)

    return company_conf_data_info


def get_now_create_conf_type(request):
    '''
    获取企业创会方式列表
    :param request:
    :return:
    '''
    key = request.query_params.get('key', '')
    room_moid = request.query_params.get('room_moid', '')

    dsl = copy.deepcopy(es_ql.create_conf_type_num_list)
    dsls = [dsl]
    dsls = get_filter_dsl(request, dsls, excludes=('room_moid',))

    m_body = es_client.get_index_header_m_body(*dsls)
    logger.debug(m_body)
    try:
        create_conf_type_response = es_client.msearch(m_body)['responses'][0]
    except Exception as e:
        err = str(e)
        logger.error(err)
        create_conf_type_response = {}

    create_conf_type_data_info = []
    domain_buckets = jsonpath.jsonpath(create_conf_type_response, '$..domain.buckets')
    if domain_buckets:
        domain_buckets = domain_buckets[0]
        user_domain_dic = get_user_domain_name()

        if room_moid:
            in_room_meetingid = get_now_in_room_meetingid(request)
        else:
            in_room_meetingid = None

        for domain_bucket in domain_buckets:
            user_domain_moid = domain_bucket.get('key')
            # 通过用户域moid获取用户域名称，获取不到则返回 “--”
            user_domain_name = user_domain_dic.get(user_domain_moid) \
                if user_domain_dic.get(user_domain_moid) else '--'

            cmc_create_count = 0
            terminal_create_count = 0

            meetingids = jsonpath.jsonpath(domain_bucket, '$..meetingID.buckets[*].key')
            meetingids = meetingids if meetingids else []
            if in_room_meetingid is None:
                meetingid_set = set(meetingids)
            else:
                # 过滤机房
                # 机房下的meetingid 和 所有meetingid列表求交集
                meetingid_set = set(in_room_meetingid) & set(meetingids)

            meetingID_buckets = jsonpath.jsonpath(domain_bucket, '$..meetingID.buckets')
            meetingID_buckets = meetingID_buckets[0] if meetingID_buckets else []

            for meetingID_bucket in meetingID_buckets:
                if meetingID_bucket.get('key') in meetingid_set:
                    requestorigin_key = jsonpath.jsonpath(meetingID_bucket, '$..requestorigin..key')
                    requestorigin_key = requestorigin_key if requestorigin_key else []
                    cmc_create_count += requestorigin_key.count('1')
                    terminal_create_count += requestorigin_key.count('2')
                    # requestorigin_buckets = jsonpath.jsonpath(domain_bucket, '$..requestorigin.buckets')
            # if requestorigin_buckets:
            #     requestorigin_buckets = requestorigin_buckets[0]
            #     for requestorigin_bucket in requestorigin_buckets:
            #         if requestorigin_bucket.get('key') == '1':
            #             # requestorigin 为1：会控创会
            #             cmc_create_count += requestorigin_bucket.get('doc_count')
            #         if requestorigin_bucket.get('key') == '2':
            #             # requestorigin 为2：终端创会
            #             terminal_create_count += requestorigin_bucket.get('doc_count')

            if key:
                # 过滤条件，搜索用户域名称
                if key in user_domain_name:
                    if cmc_create_count + terminal_create_count > 0:
                        create_conf_type_data_info.append({
                            "description": user_domain_moid,
                            "name": user_domain_name,
                            "data": cmc_create_count,
                            "terminal_data": terminal_create_count
                        })
            else:
                if cmc_create_count + terminal_create_count > 0:
                    create_conf_type_data_info.append({
                        "description": user_domain_moid,
                        "name": user_domain_name,
                        "data": cmc_create_count,
                        "terminal_data": terminal_create_count
                    })

    return create_conf_type_data_info


def get_now_in_room_meetingid(request):
    '''
    获取某机房下的会议meetingid列表
    :param request:
    :return:
    '''
    room_moid = request.query_params.get('room_moid', '')
    start_time = request.query_params.get('start_time', str(es_client.get_start_time(time.time() * 1000 - 86400000)))
    end_time = request.query_params.get('end_time', str(es_client.get_end_time(time.time() * 1000)))
    in_room_conf_meetingid = []
    if room_moid:
        dsl = copy.deepcopy(es_ql.company_conf_room_statistics)
        dsls = [dsl]
        dsls = get_filter_dsl(request, dsls, excludes=('room_moid',))
        if dsl['dsl']['query']['bool'].get('filter'):
            time_of_7_days = 7 * 24 * 60 * 60 * 1000
            dsl['dsl']['query']['bool']['filter']['range']['@timestamp']['gte'] = int(start_time) - time_of_7_days
            dsl['dsl']['query']['bool']['filter']['range']['@timestamp']['lte'] = int(end_time) + time_of_7_days
        dsl['dsl']['query']['bool']['must'].append(
            {
                'match_phrase': {
                    'source.confroommoid': room_moid
                }
            }
        )
        m_body = es_client.get_index_header_m_body(*dsls)
        logger.debug(m_body)
        try:
            room_company_conf_response = es_client.msearch(m_body)['responses'][0]
        except Exception as e:
            err = str(e)
            logger.error(err)
            room_company_conf_response = {}

        if room_company_conf_response:
            in_room_conf_meetingid = jsonpath.jsonpath(room_company_conf_response, '$..meetingID..key')
            in_room_conf_meetingid = in_room_conf_meetingid if in_room_conf_meetingid else []

    return in_room_conf_meetingid


def get_appointment_conf_statistics_every_interval_min(request, interval_minute=15):
    '''
    统计当前时间 到 未来24h的 预约会议开始时间，每30分钟一个值
    :return:
    '''
    start_time = request.query_params.get('start_time', str(es_client.get_start_time(time.time() * 1000)))
    room_moid = request.query_params.get('room_moid', '')
    in_room_all_user_domain = [room_moid]
    if room_moid:
        # 查询机房下的用户域，用于机房过滤条件
        in_room_all_user_domain_sql = '''
        SELECT user_domain_moid FROM user_domain_machine WHERE machine_room_moid=%s
        '''
        params = [room_moid]
        try:
            with connections['movision'].cursor() as cursor:
                cursor.execute(in_room_all_user_domain_sql, params)
                fetchall = cursor.fetchall()
                in_room_all_user_domain = [fetch[0] for fetch in fetchall]
        except Exception as e:
            logger.error(str(e))
        if in_room_all_user_domain:
            room_moid_filter = 'AND company_moid in %s'
        else:
            room_moid_filter = ''
    else:
        room_moid_filter = ''
    appointment_conf_info = []
    appointment_live_conf_info = []
    try:
        appointment_conf_sql = '''
        SELECT COUNT( start_time ) AS num ,time
        FROM
            (
            SELECT  start_time,id,
            DATE_FORMAT(
                concat( date( start_time ), ' ', HOUR ( start_time ), ':', floor( MINUTE ( start_time ) / {interval_minute} ) * {interval_minute} ),
                '%%Y-%%m-%%d %%H:%%i:00'
            )AS time 
        FROM meeting
        WHERE create_type=0 -- 预约会议
        AND state in (1,2) -- 会议状态 1:预约; 2:开始; 3:结束; 4:删除;5:平台占用;6:待审批;7:审批不通过
        AND start_time >= %s 
        AND start_time <= %s -- start_time的未来24小时
        ) a 
        
        LEFT JOIN v_meeting vm ON a.id=vm.meeting_id
        -- LEFT JOIN v_meeting_video_live vmvl ON a.id=vmvl.meeting_id
        -- WHERE vmvl.enable_live!=1
        WHERE 1=1 {room_moid_filter}
        GROUP BY DATE_FORMAT( time, '%%Y-%%m-%%d %%H:%%i:00' )
        ORDER BY time;
        '''.format(interval_minute=interval_minute, room_moid_filter=room_moid_filter)

        appointment_live_conf_sql = '''
        SELECT COUNT( start_time ) AS num ,time
        FROM
            (
            SELECT  start_time,id,
            DATE_FORMAT(
                concat( date( start_time ), ' ', HOUR ( start_time ), ':', floor( MINUTE ( start_time ) / {interval_minute} ) * {interval_minute} ),
                '%%Y-%%m-%%d %%H:%%i:00'
            )AS time 
            FROM meeting 
            WHERE create_type=0 -- 预约会议
            AND state in (1,2) -- 会议状态 1:预约; 2:开始; 3:结束; 4:删除;5:平台占用;6:待审批;7:审批不通过
            AND start_time >= %s 
            AND start_time <= %s -- start_time的未来24小时
        ) a 
        
        LEFT JOIN v_meeting_video_live vmvl ON a.id=vmvl.meeting_id
        LEFT JOIN v_meeting vm ON a.id=vm.meeting_id
        WHERE vmvl.enable_live=1 {room_moid_filter}
        GROUP BY DATE_FORMAT( time, '%%Y-%%m-%%d %%H:%%i:00' )
        ORDER BY time;
        '''.format(interval_minute=interval_minute, room_moid_filter=room_moid_filter)
        try:
            begin_time = get_timestamp_near_15min(start_time)
            begin_time_add_24h = begin_time + datetime.timedelta(hours=24)
            logger.debug(begin_time)
        except TypeError as e:
            begin_time = get_now_near_15min()
            begin_time_add_24h = begin_time + datetime.timedelta(hours=24)
        if room_moid_filter:
            params = [begin_time, begin_time_add_24h, in_room_all_user_domain]
        else:
            params = [begin_time, begin_time_add_24h]

        connections.close_all()
        with connections['meeting'].cursor() as cursor:
            # 预约会议sql
            cursor.execute(appointment_conf_sql, params)
            appointment_conf_fetchall = cursor.fetchall()
            # 预约直播会议sql
            cursor.execute(appointment_live_conf_sql, params)
            appointment_live_conf_fetchall = cursor.fetchall()
        logger.debug(appointment_conf_fetchall)
        logger.debug(appointment_live_conf_fetchall)

        now_timestamp = int(begin_time.timestamp() * 1000)
        tuple_index = 0
        live_tuple_index = 0
        # 1天转换为毫秒
        oneday2ms = 24 * 60 * 60 * 1000
        # 间隔分钟数转换为毫秒
        interval_minute2ms = interval_minute * 60 * 1000
        for timestamp in range(now_timestamp, now_timestamp + oneday2ms + interval_minute2ms, interval_minute2ms):
            # 预约会议数据处理
            try:
                if appointment_conf_fetchall:
                    fetch = appointment_conf_fetchall[tuple_index]
                    fetch_count = fetch[0]
                    fetch_time = fetch[1]
                    fetch_timestamp = int(
                        timezone.datetime.strptime(fetch_time, '%Y-%m-%d %H:%M:%S').timestamp() * 1000)

                    if fetch_timestamp == timestamp:
                        appointment_conf_info.append([timestamp, fetch_count])
                        if tuple_index < len(appointment_conf_fetchall) - 1:
                            tuple_index += 1
                    else:
                        appointment_conf_info.append([timestamp, 0])
                else:
                    appointment_conf_info.append([timestamp, 0])
            except Exception as e:
                err = str(e)
                logger.error(err)

            # 预约直播会议数据处理
            try:
                if appointment_live_conf_fetchall:
                    fetch = appointment_live_conf_fetchall[live_tuple_index]
                    fetch_count = fetch[0]
                    fetch_time = fetch[1]
                    fetch_timestamp = int(
                        timezone.datetime.strptime(fetch_time, '%Y-%m-%d %H:%M:%S').timestamp() * 1000)

                    if fetch_timestamp == timestamp:
                        appointment_live_conf_info.append([timestamp, fetch_count])
                        if live_tuple_index < len(appointment_live_conf_fetchall) - 1:
                            live_tuple_index += 1
                    else:
                        appointment_live_conf_info.append([timestamp, 0])
                else:
                    appointment_live_conf_info.append([timestamp, 0])
            except Exception as e:
                err = str(e)
                logger.error(err)

    except Exception as e:
        err = str(e)
        logger.error(err)

    return appointment_conf_info, appointment_live_conf_info


def get_time_aggs_vrs_info(request):
    start_time = request.query_params.get('start_time', str(es_client.get_start_time(time.time() * 1000 - 86400000)))
    end_time = request.query_params.get('end_time', str(es_client.get_end_time(time.time() * 1000)))
    interval = request.query_params.get('interval', es_client.get_interval_time(start_time, end_time, point=40))
    base_dsl = es_ql.base_vrs_info
    dsls = [base_dsl]

    get_filter_dsl(request, dsls, includes=('platform_moid',))
    live_conf_info = {
        "name": "live_confs",
        "description": "直播会议数",
        "data": []
    }
    viewer_info = {
        "name": "viewers",
        "description": "观看直播人数",
        "data": []
    }
    # ts = time.time()
    dsls, infos = es_client.get_every_time_dsls(base_dsl, start_time, end_time, interval, [live_conf_info, viewer_info])
    # t1 = time.time()
    # logger.debug('获取dsls:%ss' % (t1 - ts))
    live_conf_info = infos[0]
    viewer_info = infos[1]
    m_body = es_client.get_index_header_m_body(*dsls)
    # logger.debug(m_body)
    try:
        vrs_responses = es_client.msearch(m_body)['responses']
        # t2 = time.time()
        # logger.debug('获取vrs_responses:%ss' % (t2 - t1))
    except Exception as e:
        err = str(e)
        logger.error(err)
        vrs_responses = {}
        # t2 = time.time()
        # logger.debug('获取vrs_responses:%ss' % (t2 - t1))

    if vrs_responses:
        for index, vrs_response in enumerate(vrs_responses):
            # 直播会议数数据处理
            create_conf_e164_buckets = jsonpath.jsonpath(vrs_response, '$..create_live_conf_e164.buckets')
            create_conf_e164_buckets = create_conf_e164_buckets[0] if create_conf_e164_buckets else []
            # [{'key': '0000003', 'doc_count': 3},{'key': '0000004', 'doc_count': 2}]
            create_conf_dict = {e164.get('key'): e164.get('doc_count') for e164 in create_conf_e164_buckets}

            destroy_conf_e164_buckets = jsonpath.jsonpath(vrs_response, '$..destroy_live_conf_e164.buckets')
            destroy_conf_e164_buckets = destroy_conf_e164_buckets[0] if destroy_conf_e164_buckets else []
            destroy_conf_dict = {e164.get('key'): e164.get('doc_count') for e164 in destroy_conf_e164_buckets}

            # tts = time.time()
            for conf in destroy_conf_dict:
                if conf in create_conf_dict:
                    create_conf_dict[conf] = create_conf_dict[conf] - destroy_conf_dict[conf] \
                        if create_conf_dict[conf] >= destroy_conf_dict[conf] else 0
            # tt1 = time.time()
            # logger.debug('获取create_conf_dict:%ss' % (tt1 - tts))

            conf_num = sum(create_conf_dict.values())
            live_conf_info['data'][index].append(conf_num)

            # 观看直播人数数据处理
            conf_e164_buckets = jsonpath.jsonpath(vrs_response, '$..conf_e164.buckets')
            conf_e164_buckets = conf_e164_buckets[0] if conf_e164_buckets else []
            # 当前正在召开的会议e164号码列表
            confs = []
            for conf in create_conf_dict:
                if create_conf_dict[conf] > 0:
                    confs.append(conf)
            curr_viewer_num = 0
            online_num = 0
            offline_num = 0
            for conf_e164_bucket in conf_e164_buckets:
                if conf_e164_bucket.get('key') in confs:
                    user_moid_buckets = jsonpath.jsonpath(conf_e164_bucket, '$..user_moid.buckets')
                    user_moid_buckets = user_moid_buckets[0] if user_moid_buckets else []

                    for user_moid_bucket in user_moid_buckets:
                        user_state_buckets = jsonpath.jsonpath(user_moid_bucket, '$..user_state.buckets')
                        user_state_buckets = user_state_buckets[0] if user_state_buckets else []
                        if len(user_state_buckets) == 1 and user_state_buckets[0].get('key') == 1:
                            curr_viewer_num += 1
                        else:
                            for user_state_bucket in user_state_buckets:
                                if user_state_bucket.get('key') == 1:
                                    online_num = user_state_bucket.get('doc_count')
                                else:
                                    offline_num = user_state_bucket.get('doc_count')
                            if online_num > offline_num:
                                curr_viewer_num += 1
            viewer_info['data'][index].append(curr_viewer_num)
            # tt2 = time.time()
            # logger.debug('获取infott:%ss' % (tt2 - tt1))

        # t3 = time.time()
        # logger.debug('获取info:%ss' % (t3 - t2))
        # logger.debug('总时长:%ss' % (t3 - ts))
    return live_conf_info, viewer_info


def get_time_aggs_vrs_resources_info(request):
    '''
    vrs资源统计
    :param request:
    :return:
    '''
    start_time = request.query_params.get('start_time', str(es_client.get_start_time(time.time() * 1000 - 86400000)))
    end_time = request.query_params.get('end_time', str(es_client.get_end_time(time.time() * 1000)))
    interval = request.query_params.get('interval', es_client.get_interval_time(start_time, end_time, point=40))
    platform_moid = request.query_params.get('platform_moid', '')
    room_moid = request.query_params.get('room_moid', '')
    should = []
    base_dsl = copy.deepcopy(es_ql.base_vrs_resources_info)
    server_moids = []
    luban_cursor = connections['luban'].cursor()
    # 判断是否存在vrs设备
    has_vrs_sql = '''
    SELECT si.server_moid FROM server_info si
    WHERE si.server_type="vrs"
    '''
    luban_cursor.execute(has_vrs_sql)
    fetchall = luban_cursor.fetchall()
    if fetchall:
        has_vrs = True
    else:
        has_vrs = False

    if room_moid:
        room_moid_filter_sql = '''
        SELECT si.server_moid FROM server_info si
        LEFT JOIN machine_room_info mri ON si.machine_room_moid=mri.machine_room_moid
        WHERE si.machine_room_moid=%s AND si.server_type="vrs"
        '''
        params = [room_moid]
        luban_cursor.execute(room_moid_filter_sql, params)
        fetchall = luban_cursor.fetchall()
        server_moids += [fetch[0] for fetch in fetchall]
    elif platform_moid:
        platform_moid_filter_sql = '''
        SELECT si.server_moid FROM server_info si
        LEFT JOIN machine_room_info mri ON si.machine_room_moid=mri.machine_room_moid
        WHERE mri.domain_moid=%s AND si.server_type="vrs"
        '''
        params = [room_moid]
        luban_cursor.execute(platform_moid_filter_sql, params)
        fetchall = luban_cursor.fetchall()
        server_moids += [fetch[0] for fetch in fetchall]
    luban_cursor.close()
    server_moids = list(set(server_moids))

    for server_moid in server_moids:
        should.append({'match_phrase': {'beat.dev_moid': server_moid}})
    if should:
        base_dsl['dsl']['query']['bool']['must'].append(
            {'bool': {'should': should, 'minimum_should_match': 1}}
        )
    else:
        # 机房内无vrs，则搜索不存在的内容，使数据为空
        base_dsl['dsl']['query']['bool']['must'].append(
            {'bool': {'should': [{'match_phrase': {'beat.dev_moid': '---'}}], 'minimum_should_match': 1}}
        )
    # 使用部署数据查询机房内的所有设备，解决消息中无机房moid的问题
    # dsls = [base_dsl]
    # get_filter_dsl(request, dsls, includes=('platform_moid',))
    video_room_resources_info = {
        "name": "video_room_resources",
        "description": "录像室资源",
        "data": []
    }
    live_resources_info = {
        "name": "live_resources",
        "description": "直播资源",
        "data": []
    }

    dsls, infos = es_client.get_every_time_dsls(base_dsl, start_time, end_time, interval,
                                                [video_room_resources_info, live_resources_info])
    video_room_resources_info, live_resources_info = infos
    m_body = es_client.get_index_header_m_body(*dsls)
    try:
        vrs_responses = es_client.msearch(m_body)['responses']
    except Exception as e:
        err = str(e)
        logger.error(err)
        vrs_responses = {}
        video_room_resources_info['data'] = []
        live_resources_info['data'] = []

    if vrs_responses:
        for index, vrs_response in enumerate(vrs_responses):
            dev_moid_buckets = jsonpath.jsonpath(vrs_response, '$..dev_moid.buckets')
            dev_moid_buckets = dev_moid_buckets[0] if dev_moid_buckets else []
            all_live_total = 0
            all_live_used = 0
            video_room_total = 0
            video_room_used = 0
            if has_vrs:
                # 无vrs设备时，数据均为历史无效数据
                for dev_moid_bucket in dev_moid_buckets:
                    vrs_info = jsonpath.jsonpath(dev_moid_bucket, '$..vrs_info')
                    if vrs_info:
                        vrs_info = vrs_info[0]
                    else:
                        vrs_info = {}
                    # 直播相关
                    html5_used = vrs_info.get('vrs_html5lcastocp', 0)
                    html5_total = vrs_info.get('vrs_html5lcasttotal', 0)
                    asf_used = vrs_info.get('vrs_lcastocp', 0)
                    asf_total = vrs_info.get('vrs_lcasttotal', 0)

                    all_live_used += html5_used + asf_used
                    all_live_total += html5_total + asf_total
                    # 录像相关
                    video_room_used += vrs_info.get('vrs_recroomocp', 0)
                    video_room_total += vrs_info.get('vrs_recroomtotal', 0)

            live_resources_info['data'][index].append(all_live_total)
            live_resources_info['data'][index].append(all_live_used)
            video_room_resources_info['data'][index].append(video_room_total)
            video_room_resources_info['data'][index].append(video_room_used)

    return video_room_resources_info, live_resources_info


def get_now_support_conf_info(request):
    platform_moid = request.query_params.get('platform_moid', '')
    room_moid = request.query_params.get('room_moid', '')
    dsl = copy.deepcopy(es_ql.now_media_resource_from_rediswatcher_dsl)
    if platform_moid:
        dsl['dsl']['query']['bool']['must'].append(
            {'match_phrase': {'beat.platform_moid': platform_moid}}
        )
    if room_moid:
        dsl['dsl']['query']['bool']['must'].append(
            {'match_phrase': {'beat.roomid': room_moid}}
        )
    dsls = [dsl]
    m_body = es_client.get_index_header_m_body(*dsls)
    logger.debug(m_body)
    try:
        es_response = es_client.msearch(m_body)['responses'][0]
    except Exception as e:
        err = str(e)
        logger.error(err)
        es_response = None

    support_conf_info = {}
    if es_response:
        room_buckets = jsonpath.jsonpath(es_response, '$..room.buckets')
        if room_buckets:
            room_buckets = room_buckets[0]
            for room_bucket in room_buckets:
                traditional_conf_info = jsonpath.jsonpath(room_bucket, '$..resource_info.traditional_conf_info')
                if traditional_conf_info:
                    traditional_conf_info = traditional_conf_info[0]
                    for conf_type in traditional_conf_info:
                        if support_conf_info.get(conf_type):
                            support_conf_info[conf_type]['support'] += traditional_conf_info[conf_type].get('free', 0)
                        else:
                            support_conf_info.update(
                                {conf_type: {'support': traditional_conf_info[conf_type].get('free', 0)}})
    logger.info(support_conf_info)
    return support_conf_info
