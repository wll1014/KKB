#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

import configparser
import logging
import os
import sys
import subprocess
import datetime
from django.utils import timezone

logger = logging.getLogger("ops." + __name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class NewConfigParser(configparser.ConfigParser):
    def optionxform(self, optionstr):
        return optionstr

    def add_section(self, section):
        if section not in self.sections():
            self._validate_value_types(section=section)
            super().add_section(section)


def get_conf(section, key=None, path=None):
    '''
    读取配置文件内容
    :param section:
    :param key:
    :param path: 配置文件相对项目根目录的路径，默认为conf/ops.ini
    :return: 配置文件内容，如为整数，则返回int类型
    '''
    conf = NewConfigParser()
    if path:
        conf_path = path
    else:
        conf_path = os.path.join(BASE_DIR, 'conf/ops.ini')
    conf.read(conf_path, 'utf-8')

    if key is not None:
        # 获取指定section的key的值
        try:
            str_val = conf.get(section, key)
        except Exception as e:
            logger.error(e)
            str_val = None
        if str_val:
            if str_val.isdigit():
                return int(str_val)
        return str_val
    else:
        # 获取指定section的内容
        if conf.has_section(section):
            return conf[section]
        else:
            return None


def get_token(ip, port=80):
    '''
    获取登录token
    :param ip: sso地址
    :param port: sso端口
    :return: token
    '''
    import requests
    from lxml import etree
    params = {
        'oauth_consumer_key': 'LuBan',
        'oauth_consumer_secret': '12345678'
    }

    baseurl = 'http://%s:%s/' % (ip, port)
    url = baseurl + 'apiCore/accountToken'
    token = ''
    try:
        ret = requests.post(url, params=params, timeout=3)
        html_dom = etree.fromstring(ret.text)
        token = html_dom.xpath('/OAuthData/accountToken/text()')[0]
        ret.close()
    except Exception as e:
        logger.error(str(e))
    return token


def init_sidebar():
    # 初始化侧边菜单栏
    from sidebar.models import ModelSidebar
    manage_path = os.path.join(BASE_DIR, 'manage.py')
    dumpdata_path = os.path.join(BASE_DIR, 'sidebar', 'sidebar.json')
    status, python3_path = subprocess.getstatusoutput('which python3')
    if 'no' in python3_path:
        python3_path = '/opt/midware/python3/bin/python3'
    try:
        sidebar = ModelSidebar.objects.all()
        if not sidebar:
            # 不存在则加载导出的json
            if os.path.exists(manage_path) and os.path.exists(dumpdata_path) and os.path.exists(python3_path):
                status, data = subprocess.getstatusoutput(
                    '%s %s loaddata %s' % (python3_path, manage_path, dumpdata_path))
                logger.debug('%s %s loaddata %s' % (python3_path, manage_path, dumpdata_path))
                logger.debug('status: %s , data: %s' % (status, data))
                sidebar = ModelSidebar.objects.all()
            else:
                logger.error('please check %s/%s/%s is available!')
        return sidebar
    except Exception as e:
        logger.error(str(e))
        return []


def get_response(is_success=1, data=None, error_code=10000, error_msg=''):
    '''
    获取response的字典，默认未知错误代码10000
    :param is_success: 是否成功 0：失败， 1： 成功
    :param data: json格式数据
    :param error_code: 错误码
    :return: response的字典
    '''
    response = dict()
    response['success'] = is_success

    if is_success:
        if data is not None:
            response['data'] = data
    else:
        if isinstance(error_code, int):
            error_code = str(error_code)
        response['error_code'] = error_code
        if data is not None:
            response['data'] = data
        if error_msg:
            response['msg'] = error_msg
        else:
            response['msg'] = ERROR.get(error_code, '')

    return response


def format_timestamp(time, utc=False):
    d = datetime.datetime.fromtimestamp(time, tz=datetime.timezone.utc if utc else None)
    utc_format = "%Y%m%d%H%M%S"
    timestamp = d.strftime(utc_format)

    return timestamp


def get_now_near_30min(format_timestamp=False):
    '''
    获取当前时间之前，最近的 整30分钟的 setting中 timezone相同时区的时间
    :param format_timestamp: Ture 则返回毫秒级时间戳，否则返回 datetime
    :return:
    '''

    now = timezone.datetime.now(tz=timezone.get_current_timezone())

    now_minute = now.minute
    if now_minute > 30:
        now_minute = 30
    else:
        now_minute = 0

    now_near_30min = now.replace(minute=now_minute, second=0, microsecond=0)
    if format_timestamp:
        return now_near_30min.timestamp() * 1000
    return now_near_30min


def get_timestamp_near_30min(start_time, format_timestamp=False):
    '''
    获取start_time时间之前，最近的 整30分钟的 setting中 timezone相同时区的时间
    :param format_timestamp: Ture 则返回毫秒级时间戳，否则返回 datetime
    :return:
    '''
    try:
        start_time = float(start_time)
    except Exception as e:
        err = str(e)
        logger.error(err)
        raise TypeError('开始时间错误')
    else:
        now = timezone.datetime.fromtimestamp(start_time / 1000, tz=timezone.get_current_timezone())

        now_minute = now.minute
        if now_minute > 30:
            now_minute = 30
        else:
            now_minute = 0

        now_near_30min = now.replace(minute=now_minute, second=0, microsecond=0)
        if format_timestamp:
            return now_near_30min.timestamp() * 1000
        return now_near_30min


def get_timestamp_near_15min(start_time, format_timestamp=False):
    '''
    获取start_time时间之前，最近的 整15分钟的 setting中 timezone相同时区的时间
    :param format_timestamp: Ture 则返回毫秒级时间戳，否则返回 datetime
    :return:
    '''
    try:
        start_time = float(start_time)
    except Exception as e:
        err = str(e)
        logger.error(err)
        raise TypeError('开始时间错误')
    else:
        now = timezone.datetime.fromtimestamp(start_time / 1000, tz=timezone.get_current_timezone())

        now_minute = now.minute
        if now_minute >= 45:
            now_minute = 45
        elif now_minute >= 30:
            now_minute = 30
        elif now_minute >= 15:
            now_minute = 15
        else:
            now_minute = 0

        now_near_15min = now.replace(minute=now_minute, second=0, microsecond=0)
        if format_timestamp:
            return now_near_15min.timestamp() * 1000
        return now_near_15min


def get_now_near_15min(format_timestamp=False):
    '''
    获取当前时间之前，最近的 整15分钟的 setting中 timezone相同时区的时间
    :param format_timestamp: Ture 则返回毫秒级时间戳，否则返回 datetime
    :return:
    '''

    now = timezone.datetime.now(tz=timezone.get_current_timezone())

    now_minute = now.minute
    if now_minute >= 45:
        now_minute = 45
    elif now_minute >= 30:
        now_minute = 30
    elif now_minute >= 15:
        now_minute = 15
    else:
        now_minute = 0

    now_near_15min = now.replace(minute=now_minute, second=0, microsecond=0)
    if format_timestamp:
        return now_near_15min.timestamp() * 1000
    return now_near_15min


es_hosts = get_conf('elasticsearch', 'hosts')
ERROR = {
    '10000': ' 未知错误',
    '10001': ' ElasticSearch中无对应数据',
    '10002': ' 无法连接到ElasticSearch [%s]' % es_hosts,
    '10003': ' token 认证失败',
    '10004': ' 无法获取luban数据',
    '10005': ' ops mysql 操作失败',
    '10006': ' 数据添加重复',
    '10007': ' 数据格式错误',
    '10008': ' 参数错误',
    '10009': ' 默认分组不支持修改',
    '10010': '参数错误',
    '10011': '无法连接平台redis',
    '10012': '会议未召开或终端未入会',
    '10013': '一键抓包失败',
    '10014': '文件分发失败',

    '30001': '参数不能为空',
    '30002': '参数格式错误',

    '20000': 'DSL生成错误',
    '10404': ' Not found.',

    '99999': '平台接口请求错误',
}
