"""
media->frame里面的码率，统一除1024再乘8，单位为kb/s      他原始单位是Bps  目前终端和平台码率用的meida上的
转发上的码率，统一除1024再乘8 单位未kb/s    他原始单位是Bps
medianet上的码率，统一除1024，单位未kb/s	  他原始单位是bps
"""

import os
import re
import datetime
import json
import logging
import jsonpath
from platmonitor.dsl import dsl, es_ql
from django.db import connections
from copy import deepcopy
from ops.settings import BASE_DIR
from common.my_redis import redis_client
from common.es_client import es_client
from common import my_elastic

from common.conf_params_enum import *
from common.timeFormatConverter import localstr2utctimestamp

logger = logging.getLogger('ops.' + __name__)


class ConfQuality:
    """
    根据时间范围批量查询终会议质量   批量查询，不提供单独会议查询接口
    """

    def __init__(self, **kwargs):
        """
        初始化
        """
        self.start_time = kwargs.get("start_time")
        self.end_time = kwargs.get("end_time")
        self.index = "platform-confexperience-*"

    def make_conf_quality_dsl(self):
        """
        构建查询会议质量的dsl
        :return: dict      dsl
        """
        # 模板
        dsl_ = deepcopy(dsl.conf_quality_by_time_dsl)
        dsl_['query']['bool']['filter']['range']['@timestamp'] = {
            "gte": self.start_time, "lte": self.end_time}
        return dsl_

    def q_conf_quality_info(self):
        """
        查询会议质量
        :return: tuple    (False,error)/(True,list)
        """
        body = self.make_conf_quality_dsl()
        es = es_client()
        try:
            quality = es.search(index=self.index, dsl=body)
        except Exception as err:
            logger.error(err)
            return False, err.args

        conf_quality_info = []
        if quality.get('hits', {}).get('total', 0) == 0:
            return True, conf_quality_info

        for sig_conf_e164_info in quality['aggregations']['conf']['buckets']:
            conf_id = sig_conf_e164_info['key']

            for sig_conf in sig_conf_e164_info['time']['buckets']:
                score = jsonpath.jsonpath(sig_conf, "$.top1..source.score")
                if score is False:
                    continue
                else:
                    conf_quality_info.append([score[0], conf_id])
        return True, conf_quality_info

    @staticmethod
    def cal(star):
        if not isinstance(star, (int, float)):
            return ""
        if star < 2.75:
            return 1
        elif 2.75 <= star < 3.75:
            return 2
        elif 3.75 <= star < 4.75:
            return 3
        else:
            return 4

    def get_quality(self, detail=False):
        """
        计算质量
        :return:list
        """
        # 查询异常离会

        quality = self.q_conf_quality_info()
        if not quality[0]:
            return quality
        else:
            quality = quality[1]

        conf_list = [x[1] for x in quality]
        score_list = [x[0] for x in quality]
        quality_only = list(map(self.cal, score_list))

        if detail:
            return True, list(zip(quality_only, conf_list))
        else:
            return True, quality_only


class ConfQualityCustomize:
    """
    根据会议号批量查询会议质量
    """

    def __init__(self, conf_list):
        """
        初始化
        :type conf_list: list
        :param conf_list: [[conf_id, s_t, e_t], ...]
        """
        self.conf_list = conf_list
        self.index = "platform-confexperience-*"
        self.init()

    def init(self):
        for conf in self.conf_list:
            end_time = conf[2]
            if end_time == ConfEndTimeType.REALTIME.name or end_time == ConfEndTimeType.MANUAL.name:
                end_time = int((datetime.datetime.now()).timestamp() * 1000)
                conf[2] = end_time
            elif end_time == ConfEndTimeType.ABEND.name:
                # 异常结会按会议时长2小时计算
                end_time = conf[1] + 7200000
                conf[2] = end_time

    def make_conf_quality_dsl(self):
        """
        构建批量查询会议质量的dsl
        :return: dict      dsl
        """
        # 模板
        dsl_ = deepcopy(dsl.conf_quality_by_confid_dsl)
        m_dsl = ""
        for conf in self.conf_list:
            dsl_['query']['bool']['must'][0]['match']['source.confe164'] = conf[0]
            # 向后多查10S
            dsl_['query']['bool']['filter']['range']['@timestamp'] = {
                "gte": conf[1], "lte": conf[2] + 10 * 1000}
            m_dsl += '{}\n' + json.dumps(dsl_) + '\n'
        return m_dsl

    def q_conf_quality_info(self):
        """
        批量查询会议质量
        :return: tuple    (False,error)/(True,list)
        """
        body = self.make_conf_quality_dsl()
        es = es_client()
        try:
            quality = es.msearch(index=self.index, dsl=body)
        except Exception as err:
            logger.error(err)
            return False, err.args

        conf_quality_info = []
        for sig_conf_e164_info in quality['responses']:
            score = jsonpath.jsonpath(
                sig_conf_e164_info, "$.hits..source.score")
            if score is False:
                conf_quality_info.append("")
            else:
                conf_quality_info.append(score[0])
        return True, conf_quality_info

    def get_quality(self):
        """
        计算质量
        :return:list
        """
        # 查询异常离会

        quality = self.q_conf_quality_info()
        if not quality[0]:
            return quality
        else:
            quality = quality[1]
        quality_only = list(map(ConfQuality.cal, quality))
        return True, quality_only


class DeviceConfQuality:
    """
    批量计算终会议终端质量
    根据终端异常离会次数、终端卡顿次数、终端丢包率计算(由于终端卡顿次数取数据困难，暂不做计算)
    点对点会议计算会议质量时终端异常离会不做计算
    """

    def __init__(self, conf_type, dev_info, summary=False):
        """
        初始化
        :param conf_type:会议类型
        :param dev_info: 会议终端信息列表,会议号码/会议起止时间/终端e164号码,例如:[(conf_e164,start,end,dev_e164...),(...),]
        :param summary: False:返回终端质量详情  True:返回会议质量统计结果
        """
        self.conf_type = conf_type
        self.summary = summary
        self.dev_info = dev_info

    def m_multi_dev_leave_dsl(self, conf_info):
        """
        构建批量查询多点会议会议终端离会原因dsl
        :param conf_info: 会议信息的列表,信息包括会议号码/会议起止时间,eg [(conf_e164,start,end),(...),]
        :return: dsl
        """
        # 会议号码模板
        conf_condition = {"match": {"source.mtinfo.confe164": ""}}
        # 构建查询语句模板
        dsl_ = deepcopy(dsl.conf_multi_dev_leave_dsl)
        must_block = dsl_['query']['bool']['must']
        # 先将模板中会议号码条件删除
        for item in must_block[::-1]:
            if 'terms' in item:
                continue
            if 'source.mtinfo.confe164' in item['match']:
                must_block.remove(item)
                break
        # 将会议号过滤条件放在位置0，方便后续修改
        must_block.insert(0, conf_condition)
        dsl_['query']['bool']['must'] = must_block

        m_dsl = ''
        for confe164, start_time, end_time in conf_info:
            if end_time == ConfEndTimeType.REALTIME.name or end_time == ConfEndTimeType.MANUAL.name:
                end_time = int(datetime.datetime.now().timestamp() * 1000)
            elif end_time == ConfEndTimeType.ABEND.name:
                # 异常结会按会议时长2小时计算
                end_time = start_time + 7200000
            # 会议号码,在must中0位置
            dsl_['query']['bool']['must'][0]["match"]["source.mtinfo.confe164"] = confe164
            # 时间
            if not end_time:
                dsl_['query']['bool']['filter']['range']['@timestamp'] = {
                    "gte": start_time}
            else:
                dsl_['query']['bool']['filter']['range']['@timestamp'] = {
                    "gte": start_time, "lte": end_time}

            m_dsl += '{}\n' + json.dumps(dsl_) + '\n'
        return m_dsl

    def q_multi_dev_leave_info(self, conf_info):
        """
        批量查询多点会议会议终端离会原因
        :param conf_info: 会议信息的列表,信息包括会议号码/会议起止时间,eg [(conf_e164,start,end),(...),]
        :return:list of dict. eg [{'111':8,'222':9},{}]
        """
        filter_path = deepcopy(dsl.conf_multi_dev_leave_filter)
        body = self.m_multi_dev_leave_dsl(conf_info)  # 获取创会dsl查询语句
        es = es_client()
        index = "platform-nmscollector-*cmu*"
        try:
            dev_leave_info = es.msearch(
                index=index, dsl=body, filter_path=filter_path)
        except Exception as err:
            logger.error(err)
            return False, err.args

        conf_leave_info = []
        for aggregations in dev_leave_info['responses']:
            dev = jsonpath.jsonpath(aggregations, '$..key')
            if not dev:
                # 列表为空
                conf_leave_info.append({})
                continue
            count = jsonpath.jsonpath(aggregations, '$..doc_count')
            if not count:
                # 列表为空
                conf_leave_info.append({})
                continue
            conf_leave_info.append(dict(zip(dev, count)))
        return True, conf_leave_info

    def m_multi_dev_lossrate_dsl(self, conf_info):
        """
        构建批量查询会议终端丢包率的dsl
        :param conf_info: 会议信息的列表,信息包括会议号码/会议起止时间,eg [(conf_e164,start,end),(...),]
        :return: dsl
        """
        # 会议号码模板
        conf_condition = {"match": {"source.conf_info.conf_e164": ""}}
        # 构建查询语句模板
        dsl_ = deepcopy(dsl.conf_pkts_lossrate_dsl)
        must_block = dsl_['query']['bool']['must']
        # 先将模板中会议号码条件删除
        for item in must_block[::-1]:
            if 'source.conf_info.conf_e164' in item['match']:
                must_block.remove(item)
                break
        # 将会议号过滤条件放在位置0，方便后续修改
        must_block.insert(0, conf_condition)
        dsl_['query']['bool']['must'] = must_block

        m_dsl = ''
        for confe164, start_time, end_time in conf_info:
            if end_time == ConfEndTimeType.REALTIME.name or end_time == ConfEndTimeType.MANUAL.name:
                end_time = int(datetime.datetime.now().timestamp() * 1000)
            elif end_time == ConfEndTimeType.ABEND.name:
                # 异常结会按会议时长2小时计算
                end_time = start_time + 7200000
            # 会议号码,在must中0位置
            dsl_[
                'query']['bool']['must'][0]["match"]["source.conf_info.conf_e164"] = confe164
            # 时间
            if not end_time:
                dsl_['query']['bool']['filter']['range']['@timestamp'] = {
                    "gte": start_time}
            else:
                dsl_['query']['bool']['filter']['range']['@timestamp'] = {
                    "gte": start_time, "lte": end_time}
            m_dsl += '{}\n' + json.dumps(dsl_) + '\n'
        return m_dsl

    def q_dev_lossrate_info(self, conf_info):
        """
        批量查询会议终端丢包率
        :param conf_info: 会议信息的列表,信息包括会议号码/会议起止时间,eg [(conf_e164,start,end),(...),]
        :return:list of dict. eg [{'111':8,'222':9},{}]
        """
        filter_path = deepcopy(dsl.conf_pkts_lossrate_filter)
        body = self.m_multi_dev_lossrate_dsl(conf_info)  # 获取丢包率dsl查询语句
        es = es_client()
        index = "platform-nmscollector-*mt*"
        try:
            dev_lossrate_info = es.msearch(
                index=index, dsl=body, filter_path=filter_path)
        except Exception as err:
            logger.error(err)
            return False, err.args

        conf_lossrate_info = []
        for aggregations in dev_lossrate_info['responses']:
            dev = jsonpath.jsonpath(aggregations, '$..key')
            if not dev:
                # 列表为空
                conf_lossrate_info.append({})
                continue
            lossrate = {}  # 单个会议的丢包率
            for d in dev:
                cur_loss = jsonpath.jsonpath(
                    aggregations,
                    "$..buckets[?(@.key=='%s')]..value" %
                    d)
                if cur_loss:
                    cur_loss = max([v for v in cur_loss if v], default=0)
                    lossrate[d] = cur_loss
            conf_lossrate_info.append(lossrate)
        return True, conf_lossrate_info

    @staticmethod
    def cal(star):
        if star < 2.75:
            return 1
        elif 2.75 <= star < 3.75:
            return 2
        elif 3.75 <= star < 4.75:
            return 3
        else:
            return 4

    def get_quality(self):
        """
        计算质量
        :return:list
        """

        conf_info = [x[:3] for x in self.dev_info]
        # 查询异常离会
        if self.conf_type == ConfType.P2P:
            # 点对点会议无离会原因
            conf_leave_info = []
            for i in range(len(conf_info)):
                conf_leave_info.append({})
        else:
            conf_leave_info = self.q_multi_dev_leave_info(conf_info)
            if not conf_leave_info[0]:
                # 如果查询失败
                return conf_leave_info
            else:
                conf_leave_info = conf_leave_info[1]

        # 查询丢包率
        conf_lossrate_info = self.q_dev_lossrate_info(conf_info)
        if not conf_lossrate_info[0]:
            # 如果查询失败
            return conf_lossrate_info
        else:
            conf_lossrate_info = conf_lossrate_info[1]

        # 查询终端卡顿次数
        # 终端卡顿次数暂不计算

        quality = []
        for count, conf in enumerate(self.dev_info):
            devices = conf[3:]  # 会议终端164号
            conf_quality = []  # 会议质量

            for device in devices:
                q = 5  # 总分5
                leave_num = conf_leave_info[count].get(device)
                # 计算异常退会
                if leave_num is not None:
                    if leave_num >= 10:
                        conf_quality.append(0)
                        continue
                    else:
                        q -= 0.5 * leave_num

                lossrate = conf_lossrate_info[count].get(device)
                # 计算丢包率
                if lossrate is not None:
                    if lossrate > 40:
                        conf_quality.append(0)
                        continue
                    elif 0 < lossrate <= 40:
                        q -= (lossrate + 10) // 10

                q = q if q > 0 else 0
                conf_quality.append(q)
            if self.summary:
                if len(devices) == 0:
                    summary_quality = 4  # 终端列表为空直接体验优秀
                else:
                    summary_quality = self.cal(
                        sum(conf_quality) / len(conf_quality))
                quality.append(summary_quality)
            else:
                quality.append(conf_quality)
        return True, quality


class MultiConfList:
    """
    查询多点会议会议列表，返回会议详细信息
    """
    # 会议号/开始时间/结束时间/会议名称/会议类型/发起人/会议规模/平台域/用户域/用户域名称/视频格式/加密方式/码率/帧率/分辨率
    conf_param_keys = [
        'conf_id',
        'start_time',
        'end_time',
        'conf_name',
        'conf_type',
        'organizer',
        'number',
        'platform_moid',
        'domain_moid',
        'domain_name',
        'format',
        'encryption',
        'bitrate',
        'frame',
        'resolution']

    def __init__(self, **kwargs):
        self.platform_moid = kwargs.get('platform_moid')
        self.domain_moid = kwargs.get('domain_moid')
        self.conf_type = kwargs.get('conf_type')
        self.conf_status = kwargs.get('conf_status')
        self.start_time = kwargs.get('start_time')  # 历史会议开始时间筛选
        self.real_conf_start_time = kwargs.get('start_time')  # 实时会议开始时间筛选
        self.end_time = kwargs.get('end_time')
        self.keywords = kwargs.get('keywords')
        self.level = kwargs.get('level')
        self.count = kwargs.get('count')
        self.start = kwargs.get('start')
        self.params_init()

    def params_init(self):
        """
        参数检查
        :return:
        """
        if self.conf_type is not None:
            # 如果会议类型参数错误，引发异常
            if self.conf_type not in [
                ConfType.TRADITION,
                ConfType.PORT,
                ConfType.MULTI]:
                raise ValueError('conference type error')
            if self.conf_type == ConfType.MULTI:
                self.conf_type = None
        # if self.conf_status is not None:
        #     # 如果会议状态参数错误，引发异常
        #     if self.conf_status not in [ConfStat.HISTORY, ConfStat.REALTIME]:
        #         raise ValueError('conference status error')
        # if self.start_time is not None:
        #     self.start_time = int(self.start_time)
        # if self.end_time is not None:
        #     self.end_time = int(self.end_time)
        # 历史会议默认搜索 24小时内的会议
        if self.start_time is None and self.end_time is None:
            self.start_time = int(
                (datetime.datetime.now() -
                 datetime.timedelta(
                     hours=24)).timestamp() *
                1000)
        # if self.level is not None:
        #     if self.level not in ['1', '2', '3', '4']:
        #         raise ValueError('level type error')

    def q_create_info(self):
        """
        从网管查询创会消息列表
        :return:一个二值元组，第一个值为查询是否成功(True:成功 False:失败)
                第二个值失败时为失败原因，成功时为结果(列表)
        """
        filter_path = self.get_creat_filter()
        body = self.m_create_dsl()  # 获取创会dsl查询语句
        es = es_client()
        index = "platform-nmscollector-*cmu*"
        try:
            conf_c_list = es.search(
                index=index, dsl=body, filter_path=filter_path)
        except Exception as err:
            logger.error(err)
            return False, err.args

        if len(conf_c_list) == 0:
            return True, []

        result = self.filter_creat_result(conf_c_list)
        return True, result

    def m_create_dsl(self):
        """
        构建创会消息查询语句
        :return: dsl语句
        """
        # 平台域
        if self.platform_moid is not None:
            plat_condition = {
                "match": {
                    "beat.platform_moid": "%s" %
                                          self.platform_moid}}
        else:
            plat_condition = None
        # 用户域
        if self.domain_moid is not None:
            user_condition = {
                "match": {
                    "source.confinfo.domainmoid": "%s" %
                                                  self.domain_moid}}
        else:
            user_condition = None
        # 会议类型
        if self.conf_type is not None:
            conf_type = {
                "match": {
                    "source.confinfo.conftype": "%s" %
                                                self.conf_type}}
        else:
            conf_type = None
        # keyword
        if self.keywords is not None:
            keyword_condition = {
                "bool": {
                    "should": [{"wildcard": {"source.confinfo.organizer.keyword": "*{}*".format(self.keywords)}},
                               {"wildcard": {"source.confinfo.confe164.keyword": "*{}*".format(self.keywords)}},
                               {"wildcard": {"source.confinfo.confname.keyword": "*{}*".format(self.keywords)}}],
                    "minimum_should_match": 1}}
        else:
            keyword_condition = None
        # 时间
        time = {}
        # 开始时间
        if self.start_time is not None:
            time["gte"] = self.start_time
        if self.end_time is not None:
            time["lte"] = self.end_time

        # 构建查询语句
        dsl_ = deepcopy(dsl.conf_multi_creat_dsl)
        must_block = dsl_['query']['bool']['must']
        # 先将模板中平台域/用户域/会议类型条件删除
        for item in must_block[::-1]:
            if 'beat.platform_moid' in item['match']:
                must_block.remove(item)
                continue
            if 'source.confinfo.domainmoid' in item['match']:
                must_block.remove(item)
                continue
            if 'source.confinfo.conftype' in item['match']:
                must_block.remove(item)
                continue
        # 将查询条件加入
        if plat_condition is not None:
            must_block.append(plat_condition)
        if user_condition is not None:
            must_block.append(user_condition)
        if conf_type is not None:
            must_block.append(conf_type)
        if keyword_condition is not None:
            must_block.append(keyword_condition)

        dsl_['query']['bool']['must'] = must_block
        dsl_['query']['bool']['filter']['range']['@timestamp'] = time
        return dsl_

    def get_creat_filter(self):
        return deepcopy(dsl.conf_multi_creat_all_filter)

    def filter_creat_result(self, conf_info):
        """
        控制创会消息返回字段
        :param conf_info: 创会消息信息列表
        :return: 会议信息的列表[{},{},...]
        """
        info = conf_info['aggregations']['confinfo']['buckets']
        if len(info) == 0:
            # 会议信息为空返回空列表
            return []

        results = []
        for single_confid in info:
            for single_conf in single_confid['begin']['buckets']:
                confe164 = jsonpath.jsonpath(single_conf, '$..confe164')  # 会议号
                begintime = jsonpath.jsonpath(
                    single_conf, '$..begintime')  # 开始时间
                endtime = jsonpath.jsonpath(single_conf, '$..endtime')  # 结束时间
                confname = jsonpath.jsonpath(
                    single_conf, '$..confname')  # 会议名称
                conftype = jsonpath.jsonpath(
                    single_conf, '$..conftype')  # 会议类型
                organizer = jsonpath.jsonpath(
                    single_conf, '$..organizer')  # 会议发起人
                scale = jsonpath.jsonpath(single_conf, '$..scale')  # 会议规模
                platform_moid = jsonpath.jsonpath(
                    single_conf, '$..platform_moid')  # 平台域moid
                domainmoid = jsonpath.jsonpath(
                    single_conf, '$..domainmoid')  # 用户域moid
                domainname = jsonpath.jsonpath(
                    single_conf, '$..domainname')  # 用户域名称
                format = jsonpath.jsonpath(single_conf, '$..format')  # 视频格式
                encryption = jsonpath.jsonpath(
                    single_conf, '$..encryption')  # 加密方式
                bitrate = jsonpath.jsonpath(single_conf, '$..bitrate')  # 码率
                frame = jsonpath.jsonpath(single_conf, '$..frame')  # 帧率
                resolution = jsonpath.jsonpath(
                    single_conf, '$..resolution')  # 分辨率

                if not all([confe164, begintime]):
                    continue
                try:
                    # 修改时间格式
                    begintime = [localstr2utctimestamp(begintime[0])]

                    if endtime is not False:
                        if endtime[0]:
                            endtime = [localstr2utctimestamp(endtime[0])]
                        else:
                            endtime = [ConfEndTimeType.MANUAL.name]
                    else:
                        endtime = [ConfEndTimeType.ABEND.name]

                    # 替换 视频格式/加密方式/分辨率
                    format = [
                        ConfVideoFormat.get(
                            format[0]).name] if format is not False else False
                    encryption = [
                        ConfEncryptionType.get(
                            encryption[0]).name] if encryption is not False else False
                    resolution = [
                        ConfVideoResolutionType.get(
                            resolution[0]).name] if resolution is not False else False
                except Exception as err:
                    logger.error(err)
                    continue
                else:
                    results.append([confe164,
                                    begintime,
                                    endtime,
                                    confname,
                                    conftype,
                                    organizer,
                                    scale,
                                    platform_moid,
                                    domainmoid,
                                    domainname,
                                    format,
                                    encryption,
                                    bitrate,
                                    frame,
                                    resolution])

        results = [[value[0] if value is not False else "" for value in item]
                   for item in results]
        results.sort(key=lambda x: x[1], reverse=True)  # 按开始时间排序
        results = [dict(zip(self.conf_param_keys, item)) for item in results]
        return results

    def q_destroy_info(self, conf_info):
        """
        查询结会消息列表
        :param conf_info:conf_info: 包括会议号码和会议开始时间的可迭代对象 eg (('1111',s_time,end_time),)
        :return:失败和失败原因或者成功和会议结束时间(map迭代器）
        """
        filter_path = deepcopy(dsl.conf_multi_destroy_filter)
        body = self.m_destroy_dsl(conf_info)
        es = es_client()
        index = "platform-nmscollector-*cmu*"
        try:
            conf_c_list = es.msearch(
                index=index, dsl=body, filter_path=filter_path)
        except Exception as err:
            logger.error(err)
            return False, err.args

        hits = jsonpath.jsonpath(conf_c_list, '$.responses[*].hits.hits')

        # 结会时间为空返回空字符串，否则返回结会时间
        def get_msg(hits_msg):
            if len(hits_msg) == 0:
                return ""
            else:
                return jsonpath.jsonpath(hits_msg, '$..sort[0]')[0]

        return True, list(map(get_msg, hits))

    def m_destroy_dsl(self, conf_info):
        """
        构建结会消息查批量询语句
        :param conf_info: conf_info: 包括会议号码和会议开始时间的可迭代对象 eg (('1111',s_time),)
        :return:
        """
        # 平台域
        if self.platform_moid is not None:
            plat_condition = {
                "match": {
                    "beat.platform_moid": "%s" %
                                          self.platform_moid}}
        else:
            plat_condition = None
        # 会议类型
        if self.conf_type is not None:
            conf_type = {
                "match": {
                    "source.confinfo.conftype": "%s" %
                                                self.conf_type}}
        else:
            conf_type = None
        # 先写到模板占坑
        template_e164 = {"match": {"source.confinfo.confe164": ""}}
        template_time = {"@timestamp": {"gte": ""}}

        dsl_ = deepcopy(dsl.conf_multi_destroy_dsl)
        # 修改通用查询条件
        must_block = dsl_['query']['bool']['must']
        # 先将模板中平台域/会议类型/会议号码条件删除
        for item in must_block[::-1]:
            if 'beat.platform_moid' in item['match']:
                must_block.remove(item)
                continue
            if 'source.confinfo.conftype' in item['match']:
                must_block.remove(item)
                continue
            if 'source.confinfo.confe164' in item['match']:
                must_block.remove(item)
                continue
        # 将查询条件加入
        if plat_condition is not None:
            must_block.append(plat_condition)
        if conf_type is not None:
            must_block.append(conf_type)
        must_block.insert(0, template_e164)  # 164号条件放在第一个位置方便后面修改参数

        dsl_['query']['bool']['must'] = must_block
        dsl_['query']['bool']['filter']['range'] = template_time

        template = deepcopy(dsl_)
        m_dsl = ''
        for e164, s_time in conf_info:
            # must列表第一个为会议号码
            template['query']['bool']['must'][0]['match']['source.confinfo.confe164'] = e164
            template['query']['bool']['filter']['range']['@timestamp']['gte'] = s_time
            m_dsl += '{}\n' + json.dumps(template) + '\n'
        return m_dsl

    def calc_conf_quality(self, conf_list):
        # stat, dev_list = MultiConfDevBaseList(conf_list=conf_list).q_confs_dev_info()  # 终端列表
        # if not stat:
        #     return stat, dev_list
        # conf_dev_list = [conf_list[i] + dev_list[i] for i in
        # range(len(conf_list))]  # 会议中终端列表
        quality_obj = ConfQualityCustomize(conf_list)
        quality = quality_obj.get_quality()
        return quality

    def q_real_time_conf(self):
        """
        从redis里查询实时会议列表
        :return:一个二值元组，第一个值为查询是否成功(True:成功 False:失败)
                第二个值失败时为失败原因，成功时为结果(列表)
        """
        script_path = os.path.join(
            BASE_DIR, 'lua', 'get_real_confs_detail.lua')
        with open(script_path, 'r', encoding='utf8') as f:
            script_content = f.read()

        try:
            # filter  domain_moid/conf_type with redis
            domain_moid = str(
                self.domain_moid) if self.domain_moid is not None else ""
            conf_type = str(
                self.conf_type) if self.conf_type is not None else ""
            multiply = redis_client.register_script(script_content)
            confs_info = multiply(args=[domain_moid, conf_type])
        except Exception as err:
            logger.error(str(err))
            return False, err.args

        real_confs_inf_list = []
        confs_info = [[[y.decode() for y in x] if isinstance(x, list) else x.decode() for x in conf] for conf in
                      confs_info]
        for conf_info in confs_info:
            keys = conf_info[0::2]
            values = conf_info[1::2]
            info_dict = dict(zip(keys, values))
            real_confs_inf_list.append(info_dict)
            # key = str(info_dict['e164']) + str(localstr2utctimestamp(info_dict['starttime']))
            # real_confs_inf_dict[key] = info_dict

        # filter keywords
        if self.keywords:
            pattern = re.compile('.*%s.*' % self.keywords)
            real_confs_inf_list = [
                conf for conf in real_confs_inf_list if (
                    re.search(pattern,
                              " ".join(conf['mtlist'] + [conf['confname'], conf['e164'], conf['creatorname']])))]

        moid = [x['moid'] for x in real_confs_inf_list]  # domain_moid

        if len(moid) == 0:
            return True, []
        # query platform_moid and domain_name
        with connections['movision'].cursor() as cursor:
            sql = "SELECT user_domain_moid,platform_domain_moid,user_domain_name FROM user_domain WHERE user_domain_moid IN %s"
            cursor.execute(sql, [moid])
            sql_result = cursor.fetchall()

        q_moid = [x[0] for x in sql_result]
        q_pd_dn = [x[1:3] for x in sql_result]
        q_domain_dict = dict(zip(q_moid, q_pd_dn))

        # add domain info to conf_info
        for conf_info in real_confs_inf_list:
            plat_domain = q_domain_dict.get(conf_info['moid'])
            conf_info['platform_moid'] = plat_domain[0] if plat_domain is not None else ""
            conf_info['doamin_name'] = plat_domain[1] if plat_domain is not None else ""

        # filter plat_domain
        if self.platform_moid is not None:
            real_confs_inf_list = [
                conf for conf in real_confs_inf_list if conf['platform_moid'] == self.platform_moid]

        result = self.filter_real_conf_result(real_confs_inf_list)
        return True, result

    def filter_real_conf_result(self, conf_info):
        """
        控制创会消息返回字段
        :param conf_info: list  redis列表 [{},{},...]
        :return: 会议信息的列表[{},{},...]
        """
        if len(conf_info) == 0:
            # 会议信息为空返回空列表
            return []

        conf_param_keys = ['conf_status'] + self.conf_param_keys
        conf_status = 1

        results = []
        for single_conf in conf_info:
            confe164 = single_conf.get('e164')  # 会议号
            begintime = single_conf.get('starttime')  # 开始时间
            endtime = single_conf.get('endtime')  # 结束时间
            confname = single_conf.get('confname')  # 会议名称
            conftype = single_conf.get('conftype')  # 会议类型
            organizer = single_conf.get('creatorname')  # 会议发起人
            scale = single_conf.get('maxjoinedmt')  # 会议规模
            platform_moid = single_conf.get('platform_moid')  # 平台域moid
            domainmoid = single_conf.get('moid')  # 用户域moid
            domainname = single_conf.get('doamin_name')  # 用户域名称
            format = single_conf.get('mediatype')  # 视频格式
            encryption = single_conf.get('encryptmode')  # 加密方式
            bitrate = single_conf.get('mediabitrate')  # 码率
            frame = single_conf.get('mediaframe')  # 帧率
            resolution = single_conf.get('mediares')  # 分辨率

            if None in [confe164, begintime]:
                continue
            try:
                # 修改时间格式
                if endtime is not None:
                    if endtime != begintime:
                        endtime = localstr2utctimestamp(endtime)
                    else:
                        endtime = ConfEndTimeType.MANUAL.name
                else:
                    endtime = ConfEndTimeType.ABEND.name

                begintime = localstr2utctimestamp(begintime)
                if self.real_conf_start_time and self.end_time:
                    flag = self.real_conf_start_time <= begintime <= self.end_time
                elif self.real_conf_start_time:
                    flag = self.real_conf_start_time <= begintime
                elif self.end_time:
                    flag = begintime <= self.end_time
                else:
                    flag = True
                if not flag:
                    continue

                # 替换 视频格式/加密方式/分辨率
                format = ConfVideoFormat.get(
                    int(format)).name if format is not None else None
                encryption = ConfEncryptionType.get(
                    int(encryption)).name if encryption is not None else None
                resolution = ConfVideoResolutionType.get(
                    int(resolution)).name if resolution is not None else None

                #
                conftype = int(conftype) if conftype is not None else ""
                scale = int(scale) if scale is not None else ""
                bitrate = int(bitrate) if bitrate is not None else ""
                frame = int(frame) if frame is not None else ""
            except Exception as err:
                logger.error(err)
                continue
            else:
                results.append([conf_status,
                                confe164,
                                begintime,
                                endtime,
                                confname,
                                conftype,
                                organizer,
                                scale,
                                platform_moid,
                                domainmoid,
                                domainname,
                                format,
                                encryption,
                                bitrate,
                                frame,
                                resolution])

        results = [[value if value is not None else "" for value in item]
                   for item in results]
        results.sort(key=lambda x: x[2], reverse=True)  # 按开始时间排序
        results = [dict(zip(conf_param_keys, item)) for item in results]
        return results

    def m_real_time_conf_dsl(self):
        """
        构建mq消息实时会议查询语句
        :return:
        """
        # 平台域
        if self.platform_moid is not None:
            plat_condition = {
                "match": {
                    "beat.platform_moid": "%s" %
                                          self.platform_moid}}
        else:
            plat_condition = None

        # 构建查询语句
        dsl_ = deepcopy(dsl.conf_multi_real_time_simple_dsl)
        must_block = dsl_['query']['bool']['must']
        # 先将模板中平台域/用户域条件删除
        for item in must_block[::-1]:
            if 'beat.platform_moid' in item['match']:
                must_block.remove(item)
                continue
        # 将查询条件加入
        if plat_condition is not None:
            must_block.append(plat_condition)
        dsl_['query']['bool']['must'] = must_block
        return dsl_

    def get_conference(self):
        """
        获取会议信息详情列表
        :return: 一个二值元组，第一个值为查询是否成功(True:成功 False:失败)
                 第二个值失败时为失败原因，成功时为结果(None表示查询结果为空)
        """
        redis_real_time_confs = self.q_real_time_conf()
        if not redis_real_time_confs[0]:
            # 如果查询失败，返回(false, err)
            return redis_real_time_confs
        else:
            # [{conf_info}, {}]
            redis_real_time_confs = redis_real_time_confs[1]

        if self.conf_status == ConfStat.REALTIME:
            # 实时会议
            total = len(redis_real_time_confs)
            redis_real_time_confs = redis_real_time_confs[self.start:self.start + self.count]

            if len(redis_real_time_confs) == 0:
                # 列表为空返回None
                return True, (None, 0)

            # 处理会议质量
            def add_conf_quality(conf_inf, qua):
                """
                添加会议质量
                :type conf_inf:dict
                """
                if qua == 1:
                    desc = "体验不好"
                elif qua == 2:
                    desc = "体验一般"
                elif qua == 3:
                    desc = "体验良好"
                elif qua == 4:
                    desc = "体验优秀"
                else:
                    desc = ""
                conf_inf.update({'level': qua, 'desc': desc})
                return conf_inf

            conf_list_simple = [[conf['conf_id'], conf['start_time'],
                                 conf['end_time']] for conf in redis_real_time_confs]
            quality = self.calc_conf_quality(conf_list_simple)
            if not quality[0]:
                # 如果会议质量获取失败，返回(false, err)
                return quality
            else:
                quality = quality[1]
            conf_full_list = list(
                map(add_conf_quality, redis_real_time_confs, quality))
            # if self.level:
            #     level = int(self.level)
            #     conf_full_list = [conf for conf in conf_full_list if conf['level'] == level]
            # else:
            #     conf_full_list = list(conf_full_list)

            conf_full_list = self.add_conf_media_type(conf_full_list)
            if len(conf_full_list) == 0:
                # 列表为空返回None
                return True, (None, 0)
            else:
                return True, (conf_full_list, total)
        else:
            # 全部会议/历史会议
            # 首先获取创会列表
            conf_create_msgs = self.q_create_info()
            if not conf_create_msgs[0]:
                # 如果创会列表获取失败，返回(false, err)
                return conf_create_msgs
            if len(conf_create_msgs[1]) == 0:
                return True, (None, 0)
            create_msgs = conf_create_msgs[1]  # 会议信息原始数据

            # 处理历史会议/全部会议
            if self.conf_status == ConfStat.HISTORY:
                # 历史会议  将实时会议过滤掉
                if len(redis_real_time_confs) == 0:
                    pass
                else:
                    for real_conf in redis_real_time_confs[:]:
                        for conf_crt in create_msgs[:]:
                            if real_conf['conf_id'] == conf_crt['conf_id'] and real_conf['start_time'] == conf_crt[
                                'start_time']:
                                create_msgs.remove(conf_crt)
                                break
                            if conf_crt['start_time'] < real_conf['start_time']:
                                break
                    if len(create_msgs) == 0:
                        return True, (None, 0)

            total = len(create_msgs)
            create_msgs = create_msgs[self.start:self.start + self.count]

            conf_start = [[conf['conf_id'], conf['start_time']]
                          for conf in create_msgs]  # 会议号码/开始时间
            # 根据创会消息列表获取结会消息列表
            end_time_list = self.q_destroy_info(conf_start)
            if not end_time_list[0]:
                # 如果查询失败，返回 (False, err)
                return end_time_list
            else:
                end_time_list = end_time_list[1]

            redis_real_conf_hash = [hash(str(x['conf_id']) + str(x['start_time']))
                                    for x in redis_real_time_confs]  # 根据会议号和开始时间计算哈希值

            # 添加会议状态和会议结束时间，并将历史会议的结束时间更新为真正结会时间
            def add_conf_status(conf_inf, end_time):
                if end_time:
                    # 历史会议
                    conf_inf['end_time'] = end_time
                    conf_inf['conf_status'] = ConfStat.HISTORY.value
                else:
                    # 实时会议/异常会议
                    if hash(
                            str(conf_inf['conf_id']) + str(conf_inf['start_time'])) in redis_real_conf_hash:
                        # 实时会议
                        conf_inf['conf_status'] = ConfStat.REALTIME.value
                    else:
                        # 历史异常会议
                        conf_inf['conf_status'] = ConfStat.HISTORY.value
                        conf_inf['end_time'] = ConfEndTimeType.ABEND.name
                return conf_inf

            conf_info = list(map(add_conf_status, create_msgs, end_time_list))

            # # 处理会议状态参数
            # if self.conf_status == ConfStat.HISTORY:
            #     # 历史会议
            #     conf_list = [conf for conf in conf_info if conf['conf_status'] == ConfStat.HISTORY]
            # else:
            #     # 全部会议
            #     conf_list = list(conf_info)

            # if len(conf_list) == 0:
            #     return True, None

            # 处理会议质量
            def add_conf_quality(conf_inf, qua):
                """
                添加会议质量
                :type conf_inf:dict
                """
                if qua == 1:
                    desc = "体验不好"
                elif qua == 2:
                    desc = "体验一般"
                elif qua == 3:
                    desc = "体验良好"
                elif qua == 4:
                    desc = "体验优秀"
                else:
                    desc = ""
                conf_inf.update({'level': qua, 'desc': desc})
                return conf_inf

            conf_list_simple = [
                [conf['conf_id'], conf['start_time'], conf['end_time']] for conf in conf_info]
            quality = self.calc_conf_quality(conf_list_simple)
            if not quality[0]:
                # 如果会议质量获取失败，返回(false, err)
                return quality
            else:
                quality = quality[1]
            conf_full_list = list(map(add_conf_quality, conf_info, quality))
            conf_full_list = self.add_conf_media_type(conf_full_list)
            # if self.level:
            #     level = int(self.level)
            #     conf_full_list = [conf for conf in conf_full_list if conf['level'] == level]
            # else:
            #     conf_full_list = list(conf_full_list)

            if len(conf_full_list) == 0:
                return True, (None, 0)
            else:
                return True, (conf_full_list, total)

    @staticmethod
    def get_query_conf_media_type_dsls2m_body(confs):
        '''
        获取批量查询的m_body
        :param confs:
        :return:
        '''
        conf_media_type_dsls = []
        for conf in confs:
            start_time = conf.get('start_time')
            start_time_str = str(datetime.datetime.fromtimestamp(start_time / 1000))
            end_time = conf.get('end_time')
            conf_e164 = conf.get('conf_id')

            if not all([start_time, end_time, isinstance(start_time, int), conf_e164]):
                # 如果会议信息中未找到这些信息，则无法搜索会议资源类型，填写默认 LOCAL 类型
                conf['conf_media_type'] = ConfMediaType.LOCAL
                logger.warning('%s can not find time/conf_e164 info, set conf_media_type 0(LOCAL)' % conf)
                # 向dsls中添加无用查询，保持会议列表和es查询的对应元素顺序一致
                conf_media_type_dsls.append({"size": 0})
                continue

            if end_time in [ConfEndTimeType.ABEND.name, ConfEndTimeType.MANUAL.name]:
                if end_time == ConfEndTimeType.ABEND.name:
                    # 异常会议，搜索的结束时间设置为开始时间的10s之后
                    end_time = start_time + 10000
                else:
                    # 实时手动结束会议
                    end_time = datetime.datetime.now().timestamp() * 1000
            else:
                if not isinstance(end_time, int):
                    logger.warning(end_time)
            base_conf_media_type_dsl = deepcopy(es_ql.conf_media_type_dsl)
            base_conf_media_type_dsl_bool = base_conf_media_type_dsl['dsl']['query']['bool']
            must_filter = {"match": {"source.confE164": conf_e164}}
            start_time_must_filter = {"match_phrase": {"source.starttime": start_time_str}}
            base_conf_media_type_dsl_bool['must'].append(must_filter)
            base_conf_media_type_dsl_bool['must'].append(start_time_must_filter)
            # 使用字符串开始时间匹配
            base_conf_media_type_dsl_bool['filter']['range']['@timestamp']['gte'] = start_time - 60000
            base_conf_media_type_dsl_bool['filter']['range']['@timestamp']['lte'] = end_time
            conf_media_type_dsls.append(base_conf_media_type_dsl)
        m_body = my_elastic.es_client.get_index_header_m_body(*conf_media_type_dsls)

        return m_body

    @staticmethod
    def get_conf_media_type_query_responses(conf_media_type_m_body):
        try:
            responses = my_elastic.es_client.msearch(body=conf_media_type_m_body)['responses']
        except Exception as e:
            logger.exception(e)
            responses = []
        return responses

    def add_conf_media_type(self, confs):
        '''
        在会议列表中增加会议类型字段
        :param confs:
        :return:
        '''
        room_moids = []
        room_moid2domain_moid = {}
        t = datetime.datetime.now().timestamp()
        conf_media_type_m_body = self.get_query_conf_media_type_dsls2m_body(confs)
        t1 = datetime.datetime.now().timestamp()
        responses = self.get_conf_media_type_query_responses(conf_media_type_m_body)
        t2 = datetime.datetime.now().timestamp()
        if responses:
            for response in responses:
                conf_room_moid = jsonpath.jsonpath(response, '$..confroommoid')
                conf_room_moid = conf_room_moid[0] if conf_room_moid else None
                media_master_room_moid = jsonpath.jsonpath(response, '$..media_master.roommoid')
                media_master_room_moid = media_master_room_moid[0] if media_master_room_moid else None
                room_moids.append([conf_room_moid, media_master_room_moid])

        # 生成机房moid去重列表
        unique_room_moids = [moid for moid in list(set(sum(room_moids, [])))]
        t3 = datetime.datetime.now().timestamp()
        if unique_room_moids:
            sql = '''
            SELECT mri.machine_room_moid, mri.domain_moid 
            FROM machine_room_info mri
            WHERE machine_room_moid IN %s AND mri.machine_room_type !=255
            '''
            # mri.machine_room_type = 255的为实验局手动添加的云机房，忽略掉
            params = [unique_room_moids]
            with connections['luban'].cursor() as cursor:
                cursor.execute(sql, params)
                fetchall = cursor.fetchall()
                room_moid2domain_moid = {fetch[0]: fetch[1] for fetch in fetchall}
        logger.info(room_moid2domain_moid)
        t4 = datetime.datetime.now().timestamp()
        logger.info('会议资源类型：生成m_body耗时：%s，查询es耗时：%s，查询mysql耗时：%s' % (t1 - t, t2 - t1, t4 - t3))
        for i, room_moid in enumerate(room_moids):
            # 会议所属机房的域，与会议媒体所属机房的域，相同则为本地会议，反之为云会议
            if room_moid2domain_moid.get(room_moid[0], '') == room_moid2domain_moid.get(room_moid[1]):
                confs[i]['conf_media_type'] = ConfMediaType.LOCAL
            else:
                confs[i]['conf_media_type'] = ConfMediaType.CLOUD
        return confs


class MultiConfExtendInfo:
    """
    # 目前仅针对实时会议

    获取会议额外信息
    发言人/管理方/双流源/录像状态/直播状态/协作状态/mix/vmp/cmu_ip/media_ip
    """

    conf_param_keys = [
        'cmu_ip',
        'speaker',
        'chairman',
        'dualstream',
        'rec_stat',
        'live_stat',
        'dcs_stat',
        'media_ip',
        'vmp',
        'mix']

    def __init__(self, conf_info):
        """
        :param conf_info: list  [[conf_id, start_time],...]
        """
        self.conf_info = conf_info

    def get_info_from_redis(self):
        """
        从redis获取实时会议的  cmu_ip/发言人/管理方/双流源/录像状态/直播状态
        录像状态   1/0 on/off
        直播状态   1/0 on/off
        :return: list
        """
        conf_id = [x[0] for x in self.conf_info]
        script_path = os.path.join(
            BASE_DIR, 'lua', 'get_conf_stat_s_c_r_d.lua')
        with open(script_path, 'r', encoding='utf8') as f:
            script_content = f.read()

        try:
            multiply = redis_client.register_script(script_content)
            conf_info = multiply(args=conf_id)
        except Exception as err:
            logger.error(err)
            return False, err.args
        results = []
        for inf in conf_info:
            if len(inf) == 0:
                results.append(["", "", "", "", 0, 0])
                continue
            result = []
            # cmu_ip/speaker/chairman/dualstream
            s_c_d = [x.decode() for x in inf[:4]]
            result.extend(s_c_d)

            rec = inf[4]
            if rec == b'':
                rec_stat = 0
                live_stat = 0
            else:
                #  1=录像/2=直播/3=both
                rec_stat = 0
                live_stat = 0
                rec = [x.decode() for x in rec]
                rec = [x if x == "" else int(x) for x in rec]
                for rec_mode in rec:
                    if rec_mode == 3:
                        rec_stat = 1
                        live_stat = 1
                    elif rec_mode == 2:
                        # rec_stat = 1
                        live_stat = 1
                    elif rec_mode == 1:
                        rec_stat = 1
            result.extend([rec_stat, live_stat])
            results.append(result)
        return True, results

    def get_vmp_mix_from_redis(self):
        """
        从redis获取实时会议的  合成/混音
        合成   1/0 on/off
        混音   1/0 on/off
        :return: list [[{vmp},{mix}],[...]...]
        """
        conf_id = [x[0] for x in self.conf_info]
        script_path = os.path.join(BASE_DIR, 'lua', 'get_conf_mix_vmp.lua')
        with open(script_path, 'r', encoding='utf8') as f:
            script_content = f.read()

        try:
            multiply = redis_client.register_script(script_content)
            conf_info = multiply(args=conf_id)
        except Exception as err:
            logger.error(err)
            return False, err.args

        results = []
        for inf in conf_info:
            result = []
            for item in inf:
                stat, mode, members = item
                stat = int(stat.decode())
                mode = int(mode.decode()) if mode else ""
                members = [x.decode() for x in members]
                members_id = members[0::2]
                members_name = members[1::2]
                members = [dict(zip(['mt_id', 'mt_name'], item))
                           for item in zip(members_id, members_name)]
                result.append(
                    dict(zip(['stat', 'mode', 'members'], [stat, mode, members])))
            results.append(result)
        return True, results

    def q_dcs_conf_info(self):
        """
        从es查询数据会议(协作会议)状态
        协作状态  1/0  on/off
        :return: list
        """
        body = self.m_dcs_conf_info_dsl()
        es = es_client()
        index = "platform-nmscollector-*dcs*"
        try:
            conf_c_list = es.msearch(index=index, dsl=body)
        except Exception as err:
            logger.error(err)
            return False, err.args

        conf_info = conf_c_list['responses']
        results = []
        for inf in conf_info:
            stat = 0
            event_id = jsonpath.jsonpath(inf, "$..eventid")
            if event_id is not False and event_id[0] == "EV_DCS_CREATE_CONF_INFO":
                stat = 1
            results.append(stat)
        return True, results

    def m_dcs_conf_info_dsl(self):
        """
        构建批量查询数据会议状态的dsl语句
        :return:
        """
        dsl_tem = deepcopy(dsl.conf_dcs_dataconf_stat_dsl)
        must_block = dsl_tem['query']['bool']['must']

        # 先将条件删除
        for condition in must_block:
            if condition.get('bool'):
                must_block.remove(condition)
                break
        dsl_tem['query']['bool']['must'] = must_block

        m_dsl = ''
        for e164, s_time in self.conf_info:
            dsl_ = deepcopy(dsl_tem)
            should_condition = {
                "bool": {
                    "should": [
                        {
                            "match": {
                                "source.createconf.confe164": e164
                            }
                        },
                        {
                            "match": {
                                "source.delconf.confe164": e164
                            }
                        }
                    ],
                    "minimum_should_match": 1
                }

            }
            dsl_['query']['bool']['must'].append(should_condition)
            dsl_['query']['bool']['filter']["range"]["@timestamp"] = {
                "gte": s_time}

            m_dsl += '{}\n' + json.dumps(dsl_) + '\n'
        return m_dsl

    def m_media_ip_info_dsl(self):
        """
        构建批量查询媒体资源服务器moid的dsl语句
        :return:
        """
        dsl_tem = {"size": 1, "_source": "beat.eqpid", "query": {"bool": {"filter": []}}}

        m_dsl = ''
        for e164, s_time in self.conf_info:
            dsl_ = deepcopy(dsl_tem)
            filter_condition = [
                {
                    "term": {
                        "source.context.conf_e164": e164
                    }
                },
                {
                    "range": {
                        "@timestamp": {
                            "gte": str(s_time),
                            "lte": "now"
                        }
                    }
                }
            ]
            dsl_['query']['bool']['filter'] = filter_condition

            m_dsl += '{}\n' + json.dumps(dsl_) + '\n'
        return m_dsl

    def get_mediaresource_ip_info(self):
        """
        从查询媒体资源服务器ip
        :return: list
        """
        body = self.m_media_ip_info_dsl()
        es = es_client()
        index = "platform-nmscollector-platformframes-*"
        try:
            media_ip_info = es.msearch(index=index, dsl=body)
        except Exception as err:
            logger.error(err)
            return False, err.args

        es_response = media_ip_info['responses']
        results = []
        for response in es_response:
            dev_moid = jsonpath.jsonpath(response, "$..eqpid")
            results.append(dev_moid)

        results = [result[0] if result is not False else "" for result in results]
        # 根据机器moid查询机器ip  暂时用ops数据库 后迁移 luban
        # with connections["luban"].cursor() as cursor:
        with connections["default"].cursor() as cursor:
            sql = "SELECT moid,local_ip FROM hosts_machine_info WHERE moid IN %s"
            # sql = """
            # SELECT
            #     mi.machine_moid,
            #     ii.ip
            # FROM
            #     machine_info mi
            #     LEFT JOIN ip_info ii ON mi.id = ii.machine_id
            # WHERE
            #     mi.machine_moid IN %s
            # """
            cursor.execute(sql, [results])
            moid_ip = cursor.fetchall()
        # 转换为字典，key为moid
        caller_dict = dict(moid_ip)
        media_ip = [caller_dict.get(moid, "") for moid in results]
        return True, media_ip

    def get_conference_info(self):
        """
        获取 发言人/管理方/双流源/录像状态/直播状态/协作状态
        :return: list [[s,c,d,r,l,d],[...],...]
        """

        stat, dcs_stat = self.q_dcs_conf_info()  # 协作状态
        if not stat:
            # err in query
            return stat, dcs_stat

        stat, redis_stat = self.get_info_from_redis()  # cmu_ip/发言人/管理方/双流源/录像状态/直播状态/
        if not stat:
            # err in query
            return stat, redis_stat

        stat, redis_vm_stat = self.get_vmp_mix_from_redis()  # vmp/mix
        if not stat:
            # err in query
            return stat, redis_vm_stat

        stat, media_ip = self.get_mediaresource_ip_info()  # 获取会议媒体资源所在机器IP
        if not stat:
            # err in query
            return stat, media_ip

        results = [x + [y] + [z] for x, y, z in zip(redis_stat, dcs_stat, media_ip)]
        final_result = [x + y for x, y in zip(results, redis_vm_stat)]
        final_result = [dict(zip(self.conf_param_keys, result))
                        for result in final_result]
        return True, final_result


class P2PConfList:
    """
    查询点对点会议会议列表，返回会议详细信息
    """

    def __init__(self, **kwargs):
        self.platform_moid = kwargs.get('platform_moid')
        self.domain_moid = kwargs.get('domain_moid')
        self.conf_type = kwargs.get('conf_type')
        self.conf_status = kwargs.get('conf_status')
        self.start_time = kwargs.get('start_time')
        self.end_time = kwargs.get('end_time')
        self.index = "platform-nmscollector-*pas*"
        self.keywords = kwargs.get('keywords')
        self.level = kwargs.get('level')
        self.params_init()

    def params_init(self):
        if self.conf_type is not None:
            # 如果会议类型参数错误，引发异常
            if self.conf_type != ConfType.P2P:
                raise ValueError('conference type error')
        if self.conf_status is not None:
            # 如果会议状态参数错误，引发异常
            if self.conf_status not in [ConfStat.HISTORY, ConfStat.REALTIME]:
                raise ValueError('conference status error')
        if self.start_time is not None:
            self.start_time = int(self.start_time)
        if self.end_time is not None:
            self.end_time = int(self.end_time)
        if self.start_time is None and self.end_time is None:
            self.start_time = int(
                (datetime.datetime.now() -
                 datetime.timedelta(
                     hours=24)).timestamp() *
                1000)
        if self.level:
            if self.level not in ['1', '2', '3', '4']:
                raise ValueError('level type error')

    def m_create_dsl(self):
        """
        构建创会消息查询语句
        :return: dsl语句
        """
        # 平台域
        if self.platform_moid is not None:
            plat_condition = {
                "match": {
                    "beat.platform_moid": "%s" %
                                          self.platform_moid}}
        else:
            plat_condition = None
        # 时间
        time = {}
        # 开始时间
        if self.start_time is not None:
            time["gte"] = self.start_time
        if self.end_time is not None:
            time["lte"] = self.end_time
        # 关键字
        if self.keywords is not None:
            keyword_condition = {"bool": {
                "should": [{"wildcard": {"source.confinfo.caller.deve164.keyword": "*{}*".format(self.keywords)}},
                           {"wildcard": {"source.confinfo.caller.devname.keyword": "*{}*".format(self.keywords)}},
                           {"wildcard": {"source.confinfo.callee.deve164.keyword": "*{}*".format(self.keywords)}},
                           {"wildcard": {"source.confinfo.callee.devname.keyword": "*{}*".format(self.keywords)}}],
                "minimum_should_match": 1}}
        else:
            keyword_condition = None
        # # 查询字段
        # source = [
        #     "@timestamp",
        #     "beat.platform_moid",
        #     "source.confinfo.caller",
        #     "source.confinfo.callee",
        # ]

        # 构建查询语句
        dsl_ = deepcopy(dsl.conf_p2p_create_dsl)
        must_block = dsl_['query']['bool']['must']
        # 先将模板中平台域条件删除
        for item in must_block[::-1]:
            if 'beat.platform_moid' in item['match']:
                must_block.remove(item)
                break
        # 将查询条件加入
        if plat_condition is not None:
            must_block.append(plat_condition)
        if keyword_condition is not None:
            must_block.append(keyword_condition)
        dsl_['query']['bool']['must'] = must_block
        dsl_['query']['bool']['filter']['range']['@timestamp'] = time
        # dsl_['_source'] = source
        return dsl_

    def filter_creat_result(self, conf_info):
        """
        控制创会消息返回字段，将会议类型(2)和加入结果列表
        :param conf_info: 创会消息信息列表start_t/plat_moid/caller_id/caller_name/callee_id/callee_name/
        :return: dict start_t/plat_moid/caller_id/caller_name/callee_id/callee_name/type
        """
        conf_param_keys = [
            "start_time",
            "platform_moid",
            "caller_id",
            "caller_name",
            "callee_id",
            "callee_name",
            "conf_type"]
        results = []
        for sig_time_conf_info in conf_info['aggregations']['time']['buckets']:
            time = sig_time_conf_info['key']
            bgt = [localstr2utctimestamp(time)]
            for sig_dev_conf_info in sig_time_conf_info['caller']['buckets']:
                pfm = jsonpath.jsonpath(
                    sig_dev_conf_info, '$..beat.platform_moid')
                caller_id = jsonpath.jsonpath(
                    sig_dev_conf_info, '$..caller.deve164')
                caller_nm = jsonpath.jsonpath(
                    sig_dev_conf_info, '$..caller.devname')
                callee_id = jsonpath.jsonpath(
                    sig_dev_conf_info, '$..callee.deve164')
                callee_nm = jsonpath.jsonpath(
                    sig_dev_conf_info, '$..callee.devname')

                results.append([bgt, pfm, caller_id, caller_nm,
                                callee_id, callee_nm, [2]])

        results = [[value[0] if value is not False else "" for value in item]
                   for item in results]
        results = [dict(zip(conf_param_keys, conf)) for conf in results]
        return results

    def get_creat_filter(self):
        return deepcopy(dsl.conf_p2p_creat_all_filter)

    def q_create_info(self):
        """
        查询创会消息列表
        :return:一个二值元组，第一个值为查询是否成功(True:成功 False:失败)
                第二个值失败时为失败原因，成功时为结果(列表)(None表示查询结果为空)
        """
        body = self.m_create_dsl()  # 获取创会dsl查询语句
        es = es_client()
        try:
            conf_c_list = es.search(index=self.index, dsl=body)
        except Exception as err:
            logger.error(err)
            return False, err.args

        if jsonpath.jsonpath(conf_c_list, '$.hits.total')[0] == 0:
            return True, None
        result = self.filter_creat_result(conf_c_list)
        if len(result) == 0:
            return True, None
        else:
            return True, result

    def m_destroy_dsl(self, conf_info):
        """
        构建结会消息批量查询语句
        :param conf_info: 会议信息的列表,会议信息包括(开始时间/主叫号码/被叫号码)
        :return: 批量查询的dsl语句
        """
        # 修改模板
        dsl_ = deepcopy(dsl.conf_p2p_destroy_dsl)
        must_block = dsl_['query']['bool']['must']
        # 先将模板中会议号码条件删除
        for item in must_block[::-1]:
            if 'source.confinfo.callerE164' in item['match']:
                must_block.remove(item)
                continue
            if 'source.confinfo.calleeE164' in item['match']:
                must_block.remove(item)
                continue

        # 将主叫号过滤条件放在位置0，被叫号过滤条件放在位置1方便后续修改
        must_block.insert(0, {"match": {"source.confinfo.callerE164": ""}})
        must_block.insert(1, {"match": {"source.confinfo.calleeE164": ""}})

        m_dsl = ''
        for start_time, caller, callee in conf_info:
            # 主叫号码在must中0号码,被叫号码在must中1位置
            dsl_['query']['bool']['must'][0]["match"]["source.confinfo.callerE164"] = caller
            dsl_['query']['bool']['must'][1]["match"]["source.confinfo.calleeE164"] = callee
            # 时间
            dsl_['query']['bool']['filter']['range']['@timestamp'] = {
                "gte": start_time}
            m_dsl += '{}\n' + json.dumps(dsl_) + '\n'
        return m_dsl

    def q_destroy_info(self, conf_info):
        """
        查询结会消息列表
        :param conf_info:conf_info: 包括会议开始时间/主叫号码/被叫号码 eg (('time','111','222'),)
        :return:失败和失败原因或者成功和会议结束时间(map迭代器）
        """
        filter_path = deepcopy(dsl.conf_p2p_destroy_filter)
        body = self.m_destroy_dsl(conf_info)
        es = es_client()
        try:
            conf_d_list = es.msearch(
                index=self.index, dsl=body, filter_path=filter_path)
        except Exception as err:
            logger.error(err)
            return False, err.args

        hits = jsonpath.jsonpath(conf_d_list, '$.responses[*].hits.hits')

        # 结会时间为空返回空字符串，否则返回结会时间
        def get_msg(hits_msg):
            if len(hits_msg) == 0:
                return ""
            else:
                et = jsonpath.jsonpath(hits_msg, '$..sort[0]')
                et = et[0] if et is not False else ""
                return et

        end_time = list(map(get_msg, hits))
        return True, end_time

    def calc_conf_quality(self, conf_list):
        quality_obj = DeviceConfQuality(
            ConfType.P2P.value, conf_list, summary=True)
        quality = quality_obj.get_quality()
        return quality

    def get_conference(self):
        """
        获取会议列表
        :return: 一个二值元组，第一个值为查询是否成功(True:成功 False:失败)
                 第二个值失败时为失败原因，成功时为结果(list)(None表示查询结果为空)
        """
        # 首先获取创会列表
        conf_create_msgs = self.q_create_info()
        if not conf_create_msgs[0]:
            # 如果创会列表获取失败，返回(false, err)
            return conf_create_msgs
        elif conf_create_msgs[1] is None:
            # 如果列表为None，返回 (true, None)
            return conf_create_msgs
        else:
            conf_create_msgs = conf_create_msgs[1]

        # 根据创会消息列表获取结会消息列表
        time_call_cale = [[x["start_time"], x["caller_id"],
                           x["callee_id"]] for x in conf_create_msgs]
        end_time_list = self.q_destroy_info(time_call_cale)
        if not end_time_list[0]:
            # 如果查询失败，返回 (False, err)
            return end_time_list
        else:
            end_time_list = end_time_list[1]

        # 将会议结束时间和会议状态加入列表
        def add_et_stat(conf, et):
            conf['end_time'] = et if et else ConfEndTimeType.REALTIME.name
            conf['conf_status'] = ConfStat.HISTORY.value if et else ConfStat.REALTIME.value
            return conf

        create_msgs = map(add_et_stat, conf_create_msgs, end_time_list)

        # 处理会议状态参数
        if self.conf_status == ConfStat.HISTORY:
            # 历史会议
            create_msgs = [
                conf for conf in create_msgs if conf['conf_status'] == ConfStat.HISTORY]
        elif self.conf_status == ConfStat.REALTIME:
            # 实时会议
            create_msgs = [
                conf for conf in create_msgs if conf['conf_status'] == ConfStat.REALTIME]
        else:
            # None表示全部会议
            create_msgs = list(create_msgs)

        if len(create_msgs) == 0:
            return True, None

        # 处理用户域
        # 从mysql查询用户域信息
        caller_all = [x["caller_id"] for x in create_msgs]
        callee_all = [x["callee_id"] for x in create_msgs]
        with connections['movision'].cursor() as cursor:
            sql = "SELECT a.e164,a.user_domain_moid,b.user_domain_name FROM user_info a LEFT JOIN user_domain b ON a.user_domain_moid = b.user_domain_moid WHERE a.e164 IN %s"
            cursor.execute(sql, [caller_all])
            caller = cursor.fetchall()
            cursor.execute(sql, [callee_all])
            callee = cursor.fetchall()
        # 转换为字典，key为e164号
        caller_dict = dict([(x[0], list(x[1:])) for x in caller])
        callee_dict = dict([(x[0], list(x[1:])) for x in callee])

        # 将用户域信息加入会议信息 并过滤用户域
        def add_domain(conf_inf):
            caller_domain = caller_dict.get(conf_inf["caller_id"])
            callee_domain = callee_dict.get(conf_inf["callee_id"])

            if caller_domain is None:
                caller_domain = ["", ""]
            if callee_domain is None:
                callee_domain = ["", ""]
            conf_inf.update(dict(zip(["caller_domain_moid",
                                      "caller_domain_name",
                                      "callee_domain_moid",
                                      "callee_domain_name"],
                                     caller_domain + callee_domain)))
            return conf_inf

        create_msgs = map(add_domain, create_msgs)

        if self.domain_moid:
            # 过滤用户域
            create_msgs = [conf for conf in create_msgs if conf["caller_damain_moid"]
                           == self.domain_moid or conf["callee_damain_moid"] == self.domain_moid]
        else:
            # None表示全部会议
            create_msgs = list(create_msgs)
        if len(create_msgs) == 0:
            return True, None

        # 处理会议质量
        def add_conf_status(conf_inf, qua):
            """
            添加会议质量
            :type conf_inf: dict
            """
            if qua == 1:
                desc = "体验不好"
            elif qua == 2:
                desc = "体验一般"
            elif qua == 3:
                desc = "体验良好"
            else:
                desc = "体验优秀"
            conf_inf.update({"level": qua, "desc": desc})
            return conf_inf

        conf_info = [[conf["caller_id"],
                      conf["start_time"],
                      conf["end_time"],
                      conf["caller_id"],
                      conf["callee_id"]] for conf in create_msgs]
        quality = self.calc_conf_quality(conf_info)
        if not quality[0]:
            # 如果会议质量获取失败，返回(false, err)
            return quality
        else:
            quality = quality[1]
        conf_full_list = map(add_conf_status, create_msgs, quality)
        if self.level:
            level = int(self.level)
            conf_full_list = [
                conf for conf in conf_full_list if conf["level"] == level]
        else:
            conf_full_list = list(conf_full_list)
        return True, conf_full_list


class SwitchLink:
    """
    处理会议信息中码流链路
    """

    def __init__(self, **kwargs):
        self.mt_e164 = kwargs.get("mt_e164")
        self.conf_id = kwargs.get("conf_id")
        self.time = kwargs.get("time")
        self.type_ = kwargs.get('type')
        self.conf_status = kwargs.get('conf_status')
        self.params_init()

    def params_init(self):
        if None in [self.conf_id, self.mt_e164, self.type_, self.time, self.conf_status]:
            raise ValueError("params error")
        if self.type_ not in [1, 2, 3]:
            raise ValueError("params error")
        if self.conf_status not in [ConfStat.REALTIME, ConfStat.HISTORY]:
            raise ValueError("params error")
        self.time = int(self.time)
        # 查询时间取时间戳前后一分钟
        self.start_time = self.time - 60 * 1000
        self.end_time = self.time + 60 * 1000

    def query_first_ssrc(self):
        """
        查询第一包src.ip/port dst.ip/port ssrc
        :return: [[src.ip, src.port, dst.ip, dst.port, ssrc], []]     ['send', 'recv']
        """
        # 上行第一包dsl
        dsl_send = self.make_first_ssrc_dsl('send')
        # 下行第一包dsl
        dsl_recv = self.make_first_ssrc_dsl('recv')

        dsl_ = '{}\n' + dsl_send + '\n{}\n' + json.dumps(dsl_recv) + '\n'
        es = es_client()
        index = "platform-nmscollector-*dss*worker*"
        try:
            results = es.msearch(index=index, dsl=dsl_)
        except Exception as err:
            logger.error(err)
            return False, err.args

        first_ssrc = []
        # 前两个是上行 第三个是下行
        for result in results['responses']:
            src_ip = jsonpath.jsonpath(result, '$..rtp_info.src.ip')
            src_port = jsonpath.jsonpath(result, '$..rtp_info.src.port')
            dst_ip = jsonpath.jsonpath(result, '$..rtp_info.dst.ip')
            dst_port = jsonpath.jsonpath(result, '$..rtp_info.dst.port')
            ssrc_key = jsonpath.jsonpath(result, '$..rtp_info.statis.ssrc')
            callid = jsonpath.jsonpath(result, '$..context.callid')
            lose_percent = jsonpath.jsonpath(
                result, '$..rtp_info.statis.rtp_lose.lose_percent.cur')

            ssrc = [
                x[0] if x is not False else "" for x in [
                    src_ip,
                    src_port,
                    dst_ip,
                    dst_port,
                    ssrc_key,
                    callid,
                    lose_percent]]
            first_ssrc.append(ssrc)
        return True, first_ssrc

    def query_media_type(self):
        type_ = {
            '1': 'video',
            '2': 'dualvideo',
            '3': 'audio'
        }
        return type_.get(str(self.type_))

    def query_switch_type(self, tp):
        type_ = {
            'vmp': '合成',
            'bas': '适配',
            'vbas': '适配',
            'abas': '适配',
            'mixer': '混音',
            'port': '端口',
            'portbas': '端口适配'
        }
        return type_.get(tp)

    def make_first_ssrc_dsl(self, flag):
        """
        构建查询第一包信息的dsl语句
        :param flag: send/recv
        :return:
        """
        dsl_ = deepcopy(dsl.switch_link_dssw_dsl)
        must_block = dsl_['query']['bool']['must']
        # 先将模板中条件删除
        for item in must_block[::-1]:
            if 'exists' in item:
                continue
            if 'source.conf_e164' in item['match']:
                must_block.remove(item)
                continue
            if 'source.context.channer.id' in item['match']:
                must_block.remove(item)
                continue
            if 'source.context.channer.local' in item['match']:
                must_block.remove(item)
                continue
            if 'source.context.chanee.id' in item['match']:
                must_block.remove(item)
                continue
            if 'source.context.chan_type' in item['match']:
                must_block.remove(item)
                continue
            if 'source.direct' in item['match']:
                must_block.remove(item)
                continue

        # 时间
        dsl_['query']['bool']['filter']['range']['@timestamp'] = {
            "gte": self.start_time, "lte": self.end_time}

        # 将过滤条件加入
        must_block.append(
            {"match": {"source.conf_e164": "{}".format(self.conf_id)}})
        must_block.append(
            {"match": {"source.context.chan_type": "{}".format(self.query_media_type())}})

        if flag == 'send':
            must_block.append(
                {"match": {"source.context.channer.id": "{}".format(self.mt_e164)}})
            must_block.append({"match": {"source.context.channer.local": 1}})
            must_block.append(
                {"match": {"source.context.chanee.id": "{}".format(self.conf_id)}})
            must_block.append({"match": {"source.direct": "up"}})
            # 上行查询分两种情况  纯转发和媒体
            # # 纯转发
            dss_dsl = deepcopy(dsl_)
            dss_dsl['query']['bool']['must'].append(
                {"range": {"source.rtp_info.dst.port": {"gte": 37050}}})
            # # 媒体
            media_dsl = deepcopy(dsl_)
            media_dsl['query']['bool']['must'].append(
                {"range": {"source.rtp_info.dst.port": {"lt": 37050}}})
            dsl_ = json.dumps(dss_dsl) + '\n{}\n' + json.dumps(media_dsl)
            return dsl_
        else:
            must_block.append(
                {"match": {"source.context.channer.id": "{}".format(self.conf_id)}})
            must_block.append({"match": {"source.context.channer.local": 1}})
            must_block.append(
                {"match": {"source.context.chanee.id": "{}".format(self.mt_e164)}})
            must_block.append({"match": {"source.direct": "down"}})
            dsl_['query']['bool']['must'] = must_block
            return dsl_

    def make_next_dss_dsl(self, flag, ip, port, ssrc):
        """
        构建查询下一个dssworker的dsl语句
        :return:
        """
        dsl_ = {
            "size": 1,
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "source.eventid": "EV_DSS_PORT_STATIS_NOTIFY"}}],
                    "filter": {
                        "range": {
                            "@timestamp": {
                                "gte": "2019-08-02T06:35:52Z",
                                "lte": "2019-08-02T06:37:52Z"}}}}},
            "sort": [
                {
                    "@timestamp": {
                        "order": "desc"}}]}

        must_block = dsl_['query']['bool']['must']
        if flag == 'send':
            must_block.append({"match": {"source.rtp_info.src.ip": ip}})
            must_block.append({"match": {"source.rtp_info.src.port": port}})
            # must_block.append({"match": {"source.rtp_info.statis.ssrc": ssrc}})
        else:
            must_block.append({"match": {"source.rtp_info.dst.ip": ip}})
            must_block.append({"match": {"source.rtp_info.dst.port": port}})
            # must_block.append({"match": {"source.rtp_info.statis.ssrc": ssrc}})
        dsl_['query']['bool']['filter']['range']['@timestamp'] = {
            "gte": self.start_time, "lte": self.end_time}
        return dsl_

    def query_next_dss_point(self, flag, ip, port, ssrc):
        """
        根据第一个点的信息查找下一个dssworker信息
        :return:
        """
        dsl_ = self.make_next_dss_dsl(flag, ip, port, ssrc)
        index = "platform-nmscollector-*dss*worker*"
        es = es_client()
        try:
            results = es.search(index=index, dsl=dsl_)
        except Exception as err:
            logger.error(err)
            return False, err.args

        res_num = jsonpath.jsonpath(results, '$.hits.total')
        if res_num[0] == 0:
            return True, None

        src_ip = jsonpath.jsonpath(results, '$..rtp_info.src.ip')
        src_port = jsonpath.jsonpath(results, '$..rtp_info.src.port')
        dst_ip = jsonpath.jsonpath(results, '$..rtp_info.dst.ip')
        dst_port = jsonpath.jsonpath(results, '$..rtp_info.dst.port')
        callid = jsonpath.jsonpath(results, '$..context.callid')
        lose_percent = jsonpath.jsonpath(
            results, '$..rtp_info.statis.rtp_lose.lose_percent.cur')
        return True, [x[0] if x is not False else "" for x in [
            src_ip, src_port, dst_ip, dst_port, callid, lose_percent]]

    def make_media_dsl(self, flag, ip, port, ssrc):
        """
        构建查询mediawoker信息的dsl语句
        :return:
        """
        dsl_ = {
            "size": 0,
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "source.eventid": "OPS_PLATFORM_MEDIA_INFO_NOTIFY"}}],
                    "filter": {
                        "range": {
                            "@timestamp": {
                                "gte": 1567748346000,
                                "lte": 1567748466000}}}}},
            "aggs": {
                "type": {
                    "terms": {
                        "field": "source.context.type.keyword",
                        "size": 10000},
                    "aggs": {
                        "data": {
                            "top_hits": {
                                "size": 1,
                                "sort": [
                                    {
                                        "@timestamp": {
                                            "order": "desc"}}],
                                "_source": [
                                    "source.rtp_info.src.port",
                                    "source.rtp_info.src.ip",
                                    "source.context.activepayload",
                                    "source.context.channel",
                                    "source.context.handle",
                                    "source.frame.bitrate",
                                    "source.frame.fps"]}}}}}}

        must_block = dsl_['query']['bool']['must']
        if flag == 'send':
            must_block.append({"match": {"source.rtp_info.src.ip": ip}})
            must_block.append({"match": {"source.rtp_info.src.port": port}})
            # must_block.append({"match": {"source.rtp_info.ssrc": ssrc}})
        else:
            must_block.append({"match": {"source.rtp_info.dst.ip": ip}})
            must_block.append({"match": {"source.rtp_info.dst.port": port}})
            # must_block.append({"match": {"source.rtp_info.ssrc": ssrc}})
        dsl_['query']['bool']['filter']['range']['@timestamp'] = {
            "gte": self.start_time, "lte": self.end_time}
        return dsl_

    def query_media_point(self, flag, ip, port, ssrc):
        """
        查找mediaworker的信息
        :return:
        """
        dsl_ = self.make_media_dsl(flag, ip, port, ssrc)
        index = "platform-nmscollector-platformframes*"
        data = []
        es = es_client()
        try:
            results = es.search(index=index, dsl=dsl_)
        except Exception as err:
            logger.error(err)
            return False, err.args

        res_num = jsonpath.jsonpath(results, '$.hits.total')
        if res_num[0] == 0:
            return True, None

        for info in results['aggregations']['type']['buckets']:
            key = [info["key"]]
            if flag == "send":
                src_ip = jsonpath.jsonpath(info, "$..src.ip")
                src_port = jsonpath.jsonpath(info, "$..src.port")
            else:
                src_ip = jsonpath.jsonpath(info, "$..src.ip")
                src_port = jsonpath.jsonpath(info, "$..src.port")
            activepayload = jsonpath.jsonpath(info, "$..activepayload")
            channel = jsonpath.jsonpath(info, "$..channel")
            handle = jsonpath.jsonpath(info, "$..handle")
            bps = jsonpath.jsonpath(info, "$..bitrate")
            pps = jsonpath.jsonpath(info, "$..fps")

            # media 上的码率，统一除1024再乘8，单位未kb/s	  他原始单位是bps
            if bps is not False:
                bps = [round(bps[0] / 1024 * 8, 2)]

            # # ['name', 'desc', 'status', 'ip', 'port', 'activepayload', 'channel', 'handle', 'bps', 'pps']
            media_info = [
                x[0] if x is not False else "" for x in [
                    key,
                    src_ip,
                    src_port,
                    activepayload,
                    channel,
                    handle,
                    bps,
                    pps]]
            media_info.insert(1, self.query_switch_type(media_info[0]))
            if flag == "send":
                media_info.insert(2, self.send_status)
            else:
                media_info.insert(2, self.recv_status)
            data.append(media_info)

        if len(data) == 0:
            return True, None
        else:
            return True, data

    def make_mt_ip_dsl(self):
        """
        构建查询终端ip的dsl语句
        :return:
        """
        dsl_ = deepcopy(dsl.mt_ip_proto_inf_dsl)
        must_block = dsl_['query']['bool']['must']
        # 先将模板中164号条件删除
        for item in must_block[::-1]:
            if 'source.e164' in item['match']:
                must_block.remove(item)
                break

        # 将终端164号过滤条件加入
        must_block.append({"match": {"source.e164": self.mt_e164}})
        # 时间
        dsl_['query']['bool']['filter']['range']['@timestamp'] = {
            "lte": self.time}
        return dsl_

    def make_mt_conf_info_dsl(self):
        """
        构建查询终会议码率/格式/分辨率的dsl语句
        :return:
        """
        dsl_ = deepcopy(dsl.dev_conf_info_dsl)
        must_block = dsl_['query']['bool']['must']
        # 先将模板中条件删除
        for item in must_block[::-1]:
            if 'source.conf_info.conf_e164' in item['match']:
                must_block.remove(item)
                continue
            if 'source.conf_info.mt_e164' in item['match']:
                must_block.remove(item)
                continue

        # 将过滤条件加入
        must_block.append(
            {"match": {"source.conf_info.mt_e164": self.mt_e164}})
        must_block.append(
            {"match": {"source.conf_info.conf_e164": self.conf_id}})
        # 时间
        # # 终端上报的数据的时间间隔为5min
        dsl_['query']['bool']['filter']['range']['@timestamp'] = {
            "gte": self.start_time - 300 * 1000, "lte": self.end_time}
        dsl_['size'] = 1
        dsl_['sort']['@timestamp']['order'] = 'desc'
        return dsl_

    def query_mt_ip(self):
        """
        获取终端ip及终端码流相关信息
        :return:
        """

        dsl_ip = self.make_mt_ip_dsl()  # 获取终端ip dsl
        dsl_conf_inf = self.make_mt_conf_info_dsl()  # 获取终端会议信息 dsl

        dsl_ = """{"index":"upuwatcher-*"}\n""" + json.dumps(
            dsl_ip) + """\n{"index":"platform-nmscollector-*mt*"}\n""" + json.dumps(dsl_conf_inf) + "\n"
        es = es_client()
        try:
            results = es.msearch(dsl=dsl_)
        except Exception as err:
            logger.error(err)
            return False, err.args

        # 获取ip/会议相关信息
        # 第一个是ip  第二个是会议信息
        # # ip
        ip = False
        if self.conf_status == ConfStat.REALTIME:
            # 实时会议 从redis取ip
            try:
                redis_conf_key = 'conf/%s' % self.conf_id
                if redis_client.exists(redis_conf_key):
                    # redis的会议key值存在
                    mtid = redis_client.hget(redis_conf_key + '/e164tomtid', self.mt_e164)
                    logger.info(redis_conf_key + '/mt/%s' % mtid.decode('utf-8'))
                    # mtid存在
                    if mtid:
                        ip = redis_client.hget(redis_conf_key + '/mt/%s' % mtid.decode('utf-8'), 'mtip')
                        if isinstance(ip, bytes):
                            ip = [ip.decode('utf-8')]
                            logger.info('redis中读取的ip: %s' % ip)
                    else:
                        logger.info('realtime conf %s has no mt %s' % (self.conf_id, self.mt_e164))
                else:
                    logger.info('%s is not a realtime conf' % self.conf_id)
            except Exception as e:
                logger.error(str(e))
        else:
            try:
                # 因循环导入问题，无法在头部导入
                from platmonitor.dsl.confDevList import EvMtInfo
                mt_info = EvMtInfo([self.mt_e164]).get_mt_info()
                # mt_info = (True, [['10.67.13.33', '5.1.0.1.1.20170610', 'TrueLink']])     # EV_MT_INFO消息
                if mt_info[0]:
                    logger.info(mt_info)
                    ip = mt_info[1][0] if mt_info[1][0] else False
                    logger.info('EV_MT_INFO消息中读取的ip: %s' % ip)
            except Exception as e:
                logger.error(str(e))
            if not ip:
                ip = jsonpath.jsonpath(results['responses'][0], '$.hits.hits..mtaddr')  # upuwatcher消息
                logger.info('upuwatcher消息中读取的ip: %s' % ip)

        if self.type_ == 1:
            # 主流
            bitrate_down = jsonpath.jsonpath(
                results['responses'][1],
                '$..conf_info.privideo_recv[?(@.id==0)].video_down_bitrate')
            format_down = jsonpath.jsonpath(
                results['responses'][1],
                '$..conf_info.privideo_recv[?(@.id==0)].format')
            res_down = jsonpath.jsonpath(
                results['responses'][1],
                '$..conf_info.privideo_recv[?(@.id==0)].res')
            bitrate_up = jsonpath.jsonpath(
                results['responses'][1],
                '$..conf_info.privideo_send[?(@.id==0)].video_up_bitrate')
            format_up = jsonpath.jsonpath(
                results['responses'][1],
                '$..conf_info.privideo_send[?(@.id==0)].format')
            res_up = jsonpath.jsonpath(
                results['responses'][1],
                '$..conf_info.privideo_send[?(@.id==0)].res')

            send = [ip, bitrate_up, format_up, res_up]
            recv = [ip, bitrate_down, format_down, res_down]

            send = [x[0] if x is not False else "" for x in send]
            recv = [x[0] if x is not False else "" for x in recv]

            # 转换格式
            send[2] = send[2] if send[2] == "" else MtVideoFormatNMS.get(
                send[2]).name
            send[3] = send[3] if send[3] == "" else MtVideoResolutionNMSDesc.get(
                MtVideoResolutionTypeNMS.get(send[3]).name)

            recv[2] = recv[2] if recv[2] == "" else MtVideoFormatNMS.get(
                recv[2]).name
            recv[3] = recv[3] if recv[3] == "" else MtVideoResolutionNMSDesc.get(
                MtVideoResolutionTypeNMS.get(recv[3]).name)

        elif self.type_ == 2:
            # 辅流(双流)
            bitrate_down = jsonpath.jsonpath(
                results['responses'][1],
                '$..conf_info.assvideo_recv[?(@.id==0)].video_down_bitrate')
            format_down = jsonpath.jsonpath(
                results['responses'][1],
                '$..conf_info.assvideo_recv[?(@.id==0)].format')
            res_down = jsonpath.jsonpath(
                results['responses'][1],
                '$..conf_info.assvideo_recv[?(@.id==0)].res')
            bitrate_up = jsonpath.jsonpath(
                results['responses'][1],
                '$..conf_info.assvideo_send[?(@.id==0)].video_up_bitrate')
            format_up = jsonpath.jsonpath(
                results['responses'][1],
                '$..conf_info.assvideo_send[?(@.id==0)].format')
            res_up = jsonpath.jsonpath(
                results['responses'][1],
                '$..conf_info.assvideo_send[?(@.id==0)].res')

            send = [ip, bitrate_up, format_up, res_up]
            recv = [ip, bitrate_down, format_down, res_down]

            send = [x[0] if x is not False else "" for x in send]
            recv = [x[0] if x is not False else "" for x in recv]

            # 转换格式
            send[2] = send[2] if send[2] == "" else MtVideoFormatNMS.get(
                send[2]).name
            send[3] = send[3] if send[3] == "" else MtVideoResolutionNMSDesc.get(
                MtVideoResolutionTypeNMS.get(send[3]).name)

            recv[2] = recv[2] if recv[2] == "" else MtVideoFormatNMS.get(
                recv[2]).name
            recv[3] = recv[3] if recv[3] == "" else MtVideoResolutionNMSDesc.get(
                MtVideoResolutionTypeNMS.get(recv[3]).name)
        else:
            # 音频
            bitrate_down = jsonpath.jsonpath(
                results['responses'][1],
                '$..conf_info.audio_recv[?(@.id==0)].audio_down_bitrate')
            format_down = jsonpath.jsonpath(
                results['responses'][1],
                '$..conf_info.audio_recv[?(@.id==0)].format')
            bitrate_up = jsonpath.jsonpath(
                results['responses'][1],
                '$..conf_info.audio_send[?(@.id==0)].audio_up_bitrate')
            format_up = jsonpath.jsonpath(
                results['responses'][1],
                '$..conf_info.audio_send[?(@.id==0)].format')

            send = [ip, bitrate_up, format_up]
            recv = [ip, bitrate_down, format_down]

            send = [x[0] if x is not False else "" for x in send]
            recv = [x[0] if x is not False else "" for x in recv]

            # 转换格式
            send[2] = send[2] if send[2] == "" else MtAudioFormatNMS.get(
                send[2]).name
            recv[2] = recv[2] if recv[2] == "" else MtAudioFormatNMS.get(
                recv[2]).name

        # 增加status字段，标识终端状态 0：异常，1：正常，判断规则未定，先按正常显示
        mt_status = 1
        names_mt = ['status', 'name', 'desc', 'ip', 'bitrate', 'format', 'res']
        # 上行
        send = dict(zip(names_mt, [mt_status, 'mt', '终端'] + send))
        # 下行
        recv = dict(zip(names_mt, [mt_status, 'mt', '终端'] + recv))
        return True, [send, recv]

    def query_send_line(self, first_pk_info):
        """
        根据第一个包的信息查找上行dssworker信息的信息及mediaworker的信息
        :param first_pk_info: list  [src.ip/port dst.ip/port ssrc call_id pk_loss]
        :return:
        """
        flag = 'send'
        res = []
        # 上行链路分为纯转发和过媒体
        for first_info in first_pk_info:
            data = []
            # 第一个是纯转发  第二个是过媒体
            if "" in first_info[2:5]:
                # 第一包信息 dst.ip/port/ssrc为空
                logger.info(first_info)
                logger.info(
                    "query send info termination:{}-{}-{}-{}".format(
                        self.conf_id, self.mt_e164, self.type_, self.time))
                continue

            # 如果ssrc为0 则链路状态不正常
            if first_info[4] == 0:
                self.send_status = 0
            else:
                self.send_status = 1

            names_dss = [
                'name',
                'desc',
                'status',
                'ip',
                'port',
                'callid',
                'lose_percent']
            names_media = [
                'name',
                'desc',
                'status',
                'ip',
                'port',
                'activepayload',
                'channel',
                'handle',
                'bps',
                'pps']

            # 先将终端信息和第一包信息加入
            # # 终端信息
            data.append(self.ip[0])
            # # 第一包信息
            value_dss = [
                'dss',
                '转发',
                self.send_status,
                first_info[0],
                first_info[1],
                first_info[5],
                first_info[6]]
            data.append(dict(zip(names_dss, value_dss)))

            src_ip = first_info[2]  # 第一包的dst_ip
            src_port = first_info[3]  # 第一包的dst_port
            ssrc = first_info[4]
            while True:
                inf = self.query_next_dss_point(flag, src_ip, src_port, ssrc)
                if not inf[0]:
                    # 查询失败
                    return inf
                elif inf[1] is None:
                    # 无数据
                    break

                value_dss = [
                    'dss',
                    '转发',
                    self.send_status,
                    inf[1][0],
                    inf[1][1],
                    inf[1][4],
                    inf[1][5]]
                data.append(dict(zip(names_dss, value_dss)))

                if inf[1][2] == "" or inf[1][3] == "":
                    res.append({'data': data})
                    continue
                src_ip, src_port = inf[1][2], inf[1][3]

            media_info = self.query_media_point(flag, src_ip, src_port, ssrc)
            if not media_info[0]:
                # 获取media信息失败 返回失败原因
                return media_info
            elif media_info[1] is None:
                # 查询media数据为空
                res.append({'data': data})
                continue

            for media_inf in media_info[1]:
                data_ = deepcopy(data)
                data_.append(dict(zip(names_media, media_inf)))
                res.append({'data': data_})
        return True, res

    def query_recv_line(self, first_pk_info):
        """
        根据第一个包的信息查找下行dssworker信息的信息及mediaworker的信息
        :param first_pk_info: list  [src.ip/port dst.ip/port ssrc call_id pk_loss]
        :return:
        """
        flag = 'recv'
        data = []
        res = []

        if "" in [first_pk_info[0], first_pk_info[1], first_pk_info[4]]:
            # 第一包信息 src.ip/port/ssrc为空
            logger.info(first_pk_info)
            logger.info(
                "query send info termination:{}-{}-{}-{}".format(
                    self.conf_id,
                    self.mt_e164,
                    self.type_,
                    self.time))
            return True, res

        # 如果ssrc为0 则链路状态不正常
        if first_pk_info[4] == 0:
            self.recv_status = 0
        else:
            self.recv_status = 1

        names_dss = [
            'name',
            'desc',
            'status',
            'ip',
            'port',
            'callid',
            'lose_percent']
        names_media = [
            'name',
            'desc',
            'status',
            'ip',
            'port',
            'activepayload',
            'channel',
            'handle',
            'bps',
            'pps']

        # 先将终端信息和第一包信息加入
        # # 终端信息
        data.append(self.ip[1])
        # # 第一包信息
        value_dss = [
            'dss',
            '转发',
            self.recv_status,
            first_pk_info[0],
            first_pk_info[1],
            first_pk_info[5],
            first_pk_info[6]]
        data.insert(0, dict(zip(names_dss, value_dss)))

        dst_ip = first_pk_info[0]
        dst_port = first_pk_info[1]
        ssrc = first_pk_info[4]
        while True:
            inf = self.query_next_dss_point(flag, dst_ip, dst_port, ssrc)
            if not inf[0]:
                # 查询失败
                return inf
            elif inf[1] is None:
                # 无数据
                break

            value_dss = [
                'dss',
                '转发',
                self.recv_status,
                inf[1][0],
                inf[1][1],
                inf[1][4],
                inf[1][5]]
            data.insert(0, dict(zip(names_dss, value_dss)))

            if inf[1][0] == "" or inf[1][1] == "":
                res.append({'data': data})
                return True, res
            dst_ip, dst_port = inf[1][0], inf[1][1]

        media_info = self.query_media_point(flag, dst_ip, dst_port, ssrc)
        if not media_info[0]:
            # 获取media信息失败 返回失败原因
            return media_info
        elif media_info[1] is None:
            # 查询media数据为空
            res.append({'data': data})
            return True, res

        for media_inf in media_info[1]:
            data_ = deepcopy(data)
            data_.insert(0, dict(zip(names_media, media_inf)))
            res.append({'data': data_})
        return True, res

    def get_data(self):
        """
        查询会议终端上下行码流链路
        :return:
        """
        # 获取终端ip
        logger.info("begin query switch link:{}-{}-{}-{}".format(self.conf_id,
                                                                 self.mt_e164, self.type_, self.time))
        ip = self.query_mt_ip()
        if not ip[0]:
            # 获取信息失败 返回失败原因
            return ip
        else:
            self.ip = ip[1]  # [send, recv]

        # 首先查询第一包信息 src.ip/port dst.ip/port ssrc
        first_pk_inf = self.query_first_ssrc()  # 前两个是上行 第三个是下行
        if not first_pk_inf[0]:
            # 获取信息失败 返回失败原因
            return first_pk_inf

        info = {}
        first_pk_inf = first_pk_inf[1]

        # 获取上行码流里链路 前两个是上行 第三个是下行
        send = self.query_send_line(first_pk_inf[0:2])
        if not send[0]:
            # 获取信息失败 返回失败原因
            return send
        else:
            info['send'] = send[1]
        # 获取下行码流链路
        recv = self.query_recv_line(first_pk_inf[2])
        if not recv[0]:
            # 获取信息失败 返回失败原因
            return recv
        else:
            info['recv'] = recv[1]
        return True, info


class DevConfTopology:
    """
    实时多点会议终端会议拓扑
    """

    def __init__(self, conf_dev_list, stat_only=False):
        """
        :param conf_dev_list: list  [conf_id, s_t, e_t, mts...]
        :param stat_only: return mt_status only if true
        """
        self.conf_id = conf_dev_list[0]
        self.start_time = int(conf_dev_list[1])
        self.end_time = int(conf_dev_list[2])
        self.dev_list = conf_dev_list[3:]
        self.stat_only = stat_only

    def get_dev_moid(self):
        """
        根据e164号从mysql数据库获取设备moid/machine_room_moid/machine_room_name
        :return : str or None
        """
        with connections['movision'].cursor() as cursor:
            sql = """
                SELECT
                    uf.e164,
                    uf.moid,
                    udm.machine_room_moid,
                    mr.machine_room_name
                FROM
                    user_info uf
                    LEFT JOIN user_domain_machine udm ON uf.user_domain_moid = udm.user_domain_moid
                    LEFT JOIN machine_room mr ON udm.machine_room_moid = mr.machine_room_moid
                WHERE
                    uf.e164 IN %s
                    AND uf.binded = '0'
                """
            cursor.execute(sql, [self.dev_list])
            moid = cursor.fetchall()

        try:
            e164_moid_dict = dict([(x[0], list(x[1:])) for x in moid])
        except Exception as err:
            logger.error(err)
            return [["", "", ""] for dev in self.dev_list]
        else:
            moids = []
            for e164 in self.dev_list:
                moid = e164_moid_dict.get(e164)
                if moid:
                    moids.append(moid)
                else:
                    moids.append(["", "", ""])
        return moids

    def get_dev_info(self, moids):
        """
        get mt_info of the topology_info
        :param moids: list of moid
        :return:
        """
        param_keys = ["name", "desc", "moid"]
        return [dict(zip(param_keys, ["mt", "终端", moid[0]])) for moid in moids]

    def get_machine_room_info(self, moids):
        """
        query the machineroom moid and name
        :return: tuple
        """
        param_keys = ["name", "desc", "machineroot_moid", "machineroom_name"]
        machineroom_moid, machineroot_name = "", ""
        return [dict(zip(param_keys, ["machineroom", "机房", moid[1], moid[2]]))
                for moid in moids]

    def make_perpheral_dsl(self, moids):
        """
        构建查询终端外设信息的dsl语句
        :param moids: list
        :return:
        """
        dsl_ = deepcopy(dsl.mt_ptm_dsl)
        must_block = dsl_['query']['bool']['must']
        # 先将模板中条件删除
        for item in must_block[::-1]:
            if 'source.devid' in item['match']:
                must_block.remove(item)
                break

        # 时间
        dsl_['query']['bool']['filter']['range']['@timestamp'] = {
            "gte": self.start_time, "lte": self.end_time}
        # 将moid过滤条件加入
        must_block.insert(0, {"match": {"source.devid": ""}})

        m_dsl = ""
        for moid in moids:
            dsl_['query']['bool']['must'][0]["match"]["source.devid"] = moid
            m_dsl += '{}\n' + json.dumps(dsl_) + '\n'
        return m_dsl

    def get_perpheral_info(self, moids):
        """
        query perpheral info
        :param moids: [[moid, mr_moid, mr_name],...]
        :return:
        """
        dev_moids = [x[0] for x in moids]
        dsl_ = self.make_perpheral_dsl(dev_moids)
        es = es_client()
        index = "platform-nmscollector-*mt*"
        try:
            results = es.msearch(index=index, dsl=dsl_)
        except Exception as err:
            logger.error(err)
            return False, err.args

        perpheral_info = []
        for result in results['responses']:
            microphones = jsonpath.jsonpath(result, '$..microphones')
            loudspeakers = jsonpath.jsonpath(result, '$..loudspeakers')
            video_resource_name = jsonpath.jsonpath(
                result, '$..video_resource_name')

            mt_status = 0
            # handle microphones
            microphones = microphones[0] if microphones is not False else None
            if microphones is not None:
                dev_status = 1
                dev_info = microphones
                status = [x['status'] for x in dev_info if 'status' in x]
                if 0 in status:
                    dev_status = 0
                else:
                    mt_status = 1
                microphones = {
                    "dev_status": dev_status,
                    "dev_info": microphones}

            # handle loudspeakers
            loudspeakers = loudspeakers[0] if loudspeakers is not False else None
            if loudspeakers is not None:
                dev_status = 1
                dev_info = loudspeakers
                status = [x['status'] for x in dev_info if 'status' in x]
                if 0 in status:
                    dev_status = 0
                else:
                    mt_status = 1
                loudspeakers = {
                    "dev_status": dev_status,
                    "dev_info": loudspeakers}

            # handle video_resource_name
            video_resource_name = video_resource_name[0] if video_resource_name is not False else None
            if video_resource_name is not None:
                dev_status = 0
                video_resource_name = {
                    "dev_status": dev_status,
                    "dev_info": video_resource_name}

            info = {"name": "perpheral", "desc": "外设"}
            if microphones is not None:
                info['microphones'] = microphones
            if loudspeakers is not None:
                info['loudspeakers'] = loudspeakers
            if video_resource_name is not None:
                info['video_resource_name'] = video_resource_name

            if microphones is None and loudspeakers is None and video_resource_name is None:
                mt_status = ""

            perpheral_info.append([mt_status, info])
        return True, perpheral_info

    def get_topology(self):
        """
        获取拓扑信息及外设健康状态
        :return: dict  {"mt_status":0, "protocol_info":[]}
        """
        moids = self.get_dev_moid()  # list  [[moid,mr_moid,mr_name],...]

        # query perpheral_info
        perpheral_info = self.get_perpheral_info(moids)
        if not perpheral_info[0]:
            return perpheral_info
        else:
            mt_status_perpheral_info = perpheral_info[1]

        mt_status = [x[0] for x in mt_status_perpheral_info]  # mt_status

        if self.stat_only:
            return True, [{"mt_status": value} for value in mt_status]

        perpheral_info = [x[1]
                          for x in mt_status_perpheral_info]  # perpheral_info
        param_keys = ["mt_status", "protocol_info"]
        # query mt_info
        mt_info = self.get_dev_info(moids)

        # query machineroom_info
        machineroom_info = self.get_machine_room_info(moids)

        protocol_info = [[x, y, z] for x, y, z in zip(
            mt_info, machineroom_info, perpheral_info)]
        return True, [dict(zip(param_keys, [status, protocol]))
                      for status, protocol in zip(mt_status, protocol_info)]
