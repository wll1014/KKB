#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

import time
import logging
import copy
import json
import jsonpath
import datetime
from django.db import connections, transaction
from common.my_elastic import es_client
from redis_client import redis_client
from es_ql_threshold import *
from notice_method import send_notice
from warning.models import WarningThresholdModel, SubWarningCodeModel, ServerWarningRepairedModel, \
    ServerWarningUnrepairedModel, WarningCodeModel

logger = logging.getLogger("warning-timer")

ALARM_TYPE = 'threshold'
threshold_codes = {
    '2002': [copy.deepcopy(cpu_dsl), copy.deepcopy(cpu_core_idle_dsl)],
    '2003': [copy.deepcopy(mem_dsl)],
    '2007': [copy.deepcopy(mp_dsl)],
    '2018': [copy.deepcopy(filesystem_used_dsl)],
    '2019': [copy.deepcopy(network_in_dsl), copy.deepcopy(network_out_dsl)],
    '2025': [copy.deepcopy(mediaresource_mixer_dsl), copy.deepcopy(mps_mixer_dsl)],
    '2026': [copy.deepcopy(mediaresource_vmp_dsl), copy.deepcopy(mps_vmp_dsl)],
    '2045': [copy.deepcopy(disk_age_dsl)],
    '2047': [copy.deepcopy(disk_write_dsl)],
    '2059': [copy.deepcopy(vrs_info_dsl)],
    '2060': [copy.deepcopy(vrs_info_dsl)],
    '2061': [copy.deepcopy(live_viewer_dsl)],
    '2062': [copy.deepcopy(dcs_confnum_dsl)],
    '2063': [copy.deepcopy(dcs_mtnum_dsl)],
    '2064': [copy.deepcopy(ap_dsl)],
}


def threshold_warning_check(period=30, alarm_interval=300):
    if not (isinstance(period, int) and isinstance(alarm_interval, int)):
        raise SyntaxError('参数错误 period,alarm_interval -> int')
    while True:
        logger.info('begin threshold_warning_check...')
        try:
            connections.close_all()

            sub_terminal_warning = SubWarningCodeModel.objects.filter(sub_code__in=threshold_codes.keys())
            sub_codes = [{'sub_code': sub_code.sub_code, 'platform_moid': sub_code.domain_moid} for sub_code in
                         sub_terminal_warning]
            machine_metric_check(sub_codes, threshold_codes, alarm_interval)
            platform_metric_check(sub_codes, threshold_codes, alarm_interval)

        except Exception as e:
            logger.exception(e)

        time.sleep(period)


def platform_metric_check(sub_codes, threshold_codes, alarm_interval):
    logger.info('platform_metric_check start...')
    threshold_queryset = WarningThresholdModel.objects.all().first()

    vmp = threshold_queryset.vmp  # 2026
    mixer = threshold_queryset.mixer  # 2025
    mp = threshold_queryset.mp  # 2007
    ap = threshold_queryset.ap  # 2064
    video_num = threshold_queryset.video_num  # 2059
    live_num = threshold_queryset.live_num  # 2060
    viewer_num = threshold_queryset.viewer_num  # 2061
    dcs_conf_num = threshold_queryset.dcs_conf_num  # 2062
    dcs_user_num = threshold_queryset.dcs_user_num  # 2063

    platform_dsls = []
    for sub_code in sub_codes:
        if str(sub_code.get('sub_code')) in ['2025', '2026', '2007', '2059', '2060', '2061', '2062', '2063', '2064']:
            platform_dsls += threshold_codes.get(str(sub_code.get('sub_code')))

    if platform_dsls:
        m_body = es_client.get_index_header_m_body(*platform_dsls)
        logger.info(m_body)
        try:
            ret = es_client.msearch(body=m_body)
            responses = ret['responses']
            # 获取机房moid转换机房名称
            sql = '''
            SELECT machine_room_moid,machine_room_name
            FROM machine_room_info
            '''
            filter_keys = []
            fetchall = get_sql_fetch('luban', sql, filter_keys, many=True)
            machine_room_moid2name = {ret[0]: ret[1] for ret in fetchall}
            try:
                if jsonpath.jsonpath(responses, '$..total_vmp'):
                    # 合成器
                    code = '2026'
                    mediaresource_response = {}
                    mps_response = {}
                    for response in responses:
                        if jsonpath.jsonpath(response, '$..mediaresource_info.total_vmp'):
                            mediaresource_response = response
                        if jsonpath.jsonpath(response, '$..mps_resource_info.total_vmp'):
                            mps_response = response
                    mediaresource_room_bucksts = jsonpath.jsonpath(mediaresource_response, '$..room.buckets')
                    room_vmp = {}
                    if mediaresource_room_bucksts:
                        mediaresource_room_bucksts = mediaresource_room_bucksts[0]
                        for room_buckst in mediaresource_room_bucksts:
                            room_vmp[room_buckst.get('key', '')] = {'total': 0, 'used': 0}
                    mps_room_bucksts = jsonpath.jsonpath(mps_response, '$..room.buckets')
                    if mps_room_bucksts:
                        mps_room_bucksts = mps_room_bucksts[0]
                        for room_buckst in mps_room_bucksts:
                            room_vmp[room_buckst.get('key')] = {'total': 0, 'used': 0}

                    for machine_room_moid in room_vmp:
                        # 唯一标识使用 告警码_机房moid
                        device_moid = '%s%s' % (code, machine_room_moid)
                        machine_moids = {
                            device_moid: ['', '', machine_room_moid,
                                          machine_room_moid2name.get(machine_room_moid, ''), '']}
                        mps_total_vmp = jsonpath.jsonpath(mps_response, '$..mps_resource_info.total_vmp')
                        mps_used_vmp = jsonpath.jsonpath(mps_response, '$..mps_resource_info.used_vmp')
                        mediaresource_total_vmp = jsonpath.jsonpath(mediaresource_response,
                                                                    '$..mediaresource_info.total_vmp')
                        mediaresource_used_vmp = jsonpath.jsonpath(mediaresource_response,
                                                                   '$..mediaresource_info.used_vmp')
                        values = [0]
                        if mps_total_vmp:
                            room_vmp[machine_room_moid]['total'] += sum(mps_total_vmp)
                            room_vmp[machine_room_moid]['used'] += sum(mps_used_vmp)
                        if mediaresource_total_vmp:
                            room_vmp[machine_room_moid]['total'] += sum(mediaresource_total_vmp)
                            room_vmp[machine_room_moid]['used'] += sum(mediaresource_used_vmp)
                        if room_vmp[machine_room_moid]['total']:
                            values.append(room_vmp[machine_room_moid]['used'] / room_vmp[machine_room_moid]['total'])
                        logger.info(room_vmp)
                        threshold = vmp * 0.01
                        ret = warning_handle(values, threshold, device_moid, machine_moids, code, alarm_interval)

            except Exception as e:
                logger.error('合成器告警错误')
                logger.exception(e)

            try:
                if jsonpath.jsonpath(responses, '$..total_mixer'):
                    # 混音器
                    code = '2025'
                    mediaresource_response = {}
                    mps_response = {}
                    for response in responses:
                        if jsonpath.jsonpath(response, '$..mediaresource_info.total_mixer'):
                            mediaresource_response = response
                        if jsonpath.jsonpath(response, '$..mps_resource_info.total_mixer'):
                            mps_response = response

                    mediaresource_room_bucksts = jsonpath.jsonpath(mediaresource_response, '$..room.buckets')
                    room_mixer = {}
                    if mediaresource_room_bucksts:
                        mediaresource_room_bucksts = mediaresource_room_bucksts[0]
                        for room_buckst in mediaresource_room_bucksts:
                            room_mixer[room_buckst.get('key', '')] = {'total': 0, 'used': 0}
                    mps_room_bucksts = jsonpath.jsonpath(mps_response, '$..room.buckets')
                    if mps_room_bucksts:
                        mps_room_bucksts = mps_room_bucksts[0]
                        for room_buckst in mps_room_bucksts:
                            room_mixer[room_buckst.get('key')] = {'total': 0, 'used': 0}

                    for machine_room_moid in room_mixer:
                        # 唯一标识使用 告警码_机房moid
                        device_moid = '%s%s' % (code, machine_room_moid)
                        machine_moids = {
                            device_moid: ['', '', machine_room_moid,
                                          machine_room_moid2name.get(machine_room_moid, ''), '']}
                        mps_total_mixer = jsonpath.jsonpath(mps_response, '$..mps_resource_info.total_mixer')
                        mps_used_mixer = jsonpath.jsonpath(mps_response, '$..mps_resource_info.used_mixer')
                        mediaresource_total_mixer = jsonpath.jsonpath(mediaresource_response,
                                                                      '$..mediaresource_info.total_mixer')
                        mediaresource_used_mixer = jsonpath.jsonpath(mediaresource_response,
                                                                     '$..mediaresource_info.used_mixer')
                        values = [0]
                        if mps_total_mixer:
                            room_mixer[machine_room_moid]['total'] += sum(mps_total_mixer)
                            room_mixer[machine_room_moid]['used'] += sum(mps_used_mixer)
                        if mediaresource_total_mixer:
                            room_mixer[machine_room_moid]['total'] += sum(mediaresource_total_mixer)
                            room_mixer[machine_room_moid]['used'] += sum(mediaresource_used_mixer)
                        if room_mixer[machine_room_moid]['total']:
                            values.append(
                                room_mixer[machine_room_moid]['used'] / room_mixer[machine_room_moid]['total'])
                        logger.info(room_mixer)
                        threshold = mixer * 0.01
                        ret = warning_handle(values, threshold, device_moid, machine_moids, code, alarm_interval)
            except Exception as e:
                logger.error('混音器告警错误')
                logger.exception(e)
            try:
                if jsonpath.jsonpath(responses, '$..mp_info'):
                    # 媒体端口
                    code = '2007'
                    device_moid, machine_moids = '', {}
                    mp_info = jsonpath.jsonpath(responses, '$..mp_info')[0]
                    values = []
                    if mp_info.get('total_h264'):
                        values.append(mp_info.get('used_h264') / mp_info.get('total_h264'))
                    if mp_info.get('total_h265'):
                        values.append(mp_info.get('used_h265') / mp_info.get('total_h265'))
                    threshold = mp * 0.01
                    ret = warning_handle(values, threshold, device_moid, machine_moids, code, alarm_interval)
            except Exception as e:
                logger.error('媒体端口告警错误')
                logger.exception(e)
            try:
                if jsonpath.jsonpath(responses, '$..ap_info'):
                    # 接入端口
                    code = '2064'
                    device_moid, machine_moids = '', {}
                    ap_info = jsonpath.jsonpath(responses, '$..ap_info')[0]
                    values = []
                    if ap_info.get('total'):
                        values.append(ap_info.get('used') / ap_info.get('total'))
                    threshold = ap * 0.01
                    ret = warning_handle(values, threshold, device_moid, machine_moids, code, alarm_interval)
            except Exception as e:
                logger.error('接入端口告警错误')
                logger.exception(e)
            try:
                if jsonpath.jsonpath(responses, '$..vrs_recroomocp'):
                    # 录像并发数
                    code = '2059'
                    device_moid, machine_moids = '', {}
                    vrs_info = jsonpath.jsonpath(responses, '$..vrs_info')[0]
                    values = []
                    if vrs_info.get('vrs_recroomocp'):
                        values.append(vrs_info.get('vrs_recroomocp'))
                    threshold = video_num
                    ret = warning_handle(values, threshold, device_moid, machine_moids, code, alarm_interval)
            except Exception as e:
                logger.error('录像并发数告警错误')
                logger.exception(e)
            try:
                if jsonpath.jsonpath(responses, '$..vrs_html5lcastocp') or \
                        jsonpath.jsonpath(responses, '$..vrs_lcastocp'):
                    # 直播并发数
                    code = '2060'
                    device_moid, machine_moids = '', {}
                    vrs_info = jsonpath.jsonpath(responses, '$..vrs_info')[0]
                    values = []
                    html5_num = 0
                    asf_num = 0
                    if vrs_info.get('vrs_html5lcastocp'):
                        html5_num += vrs_info.get('vrs_html5lcastocp')
                    if vrs_info.get('vrs_lcastocp'):
                        asf_num += vrs_info.get('vrs_lcastocp')
                    values.append(html5_num + asf_num)
                    threshold = live_num
                    ret = warning_handle(values, threshold, device_moid, machine_moids, code, alarm_interval)
            except Exception as e:
                logger.error('直播并发数告警错误')
                logger.exception(e)
            try:
                if jsonpath.jsonpath(responses, '$..user_state'):
                    # 观看直播人数并发数
                    code = '2061'
                    device_moid, machine_moids = '', {}
                    user_states = jsonpath.jsonpath(responses, '$..user_state')
                    values = [user_states.count(1)]
                    threshold = viewer_num
                    ret = warning_handle(values, threshold, device_moid, machine_moids, code, alarm_interval)
            except Exception as e:
                logger.error('观看直播人数告警错误')
                logger.exception(e)
            try:
                if jsonpath.jsonpath(responses, '$..source.resinfo.confnum'):
                    # 数据协作会议并发数
                    code = '2062'
                    device_moid, machine_moids = '', {}
                    values = jsonpath.jsonpath(responses, '$..source.resinfo.confnum')
                    threshold = dcs_conf_num
                    ret = warning_handle(values, threshold, device_moid, machine_moids, code, alarm_interval)
            except Exception as e:
                logger.error('数据协作会议数告警错误')
                logger.exception(e)
            try:
                if jsonpath.jsonpath(responses, '$..source.resinfo.mtnum'):
                    # 数据协作人数并发数
                    code = '2063'
                    device_moid, machine_moids = '', {}
                    values = jsonpath.jsonpath(responses, '$..source.resinfo.mtnum')
                    threshold = dcs_user_num
                    ret = warning_handle(values, threshold, device_moid, machine_moids, code, alarm_interval)
            except Exception as e:
                logger.error('数据协作人数告警错误')
                logger.exception(e)
        except Exception as e:
            logger.exception(e)


def machine_metric_check(sub_codes, threshold_codes, alarm_interval):
    logger.info('machine_metric_check start...')
    threshold_queryset = WarningThresholdModel.objects.all().first()
    cpu = threshold_queryset.cpu  # 2002
    memory = threshold_queryset.memory  # 2003
    disk = threshold_queryset.disk  # 2018

    diskwritespeed = threshold_queryset.diskwritespeed  # 2047
    rateofflow = threshold_queryset.rateofflow  # 2019
    diskage = threshold_queryset.diskage  # 2045

    machine_dsls = []
    sql = '''
    SELECT mi.machine_moid,mi.machine_name,ii.ip,mi.machine_room_moid,mi.machine_room_name,mi.machine_type
    FROM ip_info ii
    LEFT JOIN machine_info mi on mi.id=ii.machine_id
    WHERE ii.flag=1
    '''
    filter_keys = []
    ret = get_sql_fetch('luban', sql, filter_keys, many=True)
    machine_moids = {moid[0]: moid[1:] for moid in ret}

    for sub_code in sub_codes:
        if str(sub_code.get('sub_code')) in ['2002', '2003', '2018', '2019', '2045', '2047']:
            machine_dsls += threshold_codes.get(str(sub_code.get('sub_code')))
    if machine_dsls:
        m_body = es_client.get_index_header_m_body(*machine_dsls)
        logger.info(m_body)
        try:
            ret = es_client.msearch(body=m_body)
            for response in ret['responses']:
                if jsonpath.jsonpath(response, '$..write_bytes'):
                    # 磁盘写入速率
                    code = '2047'
                    buckets = jsonpath.jsonpath(response, '$..aggregations.machine_terms.buckets')[0]
                    for bucket in buckets:
                        device_moid = bucket.get('key')
                        if bucket.get('key') in machine_moids.keys():
                            values = jsonpath.jsonpath(bucket, '$..normalized_value')
                            threshold = diskwritespeed * 1024 * 1024
                            ret = warning_handle(values, threshold, device_moid, machine_moids, code, alarm_interval)

                if jsonpath.jsonpath(response, '$..in_bytes') or jsonpath.jsonpath(response, '$..out_bytes'):
                    # 网口吞吐
                    code = '2019'
                    buckets = jsonpath.jsonpath(response, '$..aggregations.machine_terms.buckets')[0]
                    for bucket in buckets:
                        device_moid = bucket.get('key')
                        if bucket.get('key') in machine_moids.keys():
                            values = jsonpath.jsonpath(bucket, '$..normalized_value')
                            threshold = rateofflow * 1024 * 1024
                            ret = warning_handle(values, threshold, device_moid, machine_moids, code, alarm_interval)

                if jsonpath.jsonpath(response, '$..source.diskage.age'):
                    # 磁盘寿命
                    code = '2045'
                    buckets = jsonpath.jsonpath(response, '$..buckets')[0]
                    for bucket in buckets:
                        device_moid = bucket.get('key')
                        if bucket.get('key') in machine_moids.keys():
                            values = jsonpath.jsonpath(bucket, '$..age')
                            threshold = diskage
                            ret = warning_handle(values, threshold, device_moid, machine_moids, code, alarm_interval,
                                                 value_gt_threshold=False)
                if jsonpath.jsonpath(response, '$..avg_cpu_total'):
                    # cpu总使用率
                    code = '2002'
                    buckets = jsonpath.jsonpath(response, '$..buckets')[0]
                    for bucket in buckets:
                        device_moid = bucket.get('key')
                        if bucket.get('key') in machine_moids.keys():
                            values = [bucket.get('avg_cpu_total').get('value') / bucket.get('avg_core').get('value')]
                            threshold = cpu * 0.01
                            ret = warning_handle(values, threshold, device_moid, machine_moids, code, alarm_interval)

                if jsonpath.jsonpath(response, '$..avg_cpu_core_idle'):
                    # cpu每个核的空闲率
                    code = '2002'
                    buckets = jsonpath.jsonpath(response, '$..aggregations.machine_terms.buckets')[0]
                    for bucket in buckets:
                        device_moid = bucket.get('key')
                        if device_moid in machine_moids.keys():
                            values = jsonpath.jsonpath(bucket, '$..value')
                            threshold = cpu * 0.01
                            values = [1 - value for value in values]
                            ret = warning_handle(values, threshold, device_moid, machine_moids, code, alarm_interval)

                if jsonpath.jsonpath(response, '$..avg_mem'):
                    # 内存使用率
                    code = '2003'
                    buckets = jsonpath.jsonpath(response, '$..buckets')[0]
                    for bucket in buckets:
                        device_moid = bucket.get('key')
                        if bucket.get('key') in machine_moids.keys():
                            values = [bucket.get('avg_mem').get('value')]
                            threshold = memory * 0.01
                            ret = warning_handle(values, threshold, device_moid, machine_moids, code, alarm_interval)

                if jsonpath.jsonpath(response, '$..avg_filesystem_used'):
                    # 磁盘使用率
                    code = '2018'
                    buckets = jsonpath.jsonpath(response, '$..aggregations.machine_terms.buckets')[0]
                    for bucket in buckets:
                        device_moid = bucket.get('key')
                        if bucket.get('key') in machine_moids.keys():
                            values = jsonpath.jsonpath(bucket, '$..value')
                            threshold = disk * 0.01
                            ret = warning_handle(values, threshold, device_moid, machine_moids, code, alarm_interval)

        except Exception as e:
            logger.exception(e)


def get_sql_fetch(db_name, sql, filter_keys, many=False):
    connections[db_name].close()
    with connections[db_name].cursor() as cursor:
        cursor.execute(sql, filter_keys)
        if many:
            ret = cursor.fetchall()
        else:
            ret = cursor.fetchone()
        return ret


def get_warning_info(code):
    code_queryset = WarningCodeModel.objects.filter(code=code).first()
    level = code_queryset.level
    description = code_queryset.description
    suggestion = code_queryset.suggestion
    name = code_queryset.name

    return level, description, suggestion, name


def warning_handle(values, threshold, device_moid, machine_moids, code, alarm_interval, value_gt_threshold=True):
    redis_key = '%s_%s' % (device_moid, code)
    if machine_moids.get(device_moid) and len(machine_moids.get(device_moid)) >= 5:
        device_name, device_ip, machine_room_moid, machine_room_name, device_type = machine_moids.get(device_moid)
    else:
        device_name, device_ip, machine_room_moid, machine_room_name, device_type = ['' for _ in range(5)]
    # device_name = machine_moids.get(device_moid)[0]
    # device_ip = machine_moids.get(device_moid)[1]
    # machine_room_moid = machine_moids.get(device_moid)[2]
    # machine_room_name = machine_moids.get(device_moid)[3]
    # device_type = machine_moids.get(device_moid)[4]
    level, description, suggestion, name = get_warning_info(code)
    if code in [str(_) for _ in range(2059, 2064)]:
        description = '{}({}个)'.format(description, threshold)
    elif code in ['2019', '2047']:
        description = '{}({}M)'.format(description, threshold / 1024 / 1024)
    elif code == '2045':
        description = '{}({}%)'.format(description, threshold)
    else:
        description = '{}({}%)'.format(description, threshold * 100)
    warning_flag = 0

    if values is False:
        values = []
    if not value_gt_threshold:
        values, threshold = threshold, values
    for value in values:
        if value > threshold:
            warning_flag = 1
            break

    now_datetime = datetime.datetime.now()
    if warning_flag:
        logger.info('%s: %s 阈值超出 %s----%s' % (code, device_name, values, threshold))
        is_exist = ServerWarningUnrepairedModel.objects.filter(
            device_moid=device_moid,
            code=code
        ).exists()
        if is_exist:
            # 告警已存在
            queryset = ServerWarningUnrepairedModel.objects.filter(
                device_moid=device_moid,
                code=code
            ).first()
            warning_start_time = queryset.start_time
            warning_key = redis_client.get(redis_key)
            if not warning_key:
                redis_client.set(redis_key, 'notice',
                                 ex=alarm_interval)
                # 发送告警通知
                alarm_detail = {
                    'type': '%s_warning' % ALARM_TYPE,
                    'action': '告警重复通知',
                    'device_name': device_name,
                    'threshold': threshold,
                    'values': values,
                    'device_ip': device_ip,
                    'device_type': device_type,
                    'machine_room_name': machine_room_name,
                    'name': name,
                    'alarm_type': ALARM_TYPE,
                    'code': code,
                    'level': level,
                    'desc': description,
                    'suggestion': suggestion,
                    'warning_start_time': warning_start_time,
                    'warning_resolve_time': '',
                }
                send_notice(code, alarm_detail, alarm_type=ALARM_TYPE)
                return True
            else:
                return False
        else:
            # 告警不存在
            redis_client.set(redis_key, 'notice', ex=alarm_interval)
            ServerWarningUnrepairedModel.objects.create(
                device_moid=device_moid,
                device_name=device_name,
                device_type=device_type,
                device_ip=device_ip,
                machine_room_name=machine_room_name,
                machine_room_moid=machine_room_moid,
                code=code,
                level=level,
                description=description,
                start_time=now_datetime,
            )
            alarm_detail = {
                'type': '%s_warning' % ALARM_TYPE,
                'action': '产生告警',
                'device_name': device_name,
                'threshold': threshold,
                'values': values,
                'device_ip': device_ip,
                'device_type': device_type,
                'machine_room_name': machine_room_name,
                'name': name,
                'alarm_type': ALARM_TYPE,
                'code': code,
                'level': level,
                'desc': description,
                'suggestion': suggestion,
                'warning_start_time': now_datetime,
                'warning_resolve_time': '',
            }
            send_notice(code, alarm_detail, alarm_type=ALARM_TYPE)
            return True
    else:
        logger.info('%s: %s 阈值未超出 %s----%s' % (code, device_name, values, threshold))
        server_warning_queryset = ServerWarningUnrepairedModel.objects.filter(
            device_moid=device_moid,
            code=code
        ).first()
        if server_warning_queryset:
            try:
                warning_start_time = server_warning_queryset.start_time
                with transaction.atomic():
                    # 已修复告警表添加数据
                    ServerWarningRepairedModel.objects.create(
                        device_moid=server_warning_queryset.device_moid,
                        device_name=server_warning_queryset.device_name,
                        device_type=server_warning_queryset.device_type,
                        device_ip=server_warning_queryset.device_ip,
                        machine_room_name=server_warning_queryset.machine_room_name,
                        machine_room_moid=server_warning_queryset.machine_room_moid,
                        code=server_warning_queryset.code,
                        level=server_warning_queryset.level,
                        description=server_warning_queryset.description,
                        start_time=warning_start_time,
                        resolve_time=now_datetime,
                    )
                    # 未修复告警表删除数据
                    ServerWarningUnrepairedModel.objects.filter(
                        device_moid=device_moid,
                        code=code
                    ).delete()
                    # 删除redis_key
                    redis_client.delete(redis_key)

                    # 发送告警通知
                    alarm_detail = {
                        'type': '%s_warning' % ALARM_TYPE,
                        'action': '恢复告警',
                        'device_name': device_name,
                        'threshold': threshold,
                        'values': values,
                        'device_ip': device_ip,
                        'device_type': device_type,
                        'machine_room_name': machine_room_name,
                        'name': name,
                        'alarm_type': ALARM_TYPE,
                        'code': code,
                        'level': level,
                        'desc': description,
                        'suggestion': suggestion,
                        'warning_start_time': warning_start_time,
                        'warning_resolve_time': now_datetime,
                    }
                    send_notice(code, alarm_detail, alarm_type=ALARM_TYPE)
                    return True
            except Exception as e:
                logger.exception(e)
                return False
        else:
            return False
