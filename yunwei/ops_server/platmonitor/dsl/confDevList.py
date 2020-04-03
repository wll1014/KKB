#!/usr/bin/env python3
# -*- coding:utf-8 -*-


import os
import re
import json
import datetime
import logging
import jsonpath
from copy import deepcopy
from django.db import connections
from ops.settings import BASE_DIR
from platmonitor.dsl import dsl
from common.conf_params_enum import *
from common.es_client import es_client
from common.my_redis import redis_client
from platmonitor.dsl.es_query import DeviceConfQuality
from platmonitor.dsl.es_query import DevConfTopology

logger = logging.getLogger('ops.' + __name__)


class EvMtInfo:
    """
    query mt information from message EV_MT_INFO report by NMSCollector, mt_e164 number is required.
    mt_info: mt_ip/mt_ver/mt_type/aps_ip/nat_ip/sip_addr/gk_addr(pas)
    """

    def __init__(self, mt_ids, start_time=None, end_time=None):
        """
        :param mt_ids: mt_e16e numbers, a iterable object
        :param start_time: unix timestamp, start_time to search
        :param end_time: unix timestamp, end_time to search, default is the current time
        """
        self.mt_ids = mt_ids
        self.start_time = start_time
        self.end_time = end_time
        self.index = "platform-nmscollector-*mt*"
        self._init()

    def _init(self):
        self.mt_ids = [str(e164) for e164 in self.mt_ids]
        if self.end_time is None:
            self.end_time = int((datetime.datetime.now()).timestamp() * 1000)
        # if self.start_time is None:
        #     self.start_time = self.end_time - 30 * 24 * 60 * 60 * 1000

        if self.start_time is not None and self.end_time < self.start_time:
            raise ValueError('start_time must big than end_time')

    def query_moid_by_e164(self):
        """
        query terminal moids from mysql through mt_ids(e164)
        :return : dict  {e164:moid,...}
        """
        if len(self.mt_ids) == 0:
            return True, {}

        with connections['movision'].cursor() as cursor:
            sql = "SELECT e164,moid FROM user_info WHERE e164 IN %s AND binded='0'"
            cursor.execute(sql, [self.mt_ids])
            caller = cursor.fetchall()
        try:
            e164_moid = dict(caller)
        except Exception as err:
            logger.error(str(err.args))
            return False, err.args
        else:
            moids = {e164: e164_moid.get(e164, '') for e164 in self.mt_ids}
        return True, moids

    def get_dev_extra_info(self, moid_list, dev_type):
        """
        query mt_ip/mt_ver/mt_type/aps_ip/nat_ip/sip_addr/gk_addr from ES
        :param moid_list: list of dev moid
        :type moid_list: list
        :param dev_type: int   终端类型 1:正常 2:异常
        :return: list
        """

        if dev_type == 2:
            # 异常终端返回空
            return True, [[""]*6 for moid in moid_list]

        if len(moid_list) == 0:
            return True, []

        # 修改模板
        dsl_ = deepcopy(dsl.conf_p2p_dev_extra_dsl)
        must_block = dsl_['query']['bool']['must']
        # 先将模板中平台域条件删除
        for item in must_block[::-1]:
            if 'source.devid' in item['match']:
                must_block.remove(item)
                break

        # 将终端moid过滤条件加入位置0 方便后续修改
        must_block.insert(0, {"match": {"source.devid": ""}})
        # 时间
        if self.start_time:
            dsl_['query']['bool']['filter']['range']['@timestamp'] = {
                "gte": self.start_time, "lte": self.end_time}
        else:
            dsl_['query']['bool']['filter']['range']['@timestamp'] = {"lte": self.end_time}

        # 构建批量查询语句
        m_dsl = ''
        for moid in moid_list:
            # moid在must中0位置
            dsl_['query']['bool']['must'][0]["match"]["source.devid"] = moid
            m_dsl += '{}\n' + json.dumps(dsl_) + '\n'
        # 查询
        filter_path = deepcopy(dsl.conf_p2p_dev_extra_filter)
        es = es_client()
        try:
            results = es.msearch(
                index=self.index,
                dsl=m_dsl,
                filter_path=filter_path)
        except Exception as err:
            logger.error(str(err.args))
            return False, err.args
        if len(results) == 0:
            # 数据为空
            return True, [[""]*6 for moid in moid_list]

        # mt_ip/mt_ver/mt_type/aps_ip/nat_ip/sip_addr/gk_addr
        ip_ver_s = []
        for result in results['responses']:
            mt_ip = jsonpath.jsonpath(result, '$..netinfo.ip')
            mt_ver = jsonpath.jsonpath(result, '$..mt_info.devver')
            mt_type = jsonpath.jsonpath(result, '$..source.devtype')

            aps_ip = jsonpath.jsonpath(result, '$..aps_addr.ip')
            nat_ip = jsonpath.jsonpath(result, '$..netinfo.nat_ip')
            sip_addr = jsonpath.jsonpath(result, '$..sip_addr')
            gk_addr = jsonpath.jsonpath(result, '$..gk_addr')

            ip_ver = [x[0] if x is not False else "" for x in [mt_ip, mt_ver, mt_type, aps_ip, nat_ip, sip_addr, gk_addr]]
            ip_ver_s.append(ip_ver)
        return True, ip_ver_s

    def get_mt_info(self):
        """
        main function
        :return: tuple, (True, {})/(False, err)
                ["mt_addr", "mt_soft", "mt_type"]
        """
        mt_moid_s = self.query_moid_by_e164()
        if not mt_moid_s[0]:
            return mt_moid_s
        else:
            mt_moid_s = mt_moid_s[1]
        if len(mt_moid_s) == 0:
            return True, []

        abnormal_mt_moid = [value for key,
                            value in mt_moid_s.items() if not value]
        abnormal_mt_e164 = [
            key for key,
            value in mt_moid_s.items() if not value]
        abnormal_mt_info = self.get_dev_extra_info(
            abnormal_mt_moid, dev_type=2)
        abnormal_info = dict(zip(abnormal_mt_e164, abnormal_mt_info[1]))

        normal_mt_moid = [value for key, value in mt_moid_s.items() if value]
        normal_mt_e164 = [key for key, value in mt_moid_s.items() if value]
        normal_mt_info = self.get_dev_extra_info(normal_mt_moid, dev_type=1)
        if not normal_mt_info[0]:
            return normal_mt_info
        else:
            normal_mt_info = normal_mt_info[1]
        normal_info = dict(zip(normal_mt_e164, normal_mt_info))

        normal_info.update(abnormal_info)
        info = [normal_info.get(e164) for e164 in self.mt_ids]
        return True, info


class MtUpuWatcherInfo:
    """
    根据 终端E164号查询UPU消息
    mt_ip/mt_type/prototype/status/pas_ip(nuaddr)/nuplatformid/userdomain/roommoid
    """

    def __init__(self, mt_ids, start_time=None, end_time=None):
        """
        :param mt_ids: mt_e16e numbers, a iterable object
        :param start_time: unix timestamp, start_time to search
        :param end_time: unix timestamp, end_time to search, default is the current time
        """
        self.mt_ids = mt_ids
        self.start_time = start_time
        self.end_time = end_time
        self.index = "upuwatcher-*"
        self._init()

    def _init(self):
        self.mt_ids = [str(e164) for e164 in self.mt_ids]
        if self.end_time is None:
            self.end_time = int((datetime.datetime.now()).timestamp() * 1000)

        if self.start_time is not None and self.end_time < self.start_time:
            raise ValueError('start_time must big than end_time')

    def make_querydsl_from_upuwatcher(self):

        # 修改模板
        dsl_ = deepcopy(dsl.mt_upuwatcher_info)
        must_block = dsl_['query']['bool']['must']
        # 先将模板中平台域条件删除
        for item in must_block[::-1]:
            if 'source.e164' in item['match']:
                must_block.remove(item)
                break

        # 将终端e164过滤条件加入位置0 方便后续修改
        must_block.insert(0, {"match": {"source.e164": ""}})
        # 时间
        if self.start_time:
            dsl_['query']['bool']['filter']['range']['@timestamp'] = {
                "gte": self.start_time, "lte": self.end_time}
        else:
            dsl_['query']['bool']['filter']['range']['@timestamp'] = {"lte": self.end_time}

        # 构建批量查询语句
        m_dsl = ''
        for e164 in self.mt_ids:
            # e164在must中0位置
            dsl_['query']['bool']['must'][0]["match"]["source.e164"] = e164
            m_dsl += '{}\n' + json.dumps(dsl_) + '\n'
        return m_dsl

    def get_mt_info(self):
        """
        main function
        :return: tuple, (True, [])/(False, err)
        mt_ip/mt_type/prototype/status/pas_ip(nuaddr)/nuplatformid/userdomain/roommoid
        """
        m_dsl = self.make_querydsl_from_upuwatcher()
        filter_path = dsl.mt_upuwatcher_info_filter
        # 查询
        es = es_client()
        try:
            results = es.msearch(
                index=self.index,
                dsl=m_dsl,
                filter_path=filter_path)
        except Exception as err:
            logger.error(str(err.args))
            return False, err.args
        if len(results) == 0:
            # 数据为空
            return True, [[""] * 8 for _ in self.mt_ids]

        # mt_ip/mt_type/prototype/status/pas_ip(nuaddr)/nuplatformid/userdomain/roommoid
        mt_infos = []
        for result in results['responses']:
            mt_ip = jsonpath.jsonpath(result, '$..mtaddr')
            mt_proto = jsonpath.jsonpath(result, '$..prototype')
            mt_type = jsonpath.jsonpath(result, '$..mttype')
            mt_status = jsonpath.jsonpath(result, '$..status')

            pas_ip = jsonpath.jsonpath(result, '$..nuaddr')
            pas_platformid = jsonpath.jsonpath(result, '$..nuplatformid')
            userdomain = jsonpath.jsonpath(result, '$..userdomain')
            roommoid = jsonpath.jsonpath(result, '$..roommoid')

            me_info = [x[0] if x is not False else "" for x in
                      [mt_ip, mt_type, mt_proto, mt_status, pas_ip, pas_platformid, userdomain, roommoid]]
            mt_infos.append(me_info)
        return True, mt_infos


class MultiConfDevList:
    """
    根据会议号码/会议起止查询多点会议终端列表，返回终端详情
    """

    def __init__(self, conf_info):
        """
        :param conf_info: list or tuple, like [conf_id, start_time, end_time, status], status is instance of ConfStat
        """
        self.conf_id = conf_info[0]
        self.start_time = int(conf_info[1])
        self.end_time = conf_info[2]
        self.conf_status = int(conf_info[3])
        self.condition = conf_info[4]
        if self.end_time == ConfEndTimeType.REALTIME.name or self.end_time == ConfEndTimeType.MANUAL.name:
            self.end_time = int((datetime.datetime.now()).timestamp() * 1000)
        elif self.end_time == ConfEndTimeType.ABEND.name:
            # 异常结会按会议时长2小时计算
            self.end_time = self.start_time + 7200000
        else:
            self.end_time = int(self.end_time)
        self.index = "platform-nmscollector-*mt*"

    def get_dev_list(self):
        """
        查询入会终端列表，返回终端 号码/ip/别名/版本/add_type/add_desc
        :return: (bool, list, list)  list: list of dict
        """
        # 会议号码
        conf_condition = {
            "match": {
                "source.mtinfo.confe164.keyword": "%s" %
                self.conf_id}}
        # 时间
        time = {"gte": self.start_time, "lte": self.end_time}

        # 构建查询语句
        dsl_ = deepcopy(dsl.conf_multi_dev_filter_add_dsl)
        must_block = dsl_['query']['bool']['must']
        # 先将模板中会议号码条件删除
        for item in must_block[::-1]:
            if 'source.mtinfo.confe164.keyword' in item['match']:
                must_block.remove(item)
                break
        # 将查询条件加入
        must_block.append(conf_condition)
        dsl_['query']['bool']['must'] = must_block
        dsl_['query']['bool']['filter']['range']['@timestamp'] = time

        if self.condition is not None:
            should = [
                {
                    "wildcard": {
                        "source.mtinfo.mtaccount.keyword": {
                            "value": "*{}*".format(self.condition)
                        }
                    }
                },
                {
                    "wildcard": {
                        "source.mtinfo.mtname.keyword": {
                            "value": "*{}*".format(self.condition)
                        }
                    }
                }
            ]
            dsl_['query']['bool']['should'] = should
            dsl_['query']['bool']['minimum_should_match'] = 1

        es = es_client()
        index = "platform-nmscollector-*cmu*"
        try:
            conf_dev_list = es.search(index=index, dsl=dsl_)
        except Exception as err:
            logger.error(err)
            return False, err.args

        results = conf_dev_list['aggregations']['mtaccount']['buckets']
        if len(results) == 0:
            return True, None

        normal_dev_list = []
        abnormal_dev_list = []
        add_param_keys = [
            "mt_e164",
            "mt_name",
            "mt_addr",
            "mt_soft",
            "add_type",
            "add_desc"]
        for sig_account in results:
            for sig_mtip in sig_account['mtip']['buckets']:
                try:
                    mtip = jsonpath.jsonpath(sig_mtip, '$..mtip')
                    mtaccount = jsonpath.jsonpath(sig_mtip, '$..mtaccount')
                    mtname = jsonpath.jsonpath(sig_mtip, '$..mtname')
                    add_type = jsonpath.jsonpath(sig_mtip, '$..mttype')
                    softversion = jsonpath.jsonpath(sig_mtip, '$..softversion')
                    add_desc = [
                        ConfMtAddDesc.get(
                            ConfMtAddTypeNMS.get(
                                add_type[0]).name)]
                    tmp_inf = [
                        x[0] if x is not False else "" for x in [
                            mtaccount,
                            mtname,
                            mtip,
                            softversion,
                            add_type,
                            add_desc]]
                    if mtaccount and mtaccount[0] and add_type and add_type[0] == 3:
                        # 终端164号存在且类型为3
                        normal_dev_list.append(
                            dict(zip(add_param_keys, tmp_inf)))
                    else:
                        abnormal_dev_list.append(
                            dict(zip(add_param_keys, tmp_inf)))
                except Exception as err:
                    logger.error(err)
                    continue
        return True, normal_dev_list, abnormal_dev_list

    def get_real_conf_dev_info_redis(self):
        """
        从redis里查询实时会议终端列表
        :return:一个二值元组，第一个值为查询是否成功(True:成功 False:失败)
                第二个值失败时为失败原因，成功时为结果(列表)
        """
        script_path = os.path.join(BASE_DIR, 'lua', 'get_conf_mts_detail.lua')
        with open(script_path, 'r', encoding='utf8') as f:
            script_content = f.read()

        try:
            start_time = datetime.datetime.fromtimestamp(
                self.start_time / 1000).strftime("%Y-%m-%d %H:%M:%S")
            multiply = redis_client.register_script(script_content)
            mts_info = multiply(args=[self.conf_id, start_time])
        except Exception as err:
            logger.error(err)
            return False, err.args

        add_param_keys = [
            "mt_e164",
            "mt_name",
            "mt_addr",
            "add_type",
            "add_desc",
            'bitrate',
            'mt_prot',
            'mt_type',
            "is_online"]
        real_conf_mts_list = []
        if self.condition is not None:
            pattern = ".*%s.*" % self.condition
        else:
            pattern = None
        for mt_info in mts_info:
            mt_info = [x.decode() for x in mt_info]

            mt_e164 = mt_info[0]
            mt_name = mt_info[1]

            if pattern is not None:
                if not (
                    re.search(
                        pattern,
                        mt_name) or re.search(
                        pattern,
                        mt_e164)):
                    #
                    continue

            mt_addr = mt_info[2]
            add_type = int(mt_info[3]) if mt_info[3] else 0
            add_desc = ConfMtAddDesc.get(ConfMtAddTypeRedis.get(add_type).name)
            add_type = ConvertRedisTypeToNMS(add_type)
            bitrate = mt_info[4]
            mt_prot = MtProtocol(int(mt_info[5])).name
            mt_type = mt_info[6]
            is_online = int(mt_info[7])
            info_dict = dict(zip(add_param_keys,
                                 [mt_e164,
                                  mt_name,
                                  mt_addr,
                                  add_type,
                                  add_desc,
                                  bitrate,
                                  mt_prot,
                                  mt_type,
                                  is_online]))

            real_conf_mts_list.append(info_dict)
        if len(real_conf_mts_list) == 0:
            return True, None
        return True, real_conf_mts_list

    def get_real_conf_dev_soft_info(self, dev_list, dev_type):
        """
        返回终端版本号
        :return: list of dict
        """
        dict_keys = ["mt_soft", "aps_ip", "nat_ip", "sip_ip", "gk_ip"]
        if dev_type == 2:
            # 异常终端返回空
            return True, [{}.fromkeys(dict_keys, "") for dev in dev_list]

        if len(dev_list) == 0:
            return True, []

        # mt_ip/mt_ver/mt_type/aps_ip/nat_ip/sip_ip/gk_ip(pas)
        mt_ev_info = EvMtInfo(dev_list, end_time=self.end_time).get_mt_info()
        # mt_ip / mt_type / prototype / status / pas_ip(nuaddr) / nuplatformid / userdomain / roommoid
        mt_upu_info = MtUpuWatcherInfo(dev_list, end_time=self.end_time).get_mt_info()

        if not mt_ev_info[0]:
            return mt_ev_info
        else:
            if not mt_upu_info[0]:
                mt_infos = [[info[1], info[3], info[4], info[5], info[6]] for info in mt_ev_info[1]]
                return True, [dict(zip(dict_keys, info)) for info in mt_infos]
            else:
                for index, value in enumerate(mt_ev_info[1]):
                    value.extend(mt_upu_info[1][index])
                mt_ev_info = [[info[1], info[3], info[4], info[5], info[11]] for info in mt_ev_info[1]]
                return True, [dict(zip(dict_keys, info)) for info in mt_ev_info]

    def m_dev_conf_info_dsl(self, dev_list):
        """
        构建批量查询终端会议信息的dsl语句
        :return:
        """
        # 修改模板
        dsl_ = deepcopy(dsl.conf_multi_dev_conf_info_dsl)
        must_block = dsl_['query']['bool']['must']
        # 先将模板中会议号码和终端号码条件删除
        for item in must_block[::-1]:
            if 'source.conf_info.mt_e164' in item['match']:
                must_block.remove(item)
                continue
            if 'source.conf_info.conf_e164' in item['match']:
                must_block.remove(item)
                continue
        # 将终端号过滤条件放在位置0，方便后续修改
        must_block.append(
            {"match": {"source.conf_info.conf_e164": "{}".format(self.conf_id)}})
        must_block.insert(0, {"match": {"source.conf_info.mt_e164": ""}})
        # 时间
        dsl_['query']['bool']['filter']['range']['@timestamp'] = {
            "gte": self.start_time, "lte": self.end_time}

        # 构建批量查询语句
        m_dsl = ''
        for dev in dev_list:
            # 终端号码,在must中0位置
            dsl_['query']['bool']['must'][0]["match"]["source.conf_info.mt_e164"] = dev
            m_dsl += '{}\n' + json.dumps(dsl_) + '\n'
        return m_dsl

    def q_dev_conf_info(self, dev_list, dev_type):
        """
        从终端会议信息中查询终端会议信息 包括：
            终端类型/呼叫码率

        :param dev_list: list   终端列表
        :param dev_type: int   终端类型 1:正常 2:异常
        :return: zip迭代器
        """
        mt_param_keys = [
            "bitrate",
            "mt_type"
        ]

        if dev_type == 2:
            mt_infos = [{}.fromkeys(mt_param_keys, "") for dev in dev_list]
            return True, mt_infos

        if len(dev_list) == 0:
            return True, []

        m_dsl = self.m_dev_conf_info_dsl(dev_list)
        # 查询终端详情
        es = es_client()
        try:
            results = es.msearch(index=self.index, dsl=m_dsl)
        except Exception as err:
            logger.error(err)
            return False, err.args

        # 获取终端信息
        mt_infos = []
        for count, result in enumerate(results['responses']):
            bitrate = jsonpath.jsonpath(result, '$..conf_info.bitrate')  # 呼叫码率
            mt_type = jsonpath.jsonpath(result, '$..source.devtype')  # 终端类型

            mt_info = [
                x[0] if x is not False else "" for x in [
                    bitrate, mt_type]]
            mt_info_dict = dict(zip(mt_param_keys, mt_info))

            mt_infos.append(mt_info_dict)
        return True, mt_infos

    def get_dev_quality(self, dev_list, dev_type):
        """
        计算终端的会议质量
        :param dev_list: list  终端列表
        :param dev_type: int   终端类型 1:正常 2:异常
        :return:
        """
        if dev_type == 2:
            # 异常终端返回空
            return True, [{}.fromkeys(["mt_expe"], "") for dev in dev_list]

        if len(dev_list) == 0:
            return True, []

        conf_dev_list = [
            [self.conf_id, self.start_time, self.end_time] + dev_list]
        quality_obj = DeviceConfQuality(3, conf_dev_list, summary=False)
        quality = quality_obj.get_quality()
        if not quality[0]:
            # 获取终端质量信息失败
            return quality
        else:
            quality = quality[1]
        return True, [{}.fromkeys(["mt_expe"], qua) for qua in quality[0]]

    def m_mt_protocol_dsl(self, dev_list):
        """
        构建批量查询终端ip/登陆协议的dsl语句
        :param dev_list: list  终端列表
        :param dev_type: int   终端类型 1:正常 2:异常
        :return:
        """
        dsl_ = deepcopy(dsl.mt_ip_proto_inf_dsl)
        must_block = dsl_['query']['bool']['must']
        # 先将模板中164号条件删除
        for item in must_block[::-1]:
            if 'source.e164' in item['match']:
                must_block.remove(item)
                break
        # 将e164号筛选条件加入
        must_block.insert(0, {"match": {"source.e164": ""}})
        dsl_['query']['bool']['filter']['range']['@timestamp'] = {
            "lte": self.end_time}
        dsl_['query']['bool']['must'] = must_block

        # 将终端164号过滤条件加入
        m_dsl = ''
        for dev in dev_list:
            dsl_['query']['bool']['must'][0]['match'] = {
                "source.e164": "%s" % dev}
            m_dsl += '{}\n' + json.dumps(dsl_) + '\n'
        return m_dsl

    def q_mt_protocol_dsl(self, dev_list, dev_type):
        """
        查询终端协议类型
        :param dev_list: list   终端列表
        :param dev_type: int   终端类型 1:正常 2:异常
        """
        if dev_type == 2:
            # 异常终端返回空
            return True, [{}.fromkeys(["mt_prot"], "") for dev in dev_list]

        if len(dev_list) == 0:
            return True, []

        m_dsl = self.m_mt_protocol_dsl(dev_list)
        # 查询终端详情
        index = "upuwatcher-*"
        es = es_client()
        try:
            results = es.msearch(index=index, dsl=m_dsl)
        except Exception as err:
            logger.error(err)
            return False, err.args

        mt_protocol = []
        for result in results['responses']:
            proto = jsonpath.jsonpath(result, '$..source.prototype')
            mt_protocol.append(proto)

        def prot_converter(prot_type):
            if 'SIP' in prot_type.upper():
                return "SIP"
            elif "H323" in prot_type.upper():
                return "H323"
            else:
                return ""

        mt_protocol = [x[0] if x is not False else "" for x in mt_protocol]
        mt_protocol = list(map(prot_converter, mt_protocol))

        return True, [{}.fromkeys(["mt_prot"], prot) for prot in mt_protocol]

    def q_mt_topology_info(self, dev_list, dev_type):
        """
        query device topology info
        :param dev_list: list  终端列表
        :param dev_type: int   终端类型 1:正常 2:异常
        :return:
        """
        if dev_type == 2:
            # 异常终端返回空
            return True, [{"mt_status": "", "protocol_info": []}
                          for dev in dev_list]

        if len(dev_list) == 0:
            return True, []

        conf_dev_list = [
            self.conf_id,
            self.start_time,
            self.end_time] + dev_list
        topology_obj = DevConfTopology(
            conf_dev_list, stat_only=True)  # only mt_status
        topology = topology_obj.get_topology()
        if not topology[0]:
            # 获取终端拓扑信息失败
            return topology
        else:
            topology = topology[1]
        return True, topology

    def get_real_conf_dev_info(self):
        """
        实时会议终端列表
        :return: list
        """
        dev_list = self.get_real_conf_dev_info_redis()
        if not dev_list[0]:
            # 获取终端列表失败
            return dev_list
        elif dev_list[1] is None:
            return True, []
        else:
            dev_list = dev_list[1]

        # 终端信息
        normal_dev_info = [x for x in dev_list if x['add_type']
                           == ConfMtAddTypeNMS.MT]  # 正常终端 list of dict
        abnormal_dev_info = [x for x in dev_list if x['add_type']
                             != ConfMtAddTypeNMS.MT]  # 其他  list of dict

        # 终端列表
        normal_dev_list = [x['mt_e164'] for x in normal_dev_info]
        abnormal_dev_list = [x['mt_e164'] for x in abnormal_dev_info]

        # 终端质量
        normal_dev_qua_info = self.get_dev_quality(normal_dev_list, 1)
        if not normal_dev_qua_info[0]:
            return normal_dev_qua_info
        else:
            normal_dev_qua_info = normal_dev_qua_info[1]
        abnormal_dev_qua_info = self.get_dev_quality(abnormal_dev_list, 2)[1]

        # 终端版本
        normal_dev_soft_info = self.get_real_conf_dev_soft_info(
            normal_dev_list, 1)
        if not normal_dev_soft_info[0]:
            return normal_dev_soft_info
        else:
            normal_dev_soft_info = normal_dev_soft_info[1]
        abnormal_dev_soft_info = self.get_real_conf_dev_soft_info(abnormal_dev_list, 2)[
            1]

        # 实时会议判断终端拓扑状态
        normal_dev_topology_info = self.q_mt_topology_info(normal_dev_list, 1)
        if not normal_dev_topology_info[0]:
            return normal_dev_topology_info
        else:
            normal_dev_topology_info = normal_dev_topology_info[1]
        abnormal_dev_topology_info = self.q_mt_topology_info(abnormal_dev_list, 2)[
            1]

        # #  合并数据
        def dict_update(x, y, z, w):
            x.update(y)
            x.update(z)
            x.update(w)
            return x

        normal_dev_info = [
            dict_update(
                x,
                y,
                z,
                w) for x,
            y,
            z,
            w in zip(
                normal_dev_info,
                normal_dev_qua_info,
                normal_dev_soft_info,
                normal_dev_topology_info)]
        abnormal_dev_info = [
            dict_update(
                x,
                y,
                z,
                w) for x,
            y,
            z,
            w in zip(
                abnormal_dev_info,
                abnormal_dev_qua_info,
                abnormal_dev_soft_info,
                abnormal_dev_topology_info)]

        normal_dev_info.extend(abnormal_dev_info)
        normal_dev_info.sort(key=lambda x: x['is_online'], reverse=True)
        return True, normal_dev_info

    def get_hist_conf_dev_info(self):
        """
        历史会议终端列表
        :return: list
        """
        dev_list = self.get_dev_list()
        if not dev_list[0]:
            # 获取终端列表失败
            return dev_list
        elif dev_list[1] is None:
            return True, []

        # 终端入会消息
        normal_dev_info = dev_list[1]  # 正常终端 list of dict
        abnormal_dev_info = dev_list[2]  # 其他  list of dict

        # 终端列表
        normal_dev_list = [x['mt_e164'] for x in normal_dev_info]
        abnormal_dev_list = [x['mt_e164'] for x in abnormal_dev_info]

        # 终端会议消息
        normal_dev_conf_info = self.q_dev_conf_info(normal_dev_list, 1)
        if not normal_dev_conf_info[0]:
            # 查询失败
            return normal_dev_conf_info
        else:
            normal_dev_conf_info = normal_dev_conf_info[1]
        abnormal_dev_conf_info = self.q_dev_conf_info(abnormal_dev_list, 2)[1]

        # 终端质量
        normal_dev_qua_info = self.get_dev_quality(normal_dev_list, 1)
        if not normal_dev_qua_info[0]:
            return normal_dev_qua_info
        else:
            normal_dev_qua_info = normal_dev_qua_info[1]
        abnormal_dev_qua_info = self.get_dev_quality(abnormal_dev_list, 2)[1]

        # 获取终端协议类型
        normal_dev_prot_info = self.q_mt_protocol_dsl(normal_dev_list, 1)
        if not normal_dev_prot_info[0]:
            return normal_dev_prot_info
        else:
            normal_dev_prot_info = normal_dev_prot_info[1]
        abnormal_dev_prot_info = self.q_mt_protocol_dsl(
            abnormal_dev_list, 2)[1]

        # 终端版本
        normal_dev_soft_info = self.get_real_conf_dev_soft_info(
            normal_dev_list, 1)
        if not normal_dev_soft_info[0]:
            return normal_dev_soft_info
        else:
            normal_dev_soft_info = normal_dev_soft_info[1]
        abnormal_dev_soft_info = self.get_real_conf_dev_soft_info(abnormal_dev_list, 2)[
            1]

        # #  合并数据
        def dict_update(x, y, z, w, v):
            x.update(y)
            x.update(z)
            x.update(w)
            x.update(v)
            return x

        normal_dev_info = [
            dict_update(
                x,
                y,
                z,
                w,
                v) for x,
            y,
            z,
            w,
            v in zip(
                normal_dev_info,
                normal_dev_conf_info,
                normal_dev_qua_info,
                normal_dev_prot_info,
                normal_dev_soft_info)]
        abnormal_dev_info = [
            dict_update(
                x,
                y,
                z,
                w,
                v) for x,
            y,
            z,
            w,
            v in zip(
                abnormal_dev_info,
                abnormal_dev_conf_info,
                abnormal_dev_qua_info,
                abnormal_dev_prot_info,
                abnormal_dev_soft_info)]

        normal_dev_info.extend(abnormal_dev_info)
        return True, normal_dev_info

    def get_dev_info(self):
        if self.conf_status == ConfStat.REALTIME:
            mts = self.get_real_conf_dev_info()
        else:
            mts = self.get_hist_conf_dev_info()
        return mts


class MultiConfDevChannelInfo:
    """
    多点会议通道信息
    """

    def __init__(self, conf_info):
        """
        :param conf_info: list or tuple, like [conf_id, start_time, end_tiem, status, mt_id], status is instance of ConfStat
        """
        self.conf_id = conf_info[0]
        self.start_time = int(conf_info[1])
        self.end_time = conf_info[2]
        self.conf_status = int(conf_info[3])
        self.mt_id = conf_info[4]
        if self.end_time == ConfEndTimeType.REALTIME.name or self.end_time == ConfEndTimeType.MANUAL.name:
            self.end_time = int((datetime.datetime.now()).timestamp() * 1000)
        elif self.end_time == ConfEndTimeType.ABEND.name:
            # 异常结会按会议时长2小时计算
            self.end_time = self.start_time + 7200000
        else:
            self.end_time = int(self.end_time)
        self.index = "platform-nmscollector-*mt*"

    def get_real_conf_channel_info(self):
        """
        从redis里查询实时会议终端通道信息
        :return:一个二值元组，第一个值为查询是否成功(True:成功 False:失败)
                第二个值失败时为失败原因，成功时为结果(列表)
        """
        script_path = os.path.join(BASE_DIR, 'lua', 'get_conf_mt_channel.lua')
        with open(script_path, 'r', encoding='utf8') as f:
            script_content = f.read()

        try:
            start_time = datetime.datetime.fromtimestamp(
                self.start_time / 1000).strftime("%Y-%m-%d %H:%M:%S")
            multiply = redis_client.register_script(script_content)
            channel_info = multiply(
                args=[
                    self.conf_id,
                    start_time,
                    self.mt_id])
        except Exception as err:
            logger.error(err)
            return False, err.args

        chn_param_keys = [
            "privideo_video_up_bitrate",
            "privideo_video_up_framerate",
            "privideo_video_up_res",
            "privideo_video_up_format",
            "privideo_video_down_bitrate",
            "privideo_video_down_framerate",
            "privideo_video_down_res",
            "privideo_video_down_format",

            "assvideo_video_up_bitrate",
            "assvideo_video_up_framerate",
            "assvideo_video_up_res",
            "assvideo_video_up_format",
            "assvideo_video_down_bitrate",
            "assvideo_video_down_framerate",
            "assvideo_video_down_res",
            "assvideo_video_down_format",

            "audio_up_bitrate",
            "audio_up_format",
            "audio_down_bitrate",
            "audio_down_format",
        ]

        # vsendchn", vrcvchns, dsendchns, drcvchns, asendchns, arcvchns
        channel_info = [[x.decode() for x in sig_chn]
                        for sig_chn in channel_info]

        mt_chn_info = []
        for chn_num, chn_info in enumerate(channel_info):
            if chn_num in [4, 5]:
                # asendchns, arcvchns
                # # bitrate format
                if len(chn_info) == 0:
                    rate, fmt = "", ""
                else:
                    rate, fmt = chn_info
                rate = int(rate) if rate else ""
                fmt = MtAudioFormatRedis.get(int(fmt), "Other") if fmt else ""
                mt_chn_info.extend([rate, fmt])
            else:
                # vsendchn", vrcvchns, dsendchns, drcvchns
                # bitrate frame res format
                if len(chn_info) == 0:
                    rate, frame, res, fmt = "", "", "", ""
                else:
                    rate, frame, res, fmt = chn_info
                rate = int(rate) if rate else ""
                frame = int(frame) if frame else ""
                res = MtVideoResolutionRedisDesc.get(
                    int(res), "Other") if res else ""
                fmt = MtVideoFormatRedis.get(int(fmt)).name if fmt else ""
                mt_chn_info.extend([rate, frame, res, fmt])

        result = dict(zip(chn_param_keys, mt_chn_info))
        # redis上报的主视频带宽为总带宽  如果开启辅流 主流实际带宽 = 主流带宽 - 辅流带宽 (上下行计算规则相同)
        if result["privideo_video_up_bitrate"] != "" and result["assvideo_video_up_bitrate"] != "":
            result["privideo_video_up_bitrate"] -= result["assvideo_video_up_bitrate"]
        if result["privideo_video_down_bitrate"] != "" and result["assvideo_video_down_bitrate"] != "":
            result["privideo_video_down_bitrate"] -= result["assvideo_video_down_bitrate"]

        return True, result

    def make_hist_conf_dev_info_dsl(self):
        """
        构建查询终端会议信息的dsl语句 也即通道信息
        :return:
        """
        # 修改模板
        dsl_ = deepcopy(dsl.conf_multi_dev_conf_info_dsl)
        must_block = dsl_['query']['bool']['must']
        # 先将模板中会议号码和终端号码条件删除
        for item in must_block[::-1]:
            if 'source.conf_info.mt_e164' in item['match']:
                must_block.remove(item)
                continue
            if 'source.conf_info.conf_e164' in item['match']:
                must_block.remove(item)
                continue
        # 将终端号过滤条件放在位置0，方便后续修改
        must_block.append(
            {"match": {"source.conf_info.conf_e164": "{}".format(self.conf_id)}})
        must_block.append(
            {"match": {"source.conf_info.mt_e164": "{}".format(self.mt_id)}})
        # 时间
        dsl_['query']['bool']['filter']['range']['@timestamp'] = {
            "gte": self.start_time, "lte": self.end_time}
        return dsl_

    def get_hist_conf_channel_info(self):
        """
        从终端会议信息中查询终端会议信息 包括：
            主视频码率/帧率/分辨率（上行/下行）
            辅视频码率/帧率/分辨率（上行/下行）
            音频码率/帧率 （上行/下行）
            音频格式/视频格式
            终端类型/呼叫码率
        :return: list
        """
        mt_param_keys = [
            "audio_up_bitrate",
            "audio_up_format",
            "audio_down_bitrate",
            "audio_down_format",
            "privideo_video_down_bitrate",
            "privideo_video_down_framerate",
            "privideo_video_down_res",
            "privideo_video_down_format",
            "privideo_video_up_bitrate",
            "privideo_video_up_framerate",
            "privideo_video_up_res",
            "privideo_video_up_format",
            "assvideo_video_down_bitrate",
            "assvideo_video_down_framerate",
            "assvideo_video_down_res",
            "assvideo_video_down_format",
            "assvideo_video_up_bitrate",
            "assvideo_video_up_framerate",
            "assvideo_video_up_res",
            "assvideo_video_up_format"
        ]

        dsl_ = self.make_hist_conf_dev_info_dsl()
        # 查询终端详情
        es = es_client()
        try:
            result = es.search(index=self.index, dsl=dsl_)
        except Exception as err:
            logger.error(err)
            return False, err.args

        # 获取终端信息
        audio_up_bitrate = jsonpath.jsonpath(
            result, '$..audio_send[?(@.id==0)].audio_up_bitrate')
        audio_up_format = jsonpath.jsonpath(
            result, '$..audio_send[?(@.id==0)].format')

        audio_down_bitrate = jsonpath.jsonpath(
            result, '$..audio_recv[?(@.id==0)].audio_down_bitrate')
        audio_down_format = jsonpath.jsonpath(
            result, '$..audio_recv[?(@.id==0)].format')

        privideo_video_down_bitrate = jsonpath.jsonpath(
            result, '$..privideo_recv[?(@.id==0)].video_down_bitrate')
        privideo_video_down_framerate = jsonpath.jsonpath(
            result, '$..privideo_recv[?(@.id==0)].framerate')
        privideo_video_down_res = jsonpath.jsonpath(
            result, '$..privideo_recv[?(@.id==0)].res')
        privideo_video_down_format = jsonpath.jsonpath(
            result, '$..privideo_recv[?(@.id==0)].format')

        privideo_video_up_bitrate = jsonpath.jsonpath(
            result, '$..privideo_send[?(@.id==0)].video_up_bitrate')
        privideo_video_up_framerate = jsonpath.jsonpath(
            result, '$..privideo_send[?(@.id==0)].framerate')
        privideo_video_up_res = jsonpath.jsonpath(
            result, '$..privideo_send[?(@.id==0)].res')
        privideo_video_up_format = jsonpath.jsonpath(
            result, '$..privideo_send[?(@.id==0)].format')

        assvideo_video_down_bitrate = jsonpath.jsonpath(
            result, '$..assvideo_recv[?(@.id==0)].video_down_bitrate')
        assvideo_video_down_framerate = jsonpath.jsonpath(
            result, '$..assvideo_recv[?(@.id==0)].framerate')
        assvideo_video_down_res = jsonpath.jsonpath(
            result, '$..assvideo_recv[?(@.id==0)].res')
        assvideo_video_down_format = jsonpath.jsonpath(
            result, '$..assvideo_recv[?(@.id==0)].format')

        assvideo_video_up_bitrate = jsonpath.jsonpath(
            result, '$..assvideo_send[?(@.id==0)].video_up_bitrate')
        assvideo_video_up_framerate = jsonpath.jsonpath(
            result, '$..assvideo_send[?(@.id==0)].framerate')
        assvideo_video_up_res = jsonpath.jsonpath(
            result, '$..assvideo_send[?(@.id==0)].res')
        assvideo_video_up_format = jsonpath.jsonpath(
            result, '$..assvideo_send[?(@.id==0)].format')

        # 转换格式
        audio_up_format = [
            MtAudioFormatNMS.get(
                audio_up_format[0]).name] if audio_up_format is not False else False
        audio_down_format = [
            MtAudioFormatNMS.get(
                audio_down_format[0]).name] if audio_down_format is not False else False
        privideo_video_down_res = [MtVideoResolutionNMSDesc.get(MtVideoResolutionTypeNMS.get(
            privideo_video_down_res[0]).name)] if privideo_video_down_res is not False else False
        privideo_video_down_format = [MtVideoFormatNMS.get(
            privideo_video_down_format[0]).name] if privideo_video_down_format is not False else False
        privideo_video_up_res = [MtVideoResolutionNMSDesc.get(MtVideoResolutionTypeNMS.get(
            privideo_video_up_res[0]).name)] if privideo_video_up_res is not False else False
        privideo_video_up_format = [MtVideoFormatNMS.get(
            privideo_video_up_format[0]).name] if privideo_video_up_format is not False else False
        assvideo_video_down_res = [MtVideoResolutionNMSDesc.get(MtVideoResolutionTypeNMS.get(
            assvideo_video_down_res[0]).name)] if assvideo_video_down_res is not False else False
        assvideo_video_down_format = [MtVideoFormatNMS.get(
            assvideo_video_down_format[0]).name] if assvideo_video_down_format is not False else False
        assvideo_video_up_res = [MtVideoResolutionNMSDesc.get(MtVideoResolutionTypeNMS.get(
            assvideo_video_up_res[0]).name)] if assvideo_video_up_res is not False else False
        assvideo_video_up_format = [MtVideoFormatNMS.get(
            assvideo_video_up_format[0]).name] if assvideo_video_up_format is not False else False

        mt_info = [audio_up_bitrate,
                   audio_up_format,
                   audio_down_bitrate,
                   audio_down_format,
                   privideo_video_down_bitrate,
                   privideo_video_down_framerate,
                   privideo_video_down_res,
                   privideo_video_down_format,
                   privideo_video_up_bitrate,
                   privideo_video_up_framerate,
                   privideo_video_up_res,
                   privideo_video_up_format,
                   assvideo_video_down_bitrate,
                   assvideo_video_down_framerate,
                   assvideo_video_down_res,
                   assvideo_video_down_format,
                   assvideo_video_up_bitrate,
                   assvideo_video_up_framerate,
                   assvideo_video_up_res,
                   assvideo_video_up_format
                   ]

        mt_info = [x[0] if x is not False else "" for x in mt_info]
        mt_info_dict = dict(zip(mt_param_keys, mt_info))

        return True, mt_info_dict

    def get_channel_info(self):
        if self.conf_status == ConfStat.REALTIME:
            channel_info = self.get_real_conf_channel_info()
        else:
            channel_info = self.get_hist_conf_channel_info()
        return channel_info


class MultiConfDevTopologyInfo:
    """
    实时会议 终端拓扑
    """

    def __init__(self, conf_info):
        """
        :param conf_info: list or tuple, like [conf_id, start_time, end_tiem, status, mt_id], status is instance of ConfStat
        """
        self.conf_id = conf_info[0]
        self.start_time = int(conf_info[1])
        self.end_time = conf_info[2]
        self.conf_status = int(conf_info[3])
        self.mt_id = conf_info[4]
        if self.end_time == ConfEndTimeType.REALTIME.name or self.end_time == ConfEndTimeType.MANUAL.name:
            self.end_time = int((datetime.datetime.now()).timestamp() * 1000)
        elif self.end_time == ConfEndTimeType.ABEND.name:
            # 异常结会按会议时长2小时计算
            self.end_time = self.start_time + 7200000
        else:
            self.end_time = int(self.end_time)

    def get_topology_info(self):
        """
        query device topology info
        :return:
        """
        if self.conf_status == ConfStat.HISTORY:
            return False, "会议类型错误"

        conf_dev_list = [
            self.conf_id,
            self.start_time,
            self.end_time,
            self.mt_id]
        topology_obj = DevConfTopology(conf_dev_list)
        topology = topology_obj.get_topology()
        if not topology[0]:
            # 获取终端拓扑信息失败
            return topology
        else:
            topology = topology[1]
        return True, topology


class P2PConfDevList:
    """
    根据会议起止时间/主被叫号码查询点对点会议终端列表，返回终端列表详情
    注: 点对点会议只有两个终端
    """

    def __init__(self, conf_info):
        self.caller = conf_info[0]  # 点对点会议号码为主叫方终端E164号码
        self.start_time = int(conf_info[1])
        self.end_time = conf_info[2]
        self.conf_status = conf_info[3]
        if self.end_time == ConfEndTimeType.REALTIME.name or self.end_time == ConfEndTimeType.MANUAL.name:
            self.end_time = int(datetime.datetime.now().timestamp() * 1000)
        elif self.end_time == ConfEndTimeType.ABEND.name:
            # 异常结会按会议时长2小时计算
            self.end_time = self.start_time + 7200000
        else:
            self.end_time = int(self.end_time)

    def get_dev_add_info(self):
        """
        查询创会消息信息 终端号码/终端别名/终端协议类型/who(caller/callee)
        :return:
        """
        # 修改模板
        dsl_ = deepcopy(dsl.conf_p2p_creat_dsl)
        must_block = dsl_['query']['bool']['must']
        # 先将模板中平台域条件删除
        for item in must_block[::-1]:
            if 'beat.platform_moid' in item['match']:
                must_block.remove(item)
                break

        # 将主被叫终端号过滤条件加入
        must_block.append(
            {"match": {"source.confinfo.caller.deve164.keyword": "{}".format(self.caller)}})

        # 时间
        dsl_['query']['bool']['filter']['range']['@timestamp'] = {
            "gte": self.start_time, "lte": self.end_time}

        # _source
        dsl_['_source'] = "source.confinfo"
        dsl_['size'] = 1

        # 查询终端详情
        es = es_client()
        index = "platform-nmscollector-*pas*"
        try:
            results = es.search(index=index, dsl=dsl_)
        except Exception as err:
            logger.error(err)
            return False, err.args

        caller_e164 = jsonpath.jsonpath(results, '$..caller.deve164')
        caller_name = jsonpath.jsonpath(results, '$..caller.devname')
        caller_type = jsonpath.jsonpath(results, '$..caller.devtype')
        callee_e164 = jsonpath.jsonpath(results, '$..callee.deve164')
        callee_name = jsonpath.jsonpath(results, '$..callee.devname')
        callee_type = jsonpath.jsonpath(results, '$..callee.devtype')

        info = [
            x[0] if x is not False else "" for x in [
                caller_e164,
                caller_name,
                caller_type,
                callee_e164,
                callee_name,
                callee_type]]

        param_keys = ["mt_e164", "mt_name", "mt_prot", "who"]
        info = [dict(zip(param_keys, inf))
                for inf in [info[:3] + ["caller"], info[3:] + ["callee"]]]
        return True, info

    def get_dev_extra_info(self, mt_ids, dev_type):
        """
        获取终端ip/版本号/类型
        :param mt_ids: list of dev_e164
        :type mt_ids: list
        :param dev_type: int   终端类型 1:正常 2:异常
        :return: list
        """
        param_keys = ["mt_addr", "mt_soft"]

        if dev_type == 2:
            # 异常终端返回空
            return True, [{}.fromkeys(param_keys, "") for e164 in mt_ids]

        if len(mt_ids) == 0:
            return True, []

        # 如果e164全部为空 返回空字符
        if not any(mt_ids):
            return True, [{}.fromkeys(param_keys, "") for e164 in mt_ids]

        mt_info = EvMtInfo(mt_ids, end_time=self.start_time).get_mt_info()
        if not mt_info[0]:
            return mt_info
        else:
            mt_info = [info[:2] for info in mt_info[1]]
        return True, [dict(zip(param_keys, info)) for info in mt_info]

    def get_dev_quality(self, dev_list, dev_type):
        """
        计算终端的会议质量
        :param dev_list: list  终端列表
        :param dev_type: int   终端类型 1:正常 2:异常
        :return:
        """
        if dev_type == 2:
            # 异常终端返回空
            return True, [{}.fromkeys(["mt_expe"], "") for dev in dev_list]

        if len(dev_list) == 0:
            return True, []

        conf_dev_list = [
            self.caller,
            self.start_time,
            self.end_time] + dev_list
        quality_obj = DeviceConfQuality(2, [conf_dev_list], summary=False)
        quality = quality_obj.get_quality()
        if not quality[0]:
            # 获取终端质量信息失败
            return quality
        else:
            quality = quality[1]
        return True, [{}.fromkeys(["mt_expe"], qua) for qua in quality[0]]

    def m_dev_conf_info_dsl(self, dev_list):
        """
        构建批量查询终端会议信息的dsl语句
        :return:
        """
        # 修改模板
        dsl_ = deepcopy(dsl.conf_multi_dev_conf_info_dsl)
        must_block = dsl_['query']['bool']['must']
        # 先将模板中会议号码和终端号码条件删除
        for item in must_block[::-1]:
            if 'source.conf_info.mt_e164' in item['match']:
                must_block.remove(item)
                continue
            if 'source.conf_info.conf_e164' in item['match']:
                must_block.remove(item)
                continue
        # 将终端号过滤条件放在位置0，方便后续修改
        must_block.append(
            {"match": {"source.conf_info.conf_e164": "{}".format(self.caller)}})
        must_block.insert(0, {"match": {"source.conf_info.mt_e164": ""}})
        # 时间
        dsl_['query']['bool']['filter']['range']['@timestamp'] = {
            "gte": self.start_time, "lte": self.end_time}

        # 构建批量查询语句
        m_dsl = ''
        for dev in dev_list:
            # 终端号码,在must中0位置
            dsl_['query']['bool']['must'][0]["match"]["source.conf_info.mt_e164"] = dev
            m_dsl += '{}\n' + json.dumps(dsl_) + '\n'
        return m_dsl

    def q_dev_conf_info(self, dev_list, dev_type):
        """
        从终端会议信息中查询终端会议信息 包括：
            主视频码率/帧率/分辨率（上行/下行）
            辅视频码率/帧率/分辨率（上行/下行）
            音频码率/帧率 （上行/下行）
            音频格式/视频格式
            终端类型/呼叫码率

        :param dev_list: list   终端列表
        :param dev_type: int   终端类型 1:正常 2:异常
        :return: zip迭代器
        """
        mt_param_keys = [
            "bitrate",
            "mt_type",
            "audio_up_bitrate",
            "audio_up_format",
            "audio_down_bitrate",
            "audio_down_format",
            "privideo_video_down_bitrate",
            "privideo_video_down_framerate",
            "privideo_video_down_res",
            "privideo_video_down_format",
            "privideo_video_up_bitrate",
            "privideo_video_up_framerate",
            "privideo_video_up_res",
            "privideo_video_up_format",
            "assvideo_video_down_bitrate",
            "assvideo_video_down_framerate",
            "assvideo_video_down_res",
            "assvideo_video_down_format",
            "assvideo_video_up_bitrate",
            "assvideo_video_up_framerate",
            "assvideo_video_up_res",
            "assvideo_video_up_format"
        ]

        if dev_type == 2:
            mt_infos = [{}.fromkeys(mt_param_keys, "") for dev in dev_list]
            return True, mt_infos

        if len(dev_list) == 0:
            return True, []

        m_dsl = self.m_dev_conf_info_dsl(dev_list)
        # 查询终端详情
        es = es_client()
        index = "platform-nmscollector-*mt*"
        try:
            results = es.msearch(index=index, dsl=m_dsl)
        except Exception as err:
            logger.error(err)
            return False, err.args

        # 获取终端信息
        mt_infos = []
        for result in results['responses']:
            bitrate = jsonpath.jsonpath(result, '$..conf_info.bitrate')  # 呼叫码率
            mt_type = jsonpath.jsonpath(result, '$..source.devtype')  # 终端类型

            audio_up_bitrate = jsonpath.jsonpath(
                result, '$..audio_send[?(@.id==0)].audio_up_bitrate')
            audio_up_format = jsonpath.jsonpath(
                result, '$..audio_send[?(@.id==0)].format')

            audio_down_bitrate = jsonpath.jsonpath(
                result, '$..audio_recv[?(@.id==0)].audio_down_bitrate')
            audio_down_format = jsonpath.jsonpath(
                result, '$..audio_recv[?(@.id==0)].format')

            privideo_video_down_bitrate = jsonpath.jsonpath(
                result, '$..privideo_recv[?(@.id==0)].video_down_bitrate')
            privideo_video_down_framerate = jsonpath.jsonpath(
                result, '$..privideo_recv[?(@.id==0)].framerate')
            privideo_video_down_res = jsonpath.jsonpath(
                result, '$..privideo_recv[?(@.id==0)].res')
            privideo_video_down_format = jsonpath.jsonpath(
                result, '$..privideo_recv[?(@.id==0)].format')

            privideo_video_up_bitrate = jsonpath.jsonpath(
                result, '$..privideo_send[?(@.id==0)].video_up_bitrate')
            privideo_video_up_framerate = jsonpath.jsonpath(
                result, '$..privideo_send[?(@.id==0)].framerate')
            privideo_video_up_res = jsonpath.jsonpath(
                result, '$..privideo_send[?(@.id==0)].res')
            privideo_video_up_format = jsonpath.jsonpath(
                result, '$..privideo_send[?(@.id==0)].format')

            assvideo_video_down_bitrate = jsonpath.jsonpath(
                result, '$..assvideo_recv[?(@.id==0)].video_down_bitrate')
            assvideo_video_down_framerate = jsonpath.jsonpath(
                result, '$..assvideo_recv[?(@.id==0)].framerate')
            assvideo_video_down_res = jsonpath.jsonpath(
                result, '$..assvideo_recv[?(@.id==0)].res')
            assvideo_video_down_format = jsonpath.jsonpath(
                result, '$..assvideo_recv[?(@.id==0)].format')

            assvideo_video_up_bitrate = jsonpath.jsonpath(
                result, '$..assvideo_send[?(@.id==0)].video_up_bitrate')
            assvideo_video_up_framerate = jsonpath.jsonpath(
                result, '$..assvideo_send[?(@.id==0)].framerate')
            assvideo_video_up_res = jsonpath.jsonpath(
                result, '$..assvideo_send[?(@.id==0)].res')
            assvideo_video_up_format = jsonpath.jsonpath(
                result, '$..assvideo_send[?(@.id==0)].format')

            # 转换格式
            audio_up_format = [
                MtAudioFormatNMS.get(
                    audio_up_format[0]).name] if audio_up_format is not False else False
            audio_down_format = [
                MtAudioFormatNMS.get(
                    audio_down_format[0]).name] if audio_down_format is not False else False
            privideo_video_down_res = [MtVideoResolutionNMSDesc.get(MtVideoResolutionTypeNMS.get(
                privideo_video_down_res[0]).name)] if privideo_video_down_res is not False else False
            privideo_video_down_format = [MtVideoFormatNMS.get(
                privideo_video_down_format[0]).name] if privideo_video_down_format is not False else False
            privideo_video_up_res = [
                MtVideoResolutionNMSDesc.get(
                    MtVideoResolutionTypeNMS.get(
                        privideo_video_up_res[0]).name)] if privideo_video_up_res is not False else False
            privideo_video_up_format = [MtVideoFormatNMS.get(
                privideo_video_up_format[0]).name] if privideo_video_up_format is not False else False
            assvideo_video_down_res = [MtVideoResolutionNMSDesc.get(MtVideoResolutionTypeNMS.get(
                assvideo_video_down_res[0]).name)] if assvideo_video_down_res is not False else False
            assvideo_video_down_format = [MtVideoFormatNMS.get(
                assvideo_video_down_format[0]).name] if assvideo_video_down_format is not False else False
            assvideo_video_up_res = [
                MtVideoResolutionNMSDesc.get(
                    MtVideoResolutionTypeNMS.get(
                        assvideo_video_up_res[0]).name)] if assvideo_video_up_res is not False else False
            assvideo_video_up_format = [MtVideoFormatNMS.get(
                assvideo_video_up_format[0]).name] if assvideo_video_up_format is not False else False

            mt_info = [bitrate,
                       mt_type,
                       audio_up_bitrate,
                       audio_up_format,
                       audio_down_bitrate,
                       audio_down_format,
                       privideo_video_down_bitrate,
                       privideo_video_down_framerate,
                       privideo_video_down_res,
                       privideo_video_down_format,
                       privideo_video_up_bitrate,
                       privideo_video_up_framerate,
                       privideo_video_up_res,
                       privideo_video_up_format,
                       assvideo_video_down_bitrate,
                       assvideo_video_down_framerate,
                       assvideo_video_down_res,
                       assvideo_video_down_format,
                       assvideo_video_up_bitrate,
                       assvideo_video_up_framerate,
                       assvideo_video_up_res,
                       assvideo_video_up_format
                       ]
            mt_info = [x[0] if x is not False else "" for x in mt_info]
            mt_info_dict = dict(zip(mt_param_keys, mt_info))
            mt_infos.append(mt_info_dict)
        return True, mt_infos

    def get_dev_info(self):
        # 从创会消息获取主被叫终端信息
        dev_add_info = self.get_dev_add_info()
        # e164/name/proto_type/who(caller/callee)
        if not dev_add_info[0]:
            # 获取终端信息失败
            return dev_add_info
        else:
            dev_add_info = dev_add_info[1]

        # 终端入会消息
        normal_dev_info = [
            x for x in dev_add_info if x['mt_e164']]  # 正常终端 list of dict
        abnormal_dev_info = [
            x for x in dev_add_info if not x['mt_e164']]  # 其他  list of dict

        # 终端列表
        normal_dev_list = [x['mt_e164'] for x in normal_dev_info]
        abnormal_dev_list = [x['mt_e164'] for x in abnormal_dev_info]

        # 终端质量
        normal_dev_qua_info = self.get_dev_quality(normal_dev_list, 1)
        if not normal_dev_qua_info[0]:
            return normal_dev_qua_info
        else:
            normal_dev_qua_info = normal_dev_qua_info[1]
        abnormal_dev_qua_info = self.get_dev_quality(abnormal_dev_list, 2)[1]

        # 终端会议消息
        normal_dev_conf_info = self.q_dev_conf_info(normal_dev_list, 1)
        if not normal_dev_conf_info[0]:
            # 查询失败
            return normal_dev_conf_info
        else:
            normal_dev_conf_info = normal_dev_conf_info[1]
        abnormal_dev_conf_info = self.q_dev_conf_info(abnormal_dev_list, 2)[1]

        # calle_moid = self.get_dev_moid_info(normal_dev_list)
        # 获取ip/version
        normal_dev_ip_ver = self.get_dev_extra_info(normal_dev_list, 1)
        if not normal_dev_ip_ver[0]:
            # 查询失败
            return normal_dev_ip_ver
        else:
            normal_dev_ip_ver = normal_dev_ip_ver[1]
        abnormal_dev_ip_ver = self.q_dev_conf_info(abnormal_dev_list, 2)[1]

        # #  合并数据
        def dict_update(x, y, z, w):
            x.update(y)
            x.update(z)
            x.update(w)
            return x

        normal_dev_info = [
            dict_update(
                x,
                y,
                z,
                w) for x,
            y,
            z,
            w in zip(
                normal_dev_info,
                normal_dev_conf_info,
                normal_dev_qua_info,
                normal_dev_ip_ver)]
        abnormal_dev_info = [
            dict_update(
                x,
                y,
                z,
                w) for x,
            y,
            z,
            w in zip(
                abnormal_dev_info,
                abnormal_dev_conf_info,
                abnormal_dev_qua_info,
                abnormal_dev_ip_ver)]
        normal_dev_info.extend(abnormal_dev_info)
        caller = [x for x in normal_dev_info if x['who'] == 'caller'][0]
        callee = [x for x in normal_dev_info if x['who'] == 'callee'][0]
        caller.pop("who")
        callee.pop("who")
        return True, [caller, callee]
