#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

import time
import logging
import copy
import random

import jsonpath

from common.my_elastic import es_client
from .dsl import nginx_es_ql
from .query_func import get_filter_dsl
from common.my_exception import OpsException

logger = logging.getLogger('ops.' + __name__)


def data_offset(data, offset=5):
    """
    将data数据偏移正负百分之0-5 offset
    :param data: 数据
    :type data:float or int
    :param offset:
    :type offset:float or int
    :return:
    """
    pct = random.uniform(0, offset) / 100
    plus_minus = random.choice([0, 1])
    if plus_minus:
        # +
        data = data * (1 + pct)
    else:
        # -
        data = data * (1 - pct)
    return data


def from_request_get_common_params(request):
    '''
    从request中获取通用参数
    :param request:
    :return:
    '''
    platform_moid = request.query_params.get('platform_moid', '')
    room_moid = request.query_params.get('room_moid', '')
    start_time = request.query_params.get('start_time',
                                          str(es_client.get_start_time(time.time() * 1000 - 86400000)))
    end_time = request.query_params.get('end_time', str(es_client.get_end_time(time.time() * 1000)))
    interval = request.query_params.get('interval', es_client.get_interval_time(start_time, end_time, point=40))
    key = request.query_params.get('key', '')
    status_code = str(request.query_params.get('status_code', ''))
    client = request.query_params.get('client', '')
    module = request.query_params.get('module', '')
    export_type = request.query_params.get('export_type', '')
    try:
        start = int(request.query_params.get('start', 0)) if int(request.query_params.get('start', 0)) else 0
        count = int(request.query_params.get('count', 10)) if int(request.query_params.get('count', 10)) else 10
        slow_time_threshold = float(request.query_params.get('slow_time_threshold', 0)) \
            if request.query_params.get('slow_time_threshold', 0) else 0
    except Exception as e:
        logger.exception(e)
        raise OpsException(code='10010')

    params = {
        'room_moid': room_moid,
        'start_time': start_time,
        'end_time': end_time,
        'platform_moid': platform_moid,
        'interval': interval,
        'start': start,
        'count': count,
        'slow_time_threshold': slow_time_threshold,
        'module': module,
        'client': client,
        'key': key,
        'status_code': status_code,
        'export_type': export_type,
    }
    return params


def get_outline_pv_uv_request_time(request):
    '''
    获取pv，uv, 平均请求时间
    :param request:
    :return: outline_info
    '''
    dsl = copy.deepcopy(nginx_es_ql.outline_dsl)
    dsls = [dsl]
    logger.info(dsl)
    dsls = get_filter_dsl(request, dsls, excludes=('interval',), delay_filter_time=False)
    m_body = es_client.get_index_header_m_body(*dsls)
    logger.info(m_body)
    try:
        responses = es_client.msearch(m_body)['responses']
    except Exception as e:
        logger.exception(e)
        raise OpsException(code='10002')
    else:
        outline_response = responses[0]

        pv_total = jsonpath.jsonpath(outline_response, '$.hits.total')
        pv_total = pv_total[0] if pv_total else 0
        uv_total = jsonpath.jsonpath(outline_response, '$..sum_bucket_uv.value')
        uv_total = int(uv_total[0]) if uv_total else 0
        avg_request_time = jsonpath.jsonpath(outline_response, '$..avg_bucket_request_time.value')
        avg_request_time = round(avg_request_time[0], 3) if avg_request_time and avg_request_time[0] else 0

        outline_info = [
            {
                "description": "浏览量(PV)",
                "name": "pv",
                "data": pv_total

            },
            {
                "description": "访客数(UV)",
                "name": "uv",
                "data": uv_total
            },
            {
                "description": "平均访问时长",
                "name": "avg_request_time",
                "data": avg_request_time
            }
        ]
        return outline_info


def get_time_aggs_request_traffic(request):
    '''
    获取请求流量统计图数据
    :param request:
    :return: request_traffic_info
    '''

    dsl = copy.deepcopy(nginx_es_ql.request_traffic_dsl)
    dsls = [dsl]
    dsls = get_filter_dsl(request, dsls)

    m_body = es_client.get_index_header_m_body(*dsls)
    logger.info(m_body)
    try:
        responses = es_client.msearch(m_body)['responses']
    except Exception as e:
        logger.exception(e)
        raise OpsException(code='10002')
    else:
        request_traffic_response = responses[0]
        info_data = []
        time_buckets = jsonpath.jsonpath(request_traffic_response, '$..time.buckets')
        time_buckets = time_buckets[0] if time_buckets else []

        for time_bucket in time_buckets[:-1]:
            timestamp = time_bucket.get('key')
            body_bytes_sent = time_bucket.get('sum_body_bytes_sent', {}).get('value')
            body_bytes_sent = int(body_bytes_sent) if body_bytes_sent else 0
            # 子列表，包含时间戳和发送总流量
            sub_list = [timestamp, body_bytes_sent]
            info_data.append(sub_list)

        if info_data:
            # 最后一个值按倒数第二个值做5%的偏移
            timestamp = time_buckets[-1].get('key')
            body_bytes_sent = time_buckets[-2].get('sum_body_bytes_sent', {}).get('value')
            body_bytes_sent = int(body_bytes_sent) if body_bytes_sent else 0
            body_bytes_sent = data_offset(body_bytes_sent)
            sub_list = [timestamp, body_bytes_sent]
            info_data.append(sub_list)

        # 生成response需要的info
        request_traffic_info = [
            {
                "name": "traffic",
                "description": "请求流量统计",
                "data": info_data
            }
        ]

        return request_traffic_info


def get_time_aggs_pv(request):
    dsl = copy.deepcopy(nginx_es_ql.request_traffic_dsl)
    dsls = [dsl]
    dsls = get_filter_dsl(request, dsls)

    m_body = es_client.get_index_header_m_body(*dsls)
    logger.info(m_body)
    try:
        responses = es_client.msearch(m_body)['responses']
    except Exception as e:
        logger.exception(e)
        raise OpsException(code='10002')
    else:
        request_traffic_response = responses[0]
        info_data = []
        time_buckets = jsonpath.jsonpath(request_traffic_response, '$..time.buckets')
        time_buckets = time_buckets[0] if time_buckets else []

        for time_bucket in time_buckets[:-1]:
            timestamp = time_bucket.get('key')
            pv = time_bucket.get('doc_count')

            sub_list = [timestamp, pv]
            info_data.append(sub_list)

        if info_data:
            # 最后一个值按倒数第二个值做5%的偏移
            timestamp = time_buckets[-1].get('key')
            pv = time_buckets[-2].get('doc_count')
            pv = data_offset(pv)
            sub_list = [timestamp, pv]
            info_data.append(sub_list)

        pv_info = [
            {
                "name": "pv",
                "description": "访问量统计",
                "data": info_data
            }
        ]

        return pv_info


def get_ip_info(request):
    dsl = copy.deepcopy(nginx_es_ql.ip_info_dsl)
    dsls = [dsl]
    dsls = get_filter_dsl(request, dsls)

    m_body = es_client.get_index_header_m_body(*dsls)
    logger.info(m_body)
    try:
        responses = es_client.msearch(m_body)['responses']
    except Exception as e:
        logger.exception(e)
        raise OpsException(code='10002')
    else:
        request_traffic_response = responses[0]
        info_data = []
        remote_addr_buckets = jsonpath.jsonpath(request_traffic_response, '$..remote_addr.buckets')
        remote_addr_buckets = remote_addr_buckets[0] if remote_addr_buckets else []

        for remote_addr_bucket in remote_addr_buckets:
            ip = remote_addr_bucket.get('key')
            pv = remote_addr_bucket.get('doc_count')

            sub_list = [ip, pv]
            info_data.append(sub_list)

        return info_data


def get_slow_responses_info(request):
    dsl = copy.deepcopy(nginx_es_ql.slow_responses_or_url_dsl)
    params = from_request_get_common_params(request)
    slow_time_threshold = params.get('slow_time_threshold')
    slow_request_filter = {"bool": {"filter": {"range": {"request_time": {"gte": slow_time_threshold}}}}}
    dsl['dsl']['query']['bool']['must'].append(slow_request_filter)
    dsls = [dsl]
    dsls = get_filter_dsl(request, dsls)

    m_body = es_client.get_index_header_m_body(*dsls)
    logger.info(m_body)
    try:
        responses = es_client.msearch(m_body)['responses']
    except Exception as e:
        logger.exception(e)
        raise OpsException(code='10002')
    else:
        slow_responses_response = responses[0]
        info_data = []
        uri_buckets = jsonpath.jsonpath(slow_responses_response, '$..uri.buckets')
        uri_buckets = uri_buckets[0] if uri_buckets else []

        for uri_bucket in uri_buckets:
            uri = uri_bucket.get('key')
            count = uri_bucket.get('doc_count')

            sub_list = [uri, count]
            info_data.append(sub_list)

        return info_data


def get_url_info(request):
    dsl = copy.deepcopy(nginx_es_ql.slow_responses_or_url_dsl)
    dsls = [dsl]
    dsls = get_filter_dsl(request, dsls)

    m_body = es_client.get_index_header_m_body(*dsls)
    logger.info(m_body)
    try:
        responses = es_client.msearch(m_body)['responses']
    except Exception as e:
        logger.exception(e)
        raise OpsException(code='10002')
    else:
        url_response = responses[0]
        info_data = []
        uri_buckets = jsonpath.jsonpath(url_response, '$..uri.buckets')
        uri_buckets = uri_buckets[0] if uri_buckets else []

        for uri_bucket in uri_buckets:
            uri = uri_bucket.get('key')
            count = uri_bucket.get('doc_count')

            sub_list = [uri, count]
            info_data.append(sub_list)

        return info_data


def get_clients_pct_info(request):
    dsl = copy.deepcopy(nginx_es_ql.clients_pct_dsl)
    dsls = [dsl]
    dsls = get_filter_dsl(request, dsls)

    m_body = es_client.get_index_header_m_body(*dsls)
    logger.info(m_body)
    try:
        responses = es_client.msearch(m_body)['responses']
    except Exception as e:
        logger.exception(e)
        raise OpsException(code='10002')
    else:
        clients_pct_response = responses[0]

        chrome_count = jsonpath.jsonpath(clients_pct_response, '$..chrome.doc_count')
        chrome_count = chrome_count[0] if chrome_count else 0
        firefox_count = jsonpath.jsonpath(clients_pct_response, '$..firefox.doc_count')
        firefox_count = firefox_count[0] if firefox_count else 0
        movision_count = jsonpath.jsonpath(clients_pct_response, '$..movision.doc_count')
        movision_count = movision_count[0] if movision_count else 0
        ie_count = jsonpath.jsonpath(clients_pct_response, '$..ie.doc_count')
        ie_count = ie_count[0] if ie_count else 0
        other_count = jsonpath.jsonpath(clients_pct_response, '$..other.doc_count')
        other_count = other_count[0] if other_count else 0

        total_count = chrome_count + firefox_count + movision_count + ie_count + other_count
        # 防止分子为0
        total_count = total_count if total_count else 1
        chrome_pct = round(chrome_count / total_count, 2)
        firefox_pct = round(firefox_count / total_count, 2)
        movision_pct = round(movision_count / total_count, 2)
        ie_pct = round(ie_count / total_count, 2)
        # 无数据时百分比为0
        if other_count == total_count - 1 == 0:
            other_pct = 0
        else:
            other_pct = 1 - chrome_pct - firefox_pct - movision_pct - ie_pct

        data_info = [
            {
                "description": "谷歌",
                "name": "chrome",
                "data": chrome_pct
            },
            {
                "description": "火狐",
                "name": "firefox",
                "data": firefox_pct
            },
            {
                "description": "IE",
                "name": "ie",
                "data": ie_pct
            },
            {
                "description": "摩云",
                "name": "movision",
                "data": movision_pct
            },
            {
                "description": "其他",
                "name": "other",
                "data": other_pct
            }
        ]
        return data_info


def get_clients_info(request):
    dsl = copy.deepcopy(nginx_es_ql.clients_dsl)
    params = from_request_get_common_params(request)
    client = params.get('client')
    if client:
        client_must_filter = {
            'match': {
                'http_user_agent': client
            }
        }
        client_must_not_filter = None
        if client == 'chrome':
            # 默认过滤规则
            pass
        elif client == 'movision':
            # 默认过滤规则
            pass
        elif client == 'firefox':
            # 默认过滤规则
            pass
        elif client == 'ie':
            client_must_filter = {
                "bool": {
                    "should": [
                        {
                            "match": {
                                "http_user_agent": "trident"
                            }
                        },
                        {
                            "match": {
                                "http_user_agent": "msie"
                            }
                        }
                    ],
                    "minimum_should_match": 1
                }
            }
        elif client == 'other':
            client_must_filter = None
            client_must_not_filter = {
                'match': {
                    'http_user_agent': 'chrome || firefox || movision || trident || msie'
                }
            }
        else:
            raise OpsException(code='10010')

        if client_must_filter:
            dsl['dsl']['query']['bool']['must'].append(client_must_filter)
        if client_must_not_filter:
            dsl['dsl']['query']['bool']['must_not'].append(client_must_not_filter)

    dsls = [dsl]
    dsls = get_filter_dsl(request, dsls)

    m_body = es_client.get_index_header_m_body(*dsls)
    logger.info(m_body)
    try:
        responses = es_client.msearch(m_body)['responses']
    except Exception as e:
        logger.exception(e)
        raise OpsException(code='10002')
    else:
        clients_response = responses[0]
        info_data = []
        user_agent_buckets = jsonpath.jsonpath(clients_response, '$..user_agent.buckets')
        user_agent_buckets = user_agent_buckets[0] if user_agent_buckets else []

        for user_agent_bucket in user_agent_buckets:
            user_agent = user_agent_bucket.get('key')
            count = user_agent_bucket.get('doc_count')

            sub_list = [user_agent, count]
            info_data.append(sub_list)

        return info_data


def get_time_aggs_status_code(request):
    dsl = copy.deepcopy(nginx_es_ql.status_code_dsl)
    dsls = [dsl]
    dsls = get_filter_dsl(request, dsls)

    m_body = es_client.get_index_header_m_body(*dsls)
    logger.info(m_body)
    try:
        responses = es_client.msearch(m_body)['responses']
    except Exception as e:
        logger.exception(e)
        raise OpsException(code='10002')
    else:
        status_code_response = responses[0]
        status_2xx_info = {
            "name": "2xx",
            "data": [],
            "description": "2xx"
        }
        status_3xx_info = {
            "name": "3xx",
            "data": [],
            "description": "3xx"
        }
        status_4xx_info = {
            "name": "4xx",
            "data": [],
            "description": "4xx"
        }
        status_5xx_info = {
            "name": "5xx",
            "data": [],
            "description": "5xx"
        }
        info_data = [status_2xx_info, status_3xx_info, status_4xx_info, status_5xx_info]

        time_buckets = jsonpath.jsonpath(status_code_response, '$..time.buckets')
        time_buckets = time_buckets[0] if time_buckets else []

        for time_bucket in time_buckets:
            timestamp = time_bucket.get('key')
            status_2xx = time_bucket.get('2xx', {}).get('doc_count')
            status_3xx = time_bucket.get('3xx', {}).get('doc_count')
            status_4xx = time_bucket.get('4xx', {}).get('doc_count')
            status_5xx = time_bucket.get('5xx', {}).get('doc_count')

            status_2xx_info['data'].append([timestamp, status_2xx])
            status_3xx_info['data'].append([timestamp, status_3xx])
            status_4xx_info['data'].append([timestamp, status_4xx])
            status_5xx_info['data'].append([timestamp, status_5xx])

        return info_data


def get_error_info(request):
    dsl = copy.deepcopy(nginx_es_ql.errors_dsl)
    dsls = [dsl]
    dsls = get_filter_dsl(request, dsls)

    m_body = es_client.get_index_header_m_body(*dsls)
    logger.info(m_body)
    try:
        responses = es_client.msearch(m_body)['responses']
    except Exception as e:
        logger.exception(e)
        raise OpsException(code='10002')
    else:
        errors_response = responses[0]
        info_data = []

        errors_buckets = jsonpath.jsonpath(errors_response, '$..uri.buckets')
        errors_buckets = errors_buckets[0] if errors_buckets else []

        for errors_bucket in errors_buckets:
            uri = errors_bucket.get('key')
            count = errors_bucket.get('doc_count')
            status = jsonpath.jsonpath(errors_bucket, '$.._source.status')
            status = status[0] if status else 0
            upstream_status = jsonpath.jsonpath(errors_bucket, '$.._source.upstream_status')
            upstream_status = upstream_status[0] if upstream_status else 0
            # 小数组中的4个元素
            sub_list = [uri, count, status, upstream_status]
            info_data.append(sub_list)

        return info_data


def get_methods_info(request):
    dsl = copy.deepcopy(nginx_es_ql.methods_dsl)
    dsls = [dsl]
    dsls = get_filter_dsl(request, dsls)

    m_body = es_client.get_index_header_m_body(*dsls)
    logger.info(m_body)
    try:
        responses = es_client.msearch(m_body)['responses']
    except Exception as e:
        logger.exception(e)
        raise OpsException(code='10002')
    else:
        methods_response = responses[0]
        method_info_index_dict = {
            'get': 0,
            'post': 1,
            'put': 2,
            'delete': 3,
        }
        info_data = [
            {
                "name": "get",
                "data": 0,
                "description": "GET"
            },
            {
                "name": "post",
                "data": 0,
                "description": "POST"
            },
            {
                "name": "put",
                "data": 0,
                "description": "PUT"
            },
            {
                "name": "delete",
                "data": 0,
                "description": "DELETE"
            }
        ]

        methods_buckets = jsonpath.jsonpath(methods_response, '$..methods.buckets')
        methods_buckets = methods_buckets[0] if methods_buckets else []

        for methods_bucket in methods_buckets:
            method = methods_bucket.get('key')
            count = methods_bucket.get('doc_count')
            if isinstance(method, str) and isinstance(method_info_index_dict.get(method.lower()), int):
                info_data[method_info_index_dict.get(method.lower())]['data'] = count

        return info_data


def get_modules(request):
    dsl = copy.deepcopy(nginx_es_ql.modules_dsl)
    dsls = [dsl]
    dsls = get_filter_dsl(request, dsls)

    m_body = es_client.get_index_header_m_body(*dsls)
    logger.info(m_body)
    try:
        responses = es_client.msearch(m_body)['responses']
    except Exception as e:
        logger.exception(e)
        raise OpsException(code='10002')
    else:
        modules_response = responses[0]
        info_data = jsonpath.jsonpath(modules_response, '$..modules.buckets[*].key')
        info_data = info_data if info_data else []

        return info_data


def get_detail_info(request):
    dsl = copy.deepcopy(nginx_es_ql.detail_dsl)
    params = from_request_get_common_params(request)
    # 支持过滤的参数
    key = params.get('key')
    client = params.get('client')
    status_code = params.get('status_code')
    module = params.get('module')
    slow_time_threshold = params.get('slow_time_threshold')
    start = params.get('start')
    count = params.get('count')

    # 根据过滤参数修改dsl
    dsl_must = dsl['dsl']['query']['bool']['must']
    # 翻页
    dsl['dsl']['size'] = count
    dsl['dsl']['from'] = start
    # 模块
    if module:
        module_filter = {
            "match": {
                "module.keyword": module
            }
        }
        dsl_must.append(module_filter)
    # 客户端
    if client:
        pass
    # 模糊匹配uri或remote_addr
    if key:
        key_filter = {
            "bool": {
                "should": [
                    {
                        "wildcard": {
                            "uri.keyword": '*%s*' % key
                        }
                    },
                    {
                        "wildcard": {
                            "request_uri.keyword": '*%s*' % key
                        }
                    },
                    {
                        "wildcard": {
                            "remote_addr.keyword": '*%s*' % key
                        }
                    }
                ],
                "minimum_should_match": 1
            }
        }
        dsl_must.append(key_filter)
    # 慢查询
    if slow_time_threshold:
        slow_time_threshold_filter = {
            "bool": {
                "filter": {
                    "range": {
                        "request_time": {
                            "gte": slow_time_threshold
                        }
                    }
                }
            }
        }
        dsl_must.append(slow_time_threshold_filter)
    # http状态码
    if status_code and isinstance(status_code, str):
        if status_code in ['1xx', '2xx', '3xx', '4xx', '5xx']:
            status_code_range = ('%s00' % status_code.split('xx')[0], '%s00' % (int(status_code.split('xx')[0]) + 1))
            status_code_filter = {
                "bool": {
                    "filter": {
                        "range": {
                            "status": {
                                "gte": status_code_range[0],
                                "lt": status_code_range[1]
                            }
                        }
                    }
                }
            }
        elif status_code.isdigit():
            status_code_filter = {
                "match": {
                    "status": status_code
                }
            }
        else:
            raise OpsException(code='10010')

        dsl_must.append(status_code_filter)

    dsls = [dsl]
    dsls = get_filter_dsl(request, dsls)

    m_body = es_client.get_index_header_m_body(*dsls)
    logger.info(m_body)
    try:
        responses = es_client.msearch(m_body)['responses']
    except Exception as e:
        logger.exception(e)
        raise OpsException(code='10002')
    else:
        detail_response = responses[0]
        total = jsonpath.jsonpath(detail_response, '$.hits.total')
        total = total[0] if total else 0

        data_info = jsonpath.jsonpath(detail_response, '$.hits.hits[*]._source')
        data_info = data_info if data_info else []

        return data_info, total
