#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import logging
import logging.handlers
import datetime
import time
import json
import copy
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'ops.settings'
django.setup()

import MySQLdb
from setproctitle import setproctitle

from common.global_func import get_conf
from common.my_elastic import es_client
from common.my_redis import redis_client

logger_name = 'resource_watcher'
logger = logging.getLogger(logger_name)
INTERVAL = 30


def init_logger(logger_name):
    if sys.platform == 'linux':
        log_path = get_conf('log', 'path')
        log_file = '%s/%s.log' % (log_path, logger_name)
    else:
        log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '%s.log' % logger_name)
    if not os.path.exists(os.path.dirname(log_file)):
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    formatter = logging.Formatter(
        '%(levelname)-7s %(asctime)-24s %(filename)s %(lineno)4d: %(message)s')

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    handler = logging.handlers.RotatingFileHandler(
        filename=log_file, encoding='utf-8')
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return handler


class ResourceWatcher:
    '''
    采集媒体支持的会议数量，写入es的platform-nmscollector-{平台域moid}-resource-{%Y-%M-%D}
    索引根据日期变化，每周生成一个
    '''

    def __init__(self):
        '''
        redis数据采集器
        :param machine_room_moids: 机房moid列表
        :param platform_moid: 平台域moid
        '''
        self.logger_name = self.process_name = 'resource_watcher'
        init_logger(self.logger_name)
        self._set_process_name()
        self._validate()
        self.conf_cap = ['4cif', '720p30', '720p60', '1080p30', '1080p60']
        self.mt_cnt = ['8', '192']
        self.platform_moid = ''
        self.machine_room_moids = []
        self.redis_client = redis_client
        self.es_client = es_client
        self.luban_mysql_cursor = self._get_luban_mysql_cursor()
        self._set_platform_and_rooms()

    def _set_process_name(self):
        setproctitle(self.process_name)

    def __del__(self):
        if hasattr(self.redis_client, 'close'):
            self.redis_client.close()
        if hasattr(self.es_client, 'close'):
            self.es_client.close()
        if hasattr(self.luban_mysql_cursor, 'close'):
            self.luban_mysql_cursor.close()

    def _get_redis_client(self):
        try:
            redis_client.ping()
            logger.info(redis_client)
            return redis_client
        except Exception as e:
            logger.error(str(e))
            return False

    def _get_elasticsearch_client(self):
        try:
            es_client.ping()
            return es_client
        except Exception as e:
            logger.error(str(e))
            return False

    def _get_luban_mysql_cursor(self):
        host = get_conf('lubandb', 'host')
        port = get_conf('lubandb', 'port')
        user = get_conf('lubandb', 'user')
        password = get_conf('lubandb', 'password')
        database = get_conf('lubandb', 'database')
        try:
            conn = MySQLdb.connect(
                host=host,
                port=port,
                user=user,
                passwd=password,
                db=database,
            )
            return conn.cursor()
        except Exception as e:
            logger.error(str(e))
            return False

    def _validate(self):
        redis_client_ok = self._get_redis_client()
        elasticsearch_client_ok = self._get_elasticsearch_client()
        luban_mysql_ok = self._get_luban_mysql_cursor()
        if not redis_client_ok:
            raise Exception('无法连接redis')
        if not elasticsearch_client_ok:
            raise Exception('无法连接elasticsearch')
        if not luban_mysql_ok:
            raise Exception('无法连接lubandb')

    def _set_platform_and_rooms(self):
        sql = '''
        SELECT machine_room_moid,domain_moid FROM `machine_room_info` WHERE machine_num>0;
        '''
        self.luban_mysql_cursor.execute(sql, )
        fetchall = self.luban_mysql_cursor.fetchall()
        for fetch in fetchall:
            self.platform_moid = fetch[1]
            if fetch[0] not in self.machine_room_moids:
                self.machine_room_moids.append(fetch[0])

    def register_script(self, script_name):
        lua_path = os.path.join(BASE_DIR, 'lua')
        script_path = os.path.join(lua_path, script_name)
        if os.path.exists(script_path):
            with open(script_path, 'r', encoding='utf-8') as f:
                script = f.read()
            registered_script = redis_client.register_script(script=script)
            return registered_script
        else:
            raise Exception('%s is not exists' % script_path)

    def get_conf_count_from_lua(self, get_conf_cnt):
        '''
        获取可召开的各类型的会议数量
        :param get_conf_cnt: register_script 注册的GetConfCnt.lua脚本
        :return:
        '''
        conf_count_info = {}
        for machine_room_moid in self.machine_room_moids:
            conf_count_info[machine_room_moid] = []
            for conf_cap in self.conf_cap:
                for mt_cnt in self.mt_cnt:
                    ret = get_conf_cnt(keys=(machine_room_moid, conf_cap, mt_cnt))
                    conf_count_info[machine_room_moid].append(
                        {'conf_cap': conf_cap,
                         'mt_cnt': mt_cnt,
                         'conf_type': '%s_%s' % (conf_cap, mt_cnt),
                         'value': ret}
                    )
        return conf_count_info

    def format_to_elasticsearch_data(self, t, conf_count_info):
        timestamp = self.format_timestamp(t)
        all_data = []
        for machine_room_moid in conf_count_info:
            elasticsearch_data = {
                "@timestamp": timestamp,  # 0 时区时间戳
                "source": {
                    "resource_info": {  # 媒体资源信息
                        "traditional_conf_info": {},  # 传统会议信息
                        "port_info": {}  # 端口信息
                    }
                },
                "beat": {
                    "roomid": machine_room_moid,
                    "platform_moid": self.platform_moid,
                }
            }
            for conf_cap in conf_count_info[machine_room_moid]:
                elasticsearch_data['source']['resource_info']['traditional_conf_info'].update(
                    {conf_cap.get('conf_type'): {'free': conf_cap.get('value')}})

            all_data.append(elasticsearch_data)
        return all_data

    def format_timestamp(self, time):
        d = datetime.datetime.fromtimestamp(time, tz=datetime.timezone.utc)
        utc_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        timestamp = d.strftime(utc_format)

        return timestamp

    def get_bulk_data(self, t, all_data):
        '''
        获取elasticsearch bulk格式的数据
        :param t: time.time()
        :param all_data: 要写入elasticsearch的数据列表
        :return: elasticsearch bulk格式的数据
        '''
        now_datetime = datetime.datetime.fromtimestamp(t)
        week_number = now_datetime.isocalendar()[1]
        year = now_datetime.year
        month = now_datetime.month
        base_index = 'rediswatcher-{platform_moid}-{year}.{month}-{week_number}'

        index = copy.deepcopy(base_index).format(
            platform_moid=self.platform_moid,
            year=year,
            month=month,
            week_number=week_number,
        )
        bulk_data = ''
        bulk_method = 'index'
        bulk_header = {bulk_method: {'_index': index, '_type': '_doc'}}
        bulk_header = json.dumps(bulk_header, separators=(',', ':'))
        for data in all_data:
            bulk_data += bulk_header
            bulk_data += '\n'
            bulk_data += json.dumps(data, separators=(',', ':'))
            bulk_data += '\n'

        return bulk_data

    def post_data_to_elasticsearch(self, bulk_data):
        '''
        写入文档
        :param bulk_data: 符合elasticsearch bulk接口数据格式的数据
        :return: 创建结果
        '''
        try:
            return es_client.bulk(body=bulk_data)
        except Exception as e:
            logger.error(str(e))
            raise e


if __name__ == '__main__':
    try:
        watcher = ResourceWatcher()
    except Exception as e:
        logger.error(str(e))
        print(e)
        exit(2)
    else:
        get_conf_cnt = watcher.register_script(script_name='GetConfCnt.lua')
        while True:
            now = time.time()
            try:
                conf_count_info = watcher.get_conf_count_from_lua(get_conf_cnt)
            except Exception as e:
                logger.error(str(e))
                print(e)
                exit(3)
            else:
                all_data = watcher.format_to_elasticsearch_data(now, conf_count_info)
                bulk_data = watcher.get_bulk_data(now, all_data)
                ret = watcher.post_data_to_elasticsearch(bulk_data)
                logger.info(ret)
                time.sleep(INTERVAL)
