#!/usr/bin/env python3
# coding: utf-8

__author__ = 'wanglei_sxcpx@kedacom.com'

import time
import logging
import copy
import json
import jsonpath

from django.db import connections, transaction
from warning.models import SubWarningCodeModel, TerminalWarningRepairedModel, TerminalWarningUnrepairedModel, \
    WarningCodeModel
from common.my_elastic import es_client
from es_ql_terminal import terminal_alarm_dsl
from redis_client import redis_client
from server_check import notice_handler, get_warning_dsls, get_sub_codes, query_es, get_sql_fetch, timer

logger = logging.getLogger("warning-timer")
ALARM_INTERVAL = 300
PERIOD = 30
ALARM_TYPE = 'terminal'


@timer
def get_terminal_warning_data():
    '''
    获取订阅的告警数据
    :return: {
        '2011':{'{devmoid}':['{warning_info1}','{warning_info2}']},
        '2012':{'{devmoid}':['{warning_info1}','{warning_info2}']}
    }
    '''
    warning_data = {}

    dsls = get_warning_dsls(base_dsl=terminal_alarm_dsl, warning_type='terminal')
    es_responses = query_es(dsls, warning_type=ALARM_TYPE)
    for response in es_responses:
        warning_code = jsonpath.jsonpath(response, '$..source.alarm_info.code_id')
        if warning_code:
            warning_code = warning_code[0]
            warning_data[warning_code] = {}
            dev_buckets = jsonpath.jsonpath(response, '$..dev_moid.buckets')
            if dev_buckets:
                dev_buckets = dev_buckets[0]
                for dev_bucket in dev_buckets:
                    dev_moid = jsonpath.jsonpath(dev_bucket, '$.key')
                    if dev_moid:
                        dev_moid = dev_moid[0]
                        if not warning_data[warning_code].get(dev_moid):
                            warning_data[warning_code][dev_moid] = []
                        alarm_infos = jsonpath.jsonpath(dev_bucket, '$..source.alarm_info')
                        if alarm_infos:
                            for alarm_info in alarm_infos:
                                dev_type = jsonpath.jsonpath(dev_bucket, '$..source.devtype')
                                src_type = jsonpath.jsonpath(dev_bucket, '$..beat.src_type')
                                report_time = jsonpath.jsonpath(dev_bucket, '$..@timestamp')
                                alarm_info['src_type'] = src_type[0] if src_type else ''
                                alarm_info['dev_type'] = dev_type[0] if dev_type else ''
                                alarm_info['report_time'] = report_time[0] if report_time else ''

                                warning_data[warning_code][dev_moid].append(alarm_info)

    return warning_data


def generate_alarm(*args, **kwargs):
    '''
    产生告警
    :return:
    '''
    code, dev_moid, device_name, device_e164, dev_type, src_type, device_ip, domain_moid, \
    domain_name, level, description, report_time, redis_key, name, suggestion = args
    send_notice_flag = 0
    alarm_msg = {}
    is_exist = TerminalWarningUnrepairedModel.objects.filter(
        device_moid=dev_moid,
        code=code
    ).exists()
    if is_exist:
        # 告警已存在
        warning_key = redis_client.get(redis_key)
        if not warning_key:
            redis_client.set(redis_key, 'notice',
                             ex=ALARM_INTERVAL)
            # 发送告警通知
            logger.info('告警重复通知，告警码：{code}，告警设备：{device_name}，告警描述：{description}'.format(
                code=code, device_name=device_name, description=description))
            alarm_msg = {
                'type': '%s_warning' % ALARM_TYPE,
                'action': '告警重复通知',
                'device_name': device_name,
                'domain_name': domain_name,
                'device_e164': device_e164,
                'device_type': dev_type,
                'name': name,
                'alarm_type': ALARM_TYPE,
                'code': code,
                'level': level,
                'desc': description,
                'suggestion': suggestion,
                'warning_start_time': report_time,
                'warning_resolve_time': '',
            }
            send_notice_flag = 1

    else:
        # 告警不存在
        redis_client.set(redis_key, 'notice', ex=ALARM_INTERVAL)
        TerminalWarningUnrepairedModel.objects.create(
            device_moid=dev_moid,
            device_name=device_name,
            device_type=dev_type,
            device_ip=device_ip,
            device_e164=device_e164,
            domain_name=domain_name,
            domain_moid=domain_moid,
            code=code,
            level=level,
            description=description,
            start_time=report_time,
        )

        # 发送告警通知
        logger.info('产生告警，告警码：{code}，告警设备：{device_name}，告警描述：{description}'.format(
            code=code, device_name=device_name, description=description))
        alarm_msg = {
            'type': '%s_warning' % ALARM_TYPE,
            'action': '产生告警',
            'device_name': device_name,
            'domain_name': domain_name,
            'device_e164': device_e164,
            'device_type': dev_type,
            'name': name,
            'alarm_type': ALARM_TYPE,
            'code': code,
            'level': level,
            'desc': description,
            'suggestion': suggestion,
            'warning_start_time': report_time,
            'warning_resolve_time': '',
        }
        send_notice_flag = 1

    notice_handler(send_notice_flag, code, alarm_msg, alarm_type=ALARM_TYPE)


def repaired_alarm(*args, **kwargs):
    '''
    恢复告警
    :return:
    '''
    code, dev_moid, device_name, device_e164, dev_type, src_type, device_ip, domain_moid, \
    domain_name, level, description, report_time, redis_key, name, suggestion = args
    send_notice_flag = 0
    alarm_msg = {}
    is_exist = TerminalWarningUnrepairedModel.objects.filter(
        device_moid=dev_moid,
        code=code
    ).exists()
    if is_exist:
        # 告警已存在
        terminal_warning_queryset = TerminalWarningUnrepairedModel.objects.filter(
            device_moid=dev_moid,
            code=code
        ).first()
        warning_start_time = terminal_warning_queryset.start_time
        try:
            with transaction.atomic():
                # 已修复告警表添加数据
                TerminalWarningRepairedModel.objects.create(
                    device_moid=terminal_warning_queryset.device_moid,
                    device_name=terminal_warning_queryset.device_name,
                    device_type=terminal_warning_queryset.device_type,
                    device_ip=terminal_warning_queryset.device_ip,
                    device_e164=terminal_warning_queryset.device_e164,
                    domain_name=terminal_warning_queryset.domain_name,
                    domain_moid=terminal_warning_queryset.domain_moid,
                    code=terminal_warning_queryset.code,
                    level=terminal_warning_queryset.level,
                    description=terminal_warning_queryset.description,
                    start_time=warning_start_time,
                    resolve_time=report_time,
                )
                # 未修复告警表删除数据
                TerminalWarningUnrepairedModel.objects.filter(
                    device_moid=dev_moid,
                    code=code
                ).delete()
                # 删除redis_key
                redis_client.delete(redis_key)

                # 发送告警通知
                logger.info('修复告警，告警码：{code}，告警设备：{device_name}， 告警描述：{description}'.format(
                    code=code, device_name=device_name, description=description))
                alarm_msg = {
                    'type': '%s_warning' % ALARM_TYPE,
                    'action': '修复告警',
                    'device_name': device_name,
                    'domain_name': domain_name,
                    'device_e164': device_e164,
                    'device_type': dev_type,
                    'name': name,
                    'alarm_type': ALARM_TYPE,
                    'code': code,
                    'level': level,
                    'desc': description,
                    'suggestion': suggestion,
                    'warning_start_time': warning_start_time,
                    'warning_resolve_time': report_time,
                }
                send_notice_flag = 1

        except Exception as e:
            logger.exception(e)

    notice_handler(send_notice_flag, code, alarm_msg, alarm_type=ALARM_TYPE)


@timer
def warning_data_handler(warning_data):
    '''
    告警数据处理，产生或恢复告警
    :param warning_data:
    :return:
    '''
    for code, warning in warning_data.items():
        sql = '''
        SELECT ui.moid,up.name,ui.e164,ud.user_domain_moid,ud.user_domain_name 
        FROM user_info ui 
        LEFT JOIN user_profile up on ui.moid=up.moid 
        LEFT JOIN user_domain ud on ui.user_domain_moid=ud.user_domain_moid 
        WHERE ui.isdeleted = '0' and ui.account_type != '9' and 
        (ui.device_type is null or ui.device_type not in ('519','524','530','531')) and
        ui.binded='0' and ui.account is not NULL
        '''
        # bridge26上报的老终端dev_moid为纯数字，末尾13位为终端e164号码，其余为正常的终端moid
        filter_keys = []
        filter_key = [dev_moid for dev_moid in warning.keys() if not dev_moid.isdigit()]
        brideg26_filter_key = [dev_moid[-13:] for dev_moid in warning.keys() if dev_moid.isdigit()]

        if filter_key:
            if brideg26_filter_key:
                # 两种都存在
                sql += ' AND (ui.moid in %s OR ui.e164 in %s)'
                filter_keys.append(filter_key)
                filter_keys.append(brideg26_filter_key)
            else:
                # 只存在正常moid
                sql += ' AND ui.moid in %s'
                filter_keys.append(filter_key)
        else:
            if brideg26_filter_key:
                # 只存在bridge26上报的消息
                sql += ' AND ui.e164 in %s'
                filter_keys.append(brideg26_filter_key)

        terminal_info = {}
        if filter_keys:
            logger.info(code)
            fetchall = get_sql_fetch('movision', sql, filter_keys=filter_keys, many=True)
            for fetch in fetchall:
                terminal_info[fetch[0]] = dict(
                    zip(['device_name', 'device_e164', 'domain_moid', 'domain_name'], fetch[1:]))

        for dev_moid, warning_info in warning.items():
            if dev_moid.isdigit():
                # 将bridge26上报的数字转换为moid
                device_e164 = dev_moid[-13:]
                for moid, info in terminal_info.items():
                    if info.get('device_e164') == device_e164:
                        dev_moid = moid
                        break

            for warning_detail in warning_info:
                alarm_status = warning_detail.get('status')
                dev_type = warning_detail.get('dev_type')
                src_type = warning_detail.get('src_type')
                report_time = warning_detail.get('report_time')
                device_name = terminal_info.get(dev_moid, {}).get('device_name', '')
                device_e164 = terminal_info.get(dev_moid, {}).get('device_e164', '')
                domain_moid = terminal_info.get(dev_moid, {}).get('domain_moid', '')
                domain_name = terminal_info.get(dev_moid, {}).get('domain_name', '')
                device_ip = ''
                code_queryset = WarningCodeModel.objects.filter(code=code).first()
                level = code_queryset.level
                description = code_queryset.description
                name = code_queryset.name
                suggestion = code_queryset.suggestion
                redis_key = '%s_%s' % (dev_moid, code)
                if alarm_status:
                    # 产生告警
                    args = [code, dev_moid, device_name, device_e164, dev_type, src_type, device_ip, domain_moid,
                            domain_name, level, description, report_time, redis_key, name, suggestion]
                    generate_alarm(*args)
                else:
                    # 恢复告警
                    args = [code, dev_moid, device_name, device_e164, dev_type, src_type, device_ip, domain_moid,
                            domain_name, level, description, report_time, redis_key, name, suggestion]
                    repaired_alarm(*args)


def terminal_warning_check(period=30, alarm_interval=300):
    if not (isinstance(period, int) and isinstance(alarm_interval, int)):
        raise SyntaxError('参数错误 period,alarm_interval -> int')
    global ALARM_INTERVAL, PERIOD
    ALARM_INTERVAL, PERIOD = alarm_interval, period
    while True:
        try:
            warning_data = get_terminal_warning_data()
            warning_data_handler(warning_data)
        except Exception as e:
            logger.exception(e)
        time.sleep(period)
