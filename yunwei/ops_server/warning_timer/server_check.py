#!/usr/bin/env python3
# coding: utf-8

__author__ = 'wanglei_sxcpx@kedacom.com'

import time
import datetime
import logging
import copy
import json
import jsonpath

from django.db import connections, transaction
from warning.models import SubWarningCodeModel, ServerWarningRepairedModel, ServerWarningUnrepairedModel, \
    WarningCodeModel
from common.my_elastic import es_client
from es_ql_server import server_alarm_dsl
from redis_client import redis_client
from notice_method import send_notice
from threshold_warning_check import threshold_codes

logger = logging.getLogger("warning-timer")
ALARM_INTERVAL = 300
PERIOD = 30
ALARM_TYPE = 'server'
NMSESRedisKEY = 'ops/nms_es_warning/last_check_timestamp'


def timer(func):
    '''
    时间装饰器，打印函数执行时间
    :param func:
    :return:
    '''

    def wrapper(*args, **kwargs):
        st = time.time()
        ret = func(*args, **kwargs)
        logger.info('{}: {}s'.format(func, time.time() - st))
        return ret

    return wrapper


def get_nms_not_send_to_es_warning_data():
    '''
    从网管表中获取未上报到es的告警
    :return:
    '''
    nms_not_send_to_es_warning_data = {}
    # 2065：授权即将到期、3010：单板服务器下线
    nms_not_send_to_es_warning_codes = [2065, 3010]
    redis_key = 'ops/nms_not_send_to_es_warning/nms_db_server_warning_id'
    if redis_client.exists(redis_key):
        server_warning_unrepaired_id = redis_client.hget(redis_key, 'server_warning_unrepaired')
        server_warning_unrepaired_id = server_warning_unrepaired_id.decode(
            encoding='utf-8') if server_warning_unrepaired_id else '0'
        server_warning_repaired_id = redis_client.hget(redis_key, 'server_warning_repaired')
        server_warning_repaired_id = server_warning_repaired_id.decode(
            encoding='utf-8') if server_warning_repaired_id else '0'
    else:
        server_warning_unrepaired_id = server_warning_repaired_id = '0'
        redis_client.hset(redis_key, 'server_warning_unrepaired', server_warning_unrepaired_id)
        redis_client.hset(redis_key, 'server_warning_repaired', server_warning_repaired_id)
    unrepaired_sql = '''
    SELECT id,code,device_moid,device_type,start_time 
    FROM server_warning_unrepaired 
    WHERE code IN %s AND TO_DAYS( NOW( ) ) - TO_DAYS(start_time) <= 1 AND id > %s 
    ORDER BY id
    '''
    repaired_sql = '''
    SELECT id,code,device_moid,device_type,start_time,resolve_time
    FROM server_warning_repaired 
    WHERE code IN %s AND TO_DAYS( NOW( ) ) - TO_DAYS(start_time) <= 1 AND id > %s 
    ORDER BY id
    '''
    # 查询表的最大id
    repaired_max_id_sql = '''
    SELECT id FROM server_warning_repaired
    ORDER BY id DESC LIMIT 1
    '''
    unrepaired_max_id_sql = '''
    SELECT id FROM server_warning_repaired
    ORDER BY id DESC LIMIT 1
    '''
    repaired_fetchall = []
    unrepaired_fetchall = []
    try:
        repaired_fetchall = get_sql_fetch(
            'nms_db', sql=repaired_sql, filter_keys=[nms_not_send_to_es_warning_codes, server_warning_repaired_id],
            many=True)
        unrepaired_fetchall = get_sql_fetch(
            'nms_db', sql=unrepaired_sql, filter_keys=[nms_not_send_to_es_warning_codes, server_warning_unrepaired_id],
            many=True)
        repaired_max_id = get_sql_fetch('nms_db', sql=repaired_max_id_sql, filter_keys=[], many=False)
        repaired_max_id = repaired_max_id[0] if repaired_max_id else '0'
        if int(repaired_max_id) < int(server_warning_repaired_id):
            redis_client.hdel(redis_key, 'server_warning_repaired')

        unrepaired_max_id = get_sql_fetch('nms_db', sql=unrepaired_max_id_sql, filter_keys=[], many=False)
        unrepaired_max_id = unrepaired_max_id[0] if unrepaired_max_id else '0'
        if int(unrepaired_max_id) < int(server_warning_unrepaired_id):
            redis_client.hdel(redis_key, 'server_warning_unrepaired')
    except Exception as e:
        logger.exception(e)

    for unrepaired_fetch in unrepaired_fetchall:
        id, code, device_moid, device_type, start_time = unrepaired_fetch
        redis_client.hset(redis_key, 'server_warning_unrepaired', id)
        warning_info = {
            'guid': device_moid,
            'time': start_time,
            'code': code,
            'status': 1,
            'src_type': device_type,
            'dev_type': device_type,
            'report_time': start_time,
        }
        if not nms_not_send_to_es_warning_data.get(code):
            nms_not_send_to_es_warning_data[code] = {
                device_moid: [warning_info]
            }
        else:
            if not nms_not_send_to_es_warning_data[code].get(device_moid):
                nms_not_send_to_es_warning_data[code][device_moid] = [warning_info]
            else:
                nms_not_send_to_es_warning_data[code][device_moid].append(warning_info)
    for repaired_fetch in repaired_fetchall:
        id, code, device_moid, device_type, start_time, resolve_time = repaired_fetch
        redis_client.hset(redis_key, 'server_warning_repaired', id)
        warning_info = {
            'guid': device_moid,
            'time': resolve_time,
            'code': code,
            'status': 0,
            'src_type': device_type,
            'dev_type': device_type,
            'report_time': resolve_time,
        }
        if not nms_not_send_to_es_warning_data.get(code):
            nms_not_send_to_es_warning_data[code] = {
                device_moid: [warning_info]
            }
        else:
            if not nms_not_send_to_es_warning_data[code].get(device_moid):
                nms_not_send_to_es_warning_data[code][device_moid] = [warning_info]
            else:
                nms_not_send_to_es_warning_data[code][device_moid].append(warning_info)

    return nms_not_send_to_es_warning_data


def get_warning_dsls(base_dsl, warning_type=ALARM_TYPE):
    '''
    获取告警码相关的告警数据查询语句
    :return:
    '''
    dsls = []
    sub_codes = get_sub_codes(warning_type)
    last_check_timestamp = redis_client.hget(NMSESRedisKEY, warning_type)
    if not last_check_timestamp:
        logger.warning('can not get %s last check timestamp' % warning_type)
        last_check_timestamp = 'now-1m/m'
    else:
        last_check_timestamp = last_check_timestamp.decode('utf-8')
    logger.info('warning_type:%s, last_check_timestamp:%s' % (warning_type, last_check_timestamp))
    for sub_code in sub_codes:
        dsl = copy.deepcopy(base_dsl)
        if warning_type == 'server':
            dsl['dsl']['query']['bool']['must'].append(
                {"match": {"source.warning_info.code": sub_code.get('sub_code')}},
            )
            if sub_code.get('platform_moid'):
                dsl['dsl']['query']['bool']['must'].append(
                    {"match": {"beat.platform_moid": sub_code.get('platform_moid')}},
                )
            dsl['dsl']['query']['bool']['filter']['range']['beat.estimestamp']['gt'] = last_check_timestamp
            dsls.append(dsl)

        elif warning_type == 'terminal':
            dsl = copy.deepcopy(base_dsl)
            dsl['dsl']['query']['bool']['must'].append(
                {"match": {"source.alarm_info.code_id": sub_code.get('sub_code')}},
            )
            if sub_code.get('platform_moid'):
                dsl['dsl']['query']['bool']['must'].append(
                    {"match": {"beat.platform_moid": sub_code.get('platform_moid')}},
                )
            dsl['dsl']['query']['bool']['filter']['range']['@timestamp']['gt'] = last_check_timestamp
            dsls.append(dsl)
    return dsls


def get_sub_codes(warning_type='server'):
    '''
    获取订阅的告警码
    :return:
    '''
    sub_codes = []

    try:
        connections.close_all()
        if warning_type == 'server':
            sub_warning = SubWarningCodeModel.objects.filter(sub_code__gt=2000)
            sub_codes = [{'sub_code': sub_code.sub_code, 'platform_moid': sub_code.domain_moid} for sub_code in
                         sub_warning]
        elif warning_type == 'terminal':
            sub_warning = SubWarningCodeModel.objects.filter(sub_code__gt=1000, sub_code__lt=2000)
            sub_codes = [{'sub_code': sub_code.sub_code, 'platform_moid': sub_code.domain_moid} for sub_code in
                         sub_warning]
        # 统一逻辑中不处理阈值告警
        for sub_code in sub_codes:
            if sub_code.get('sub_code') in threshold_codes.keys():
                sub_codes.remove(sub_code)
        logger.info('warning_type: %s, sub_codes: %s' % (warning_type, sub_codes))
    except Exception as e:
        logger.exception(e)
    return sub_codes


def query_es(dsls, warning_type=ALARM_TYPE):
    '''
    查询es信息
    :return:
    '''
    responses = []
    m_body = es_client.get_index_header_m_body(*dsls)
    logger.debug(m_body)
    # 记录当前查询时间，供下次查询使用
    now_timestamp = time.time() * 1000
    if m_body:
        try:
            responses = es_client.msearch(body=m_body)['responses']
            redis_client.hset(NMSESRedisKEY, warning_type, now_timestamp)
            logger.info('es查询耗时：{}s'.format(time.time() - (now_timestamp / 1000)))
        except Exception as e:
            logger.exception(e)

    return responses


def get_sql_fetch(db_name, sql, filter_keys, many=False):
    '''
    查询数据库信息
    :param db_name:
    :param sql:
    :param filter_keys:
    :param many:
    :return:
    '''
    st = time.time()
    connections[db_name].close()
    with connections[db_name].cursor() as cursor:
        cursor.execute(sql, filter_keys)
        if many:
            ret = cursor.fetchall()
        else:
            ret = cursor.fetchone()
        logger.info('mysql查询耗时：{}s'.format(time.time() - st))
        return ret


@timer
def get_server_warning_data():
    '''
    获取订阅的告警数据
    :return: {
        '2011':{'{devmoid}':['{warning_info1}','{warning_info2}']},
        '2012':{'{devmoid}':['{warning_info1}','{warning_info2}']}
    }
    '''
    warning_data = {}

    dsls = get_warning_dsls(base_dsl=server_alarm_dsl)
    es_responses = query_es(dsls)
    for response in es_responses:
        warning_code = jsonpath.jsonpath(response, '$..source.warning_info.code')
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
                        guid_buckets = jsonpath.jsonpath(dev_bucket, '$..guid.buckets')
                        if guid_buckets:
                            guid_buckets = guid_buckets[0]
                            for guid_bucket in guid_buckets:
                                warning_infos = jsonpath.jsonpath(guid_bucket, '$..source.warning_info')
                                if warning_infos:
                                    for warning_info in warning_infos:
                                        src_type = jsonpath.jsonpath(guid_bucket, '$..beat.src_type')
                                        dev_type = jsonpath.jsonpath(guid_bucket, '$..source.devtype')
                                        report_time = jsonpath.jsonpath(guid_bucket, '$..source.warning_info.timestamp')
                                        warning_info['src_type'] = src_type[0] if src_type else ''
                                        warning_info['dev_type'] = dev_type[0] if dev_type else ''
                                        warning_info['report_time'] = report_time[0] if report_time else ''
                                        warning_data[warning_code][dev_moid].append(warning_info)

    return warning_data


def notice_handler(send_notice_flag, code, alarm_msg, alarm_type=ALARM_TYPE):
    '''
    通知处理
    :return:
    '''
    if send_notice_flag:
        send_notice(code, alarm_msg, alarm_type=alarm_type)


def generate_alarm(*args, **kwargs):
    '''
    产生告警
    :return:
    '''
    code, dev_moid, device_name, dev_type, src_type, device_ip, machine_room_moid, \
    machine_room_name, guid, level, description, report_time, redis_key, name, suggestion = args
    send_notice_flag = 0
    alarm_msg = {}
    is_exist = ServerWarningUnrepairedModel.objects.filter(
        device_moid=dev_moid,
        code=code,
        device_type=dev_type
    ).exists()

    if is_exist:
        # 告警已存在
        warning_key = redis_client.get(redis_key)
        if not warning_key:
            redis_client.set(redis_key, 'notice',
                             ex=ALARM_INTERVAL)
            # 发送告警通知
            logger.info('告警重复通知，告警码：{code}，告警主机：{device_name}，告警guid：{guid}, 告警描述：{description}'.format(
                code=code, device_name=device_name, guid=guid, description=description))
            alarm_msg = {
                'type': '%s_warning' % ALARM_TYPE,
                'action': '告警重复通知',
                'device_name': device_name,
                'machine_room_name': machine_room_name,
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
        ServerWarningUnrepairedModel.objects.create(
            device_moid=dev_moid,
            guid=guid,
            device_name=device_name,
            device_type=dev_type,
            device_ip=device_ip,
            machine_room_name=machine_room_name,
            machine_room_moid=machine_room_moid,
            code=code,
            level=level,
            description=description,
            start_time=report_time,
        )
        # 发送告警通知
        logger.info('产生告警，告警码：{code}，告警主机：{device_name}，告警guid：{guid}, '
                    '告警描述：{description}，告警时间：{report_time}'.format(
            code=code, device_name=device_name, guid=guid, description=description, report_time=report_time))
        alarm_msg = {
            'type': '%s_warning' % ALARM_TYPE,
            'action': '告警重复通知',
            'device_name': device_name,
            'machine_room_name': machine_room_name,
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
    code, dev_moid, device_name, dev_type, src_type, device_ip, machine_room_moid, \
    machine_room_name, guid, level, description, report_time, redis_key, name, suggestion = args
    send_notice_flag = 0
    alarm_msg = {}
    is_exist = ServerWarningUnrepairedModel.objects.filter(
        device_moid=dev_moid,
        code=code,
        device_type=dev_type
    ).exists()
    if is_exist:
        # 告警已存在
        server_warning_queryset = ServerWarningUnrepairedModel.objects.filter(
            device_moid=dev_moid,
            code=code,
            device_type=dev_type
        ).first()
        warning_start_time = server_warning_queryset.start_time
        try:
            with transaction.atomic():
                # 已修复告警表添加数据
                c_ret = ServerWarningRepairedModel.objects.create(
                    device_moid=server_warning_queryset.device_moid,
                    guid=server_warning_queryset.guid,
                    device_name=server_warning_queryset.device_name,
                    device_type=server_warning_queryset.device_type,
                    device_ip=server_warning_queryset.device_ip,
                    machine_room_name=server_warning_queryset.machine_room_name,
                    machine_room_moid=server_warning_queryset.machine_room_moid,
                    code=server_warning_queryset.code,
                    level=server_warning_queryset.level,
                    description=server_warning_queryset.description,
                    start_time=warning_start_time,
                    resolve_time=report_time,
                )
                logger.info(c_ret)
                # 未修复告警表删除数据
                d_ret = ServerWarningUnrepairedModel.objects.filter(
                    device_moid=dev_moid,
                    code=code,
                    device_type=server_warning_queryset.device_type,
                ).delete()
                logger.info(d_ret)
                # 删除redis_key
                redis_client.delete(redis_key)

                # 发送告警通知
                logger.info(
                    '修复告警，告警码：{code}，告警主机：{device_name}，告警guid：{guid}, '
                    '告警描述：{description}，修复时间：{report_time}'.format(
                        code=code, device_name=device_name, guid=guid, description=description,
                        report_time=report_time))
                alarm_msg = {
                    'type': '%s_warning' % ALARM_TYPE,
                    'action': '修复告警',
                    'device_name': device_name,
                    'machine_room_name': machine_room_name,
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
    guids = jsonpath.jsonpath(warning_data, '$..guid')
    server_moid2name = {}
    if guids:
        sql = '''
        SELECT server_moid,server_type,server_name  
        FROM `server_info` 
        WHERE server_moid IN %s
        '''
        fetchall = get_sql_fetch('luban', sql, filter_keys=[guids, ], many=True)
        server_moid2name = {fetch[0]: fetch[1:] for fetch in fetchall}

    for code, warning in warning_data.items():
        sql = '''
        SELECT mi.machine_moid,mi.machine_name,ii.ip,mi.machine_room_moid,mi.machine_room_name 
        FROM ip_info ii
        LEFT JOIN machine_info mi on mi.id=ii.machine_id
        WHERE mi.machine_moid in %s and ii.flag=1
        '''
        filter_key = list(warning.keys())
        machine_info = {}
        if filter_key:
            fetchall = get_sql_fetch('luban', sql, filter_keys=[filter_key, ], many=True)
            for fetch in fetchall:
                machine_info[fetch[0]] = dict(
                    zip(['device_name', 'device_ip', 'machine_room_moid', 'machine_room_name'], fetch[1:]))
        logger.info(code)
        for dev_moid, warning_info in warning.items():
            for warning_detail in warning_info:
                alarm_status = warning_detail.get('status')
                dev_type = warning_detail.get('dev_type')
                src_type = warning_detail.get('src_type')
                report_time = warning_detail.get('timestamp')
                guid = warning_detail.get('guid')
                device_name = machine_info.get(dev_moid, {}).get('device_name', '')
                device_ip = machine_info.get(dev_moid, {}).get('device_ip', '')
                machine_room_moid = machine_info.get(dev_moid, {}).get('machine_room_moid', '')
                machine_room_name = machine_info.get(dev_moid, {}).get('machine_room_name', '')
                code_queryset = WarningCodeModel.objects.filter(code=code).first()
                level = code_queryset.level
                description = code_queryset.description
                name = code_queryset.name
                suggestion = code_queryset.suggestion
                if code == 2011:
                    # 进程崩溃的特殊处理
                    # 逻辑服务器名称
                    server_type_name = server_moid2name.get(guid, ['sa', device_name])
                    dev_type = server_type_name[0]
                    device_name = server_type_name[1]

                redis_key = '%s_%s' % (dev_moid, code)

                if alarm_status:
                    # 产生告警
                    args = [code, dev_moid, device_name, dev_type, src_type, device_ip, machine_room_moid,
                            machine_room_name, guid, level, description, report_time, redis_key, name, suggestion]
                    if code == 2011:
                        if guid:
                            # 存在guid为空的告警，与网管确认正常不会有，忽略
                            generate_alarm(*args)
                    else:
                        generate_alarm(*args)
                else:
                    # 恢复告警
                    args = [code, dev_moid, device_name, dev_type, src_type, device_ip, machine_room_moid,
                            machine_room_name, guid, level, description, report_time, redis_key, name, suggestion]
                    if code == 2011:
                        if guid:
                            # 存在guid为空的告警，与网管确认正常不会有，忽略
                            repaired_alarm(*args)
                    else:
                        repaired_alarm(*args)


def server_warning_check(period=30, alarm_interval=300):
    if not (isinstance(period, int) and isinstance(alarm_interval, int)):
        raise SyntaxError('参数错误 period,alarm_interval -> int')
    global ALARM_INTERVAL, PERIOD
    ALARM_INTERVAL, PERIOD = alarm_interval, period
    while True:
        try:
            warning_data = get_server_warning_data()
            nms_not_send_to_es_warning_data = get_nms_not_send_to_es_warning_data()
            logger.info(warning_data)
            logger.info(nms_not_send_to_es_warning_data)
            warning_data_handler(warning_data)
            warning_data_handler(nms_not_send_to_es_warning_data)
        except Exception as e:
            logger.exception(e)
        time.sleep(period)
