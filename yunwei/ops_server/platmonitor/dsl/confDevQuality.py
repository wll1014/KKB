#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
计算会议质量和终端质量, 会议质量和终端质量分开计算, 标准不同
会议质量:
终端质量:
"""

import json
import math
import logging
from jsonpath import jsonpath
from copy import deepcopy
from common.es_client import es_client

logger = logging.getLogger("ops." + __name__)

# 平台媒体 网络丢帧
plat_media_frame_network_loat_dsl = {"size": 0, "query": {
    "bool": {"must_not": [{"match": {"source.frame.medianet_lost": 0}}],
             "must": [{"match": {"source.eventid": "OPS_PLATFORM_MEDIA_INFO_NOTIFY"}},
                      {"exists": {"field": "source.frame.medianet_lost"}}],
             "filter": {"range": {"@timestamp": {"gte": 1576217518117, "lte": 1576218146171}}}}}}
# 平台媒体 卡顿次数
plat_medianet_rebuffer = {"size": 0, "query": {"bool": {"must_not": [{"match": {"source.rtp_info.qoe.rebuffer": 0}}],
                                                        "must": [{"match": {
                                                            "source.eventid": "OPS_PLATFORM_MEDIANET_INFO_NOTIFY"}},
                                                            {"exists": {"field": "source.rtp_info.qoe.rebuffer"}}],
                                                        "filter": {"range": {"@timestamp": {"gte": 1576217518117,
                                                                                            "lte": 1576218146171}}}}}}
# 终端丢包率
mt_max_lossrate = {"size": 0, "query": {"bool": {
    "must": [{"match": {"source.eventid": "EV_CONF_INFO"}}],
    "filter": {"range": {"@timestamp": {"gte": "now-12h", "lte": "now"}}}}}, "aggs": {
    "privideo_recv_max_lose": {"max": {"field": "source.conf_info.privideo_recv.video_pkts_loserate"}},
    "assvideo_recv_max_lose": {"max": {"field": "source.conf_info.assvideo_recv.video_pkts_loserate"}},
    "audio_recv_max_lose": {"max": {"field": "source.conf_info.audio_recv.audio_pkts_loserate"}}}}
# 终端异常退会次数
mt_abend_counts = {"size": 0, "query": {"bool": {
    "must": [{"match": {"source.eventid": "EV_MCU_MT_DEL"}},
             {"terms": {"source.mtinfo.leavereason": [1, 3, 28, 29, 30, 31]}}],
    "filter": {"range": {"@timestamp": {"gte": "now-12h", "lte": "now"}}}}}}

# 多点会议离会原因消息
conf_multi_dev_leave_dsl = {"size":0,"query":{"bool":{"must":[{"match":{"source.mtinfo.confe164":"0513**77"}},{"match":{"source.eventid":"EV_MCU_MT_DEL"}},{"match":{"beat.src_type":"cmu"}},{"terms":{"source.mtinfo.leavereason":[1,3,28,29,30,31]}}],"filter":{"range":{"@timestamp":{"gte":"2018-01-06","lte":"2018-01-06"}}}}},"aggs":{"mtaccount":{"terms":{"field":"source.mtinfo.mtaccount.keyword","size": 10000}}}}
conf_multi_dev_leave_filter = ['responses.aggregations.mtaccount.buckets']


class CalConfQuality:
    """
    计算会议质量
    会议分数:
    平台丢帧（音频/视频)        扣分 = 次数*权重(0.1)
    平台卡顿 (视频）			扣分 = 次数*权重(0.1)

    终端丢包率(主流/辅流/音频) 	扣分 = 丢包率出现的区间 0-10% 1分 10%-20% 2分 20%-30% 3分 30%-40% 4分 40%-50% 5分
    终端异常退会				扣分 = 次数*权重(0.5)
    """
    _plat_medianet_lost_weight = 0.1
    _plat_rebuffer_weight = 0.1
    _mt_abend_weight = 0.5

    def __init__(self, conf_list):
        """
        :param conf_list: list of conf information, contains conf_e164, begin_time, end_time
        :type conf_list: list  [[],...]
        """
        self.conf_list = conf_list

    @staticmethod
    def _score2experience(score):
        """
        会议分数转化为会议体验

        """
        if score < 2.75:
            return 1
        elif 2.75 <= score < 3.75:
            return 2
        elif 3.75 <= score < 4.75:
            return 3
        else:
            return 4

    def calculate(self, value):
        """
        根据参数计算会议分数
        ：param value: list of [frame_media_lost, rebuffer, abend_counts, lossrate]
        :type value: iterable object
        """
        frame_media_lost, rebuffer, abend_counts, lossrate = value
        score = 5  # default 5

        # 丢包率转化为要扣的分数
        lossrate = math.ceil(lossrate/10)
        score -= (frame_media_lost * self._plat_medianet_lost_weight + rebuffer * self._plat_rebuffer_weight + abend_counts * self._mt_abend_weight + lossrate)
        return score if score > 0 else 0

    def query_conf_medianet_lost(self):
        """
        从 OPS_PLATFORM_MEDIA_INFO_NOTIFY消息中查询会议网络丢帧 不为0的消息上报次数
        :return: (True, list)/(False, err)
        """
        dsl = deepcopy(plat_media_frame_network_loat_dsl)
        index = "platform-nmscollector-platformframes-*"
        m_dsl = ""

        for conf_e164, start_time, end_time in self.conf_list:
            dsl_ = deepcopy(dsl)
            dsl_['query']['bool']['must'].append({"match": {"source.context.conf_e164": conf_e164}})
            dsl_['query']['bool']['filter']['range']['@timestamp'] = {"gte": start_time, "lte": end_time}
            m_dsl += '{}\n' + json.dumps(dsl_) + '\n'

        es = es_client()
        try:
            results = es.msearch(index=index, dsl=m_dsl)
        except Exception as err:
            logger.error(err)
            return False, err.args

        counts = []
        for result in results['responses']:
            count = jsonpath(result, "$.hits.total")
            count = 0 if count is False else count[0]
            counts.append(count)
        return True, counts

    def query_conf_rebuffer(self):
        """
        从 OPS_PLATFORM_MEDIANET_INFO_NOTIFY消息中查询会议卡顿次数 不为0的消息上报次数
        :return: (True, list)/(False, err)
        """
        dsl = deepcopy(plat_medianet_rebuffer)
        index = "platform-nmscollector-platformframes-*"
        m_dsl = ""

        for conf_e164, start_time, end_time in self.conf_list:
            dsl_ = deepcopy(dsl)
            dsl_['query']['bool']['must'].append({"match": {"source.context.conf_e164": conf_e164}}),
            dsl_['query']['bool']['filter']['range']['@timestamp'] = {"gte": start_time, "lte": end_time}
            m_dsl += '{}\n' + json.dumps(dsl_) + '\n'

        es = es_client()
        try:
            results = es.msearch(index=index, dsl=m_dsl)
        except Exception as err:
            logger.error(err)
            return False, err.args

        counts = []
        for result in results['responses']:
            count = jsonpath(result, "$.hits.total")
            count = 0 if count is False else count[0]
            counts.append(count)
        return True, counts

    def query_conf_dev_pkg_lossrate(self):
        """
        从 EV_CONF_INFO 消息中查询会议终端丢包率
        :return: (True, list)/(False, err)
        """
        dsl = deepcopy(mt_max_lossrate)
        index = "platform-nmscollector-*mt*"
        m_dsl = ""

        for conf_e164, start_time, end_time in self.conf_list:
            dsl_ = deepcopy(dsl)
            dsl_['query']['bool']['must'].append({"match": {"source.conf_info.conf_e164": conf_e164}})
            dsl_['query']['bool']['filter']['range']['@timestamp'] = {"gte": start_time, "lte": end_time}
            m_dsl += '{}\n' + json.dumps(dsl_) + '\n'

        es = es_client()
        try:
            results = es.msearch(index=index, dsl=m_dsl)
        except Exception as err:
            logger.error(err)
            return False, err.args

        max_value = []
        for result in results['responses']:
            privideo_recv_max_lose = jsonpath(result, "$.aggregations.privideo_recv_max_lose.value")
            assvideo_recv_max_lose = jsonpath(result, "$.aggregations.assvideo_recv_max_lose.value")
            audio_recv_max_lose = jsonpath(result, "$.aggregations.audio_recv_max_lose.value")
            value = [x[0] if x is not False else 0 for x in
                     [privideo_recv_max_lose, assvideo_recv_max_lose, audio_recv_max_lose]]
            value = [x if x is not None else 0 for x in value]
            max_value.append(max(value))
        return True, max_value

    def query_conf_dev_abend(self):
        """
        从 EV_MCU_MT_DEL 消息中查询会议终端异常退会次数
        :return: (True, list)/(False, err)
        """
        dsl = deepcopy(mt_abend_counts)
        index = "platform-nmscollector-*cmu*"
        m_dsl = ""

        for conf_e164, start_time, end_time in self.conf_list:
            dsl_ = deepcopy(dsl)
            dsl_['query']['bool']['must'].append({"match": {"source.mtinfo.confe164": conf_e164}}),
            dsl_['query']['bool']['filter']['range']['@timestamp'] = {"gte": start_time, "lte": end_time}
            m_dsl += '{}\n' + json.dumps(dsl_) + '\n'

        es = es_client()
        try:
            results = es.msearch(index=index, dsl=m_dsl)
        except Exception as err:
            logger.error(err)
            return False, err.args

        counts = []
        for result in results['responses']:
            count = jsonpath(result, "$.hits.total")
            count = 0 if count is False else count[0]
            counts.append(count)
        return True, counts

    def get_conf_quality(self, is_score=False):
        """
        :param is_score: return conf score if 'True' else conf_experience, default is 'False'
        """
        frame_media_lost = self.query_conf_medianet_lost()
        if not frame_media_lost[0]:
            logger.error(frame_media_lost[1])
            return frame_media_lost
        else:
            frame_media_lost = frame_media_lost[1]
        rebuffer = self.query_conf_rebuffer()
        if not rebuffer[0]:
            logger.error(rebuffer[1])
            return rebuffer
        else:
            rebuffer = rebuffer[1]
        abend_counts = self.query_conf_dev_abend()
        if not abend_counts[0]:
            logger.error(abend_counts[1])
            return abend_counts
        else:
            abend_counts = abend_counts[1]
        lossrate = self.query_conf_dev_pkg_lossrate()
        if not lossrate[0]:
            logger.error(lossrate[1])
            return lossrate
        else:
            lossrate = lossrate[1]

        conf_ = zip(frame_media_lost, rebuffer, abend_counts, lossrate)
        conf_scores = map(self.calculate, conf_)
        if is_score:
            return True, list(conf_scores)
        else:
            conf_experience = list(map(self._score2experience, conf_scores))
            return True, conf_experience
