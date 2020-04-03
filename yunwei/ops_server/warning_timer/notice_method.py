#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

import logging
import json
import requests
from django.db import connections
from rmq_client import RMQClient
from warning.models import WarningNotifyRuleModel, WarningNotifySubCodeModel, WarningNotifyPhoneModel, \
    WarningNotifyEmailModel, WarningNotifyWeChatModel, WarningCodeModel, WarningNotifyUserModel
from common.global_func import get_conf, get_token

logger = logging.getLogger("warning-timer")

WARNING_LEVEL = {
    'critical': '严重',
    'important': '重要',
    'normal': '一般',
}


def email_notice(users, alarm_detail):
    logger.info('email notice to %s...' % users)
    send_mail_type = 'EMAIL_SEND_INSTANT'
    send_mail_syskey = 'nms_warning_mail'
    send_mail_from = get_conf('sendmail', 'mailfrom') if get_conf('sendmail', 'mailfrom') else 'zhiyou@kedacom.com'
    send_mail_subject = 'ops告警通知'

    alarm_type = alarm_detail.get('alarm_type', '')
    action = alarm_detail.get('action', '')

    text = ''
    payload = {
        "type": send_mail_type,
        "syskey": send_mail_syskey,
        "from": send_mail_from,
        "subject": send_mail_subject,
        "text": text,
        "to": ''
    }
    payload['subject'] = '{}: [{}]'.format(send_mail_subject, action)
    if alarm_type == 'terminal':
        text = [
            '{}: {}'.format('设备名称', alarm_detail.get('device_name', '')),
            '{}: {}'.format('告警描述', alarm_detail.get('desc', '')),
            '{}: {}'.format('告警等级', WARNING_LEVEL.get(alarm_detail.get('level', 'normal'))),
            '{}: {}'.format('所属用户域', alarm_detail.get('domain_name', '')),
            '{}: {}'.format('设备类型', alarm_detail.get('device_type', '')),
            '{}: {}'.format('设备e164号', alarm_detail.get('device_e164', '')),
            '{}: {}'.format('解决建议', alarm_detail.get('suggestion', '')),
        ]
    elif alarm_type == 'server':
        text = [
            '{}: {}'.format('设备名称', alarm_detail.get('device_name', '')),
            '{}: {}'.format('告警描述', alarm_detail.get('desc', '')),
            '{}: {}'.format('告警等级', WARNING_LEVEL.get(alarm_detail.get('level', 'normal'))),
            '{}: {}'.format('所属机房', alarm_detail.get('machine_room_name', '')),
            '{}: {}'.format('设备类型', alarm_detail.get('device_type', '')),
            '{}: {}'.format('设备ip', alarm_detail.get('device_ip', '')),
            '{}: {}'.format('解决建议', alarm_detail.get('suggestion', '')),
        ]
    else:
        text = [
            '{}: {}'.format('设备名称', alarm_detail.get('device_name', '')),
            '{}: {}'.format('告警描述', alarm_detail.get('desc', '')),
            '{}: {}'.format('告警阈值', alarm_detail.get('threshold', '')),
            '{}: {}'.format('当前值', alarm_detail.get('values', '')),
            '{}: {}'.format('告警等级', WARNING_LEVEL.get(alarm_detail.get('level', 'normal'))),
            '{}: {}'.format('所属机房', alarm_detail.get('machine_room_name', '')),
            '{}: {}'.format('设备类型', alarm_detail.get('device_type', '')),
            '{}: {}'.format('设备ip', alarm_detail.get('device_ip', '')),
            '{}: {}'.format('解决建议', alarm_detail.get('suggestion', '')),
        ]
    payload['text'] = '<br>'.join(text)
    try:
        rmqclient = RMQClient()
        for user in users:
            payload['to'] = user
            ret = rmqclient.pub_msg(json.dumps(payload), routing_key='service.email.k', exchange='service.email.ex')
            if ret:
                logger.info('email notice to {} success'.format(user))
            else:
                logger.info('email notice to {} failed'.format(user))

    except Exception as e:
        logger.exception(e)


def sms_notice(users, alarm_detail):
    logger.info('sms notice to %s...' % users)
    sms_models = [
        'NMS_UNREPAIRED_COMMON_WARNING',  # 网管未修复告警模板
        'NMS_REPAIRED_COMMON_WARNING',  # 网管已修复告警模板
        'NMS_UNREPAIRED_THRESHOLD_WARNING',  # 网管未修复阈值告警模板
        'NMS_REPAIRED_THRESHOLD_WARNING',  # 网管已修复阈值告警模板
    ]
    sms_model_params = {
        'NMS_REPAIRED_COMMON_WARNING': {'warning_level': '', 'device_name': '', 'warning_name': '', 'warning_time': ''},
        'NMS_UNREPAIRED_COMMON_WARNING': {'warning_level': '', 'device_name': '', 'warning_name': '',
                                          'warning_time': ''},
        'NMS_REPAIRED_THRESHOLD_WARNING': {'warning_level': '', 'device_name': '', 'warning_name': '',
                                           'warning_threshold': '', 'current_value': '', 'warning_time': ''},
        'NMS_UNREPAIRED_THRESHOLD_WARNING': {'warning_level': '', 'device_name': '', 'warning_name': '',
                                             'warning_threshold': '', 'current_value': '', 'warning_time': ''}
    }

    action = alarm_detail.get('action', '')
    # 模版参数, eval函数将获取下列变量
    warning_level = WARNING_LEVEL.get(alarm_detail.get('level', 'normal'))
    device_name = alarm_detail.get('device_name', '')
    warning_name = alarm_detail.get('name', '')
    warning_time = str(alarm_detail.get('warning_start_time', ''))
    warning_threshold = threshold = alarm_detail.get('threshold', '')
    current_value = [round(_, 3) for _ in alarm_detail.get('values', []) if isinstance(_, float)]
    # 通知手机号码（多个以英文逗号分隔）
    notice_mobiles = ','.join(filter(lambda num: len(num) == 11, users))
    # 获取token使用
    sso_ip = get_conf('auth', 'ip')
    sso_port = get_conf('auth', 'port')
    # 短信接口请求头
    request_headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}

    def get_real_params(sms_model, notice_mobiles, account_token, key_id='nms', key_secret='12345678', brand='1'):
        template_param = sms_model_params.get(sms_model).copy()
        # 模版参数, eval函数将获取下列变量
        logger.info(
            str([warning_level, device_name, warning_name, warning_time, warning_threshold, current_value]))
        for key in template_param:
            # 将实际值写入模板
            try:
                template_param[key] = eval(key)
            except NameError:
                template_param[key] = ''
            except Exception as e:
                logger.exception(e)

        params = {
            'account_token': account_token,
            'params': json.dumps({
                'key_id': key_id,
                'key_secret': key_secret,
                'brand': brand,
                'mobile': notice_mobiles,
                'type': sms_model,
                'template_param': json.dumps(template_param, separators=(',', ':'))
            }, separators=(',', ':'))
        }
        return params

    try:
        account_token = get_token(sso_ip, sso_port)
    except Exception as e:
        logger.exception(e)
        logger.info('sms notice failed')
    else:
        if action == '产生告警':
            # 产生告警
            if threshold:
                # 阈值告警
                sms_model = sms_models[2]
            else:
                # 普通告警
                sms_model = sms_models[0]
        else:
            # 恢复告警
            if threshold:
                # 阈值告警
                sms_model = sms_models[3]
            else:
                # 普通告警
                sms_model = sms_models[1]

        # 发送请求，发出通知短信
        params = get_real_params(sms_model, notice_mobiles, account_token)
        sms_url = 'http://127.0.0.1/apiCore/sms/core/shortMessage'
        # sms_url = 'http://10.67.18.11/apiCore/sms/core/shortMessage'
        logger.info(params)
        try:
            response = requests.request('POST', url=sms_url, data=params, headers=request_headers)
            logger.info(response.text)
            if json.loads(response.text).get('success', 0):
                logger.info('sms notice to [%s] success' % notice_mobiles)
            else:
                logger.info('sms notice failed')
        except Exception as e:
            logger.exception(e)
            logger.info('sms notice failed')


def wechat_notice(users, alarm_detail):
    logger.info('wechat notice to %s...' % users)
    alarm_type = alarm_detail.get('alarm_type', '')
    action = alarm_detail.get('action', '')
    code = alarm_detail.get('code', '')
    level = alarm_detail.get('level', '')
    WARNING_LEVEL.get(alarm_detail.get('level', 'normal'))
    desc = alarm_detail.get('desc', '')
    suggestion = alarm_detail.get('suggestion', '')
    device_name = alarm_detail.get('device_name', '')
    device_type = alarm_detail.get('device_type', '')
    threshold = alarm_detail.get('threshold', '')
    values = alarm_detail.get('values', '')
    if alarm_type == 'terminal':
        description = '\n'.join([
            '{}:{}'.format('告警设备类型', device_type),
            '{}:{}'.format('告警设备名称', device_name),
            '{}:{}'.format('告警描述', desc)
        ])
        payload = {
            "event": "ops_alarm_notify",
            "to_user": users,
            "name": action,
            "number": code,
            "type": alarm_type,
            "level": level,
            "description": description,
            "advice": suggestion,
        }
    elif alarm_type == 'server':
        description = '\n'.join([
            '{}:{}'.format('告警设备类型', device_type),
            '{}:{}'.format('告警设备名称', device_name),
            '{}:{}'.format('告警描述', desc)
        ])
        payload = {
            "event": "ops_alarm_notify",
            "to_user": users,
            "name": action,
            "number": code,
            "type": alarm_type,
            "level": level,
            "description": description,
            "advice": suggestion,
        }
    else:
        description = '\n'.join([
            '{}:{}'.format('告警设备类型', device_type),
            '{}:{}'.format('告警设备名称', device_name),
            '{}:{}'.format('告警描述', desc),
            '{}:{}'.format('告警阈值', threshold),
            '{}:{}'.format('当前数值', values),
        ])
        payload = {
            "event": "ops_alarm_notify",
            "to_user": users,
            "name": action,
            "number": code,
            "type": alarm_type,
            "level": level,
            "description": description,
            "advice": suggestion,
        }
    try:
        rmqclient = RMQClient()
        ret = rmqclient.pub_msg(json.dumps(payload))

        if ret:
            logger.info('wechat notice success')
        else:
            logger.info('wechat notice failed')

    except Exception as e:
        logger.exception(e)


def get_notice_rule(code):
    notice_rule = {
        'wechat': [],
        'sms': [],
        'email': []
    }
    try:
        code = str(code)
    except Exception as e:
        logger.exception(e)
        code = ''
    try:
        rules = WarningNotifyRuleModel.objects.all()
        for rule in rules:
            querysets = WarningNotifySubCodeModel.objects.filter(warning_notify_id=rule.pk)
            sub_codes = [str(queryset.sub_code) for queryset in querysets]
            if code in sub_codes:
                sms_users = [x.user_id for x in WarningNotifyPhoneModel.objects.filter(warning_notify_id=rule.pk)]
                email_users = [x.user_id for x in WarningNotifyEmailModel.objects.filter(warning_notify_id=rule.pk)]
                wechat_users = [x.user_id for x in
                                WarningNotifyWeChatModel.objects.filter(warning_notify_id=rule.pk)]
                notice_rule['wechat'] = wechat_users
                user_info = {user.user_id: {'phone': user.phone, 'email': user.email} for user in
                             WarningNotifyUserModel.objects.all()}
                notice_rule['sms'] = [user_info.get(sms_user, {}).get('phone', '') for sms_user in sms_users]
                notice_rule['email'] = [user_info.get(email_user, {}).get('email', '') for email_user in email_users]

    except Exception as e:
        logger.exception(e)
    return notice_rule


def send_notice(code, alarm_detail, alarm_type='terminal'):
    notice_rule = get_notice_rule(code)
    wechat_users = notice_rule.get('wechat')
    sms_users = notice_rule.get('sms')
    email_users = notice_rule.get('email')
    logger.info('%s %s: %s' % (alarm_type, code, notice_rule))
    if wechat_users:
        wechat_notice(wechat_users, alarm_detail)
    if sms_users:
        sms_notice(sms_users, alarm_detail)
    if email_users:
        email_notice(email_users, alarm_detail)
