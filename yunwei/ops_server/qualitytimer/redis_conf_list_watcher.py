#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
订阅redis 'notify' 频道接收创会/结会消息 并计算会议质量
"""

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'ops.settings'
django.setup()

import re
import json
import time
import logging
import datetime
import threading
import setproctitle
from daemonize import Daemonize
from ops.settings import BASE_DIR
from django.utils import timezone
from common.global_func import get_conf
from common.my_redis import redis_client
from common.es_client import es_client
from platmonitor.dsl.confDevQuality import CalConfQuality
from common.timeFormatConverter import localstr2utctimestamp


# logging
logger = logging.getLogger("ops_quality_timer")
logger.setLevel(logging.DEBUG)
log_file = '%s/quality-timer.log' % get_conf('log', 'path')
formatter = logging.Formatter(
        '%(levelname)-7s %(asctime)-24s %(filename)s %(lineno)4d: %(message)s')
handler = logging.FileHandler(filename=log_file, encoding='utf-8')
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.addHandler(handler)

# global variable, conf info,
CONF_INFO = {}
# time interval to calculate conf quality
CALCULATE_INTERVAL = 300
PARENT_NAME = 'ops_quality_timer-process'


def get_conf_list():
    """
    从redis 获取实时会议列表 包括会议号/会议名称/会议开始时间
    ：return: dict   key:{info}
    """
    script_path = os.path.join(BASE_DIR, 'lua', 'get_real_confs_detail.lua')
    with open(script_path, 'r', encoding='utf8') as f:
        script_content = f.read()
    try:
        multiply = redis_client.register_script(script_content)
        confs_info = multiply(args=["", ""])
    except Exception as err:
        logger.error(err.args)
        return {}

    confs_info = [[[y.decode() for y in x] if isinstance(x, list) else x.decode() for x in conf] for conf in confs_info]
    if len(confs_info) == 0:
        return {}
    real_confs_inf_list = []
    for conf_info in confs_info:
        keys = conf_info[0::2]
        values = conf_info[1::2]
        info_dict = dict(zip(keys, values))
        real_confs_inf_list.append(info_dict)

    # 仅返回 会议号/会议名称/会议开始时间
    # confe164/confname/starttime
    return_key = ['confname', 'starttime']
    conf_ids = [conf['e164'] for conf in real_confs_inf_list]
    conf_info = [dict(zip(return_key, [conf['confname'], conf['starttime']])) for conf in real_confs_inf_list]
    result = dict(zip(conf_ids, conf_info))
    return result


def get_sig_conf_info(conf_e164):
    """
    通过会议号码获取单个会议的 会议名称/会议开始时间
    :return: dict {'confname':"", 'starttime':""}
    """
    all_conf_info = get_conf_list()
    return all_conf_info.get(conf_e164, None)


class ConfQualityHandler:
    """
    计算会议重量
    """

    def __init__(self, conf_list):
        """
        :type conf_list: list
        :param conf_list: [[conf_e164, start_time)], ...]
        """
        self.conf_list = conf_list

    def deal_time(self):
        """
        convert start_time to timestamp and add end_time to conf_list
        """
        now = int(datetime.datetime.now(tz=timezone.utc).timestamp()*1000)
        conf_list_new = []
        for conf in self.conf_list:
            start_t = localstr2utctimestamp(conf[1])
            conf_list_new.append([conf[0], start_t, now])
        return conf_list_new

    def conf_quality(self):
        """
        计算会议质量
        :return: tuple  (True, [])/(False, error)
        """
        conf_list = self.deal_time()

        try:
            quality = CalConfQuality(conf_list).get_conf_quality(is_score=True)
        except Exception as err:
            logger.error(err.args)
            return False, err.args
        else:
            if not quality[0]:
                logger.error(quality[1])
                return quality
            else:
                return quality


class ESWriter:
    """
    写 ES
    """

    def __init__(self):
        self.connection = es_client()
        self.__es_base_index = 'platform-confexperience-{year}.{month}-{week_number}'
        self.utc_format = "%Y-%m-%dT%H:%M:%S.%fZ"

    def __es_index(self, utc_time):
        week_number = utc_time.isocalendar()[1]
        year = utc_time.year
        month = utc_time.month

        index = self.__es_base_index.format(
            year=year,
            month=month,
            week_number=week_number,
        )
        return index

    def __es_body(self, data_list):
        """
        构造es消息
        :type data_list: list
        :param data_list:[[conf_e164, conf_name, score, start_time], ...]
        """
        utc_time = datetime.datetime.now(tz=timezone.utc)
        index = self.__es_index(utc_time)

        actions = []
        for single_data in data_list:
            action = {
                "_index": index,
                "_type": "doc",
                "_source": {
                    "@timestamp": utc_time.strftime(self.utc_format),
                    "source": {
                        "confe164": single_data[0],
                        "conf_name": single_data[1],
                        "score": single_data[2],
                        "begintime": single_data[3]
                    },
                    "type": "confexperience"
                }
            }
            actions.append(action)
        return actions

    def write(self, data_list):
        """
        :type data_list: list
        :param data_list:[[conf_e164, conf_name, score, start_time], ...]
        """
        body = self.__es_body(data_list)

        try:
            success, error_list = self.connection.bulk(actions=body, stats_only=False)
        except Exception as err:
            logger.error(err.args)
        else:
            logger.info(success)
            if len(error_list) != 0:
                for e in error_list:
                    logger.error(e)


class RedisSubscribe:

    def __init__(self):
        self.__conn = redis_client
        # 频道名称
        self.channel_sub = "notify"
        self.pattern1 = re.compile("conf/(?P<confe164>\d{7})")
        self.pattern2 = re.compile("domain/.+/confs")
        self.writer = ESWriter()

    def public(self, msg):
        """
        在指定频道上发布消息
        :param msg:
        :return:
        """
        # publish(): 在指定频道上发布消息，返回订阅者的数量
        self.__conn.publish(self.channel_sub, msg)
        return True

    def subscribe(self):
        # 返回发布订阅对象，通过这个对象你能1）订阅频道 2）监听频道中的消息
        pub = self.__conn.pubsub()
        # 订阅某个频道，与publish()中指定的频道一样。消息会发布到这个频道中
        pub.subscribe(self.channel_sub)
        return pub

    def filter_create_conf(self, data):
        """
        筛选创会消息
        :return: confe164 or False
        """
        if "confs" not in data or data['confs'] != "update" or "moid" not in data:
            return False
        keys_str = " ".join(data.keys())
        re_result = re.search(self.pattern1, keys_str)
        if re_result is None:
            return False
        else:
            confe164 = re_result.group('confe164')
        return (confe164, 'create') if data.get(re_result.group()) == 'update' else False

    def filter_delete_conf(self, data):
        """
        筛选结会消息
        :return: confe164 or False
        """
        if "confs" not in data or data['confs'] != "update" or "moid" not in data:
            return False
        keys_str = " ".join(data.keys())
        if re.search(self.pattern2, keys_str):
            re_result = re.search(self.pattern1, keys_str)

            if re_result is None:
                return False
            else:
                confe164 = re_result.group('confe164')
            return (confe164, 'delete') if data.get(re_result.group()) == 'delete' else False
        else:
            return False

    def data_filter(self, data):
        """
        筛选订阅数据 返回需要进一步处理的数据
        :type data: bytes
        :param data: redis 推送的原始的二进制数据中'data'字段的值
        "return: False/confe164
        """
        try:
            data = json.loads(data.decode())
        except Exception as err:
            logger.error(err.args)
            return False
        if not isinstance(data, dict):
            return False
        if len(data) not in [3, 4]:
            return False
        elif len(data) == 3:
            result = self.filter_create_conf(data)
        else:
            result = self.filter_delete_conf(data)
        return result

    def handler(self, original_data):
        sub_data = original_data.get('data', None)
        if sub_data is None:
            return False
        elif not isinstance(sub_data, bytes):
            return False
        filter_result = self.data_filter(sub_data)
        if filter_result is False:
            return False

        conf_e164, action = filter_result

        if action == 'create':
            info = get_sig_conf_info(conf_e164)
            logger.info('create: %s' % conf_e164)
            if info is not None:
                self.writer.write([[conf_e164, info['confname'], 5, info['starttime']]])
                # 更新 会议列表
                CONF_INFO[conf_e164] = info
                return True
            else:
                logger.info("create:can not find conf from redis:%s" % conf_e164)
                return False
        else:
            # delete
            # get conf_name/start_time from CONF_INFO
            info = CONF_INFO.get(conf_e164, None)
            logger.info('delete: %s' % conf_e164)
            if info is not None:
                quality = ConfQualityHandler([[conf_e164, info['starttime']]]).conf_quality()
                if quality[0]:
                    logger.info(quality[1])
                    self.writer.write([[conf_e164, info['confname'], quality[1][0], info['starttime']]])
                    CONF_INFO.pop(conf_e164)  # 更新 会议列表
                    return True
                else:
                    logger.error("delete:calculate quality error:% s" % conf_e164)
                    return False
            else:
                logger.error("delete:can not find conf from CONF_INFO:%s" % conf_e164)
                return False

    def run(self):
        while True:
            try:
                logger.info('start redis watcher...')
                sub = self.subscribe()
                msgs = sub.listen()
                for msg in msgs:
                    self.handler(msg)
            except Exception as err:
                logger.error(err.args)
                continue


def conf_quality_calculate_runner():
    while True:
        try:
            logger.info("start calculate...")
            real_conf_list = get_conf_list()  # dict
            if len(real_conf_list) != 0:
                conf_e164 = []
                start_time = []
                conf_name = []
                for key, value in real_conf_list.items():
                    conf_e164.append(key)
                    start_time.append(value.get('starttime'))
                    conf_name.append(value.get('confname'))

                conf_list = list(zip(conf_e164, start_time))

                quality = ConfQualityHandler(conf_list).conf_quality()
                if quality[0]:
                    logger.info("calculate complete...")
                    logger.info(quality)
                    data = list(zip(conf_e164, conf_name, quality[1], start_time))
                    writer = ESWriter()
                    writer.write(data)

            time.sleep(CALCULATE_INTERVAL)
        except Exception as err:
            logger.error(err.args)
            time.sleep(CALCULATE_INTERVAL)


def main():
    # 首先拉取会议列表
    setproctitle.setproctitle(PARENT_NAME)
    conf_info = get_conf_list()
    CONF_INFO.update(conf_info)  # 更新会议列表
    subscribe = RedisSubscribe()

    quality_calculator = threading.Thread(
        daemon=True,
        target=conf_quality_calculate_runner
    )
    redis_watcher = threading.Thread(
        daemon=True,
        target=subscribe.run
    )
    quality_calculator.start()
    redis_watcher.start()
    quality_calculator.join()
    redis_watcher.join()


if __name__ == "__main__":
    logger.info('ops_quality_timer start...')
    keep_fds = [
        handler.stream.fileno(),
    ]
    pid_path = os.path.join('/opt/data/ops/', 'ops_quality_timer.pid')
    if not os.path.exists(os.path.dirname(pid_path)):
        os.makedirs(os.path.dirname(pid_path), exist_ok=True)
    daemon = Daemonize(
        app=PARENT_NAME,
        action=main,
        pid=pid_path,
        logger=logger,
        keep_fds=keep_fds
    )
    daemon.start()
