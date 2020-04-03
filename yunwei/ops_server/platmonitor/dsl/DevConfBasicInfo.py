#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
终端参会概况
包括 参会时间、主视频发送、主视频接收、辅视频发送、辅视频接收、音频发送、音频接收、主席、发言、哑音、静音

参会时间:
    multipoint conf:  查询终端入会/离会消息
    point2point conf:  会议起止时间

主视频发送、主视频接收、辅视频发送、辅视频接收、音频发送、音频接收:
    有码流接收: 取终端侧media 上报 总帧数(5s)，总帧数不为0为有码流
    有码流发送: 取dssworker上报 码率(30s) 码率不为0为有码流
    无码流接收: 取终端侧media 上报 总帧数(5s)，总帧数为0为无码流
    无码流发送:取dssworker上报 码率(30s) 码率为0为无码流

终端离会原因: 主动挂断/异常掉线/管理方挂断

"""

import datetime
import json
import logging
import jsonpath
from platmonitor.dsl import dsl
from copy import deepcopy
from common.es_client import es_client
from platmonitor.dsl.confPublicFunc import QueryDssWorkerSSRC
from common.timeFormatConverter import utcstr2utctimestamp

from common.conf_params_enum import *

logger = logging.getLogger('ops.' + __name__)

# 异常聚合数据返回点数
_POINTS_NUM = 12

_allow_media_types = ['video', 'dualvideo', 'audio']

# 会议活动代码
_ACTIONS_ENUM = [1,  # 入会离会
                 2,  # 静音
                 3,  # 哑音
                 5,  # 发言人
                 6,  # 管理方
                 ]

_allow_types = [
    '1',
    '2',
    '3',
    '4',
    '5',
    '6',
    '7',
    '8',
    '9',
    '10',
    '11',
    '12',
    '13',
    '14',
    '15',
    '16',
    '17',
    '18',
    '19',
    '20']

_types_detail = {
    '1': ["time", "参会时间"],
    '2': ["actions", "会议活动"],

    '3': ["recv_no_video_bitrate", "主视频无码流(接收)"],
    '4': ["recv_no_dualvideo_bitrate", "辅视频无码流(接收)"],
    '5': ["recv_no_audio_bitrate", "音频无码流(接收)"],

    '6': ["recv_video_bitrate", "主视频有码流(接收)"],
    '7': ["recv_dualvideo_bitrate", "辅视频有码流(接收)"],
    '8': ["recv_audio_bitrate", "音频有码流(接收)"],

    '9': ["recv_video_err_info", "主视频异常(接收)"],
    '10': ["recv_dualvideo_err_info", "辅视频异常(接收)"],
    '11': ["recv_audio_err_info", "音频异常(接收)"],

    '12': ["send_no_video_bitrate", "主视频无码流(发送)"],
    '13': ["send_no_dualvideo_bitrate", "辅视频无码流(发送)"],
    '14': ["send_no_audio_bitrate", "音频无码流(发送)"],

    '15': ["send_video_bitrate", "主视频有码流(发送)"],
    '16': ["send_dualvideo_bitrate", "辅视频有码流(发送)"],
    '17': ["send_audio_bitrate", "音频有码流(发送)"],

    '18': ["send_video_err_info", "主视频异常(发送)"],
    '19': ["send_dualvideo_err_info", "辅视频异常(发送)"],
    '20': ["send_audio_err_info", "音频异常(发送)"],
}

# 丢包率(mt_medianet)、卡顿(mt_medianet)、时延(mt_medianet)、网络丢帧(mt_media)    暂无 抖动shake
_mt_recv_error_option = ['lose_rate', 'rebuffer', 'rtt', 'medianet_lost']
_mt_recv_error_option_desc = {
    'lose_rate': ['mt', 'medianet', 'source.rtp_info.qoe.fraction_lost'],
    'rebuffer': ['mt', 'medianet', 'source.rtp_info.qoe.rebuffer'],
    'rtt': ['mt', 'medianet', 'source.rtp_info.qoe.rtt'],
    'medianet_lost': ['mt', 'media', 'source.frame.medianet_lost']
}

# 码率(dss)、丢包率(plfm_medianet)、卡顿(plfm_medianet)、时延(plfm_medianet)、网络丢帧(plfm_media)
# 暂无 抖动
_mt_send_error_option = [
    'bitrate',
    'lose_rate',
    'rebuffer',
    'rtt',
    'medianet_lost']
_mt_send_error_option_desc = {
    'bitrate': ['dss', 'dss', 'source.rtp_info.statis.udp_pkt.bytes_rate.cur'],
    'lose_rate': ['plfm', 'medianet', 'source.rtp_info.qoe.fraction_lost'],
    'rebuffer': ['plfm', 'medianet', 'source.rtp_info.qoe.rebuffer'],
    'rtt': ['plfm', 'medianet', 'source.rtp_info.qoe.rtt'],
    'medianet_lost': ['plfm', 'media', 'source.frame.medianet_lost']
}

mt_media_dsl = {
    "size": 0,
    "query": {
        "bool": {
            "must": [
                {
                    "match": {
                        "source.eventid": "OPS_MT_MEDIA_INFO_NOTIFY"}}],
            "filter": {
                "range": {
                    "@timestamp": {
                        "gte": "now-1d",
                        "lte": "now"}}}}},
    "aggs": {
        "date": {
            "date_histogram": {
                "field": "@timestamp",
                "interval": "1h",
                "format": "epoch_millis",
                "min_doc_count": 0,
                "extended_bounds": {
                    "min": "now-1d",
                    "max": "now"}},
            "aggs": {
                "data": {
                    "max": {
                        "field": "source.rtp_info.qoe.fraction_lost"}},
                "max_time": {
                    "max": {
                        "field": "@timestamp"}}}}}}

mt_media_net_dsl = {
    "size": 0,
    "query": {
        "bool": {
            "must": [
                {
                    "match": {
                        "source.eventid": "OPS_MT_MEDIANET_INFO_NOTIFY"}}],
            "filter": {
                "range": {
                    "@timestamp": {
                        "gte": "now-1d",
                        "lte": "now"}}}}},
    "aggs": {
        "date": {
            "date_histogram": {
                "field": "@timestamp",
                "interval": "1h",
                "format": "epoch_millis",
                "min_doc_count": 0,
                "extended_bounds": {
                    "min": "now-1d",
                    "max": "now"}},
            "aggs": {
                "data": {
                    "max": {
                        "field": "source.rtp_info.qoe.fraction_lost"}},
                "max_time": {
                    "max": {
                        "field": "@timestamp"}}}}}}

plfm_media_dsl = {
    "aggs": {
        "date": {
            "date_histogram": {
                "interval": "150000ms",
                "extended_bounds": {
                    "min": 1577164842000,
                    "max": 1577166662000},
                "min_doc_count": 0,
                "format": "epoch_millis",
                "field": "@timestamp"},
            "aggs": {
                "type": {
                    "terms": {
                        "field": "source.context.type.keyword",
                        "size": 10},
                    "aggs": {
                        "data": {
                            "max": {
                                "field": "source.rtp_info.qoe.fraction_lost"}}}},
                "max_time": {
                    "max": {
                        "field": "@timestamp"}}}}},
    "size": 0,
    "query": {
        "bool": {
            "minimum_should_match": 1,
            "should": []}}}


mt_dss_dsl = {
    "size": 0, "query": {
        "bool": {
            "filter": {
                "range": {
                    "@timestamp": {
                        "gte": 1571743799300, "lte": 1571745599300}}}, "must_not": [
                            {
                                "match": {
                                    "source.rtp_info.statis.ssrc": 0}}], "must": [
                                        {
                                            "match": {
                                                "source.eventid": "EV_DSS_PORT_STATIS_NOTIFY"}}, {
                                                    "exists": {
                                                        "field": "source.rtp_info.statis.udp_pkt.bytes_rate.cur"}}, {
                                                            "match": {
                                                                "source.context.channer.local": 1}}]}}, "aggs": {
                                                                    "date": {
                                                                        "date_histogram": {
                                                                            "field": "@timestamp", "interval": "30s", "format": "epoch_millis", "min_doc_count": 0, "extended_bounds": {
                                                                                "min": "1571743799300", "max": "1571745599300"}}, "aggs": {
                                                                                    "data": {
                                                                                        "max": {
                                                                                            "field": "source.rtp_info.statis.udp_pkt.bytes_rate.cur"}}}}}}

mt_media_bitrate_dsl = {
    "size": 0,
    "query": {
        "bool": {
            "must": [
                {
                    "match": {
                        "source.eventid": "OPS_MT_MEDIA_INFO_NOTIFY"}}],
            "filter": {
                "range": {
                    "@timestamp": {
                        "gte": 1569496991000,
                        "lte": 1569553266081}}}}},
    "aggs": {
        "date": {
            "date_histogram": {
                "field": "@timestamp",
                "interval": "5s",
                "format": "epoch_millis",
                "min_doc_count": 0,
                "extended_bounds": {
                    "min": "1571743799300",
                    "max": "1571745599300"}},
            "aggs": {
                "data": {
                    "max": {
                        "field": "source.frame.total_frames"}}}}}}

mt_aggs_dss_dsl = {
    "size": 0, "query": {
        "bool": {
            "must": [
                {
                    "match": {
                        "source.eventid": "EV_DSS_PORT_STATIS_NOTIFY"}}, {
                            "match": {
                                "source.context.channer.local": 1}}], "must_not": [
                                    {
                                        "match": {
                                            "source.rtp_info.statis.ssrc": 0}}], "filter": {
                                                "range": {
                                                    "@timestamp": {
                                                        "gte": 1569496991000, "lte": 1569553266081}}}}}, "aggs": {
                                                            "date": {
                                                                "date_histogram": {
                                                                    "field": "@timestamp", "interval": "1h", "format": "epoch_millis", "min_doc_count": 0, "extended_bounds": {
                                                                        "min": "1569568654000", "max": "1569582629127"}}, "aggs": {
                                                                            "data": {
                                                                                "max": {
                                                                                    "field": "source.rtp_info.qoe.thruput.pps"}}, "max_time": {
                                                                                        "max": {
                                                                                            "field": "@timestamp"}}}}}}

platform_media_net_dsl = {
    "size": 0,
    "query": {
        "bool": {
            "should": [],
            "minimum_should_match": 1}},
    "aggs": {
        "mediatype": {
            "terms": {
                "field": "source.context.type.keyword",
                "size": 10000},
            "aggs": {
                "date": {
                    "date_histogram": {
                        "field": "@timestamp",
                        "interval": "1h",
                        "format": "epoch_millis",
                        "min_doc_count": 0,
                        "extended_bounds": {
                            "min": "1569568654000",
                            "max": "1569582629127"}},
                    "aggs": {
                        "data": {
                            "max": {
                                "field": "source.rtp_info.qoe.thruput.pps"}}}}}}}}


def getBasicInfoOption(num):
    """
    if num is None then return all options in _allow_options, else return the num option details
    :param num: str
    """
    if num is None:
        return _allow_types
    else:
        return _types_detail.get(num)


def find_constant_0(data):
    """
    找到列表里值为0的索引段
    :param data:
    :return:
    """

    def find_first_0(a_list, start):
        try:
            start = a_list.index(0, start)
        except ValueError:
            return None

        end = None
        for i in range(start, len(a_list)):
            if a_list[i] != 0:
                end = i
                break
        return [start, end]

    time_dur = []
    begin = 0
    while True:
        start_index = find_first_0(data, begin)
        if start_index is None:
            break
        elif start_index[1] is None:
            time_dur.append(start_index)
            break
        else:
            time_dur.append([start_index[0], start_index[1] - 1])
            begin = start_index[1]
    return time_dur


def find_constant_1(data):
    """
    找到0/1列表里1的索引段
    :param data:
    :return:
    """

    def find_first_1(a_list, start):
        try:
            start = a_list.index(1, start)
        except ValueError:
            return None

        try:
            end = a_list.index(0, start)
        except ValueError:
            return [start, None]
        else:
            return [start, end]

    time_dur = []
    begin = 0
    while True:
        start_index = find_first_1(data, begin)
        if start_index is None:
            break
        elif start_index[1] is None:
            time_dur.append(start_index)
            break
        else:
            time_dur.append([start_index[0], start_index[1] - 1])
            begin = start_index[1]
    return time_dur


def find_not_constant_0(data):
    """
    找到列表里值非0的索引段
    :param data:
    :return:
    """
    constant_0_index = find_constant_0(data)
    index_dur = []
    l = len(constant_0_index)
    if l == 0:
        index_dur.append([0, None])
    else:
        first = constant_0_index[0]
        end = constant_0_index[-1]
        if first[0] != 0:
            index_dur.append([0, first[0] - 1])

        if l > 1:
            for i in range(l - 1):
                index_dur.append([constant_0_index[i][1] + 1,
                                  constant_0_index[i + 1][0] - 1])

        if end[1] is not None:
            index_dur.append([end[1] + 1, None])
    return index_dur


class DevConfBasicInfo:
    """
    查询终端会议概况,返回终端与会时间/音视频无码流相关信息
    """

    media_desc = {
        "vmp": "合成",
        "vbas": "适配",
        "port": "端口",
        "portbas": "端口适配",
        "abas": "适配",
        "mixer": "混音"
    }

    def __init__(self, **kwargs):
        self.conf_id = kwargs.get('conf_id')
        self.mt_e164 = kwargs.get('mt_e164')
        self.conf_type = kwargs.get('conf_type')
        self.conf_status = kwargs.get('conf_status')
        self.start_time = kwargs.get('start_time')
        self.end_time = kwargs.get('end_time')
        self.types = kwargs.get('types')
        self.interval = kwargs.get('interval')
        self.time_on = kwargs.get('time_on')
        self.meeting_time = None
        self.ssrc_up = None
        self.ssrc_down = None
        self.params_init()

    def params_init(self):
        """
        处理异常查询条件
        :return:
        """
        if not all([self.conf_id,
                    self.mt_e164,
                    self.start_time,
                    self.end_time]):
            assert ValueError("params error")
        if self.conf_type is None or self.conf_type not in ConfType.values():
            raise ValueError('conference type error')
        if self.conf_status is None or self.conf_status not in ConfStat.values():
            raise ValueError('conference type error')
        self.start_time = int(self.start_time)
        if self.end_time == ConfEndTimeType.REALTIME.name or self.end_time == ConfEndTimeType.MANUAL.name:
            self.end_time = int(datetime.datetime.now().timestamp() * 1000)
        elif self.end_time == ConfEndTimeType.ABEND.name:
            # 异常结会按会议时长2小时计算
            self.end_time = self.start_time + 7200000
        else:
            self.end_time = int(self.end_time)
        if self.interval is not None:
            self.interval = str(int(self.interval)) + "ms"
        else:
            self.interval = str(
                (self.end_time - self.start_time) // _POINTS_NUM) + "ms"

    def get_conf_time(self):
        """
        计算与会时间段 及 入会离会事件
        :return: tuple
        """
        if self.conf_type == ConfType.P2P:
            # 点对点会议与会时间与会议时间相同
            # # 点对点会议暂不实现
            conf_time = [
                {'start_time': self.start_time, 'end_time': self.end_time}]
            # conf_actions = {self.start_time: {"code": 1, "desc": "入会"}, self.end_time: {"code": 1, "desc": "离会"}}
            conf_actions = {}
            return True, conf_time, conf_actions
        else:
            # 多点会议
            # 查询 是否在查询时间段前入会
            pre_stat = self.get_multi_conf_pre_one_add_del()
            if not pre_stat[0]:
                # 如果查询失败 则认为终端查询时间前已经入会
                pre_stat = True
            else:
                pre_stat = pre_stat[1]

            add_del_time = self.get_multi_conf_add_del()
            if not add_del_time[0]:
                # 获取失败返回失败原因
                return add_del_time
            elif add_del_time[1] is None:
                # 如果没查到终端入会离会消息
                if pre_stat:
                    conf_time = [
                        {'start_time': self.start_time, 'end_time': self.end_time}]
                    conf_actions = {}
                    return True, conf_time, conf_actions
                else:
                    return True, None
            else:
                add_del_time_id, add_del_time_time, leave_reason = add_del_time[1]

                conf_time = []  # 会议时间段数组
                single_time = {}  # 单个参会离会时间段

                conf_actions = {}  # 会议入会离会活动字典  {'t':[{}]}
                mt_del_count = 0
                if pre_stat:
                    conf_stat = True  # 会议状态
                    single_time["start_time"] = self.start_time
                else:
                    conf_stat = False  # 会议状态

                for index, event in enumerate(add_del_time_id):
                    if event == "EV_MCU_MT_ADD":
                        if conf_stat:
                            continue
                        conf_stat = True
                        single_time["start_time"] = add_del_time_time[index]
                        conf_actions[add_del_time_time[index]] = [
                            {"code": 1, "desc": "入会"}]
                        continue
                    if event == "EV_MCU_MT_DEL":
                        if not conf_stat:
                            mt_del_count += 1
                            continue
                        conf_stat = False
                        single_time["end_time"] = add_del_time_time[index]
                        conf_actions[add_del_time_time[index]] = [{"code": 1, "desc": "离会", "info": [{
                            "title": "离会原因", "content": getConfDevDelReason(leave_reason[mt_del_count])}]}]
                        mt_del_count += 1
                        conf_time.append(single_time)
                        single_time = {}
                        continue
                # 处理结会消息丢失
                # # 实时会议本来就没有结会消息
                if conf_stat:
                    single_time["end_time"] = self.end_time
                    conf_time.append(single_time)

                    # # 历史会议没有结会消息添加提示
                    # if self.conf_status == ConfStat.HISTORY:
                    #     conf_actions[self.end_time] = [{"code": 1, "desc": "离会",
                    #                                     "info": [{"title": "离会原因", "content": "异常掉线"}]}]

                return True, conf_time, conf_actions

    def get_multi_conf_add_del(self):
        """
        获取多点会议终端入会/离会时间
        :return: list or None   [[event_id...], [event_time...], [leave_reason...]]
        """
        index = "platform-nmscollector-*cmu*"

        # 修改模板
        dsl_ = deepcopy(dsl.conf_multi_dev_add_del_dsl)
        must_block = dsl_['query']['bool']['must']
        # 先将模板中会议号和终端号条件删除
        for item in must_block[::-1]:
            if 'source.mtinfo.confe164' in item['match']:
                must_block.remove(item)
            if 'source.mtinfo.mtaccount' in item['match']:
                must_block.remove(item)

        # 将终端会议号和终端号条件加入
        must_block.append(
            {"match": {"source.mtinfo.confe164": "{}".format(self.conf_id)}})
        must_block.append(
            {"match": {"source.mtinfo.mtaccount": "{}".format(self.mt_e164)}})
        # 时间
        dsl_['query']['bool']['filter']['range']['@timestamp'] = {
            "gte": self.start_time, "lte": self.end_time}

        # 查询
        es = es_client()
        try:
            results = es.search(index=index, dsl=dsl_)
        except Exception as err:
            logger.error(err)
            return False, err.args

        event_id = jsonpath.jsonpath(results, '$..source.eventid')
        event_time = jsonpath.jsonpath(results, '$..sort[0]')
        leave_reason = jsonpath.jsonpath(
            results, '$..source.mtinfo.leavereason')

        if event_id and event_time:
            # 如果终端入会 返回出入会信息
            return True, [event_id, event_time, leave_reason]
        else:
            # 否则 返回None
            return True, None

    def get_multi_conf_pre_one_add_del(self):
        """
        获取多点会议终端 某一时间点前 是否已经入会
        :return: True/(True/False) or False/err
        """
        index = "platform-nmscollector-*cmu*"

        # 修改模板
        dsl_ = deepcopy(dsl.conf_multi_dev_add_del_dsl)
        must_block = dsl_['query']['bool']['must']
        # 先将模板中会议号和终端号条件删除
        for item in must_block[::-1]:
            if 'source.mtinfo.confe164' in item['match']:
                must_block.remove(item)
            if 'source.mtinfo.mtaccount' in item['match']:
                must_block.remove(item)

        # 将终端会议号和终端号条件加入
        must_block.append(
            {"match": {"source.mtinfo.confe164": "{}".format(self.conf_id)}})
        must_block.append(
            {"match": {"source.mtinfo.mtaccount": "{}".format(self.mt_e164)}})
        # 时间
        dsl_['query']['bool']['filter']['range']['@timestamp'] = {
            "gte": self.time_on, "lte": self.start_time}
        dsl_['size'] = 1
        dsl_['sort']['@timestamp']['order'] = "desc"

        # 查询
        es = es_client()
        try:
            results = es.search(index=index, dsl=dsl_)
        except Exception as err:
            logger.error(err)
            return False, err.args

        event_id = jsonpath.jsonpath(results, '$..source.eventid')

        if event_id is False:
            return True, False
        elif event_id == ["EV_MCU_MT_ADD"]:
            return True, True
        elif event_id == ["EV_MCU_MT_DEL"]:
            return True, False
        else:
            return True, False

    def get_dev_mute_dumbness_info(self):
        """
        获取终端上报会议信息（5min）
        用于计算 静哑音
        :return:
        """
        index = "platform-nmscollector-*mt*"

        # 修改模板
        dsl_ = deepcopy(dsl.dev_conf_info_dsl)
        must_block = dsl_['query']['bool']['must']
        # 先将模板中会议号和终端号条件删除
        for item in must_block[::-1]:
            if 'source.conf_info.conf_e164' in item['match']:
                must_block.remove(item)
            if 'source.conf_info.mt_e164' in item['match']:
                must_block.remove(item)

        # 将终端会议号和终端号条件加入
        must_block.append(
            {"match": {"source.conf_info.conf_e164": "{}".format(self.conf_id)}})
        must_block.append(
            {"match": {"source.conf_info.mt_e164": "{}".format(self.mt_e164)}})
        # 时间
        dsl_['query']['bool']['filter']['range']['@timestamp'] = {
            "gte": self.start_time, "lte": self.end_time}

        # 查询
        dsl_['_source'] = [
            'source.conf_info.mute',
            'source.conf_info.dumbness']
        dsl_['size'] = 10000
        filter_path = ["hits.hits._source.source.conf_info", "hits.hits.sort"]
        es = es_client()
        try:
            results = es.search(index=index, dsl=dsl_, filter_path=filter_path)
        except Exception as err:
            logger.error(err)
            return False, err.args
        return True, results

    def get_dev_pre_one_mute_dumbness_info(self):
        """
        获取终端上报会议信息（5min）
        用于计算 静哑音 往前多查一个点
        静音状态: 0:off 1:on
        哑音状态: 0:off 1:on
        :return: tuple of bool   (True, False)  mute/dumbness
        """
        index = "platform-nmscollector-*mt*"

        # 修改模板
        dsl_ = deepcopy(dsl.dev_conf_info_dsl)
        must_block = dsl_['query']['bool']['must']
        # 先将模板中会议号和终端号条件删除
        for item in must_block[::-1]:
            if 'source.conf_info.conf_e164' in item['match']:
                must_block.remove(item)
            if 'source.conf_info.mt_e164' in item['match']:
                must_block.remove(item)

        # 将终端会议号和终端号条件加入
        must_block.append(
            {"match": {"source.conf_info.conf_e164": "{}".format(self.conf_id)}})
        must_block.append(
            {"match": {"source.conf_info.mt_e164": "{}".format(self.mt_e164)}})
        # 时间
        dsl_['query']['bool']['filter']['range']['@timestamp'] = {
            "gte": self.time_on, "lte": self.start_time}

        # 查询
        dsl_['_source'] = [
            'source.conf_info.mute',
            'source.conf_info.dumbness']
        dsl_['sort']['@timestamp']['order'] = "desc"
        dsl_['size'] = 1

        filter_path = ["hits.hits._source.source.conf_info", "hits.hits.sort"]
        es = es_client()
        try:
            results = es.search(index=index, dsl=dsl_, filter_path=filter_path)
        except Exception as err:
            logger.error(err)
            return False, err.args

        mute = jsonpath.jsonpath(results, "$..source.conf_info.mute")
        dumbness = jsonpath.jsonpath(results, "$..source.conf_info.dumbness")
        is_mute = mute == [1]
        is_dumbness = dumbness == [1]
        return True, (is_mute, is_dumbness)

    def make_mt_media_bitrate_dsl(self):
        """
        查询终端侧 media 总帧数信息的dsl语句  仅接收
        包括 主视频/辅视频/音频
        用于计算 终端发送有无码流

        如果查询时间等于会议开始时间(即 start_time==time_on) 有无码流的查询开始时间延迟30s
        :return: m_dsl
        """

        m_dsl = ""
        # 构建dsl语句
        for media_type in ['video', 'dualvideo', 'audio']:
            dsl_ = deepcopy(mt_media_bitrate_dsl)
            must_block = dsl_['query']['bool']['must']

            # 将过滤条件加入
            must_block.append(
                {"match": {"source.context.conf_e164": "{}".format(self.conf_id)}})
            must_block.append(
                {"match": {"source.context.mt_e164": "{}".format(self.mt_e164)}})
            must_block.append(
                {"match": {"source.context.media_type": "{}".format(media_type)}})
            must_block.append({"match": {"source.rtp_info.type": "recv"}})
            dsl_['query']['bool']['must'] = must_block

            # 时间
            for cur_time in self.meeting_time:
                if cur_time['start_time'] == self.time_on:
                    start_time = self.start_time + 30 * 1000
                    if cur_time['end_time'] <= start_time:
                        start_time = cur_time['end_time']
                else:
                    start_time = cur_time['start_time']
                dsl_['query']['bool']['filter']['range']['@timestamp'] = {
                    "gte": start_time, "lte": cur_time['end_time']}
                dsl_['aggs']['date']['date_histogram']['extended_bounds'] = {
                    "min": start_time, "max": cur_time['end_time']}

                m_dsl += '{"index":"platform-nmscollector-mtframes*"}\n' + \
                    json.dumps(dsl_) + '\n'
        return m_dsl

    def make_mt_dss_bitrate_dsl(self, direct):
        """
        查询转发侧 dss 码率信息的dsl语句  仅接收
        包括 主视频/辅视频/音频
        用于计算 终端发送有无码流

        如果查询时间等于会议开始时间(即 start_time==time_on) 有无码流的查询开始时间延迟30s
        :param direct: 'up':上行 'down':下行
        :return: m_dsl
        """

        m_dsl = ""
        # 构建dsl语句
        for media_type in ['video', 'dualvideo', 'audio']:
            dsl_ = deepcopy(mt_dss_dsl)
            must_block = dsl_['query']['bool']['must']

            # 将过滤条件加入
            must_block.append(
                {"match": {"source.conf_e164": "{}".format(self.conf_id)}})
            must_block.append(
                {"match": {"source.context.chan_type": "{}".format(media_type)}})

            if direct == 'up':
                # 转发接收 即 上行
                must_block.append(
                    {"match": {"source.context.channer.id": "{}".format(self.mt_e164)}})
                must_block.append(
                    {"match": {"source.context.chanee.id": "{}".format(self.conf_id)}})
                must_block.append({"match": {"source.direct": "up"}})
            else:
                # 转发发送 即 下行
                must_block.append(
                    {"match": {"source.context.channer.id": "{}".format(self.conf_id)}})
                must_block.append(
                    {"match": {"source.context.chanee.id": "{}".format(self.mt_e164)}})
                must_block.append({"match": {"source.direct": "down"}})

            dsl_['query']['bool']['must'] = must_block

            # 时间
            for cur_time in self.meeting_time:
                if cur_time['start_time'] == self.time_on:
                    start_time = self.start_time + 30 * 1000
                    if cur_time['end_time'] <= start_time:
                        start_time = cur_time['end_time']
                else:
                    start_time = cur_time['start_time']
                dsl_['query']['bool']['filter']['range']['@timestamp'] = {
                    "gte": start_time, "lte": cur_time['end_time']}
                dsl_['aggs']['date']['date_histogram']['extended_bounds'] = {
                    "min": start_time, "max": cur_time['end_time']}

                m_dsl += '{"index":"platform-nmscollector-*dss*worker*"}\n' + \
                    json.dumps(dsl_) + '\n'
        return m_dsl

    def make_aggs_dss_dsl(self, media_type, direct, key_word):
        """
        查询转发侧 dss 信息的dsl语句 仅上行
        包括 主视频/辅视频/音频
        聚合画图
        :param media_type: 媒体类型  video/dualvideo/audio
        :param direct: 码流方向  up上行/down下行
        :param key_word: 待查询网媒字段
        :return: m_dsl
        """

        # 构建dsl语句
        dsl_ = deepcopy(mt_aggs_dss_dsl)
        must_block = dsl_['query']['bool']['must']

        # 将过滤条件加入
        must_block.append(
            {"match": {"source.conf_e164": "{}".format(self.conf_id)}})
        must_block.append(
            {"match": {"source.context.chan_type": "{}".format(media_type)}})
        must_block.append({"exists": {"field": "source.rtp_info"}})

        if direct == "up":
            # 转发接收 即 上行
            must_block.append(
                {"match": {"source.context.channer.id": "{}".format(self.mt_e164)}})
            must_block.append(
                {"match": {"source.context.chanee.id": "{}".format(self.conf_id)}})
            must_block.append({"match": {"source.direct": "up"}})
        else:
            must_block.append(
                {"match": {"source.context.channer.id": "{}".format(self.conf_id)}})
            must_block.append(
                {"match": {"source.context.chanee.id": "{}".format(self.mt_e164)}})
            must_block.append({"match": {"source.direct": "down"}})
        dsl_['query']['bool']['must'] = must_block
        # 时间
        dsl_['query']['bool']['filter']['range']['@timestamp'] = {
            "gte": self.start_time, "lte": self.end_time}

        # 时间间隔
        dsl_['aggs']['date']['date_histogram']['interval'] = self.interval
        dsl_['aggs']['date']['date_histogram']['extended_bounds'] = {
            "min": self.start_time, "max": self.end_time}
        # 查询字段
        dsl_['aggs']['date']['aggs']['data']['max']['field'] = key_word
        return dsl_

    def query_if_data_mt_media(self):
        """
        查询终端侧 mt_media 接收 是否有数据
        :return: True(有数据)/False(无数据)
        """
        dsl_ = {
            "size": 0, "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "source.eventid": "OPS_MT_MEDIA_INFO_NOTIFY"}}, {
                            "match": {
                                "source.rtp_info.type": "recv"}}], "filter": {
                                    "range": {
                                        "@timestamp": {
                                            "gte": 1571117047000, "lte": 1571117806957}}}}}}
        must_block = dsl_['query']['bool']['must']
        must_block.append(
            {"match": {"source.context.conf_e164": "{}".format(self.conf_id)}})
        must_block.append(
            {"match": {"source.context.mt_e164": "{}".format(self.mt_e164)}})
        dsl_['query']['bool']['must'] = must_block
        dsl_['query']['bool']['filter']['range']['@timestamp'] = {
            "gte": self.start_time, "lte": self.end_time}

        es = es_client()
        index = "platform-nmscollector-mtframes*"
        try:
            results = es.search(index=index, dsl=dsl_)
        except Exception as err:
            logger.error(err)
            return False

        total = results['hits']['total']
        if total == 0:
            return False
        else:
            return True

    def query_bitrate_flow_status_data(self):
        """
        批量查询 有码流/无码流  包括 主流/辅流/音频
        终端发送 查询 dssworker 接收 码率
        终端接收 查询 (mt_media 接收 总帧数) 或者 (dssworker 发送 码率)  当终端mt_media无数据时用dssworker数据代替

        如果查询时间等于会议开始时间(即 start_time==time_on) 有无码流的查询开始时间延迟30s
        :return: recv(主流/辅流/音频)+send(主流/辅流/音频) if_mt_media_data(终端mt_media接收是否有数据)
        """
        # 首先查询终端接收mt_media是否有数据
        if_mt_media_data = self.query_if_data_mt_media()

        # 终端接收
        if if_mt_media_data:
            # mt_media有数据
            mt_recv_dsl = self.make_mt_media_bitrate_dsl()
        else:
            # mt_media无数据
            mt_recv_dsl = self.make_mt_dss_bitrate_dsl('down')

        # 终端发送
        mt_send_dsl = self.make_mt_dss_bitrate_dsl('up')

        m_dsl = mt_recv_dsl + mt_send_dsl
        es = es_client()
        try:
            results = es.msearch(dsl=m_dsl)
        except Exception as err:
            logger.error(err)
            return False, err.args
        return True, results['responses'], if_mt_media_data

    def process_mute_dumbness_data(self, dev_data):
        """
        处理静音/哑音
        :param type_: str
        :param dev_data: list
        :return: dict   {t:[{}]}
        """
        actions = [2, 3]
        actions_desc = {2: ['静音开启', '静音关闭'], 3: ['哑音开启', '哑音关闭']}
        time_dur = {}

        pre_one_info = self.get_dev_pre_one_mute_dumbness_info()
        if not pre_one_info[0]:
            pre_mute_stat, pre_dumbness_stat = False, False
        else:
            pre_mute_stat, pre_dumbness_stat = pre_one_info[1]

        t = jsonpath.jsonpath(dev_data, '$.hits.hits..sort[0]')
        mute_data = jsonpath.jsonpath(dev_data, '$.hits.hits..mute')
        dumbness_data = jsonpath.jsonpath(dev_data, '$.hits.hits..dumbness')

        if t is False:
            return time_dur

        for action in actions:
            if action == 2:
                data = mute_data
                pre_stat = pre_mute_stat
            elif action == 3:
                data = dumbness_data
                pre_stat = pre_dumbness_stat
            else:
                continue

            if data is False:
                continue
            elif len(data) == 0:
                continue

            action_index = find_constant_1(data)
            if len(action_index) == 0:
                continue
            else:
                for start, end in action_index:
                    start_time = t[start]
                    if start == 0:
                        # 如果一开始就是静哑音
                        if not pre_stat:
                            # 如果前一个状态不是静哑音
                            if start_time in time_dur.keys():
                                time_dur[start_time].append(
                                    {"code": action, "desc": actions_desc.get(action)[0]})
                            else:
                                time_dur[start_time] = [
                                    {"code": action, "desc": actions_desc.get(action)[0]}]
                    else:
                        if start_time in time_dur.keys():
                            time_dur[start_time].append(
                                {"code": action, "desc": actions_desc.get(action)[0]})
                        else:
                            time_dur[start_time] = [
                                {"code": action, "desc": actions_desc.get(action)[0]}]

                    if end is not None:
                        end_time = t[end]
                        if end_time in time_dur.keys():
                            time_dur[end_time].append(
                                {"code": action, "desc": actions_desc.get(action)[1]})
                        else:
                            time_dur[end_time] = [
                                {"code": action, "desc": actions_desc.get(action)[1]}]
        return time_dur

    def process_no_bitrate(self, type_, dev_data, if_mt_media_data):
        """
        处理 主视频/辅视频/音频无码流
        终端发送 转发 码率 为0
        终端接收 mt_media 总帧数为0
        :param type_:str
        :param dev_data: list
        :param if_mt_media_data: 终端侧接收mt_media是否有数据  True:有数据  False:无数据
        :return:list
        """
        # if type_ == '3':
        #     # 主视频无码流(接收)
        #     if if_mt_media_data:
        #         # 如果mt_media有数据
        #         b = '$..source.frame.total_frames'
        #     else:
        #         # mt_media没有数据 用转发数据代替
        #         b = '$..source.rtp_info.statis.udp_pkt.bytes_rate.cur'
        # elif type_ == '4':
        #     # 辅视频无码流(接收)
        #     if if_mt_media_data:
        #         # 如果mt_media有数据
        #         b = '$..source.frame.total_frames'
        #     else:
        #         # mt_media没有数据 用转发数据代替
        #         b = '$..source.rtp_info.statis.udp_pkt.bytes_rate.cur'
        # elif type_ == '5':
        #     # 音频无码流(接收)
        #     if if_mt_media_data:
        #         # 如果mt_media有数据
        #         b = '$..source.frame.total_frames'
        #     else:
        #         # mt_media没有数据 用转发数据代替
        #         b = '$..source.rtp_info.statis.udp_pkt.bytes_rate.cur'
        # elif type_ == '12':
        #     # 主视频无码流(发送)
        #     b = '$..source.rtp_info.statis.udp_pkt.bytes_rate.cur'
        # elif type_ == '13':
        #     # 辅视频无码流(发送)
        #     b = '$..source.rtp_info.statis.udp_pkt.bytes_rate.cur'
        # elif type_ == '14':
        #     # 音频无码流(发送)
        #     b = '$..source.rtp_info.statis.udp_pkt.bytes_rate.cur'
        # else:
        #     return True, None

        meeting_time = len(self.meeting_time)
        b = '$.aggregations..value'

        time_dur = []
        is_null = True
        for count, data in enumerate(dev_data):
            if data['hits']['total'] == 0:
                continue

            cur_data = jsonpath.jsonpath(data, b)
            cur_t = jsonpath.jsonpath(data, '$.aggregations..key')

            if cur_t is False or cur_data is False:
                continue

            # 替换第一个数据和最后一个数据的时间，解决es聚合时间偏移问题
            cur_t[0] = self.meeting_time[count]['start_time']
            cur_t[-1] = self.meeting_time[count]['end_time']

            # 处理聚合数据  最后一个数据为空的现象
            if count == meeting_time - 1:
                # 只处理最后一段会议数据
                if cur_data[-1] is None:
                    if type_ in ['3', '4', '5'] and if_mt_media_data:
                        # media 数据去掉最后6个数据
                        first_none_index = 6
                        for last_count, last_value in enumerate(
                                cur_data[:-7:-1]):
                            if last_value is not None:
                                first_none_index = last_count
                                break

                        cur_data = cur_data[:-first_none_index]
                        cur_t = cur_t[:-first_none_index]
                    else:
                        cur_data = cur_data[:-1]
                        cur_t = cur_t[:-1]

            is_null = False
            cur_data = [0 if x is None else x for x in cur_data]
            bitrate_index = find_constant_0(cur_data)
            if len(bitrate_index) == 0:
                continue
            else:
                for start, end in bitrate_index:
                    if start == 0:
                        start_time = self.meeting_time[count]['start_time']
                    else:
                        start_time = cur_t[start]
                    if end is None:
                        end_time = self.meeting_time[count]['end_time']
                    else:
                        end_time = cur_t[end + 1]
                    time_dur.append(
                        {"start_time": start_time, "end_time": end_time})
        if is_null is True:
            return True, None
        return True, time_dur

    def process_bitrate(self, type_, dev_data, if_mt_media_data):
        """
        处理 主视频/辅视频/音频有码流
        终端发送 转发 码率 不为0
        终端接收 mt_media 总帧数不为0
        :param type_:str
        :param dev_data: list
        :param if_mt_media_data: 终端侧接收mt_media是否有数据  True:有数据  False:无数据
        :return:list
        """
        # if type_ == '6':
        #     # 主视频有码流(接收)
        #     if if_mt_media_data:
        #         # 如果mt_media有数据
        #         b = '$..source.frame.total_frames'
        #     else:
        #         # mt_media没有数据 用转发数据代替
        #         b = '$..source.rtp_info.statis.udp_pkt.bytes_rate.cur'
        # elif type_ == '7':
        #     # 辅视频有码流(接收)
        #     if if_mt_media_data:
        #         # 如果mt_media有数据
        #         b = '$..source.frame.total_frames'
        #     else:
        #         # mt_media没有数据 用转发数据代替
        #         b = '$..source.rtp_info.statis.udp_pkt.bytes_rate.cur'
        # elif type_ == '8':
        #     # 音频有码流(接收)
        #     if if_mt_media_data:
        #         # 如果mt_media有数据
        #         b = '$..source.frame.total_frames'
        #     else:
        #         # mt_media没有数据 用转发数据代替
        #         b = '$..source.rtp_info.statis.udp_pkt.bytes_rate.cur'
        # elif type_ == '15':
        #     # 主视频有码流(发送)
        #     b = '$..source.rtp_info.statis.udp_pkt.bytes_rate.cur'
        # elif type_ == '16':
        #     # 辅视频有码流(发送)
        #     b = '$..source.rtp_info.statis.udp_pkt.bytes_rate.cur'
        # elif type_ == '17':
        #     # 音频有码流(发送)
        #     b = '$..source.rtp_info.statis.udp_pkt.bytes_rate.cur'
        # else:
        #     return True, None

        meeting_time = len(self.meeting_time)
        b = '$.aggregations..value'

        time_dur = []
        is_null = True
        for count, data in enumerate(dev_data):
            if data['hits']['total'] == 0:
                continue

            cur_data = jsonpath.jsonpath(data, b)
            cur_t = jsonpath.jsonpath(data, '$.aggregations..key')
            if cur_t is False or cur_data is False:
                continue

            # 替换第一个数据和最后一个数据的时间，解决es聚合时间偏移问题
            cur_t[0] = self.meeting_time[count]['start_time']
            cur_t[-1] = self.meeting_time[count]['end_time']

            # 处理聚合数据  最后一个数据为空的现象
            if count == meeting_time - 1:
                # 只处理最后一段会议数据
                if cur_data[-1] is None:
                    if type_ in ['6', '7', '8'] and if_mt_media_data:
                        # media 数据去掉最后6个数据
                        first_none_index = 6
                        for last_count, last_value in enumerate(
                                cur_data[:-7:-1]):
                            if last_value is not None:
                                first_none_index = last_count
                                break

                        cur_data = cur_data[:-first_none_index]
                        cur_t = cur_t[:-first_none_index]
                    else:
                        cur_data = cur_data[:-1]
                        cur_t = cur_t[:-1]

            is_null = False
            cur_data = [0 if x is None else x for x in cur_data]
            bitrate_index = find_not_constant_0(cur_data)
            if len(bitrate_index) == 0:
                continue
            else:
                for start, end in bitrate_index:
                    if start == 0:
                        start_time = self.meeting_time[count]['start_time']
                    else:
                        start_time = cur_t[start]
                    if end is None:
                        end_time = self.meeting_time[count]['end_time']
                    else:
                        end_time = cur_t[end + 1]
                    time_dur.append(
                        {"start_time": start_time, "end_time": end_time})
        if is_null is True:
            return True, None
        return True, time_dur

    def get_speaker_chairman_info(self):
        """
        获取多点会议发言人/主席
        :return: tuple   False/error   True/speaker/chairman
        """
        # 修改模板
        dsl_ = deepcopy(dsl.dev_conf_speaker_dsl)
        must_block = dsl_['query']['bool']['must']
        # 先将模板中会议号和终端号条件删除
        for item in must_block[::-1]:
            if 'source.confE164.keyword' in item['match']:
                must_block.remove(item)
                break

        # 将会议号条件加入
        must_block.append(
            {"match": {"source.confE164.keyword": "{}".format(self.conf_id)}})
        # 时间
        dsl_['query']['bool']['filter']['range']['@timestamp'] = {
            "gte": self.start_time, "lte": self.end_time}

        # 查询
        # filter_path = deepcopy(dsl.dev_conf_speaker_filter)
        filter_path = [
            "hits.hits._source.source.speaker",
            "hits.hits._source.source.chairman",
            "hits.hits.sort"]
        es = es_client()
        index = "mqwatcher-*"
        try:
            results = es.search(index=index, dsl=dsl_, filter_path=filter_path)
        except Exception as err:
            logger.error(err)
            return False, err.args

        sp_time = jsonpath.jsonpath(results, '$.hits.hits..sort[0]')
        speaker_data = jsonpath.jsonpath(results, '$.hits.hits..speaker.mtNO')
        chairman_data = jsonpath.jsonpath(
            results, '$.hits.hits..chairman.mtNO')

        if sp_time is False:
            return True, None, None

        if speaker_data is False:
            speaker_data = None
        else:
            speaker_data = list(zip(speaker_data, sp_time))

        if chairman_data is False:
            chairman_data = None
        else:
            chairman_data = list(zip(chairman_data, sp_time))

        return True, speaker_data, chairman_data

    def get_pre_one_speaker_chairman_info(self):
        """
        获取多点会议发言人/主席
        向前多获取一个点
        :return: tuple   False/error   True/(speaker/chairman)
        """
        # 修改模板
        dsl_ = deepcopy(dsl.dev_conf_speaker_dsl)
        must_block = dsl_['query']['bool']['must']
        # 先将模板中会议号和终端号条件删除
        for item in must_block[::-1]:
            if 'source.confE164.keyword' in item['match']:
                must_block.remove(item)
                break

        # 将会议号条件加入
        must_block.append(
            {"match": {"source.confE164.keyword": "{}".format(self.conf_id)}})
        # 时间
        dsl_['query']['bool']['filter']['range']['@timestamp'] = {
            "gte": self.time_on, "lte": self.start_time}
        dsl_['size'] = 1
        dsl_['sort']['@timestamp']['order'] = 'desc'

        # 查询
        # filter_path = deepcopy(dsl.dev_conf_speaker_filter)
        filter_path = [
            "hits.hits._source.source.speaker",
            "hits.hits._source.source.chairman",
            "hits.hits.sort"]
        es = es_client()
        index = "mqwatcher-*"
        try:
            results = es.search(index=index, dsl=dsl_, filter_path=filter_path)
        except Exception as err:
            logger.error(err)
            return False, err.args

        pre_speaker = jsonpath.jsonpath(results, '$..speaker.mtNO')
        pre_chairman = jsonpath.jsonpath(results, '$..chairman.mtNO')

        pre_speaker = pre_speaker[0] if pre_speaker is not False else ""
        pre_chairman = pre_chairman[0] if pre_chairman is not False else ""
        return True, (pre_speaker, pre_chairman)

    def get_speak_chairman_time(self):
        """
        返回终端会议发言/主席时间段
        :return: dict
        """
        actions = [5, 6]
        actions_desc = {5: ['发言人设置', '发言人取消'], 6: ['管理方设置', '管理方取消']}
        time_dur = {}

        pre_one_info = self.get_pre_one_speaker_chairman_info()
        if not pre_one_info[0]:
            pre_speaker, pre_chairman = "", ""
        else:
            pre_speaker, pre_chairman = pre_one_info[1]

        speaker_chairman_data = self.get_speaker_chairman_info()
        if not speaker_chairman_data[0]:
            speaker_data, chairman_data = None, None
        else:
            speaker_data, chairman_data = speaker_chairman_data[1], speaker_chairman_data[2]

        for action in actions:
            if action == 5:
                data = speaker_data
                pre_data = pre_speaker
            elif action == 6:
                data = chairman_data
                pre_data = pre_chairman
            else:
                continue

            if data is None:
                continue
            elif len(data) == 0:
                continue

            # 去重
            last_one_data = None
            for item in data[:]:
                if item[0] == last_one_data:
                    data.remove(item)
                else:
                    last_one_data = item[0]

            if self.mt_e164 == pre_data != data[0][0]:
                start_t = data[0][1]
                if start_t in time_dur.keys():
                    time_dur[start_t].append(
                        {"code": action, "desc": actions_desc.get(action)[1]})
                else:
                    time_dur[start_t] = [
                        {"code": action, "desc": actions_desc.get(action)[1]}]

            for index, item in enumerate(data):
                if self.mt_e164 == item[0]:
                    if index == 0 and item[0] == pre_data:
                        # 如果在查询时间段前已经是当前状态
                        if len(data) != 1:
                            end_t = data[1][1]
                            if end_t in time_dur.keys():
                                time_dur[end_t].append(
                                    {"code": action, "desc": actions_desc.get(action)[1]})
                            else:
                                time_dur[end_t] = [
                                    {"code": action, "desc": actions_desc.get(action)[1]}]
                        continue

                    start_t = item[1]
                    if start_t in time_dur.keys():
                        time_dur[start_t].append(
                            {"code": action, "desc": actions_desc.get(action)[0]})
                    else:
                        time_dur[start_t] = [
                            {"code": action, "desc": actions_desc.get(action)[0]}]

                    if index == len(data) - 1:
                        # 如果查询时间段内状态没有改变 不处理
                        continue
                    else:
                        end_t = data[index + 1][1]
                        if end_t in time_dur.keys():
                            time_dur[end_t].append(
                                {"code": action, "desc": actions_desc.get(action)[1]})
                        else:
                            time_dur[end_t] = [
                                {"code": action, "desc": actions_desc.get(action)[1]}]

        return time_dur

    def make_platform_media_net_dsl(self, media_type, direct, key_word):
        """
        构建查询平台侧medianet信息的dsl语句
        :param media_type: 媒体类型  video/dualvideo/audio
        :param direct: 码流方向  up上行/down下行
        :param key_word: 待查询网媒字段
        :return: dsl
        """
        media_media_type = {
            "video": 'vmp||vbas||port||portbas',
            "dualvideo": 'vbas||portbas',
            "audio": 'abas||mixer'
        }

        dsl_ = deepcopy(plfm_media_dsl)

        # 平台接收 即 上行
        # ssrc = self.ssrc_up.get(media_type)
        ssrc = self.ssrc_up
        # if ssrc is None:
        #     ssrc_info = ['None', self.start_time, self.end_time]
        # else:
        ssrc_info = []
        for ssrc_key, ssrc_list in ssrc.items():
            # 获取获取对应媒体类型的ssrc
            if ssrc_key != media_type:
                continue
            for single_ssrc_info in ssrc_list:
                # 每个ssrc的时间段最大时间加30s  最小时间减30s
                min_time = single_ssrc_info[1] - 30000
                max_time = single_ssrc_info[2] + 30000
                ssrc_info.append([single_ssrc_info[0], min_time, max_time])
            break
        # ssrc 为空， 设置ssrc 为 -1 这样查询数据为空 占位用
        if len(ssrc_info) == 0:
            ssrc_info = [[-1, self.start_time, self.end_time]]

        # 时间间隔
        dsl_['aggs']['date']['date_histogram']['interval'] = self.interval
        dsl_['aggs']['date']['date_histogram']['extended_bounds'] = {
            "min": self.start_time, "max": self.end_time}
        # 查询字段
        dsl_['aggs']['date']['aggs']['type']['aggs']['data']['max']['field'] = key_word

        should_block = dsl_['query']['bool']['should']
        for single_ssrc_info in ssrc_info:
            must = []
            must.append(
                {"match": {"source.context.conf_e164": "{}".format(self.conf_id)}})
            must.append({"match": {"source.context.type": "{}".format(
                media_media_type.get(media_type))}})
            must.append(
                {"match": {"source.eventid": "OPS_PLATFORM_MEDIANET_INFO_NOTIFY"}})
            must.append(
                {"match": {"source.rtp_info.ssrc": single_ssrc_info[0]}})
            must.append({"range": {"@timestamp": {
                        "gte": single_ssrc_info[1], "lte": single_ssrc_info[2]}}})
            should = {"bool": {"must": must}}
            should_block.append(should)

        dsl_['query']['bool']['should'] = should_block
        return dsl_

    def make_platform_media_dsl(self, media_type, direct, key_word):
        """
        构建查询平台侧media信息的dsl语句
        :param media_type: 媒体类型  video/dualvideo/audio
        :param direct: 码流方向  up上行/down下行
        :param key_word: 待查询网媒字段
        :return: dsl
        """
        media_media_type = {
            "video": 'vmp||vbas||port||portbas',
            "dualvideo": 'vbas',
            "audio": 'abas||mixer'
        }

        dsl_ = deepcopy(plfm_media_dsl)

        # 平台接收 即 上行
        # # 获取获取对应媒体类型的ssrc
        ssrc = self.ssrc_up.get(media_type)
        ssrc_info = []
        if ssrc is None:
            ssrc_info.append([-1, self.start_time, self.end_time])
        else:
            for single_ssrc_info in ssrc:
                # 每个ssrc的时间段最大时间加30s  最小时间减30s
                min_time = single_ssrc_info[1] - 30000
                max_time = single_ssrc_info[2] + 30000
                ssrc_info.append([single_ssrc_info[0], min_time, max_time])
            # ssrc 为空， 设置ssrc 为 -1 这样查询数据为空 占位用
            if len(ssrc_info) == 0:
                ssrc_info.append([-1, self.start_time, self.end_time])

        # 时间间隔
        dsl_['aggs']['date']['date_histogram']['interval'] = self.interval
        dsl_['aggs']['date']['date_histogram']['extended_bounds'] = {
            "min": self.start_time, "max": self.end_time}
        # 查询字段
        dsl_['aggs']['date']['aggs']['type']['aggs']['data']['max']['field'] = key_word

        should_block = dsl_['query']['bool']['should']
        for single_ssrc_info in ssrc_info:
            must = []
            must.append(
                {"match": {"source.context.conf_e164": "{}".format(self.conf_id)}})
            must.append({"match": {"source.context.type": "{}".format(
                media_media_type.get(media_type))}})
            must.append(
                {"match": {"source.eventid": "OPS_PLATFORM_MEDIA_INFO_NOTIFY"}})
            must.append({"match": {"source.frame.ssrc": single_ssrc_info[0]}})
            must.append({"range": {"@timestamp": {
                        "gte": single_ssrc_info[1], "lte": single_ssrc_info[2]}}})
            should = {"bool": {"must": must}}
            should_block.append(should)

        dsl_['query']['bool']['should'] = should_block
        return dsl_

    def query_platform_media_net_conf_info(self, options):
        """
        查询平台侧medianet上报的会议信息  包括 主视频/辅视频/音频
        :param options: 待查询的类型
        :return: dict   {'video':{'loss_rate':[[t, v],[],...]}}
        """
        info = {}

        m_dsl = ""
        for media_type in _allow_media_types:
            # 'video', 'dualvideo', 'audio'

            for op in options[:]:
                # 查询字段循环
                who_side, media_side, key_word = _mt_send_error_option_desc.get(
                    op)
                dsl_ = self.make_platform_media_net_dsl(
                    media_type, 'up', key_word)
                m_dsl += '{}\n' + json.dumps(dsl_) + '\n'

        if not m_dsl:
            return True, info

        es = es_client()
        index = "platform-nmscollector-platformframes*"
        try:
            results = es.msearch(index=index, dsl=m_dsl)
        except Exception as err:
            logger.error(err)
            return False, err.args

        op_num = len(options)
        total_media_info = {}
        for media_type_count, media_type in enumerate(_allow_media_types):
            # media_name = _allow_media_types[media_type_count]
            single_media_data = results['responses'][op_num *
                                                     media_type_count:op_num * (media_type_count + 1)]
            single_media_info = {}

            for count, result in enumerate(single_media_data):
                option_name = options[count]
                option_info = []

                for bucket in result['aggregations']['date']['buckets']:
                    cur_key_time = jsonpath.jsonpath(bucket, '$.key')[0]
                    cur_max_time = jsonpath.jsonpath(
                        bucket, '$.max_time.value_as_string')
                    if cur_max_time is not False:
                        cur_key_time = utcstr2utctimestamp(cur_max_time[0])

                    sig_interval_data = []
                    for media_type_info in bucket['type']['buckets']:
                        media_tp = jsonpath.jsonpath(
                            media_type_info, '$.key')[0]
                        cur_value = jsonpath.jsonpath(
                            media_type_info, '$.data.value')
                        if cur_value[0] is not None:
                            sig_interval_data.append({
                                "type": media_tp,
                                "value": cur_value[0],
                                "desc": self.media_desc.get(media_tp)
                            })
                    option_info.append(
                        {"timestamp": cur_key_time, option_name: sig_interval_data})
                single_media_info[option_name] = option_info
            total_media_info[media_type] = single_media_info

        return True, total_media_info

    def query_platform_media_conf_info(self, options):
        """
        查询平台侧media上报的会议信息  包括 主视频/辅视频/音频
        :param options: 待查询的类型
        :return: dict   {'video':{'loss_rate':[[t, v],[],...]}}
        """
        info = {}

        m_dsl = ""
        for media_type in _allow_media_types:
            # 'video', 'dualvideo', 'audio'

            for op in options[:]:
                # 查询字段循环
                who_side, media_side, key_word = _mt_send_error_option_desc.get(
                    op)
                dsl_ = self.make_platform_media_dsl(media_type, 'up', key_word)
                m_dsl += '{}\n' + json.dumps(dsl_) + '\n'

        if not m_dsl:
            return True, info

        es = es_client()
        index = "platform-nmscollector-platformframes*"
        try:
            results = es.msearch(index=index, dsl=m_dsl)
        except Exception as err:
            logger.error(err)
            return False, err.args

        op_num = len(options)
        total_media_info = {}
        for media_type_count, media_type in enumerate(_allow_media_types):
            # media_name = _allow_media_types[media_type_count]
            single_media_data = results['responses'][op_num *
                                                     media_type_count:op_num * (media_type_count + 1)]
            single_media_info = {}

            for count, result in enumerate(single_media_data):
                option_name = options[count]
                option_info = []

                for bucket in result['aggregations']['date']['buckets']:
                    cur_key_time = jsonpath.jsonpath(bucket, '$.key')[0]
                    cur_max_time = jsonpath.jsonpath(
                        bucket, '$.max_time.value_as_string')
                    if cur_max_time is not False:
                        cur_key_time = utcstr2utctimestamp(cur_max_time[0])

                    sig_interval_data = []
                    for media_type_info in bucket['type']['buckets']:
                        media_tp = jsonpath.jsonpath(
                            media_type_info, '$.key')[0]
                        cur_value = jsonpath.jsonpath(
                            media_type_info, '$.data.value')
                        if cur_value[0] is not None:
                            sig_interval_data.append({
                                "type": media_tp,
                                "value": cur_value[0],
                                "desc": self.media_desc.get(media_tp)
                            })
                    option_info.append(
                        {"timestamp": cur_key_time, option_name: sig_interval_data})
                single_media_info[option_name] = option_info
            total_media_info[media_type] = single_media_info

        return True, total_media_info

    def query_aggs_dss_conf_info(self, options):
        """
        查询转发 上行 上报的会议信息(目前只有码率)  包括 主视频/辅视频/音频
        :param options: 待查询的类型
        :return: dict   {'video':{'loss_rate':[[t, v],[],...]}}
        """
        info = {}

        m_dsl = ""
        for media_type in _allow_media_types:
            # 'video', 'dualvideo', 'audio'

            for op in options[:]:
                # 查询字段循环
                who_side, media_side, key_word = _mt_send_error_option_desc.get(
                    op)
                dsl_ = self.make_aggs_dss_dsl(media_type, 'up', key_word)
                m_dsl += '{}\n' + json.dumps(dsl_) + '\n'

        if not m_dsl:
            return True, info

        es = es_client()
        index = "platform-nmscollector-*dss*worker*"
        try:
            results = es.msearch(index=index, dsl=m_dsl)
        except Exception as err:
            logger.error(err)
            return False, err.args

        op_num = len(options)
        total_media_info = {}
        for media_type_count, media_type in enumerate(_allow_media_types):
            media_name = _allow_media_types[media_type_count]
            single_media_data = results['responses'][op_num *
                                                     media_type_count:op_num * (media_type_count + 1)]
            single_media_info = {}

            for count, result in enumerate(single_media_data):
                option_name = options[count]
                option_info = []

                for bucket in result['aggregations']['date']['buckets']:
                    cur_value = jsonpath.jsonpath(bucket, '$.data.value')
                    # 转发上的码率，统一除1024再乘8 单位未kb/s    他原始单位是Bps
                    cur_value = None if cur_value[0] is None else round(
                        cur_value[0] / 128, 2)
                    cur_key_time = jsonpath.jsonpath(bucket, '$.key')
                    cur_max_time = jsonpath.jsonpath(
                        bucket, '$.max_time.value_as_string')
                    if cur_value is not None:
                        sig_interval_data = [{
                            "type": "dss",
                            "value": cur_value,
                            "desc": "转发"
                        }]
                    else:
                        sig_interval_data = []
                    if cur_max_time is False:
                        option_info.append(
                            {"timestamp": cur_key_time[0], option_name: sig_interval_data})
                    else:
                        cur_max_time = utcstr2utctimestamp(cur_max_time[0])
                        option_info.append(
                            {"timestamp": cur_max_time, option_name: sig_interval_data})
                single_media_info[option_name] = option_info
            total_media_info[media_name] = single_media_info

        return True, total_media_info

    def query_mt_send_info(self):
        """
        查询终端上行信息
        码率(dss)、丢包率(plfm_medianet)、卡顿(plfm_medianet)、时延(plfm_medianet)、网络丢帧(plfm_media)    暂无 抖动
        主视频先用vmp，辅视频用vbas，主音频用mixer
        :return: dict  {'video':[{},{}], 'audio':[{},{}]}
        """
        plfm_media_options = []
        plfm_media_net_options = []
        dss_options = []
        for op in _mt_send_error_option:
            who_side, media_side, key_word = _mt_send_error_option_desc.get(op)
            if media_side == 'media':
                plfm_media_options.append(op)
            elif media_side == 'medianet':
                plfm_media_net_options.append(op)
            elif media_side == 'dss':
                dss_options.append(op)
            else:
                continue

        if len(plfm_media_options) > 0:
            if self.ssrc_up is None:
                info_mt_media = {}
            else:
                info_mt_media = self.query_platform_media_conf_info(
                    plfm_media_options)
                if not info_mt_media[0]:
                    info_mt_media = {}
                else:
                    info_mt_media = info_mt_media[1]
        else:
            info_mt_media = {}

        if len(plfm_media_net_options) > 0:
            if self.ssrc_up is None:
                info_mt_medianet = {}
            else:
                info_mt_medianet = self.query_platform_media_net_conf_info(
                    plfm_media_net_options)
                if not info_mt_medianet[0]:
                    info_mt_medianet = {}
                else:
                    info_mt_medianet = info_mt_medianet[1]
        else:
            info_mt_medianet = {}

        if len(dss_options) > 0:
            info_mt_dss = self.query_aggs_dss_conf_info(dss_options)
            if not info_mt_dss[0]:
                info_mt_dss = {}
            else:
                info_mt_dss = info_mt_dss[1]
        else:
            info_mt_dss = {}

        info = {}
        # 合并数据
        for media_type in _allow_media_types:
            mt_media_single_info = info_mt_media.get(media_type)
            mt_media_net_single_info = info_mt_medianet.get(media_type)
            mt_dss_single_info = info_mt_dss.get(media_type)

            tmp = {}
            if mt_media_single_info is not None:
                tmp.update(mt_media_single_info)
            if mt_media_net_single_info is not None:
                tmp.update(mt_media_net_single_info)
            if mt_dss_single_info is not None:
                tmp.update(mt_dss_single_info)

            if len(tmp) == 0:
                info[media_type] = None
                continue

            tmp_time = []
            keys = []
            values = []
            for key, value_list in tmp.items():
                cur_time = [x['timestamp'] for x in value_list]
                cur_key = key
                cur_value = [x[cur_key] for x in value_list]

                keys.append(cur_key)
                tmp_time.append(cur_time)
                values.append(cur_value)

            # 时间戳随机用一个
            t = tmp_time[0]

            # 检查第一个点和最后一个点的时间  解决时间偏移的问题
            # if t[0] < self.start_time:
            #     t[0] = self.start_time
            if t[0] < self.meeting_time[0]["start_time"]:
                t[0] = self.meeting_time[0]["start_time"]
            if t[-1] > self.end_time:
                t[-1] = self.end_time

            values.append(t)
            data_combine = list(zip(*values))
            keys.append('timestamp')

            single_result = [dict(zip(keys, x)) for x in data_combine]
            info[media_type] = single_result
        return info

    def make_mt_media_net_dsl(self, media_type, direct, key_word):
        """
        构建查询终端侧medianet信息的dsl语句
        :param media_type: 媒体类型  video/dualvideo/audio
        :param direct: 码流方向  up上行/down下行
        :param key_word: 待查询网媒字段
        :return: dsl
        """
        dsl_ = deepcopy(mt_media_net_dsl)

        # 构建dsl语句
        must_block = dsl_['query']['bool']['must']
        must_block.append(
            {"match": {"source.context.conf_e164": "{}".format(self.conf_id)}})
        must_block.append(
            {"match": {"source.context.mt_e164": "{}".format(self.mt_e164)}})
        must_block.append(
            {"match": {"source.context.media_type": "{}".format(media_type)}})
        if direct == 'up':
            # 终端发送
            must_block.append({"match": {"source.rtp_info.type": "send"}})
        else:
            # 终端接收
            must_block.append({"match": {"source.rtp_info.type": "recv"}})
        dsl_['query']['bool']['must'] = must_block

        # 时间
        dsl_['query']['bool']['filter']['range']['@timestamp'] = {
            "gte": self.start_time, "lte": self.end_time}

        # 聚合
        # 时间间隔
        dsl_['aggs']['date']['date_histogram']['interval'] = self.interval
        dsl_['aggs']['date']['date_histogram']['extended_bounds'] = {
            "min": self.start_time, "max": self.end_time}
        # 查询字段
        dsl_['aggs']['date']['aggs']['data']['max']['field'] = key_word

        return dsl_

    def make_mt_media_dsl(self, media_type, direct, key_word):
        """
        构建查询终端侧media信息的dsl语句
        :param media_type: 媒体类型  video/dualvideo/audio
        :param direct: 码流方向  up上行/down下行
        :param key_word: 待查询网媒字段
        :return: dsl
        """

        dsl_ = deepcopy(mt_media_dsl)

        # 构建dsl语句
        must_block = dsl_['query']['bool']['must']
        must_block.append(
            {"match": {"source.context.conf_e164": "{}".format(self.conf_id)}})
        must_block.append(
            {"match": {"source.context.mt_e164": "{}".format(self.mt_e164)}})
        must_block.append(
            {"match": {"source.context.media_type": "{}".format(media_type)}})
        if direct == 'up':
            # 终端发送
            must_block.append({"match": {"source.rtp_info.type": "send"}})
        else:
            # 终端接收
            must_block.append({"match": {"source.rtp_info.type": "recv"}})
        dsl_['query']['bool']['must'] = must_block

        # 时间
        dsl_['query']['bool']['filter']['range']['@timestamp'] = {
            "gte": self.start_time, "lte": self.end_time}

        # 聚合
        # 时间间隔
        dsl_['aggs']['date']['date_histogram']['interval'] = self.interval
        dsl_['aggs']['date']['date_histogram']['extended_bounds'] = {
            "min": self.start_time, "max": self.end_time}
        # 查询字段
        dsl_['aggs']['date']['aggs']['data']['max']['field'] = key_word
        return dsl_

    def query_mt_media_net_conf_info(self, options):
        """
        查询终端侧medianet上报的会议信息  包括 主视频/辅视频/音频
        :param options: 待查询的类型
        :return: dict   {'video':{'loss_rate':[[t, v],[],...]}}
        """
        info = {}

        m_dsl = ""
        for media_type in _allow_media_types:
            # 'video', 'dualvideo', 'audio'

            for op in options[:]:
                # 查询字段循环
                who_side, media_side, key_word = _mt_recv_error_option_desc.get(
                    op)
                dsl_ = self.make_mt_media_net_dsl(media_type, 'down', key_word)
                m_dsl += '{}\n' + json.dumps(dsl_) + '\n'

        if not m_dsl:
            return True, info

        es = es_client()
        index = "platform-nmscollector-mtframes*"
        try:
            results = es.msearch(index=index, dsl=m_dsl)
        except Exception as err:
            logger.error(err)
            return False, err.args

        op_num = len(options)
        total_media_info = {}
        for media_type_count, media_type in enumerate(_allow_media_types):
            # media_name = _allow_media_types[media_type_count]
            single_media_data = results['responses'][op_num *
                                                     media_type_count:op_num * (media_type_count + 1)]
            single_media_info = {}

            for count, result in enumerate(single_media_data):
                option_name = options[count]
                option_info = []

                for bucket in result['aggregations']['date']['buckets']:
                    cur_value = jsonpath.jsonpath(bucket, '$.data.value')
                    cur_key_time = jsonpath.jsonpath(bucket, '$.key')
                    cur_max_time = jsonpath.jsonpath(
                        bucket, '$.max_time.value_as_string')
                    if cur_value[0] is not None:
                        sig_interval_data = [{
                            "type": "mt",
                            "value": cur_value[0],
                            "desc": "终端"
                        }]
                    else:
                        sig_interval_data = []
                    if cur_max_time is False:
                        option_info.append(
                            {"timestamp": cur_key_time[0], option_name: sig_interval_data})
                    else:
                        cur_max_time = utcstr2utctimestamp(cur_max_time[0])
                        option_info.append(
                            {"timestamp": cur_max_time, option_name: sig_interval_data})
                single_media_info[option_name] = option_info
            total_media_info[media_type] = single_media_info

        return True, total_media_info

    def query_mt_media_conf_info(self, options):
        """
        查询终端侧media上报的会议信息  包括 主视频/辅视频/音频
        :param options: 待查询的类型
        :return: dict   {'video':{'loss_rate':[[t, v],[],...]}}
        """
        info = {}

        m_dsl = ""
        for media_type in _allow_media_types:
            # 'video', 'dualvideo', 'audio'

            for op in options[:]:
                # 查询字段循环
                who_side, media_side, key_word = _mt_recv_error_option_desc.get(
                    op)
                dsl_ = self.make_mt_media_dsl(media_type, 'down', key_word)
                m_dsl += '{}\n' + json.dumps(dsl_) + '\n'

        if not m_dsl:
            return True, info

        es = es_client()
        index = "platform-nmscollector-mtframes*"
        try:
            results = es.msearch(index=index, dsl=m_dsl)
        except Exception as err:
            logger.error(err)
            return False, err.args

        op_num = len(options)
        total_media_info = {}
        for media_type_count, media_type in enumerate(_allow_media_types):
            # media_name = _allow_media_types[media_type_count]
            single_media_data = results['responses'][op_num *
                                                     media_type_count:op_num * (media_type_count + 1)]
            single_media_info = {}

            for count, result in enumerate(single_media_data):
                option_name = options[count]
                option_info = []

                for bucket in result['aggregations']['date']['buckets']:
                    cur_value = jsonpath.jsonpath(bucket, '$.data.value')
                    cur_key_time = jsonpath.jsonpath(bucket, '$.key')
                    cur_max_time = jsonpath.jsonpath(
                        bucket, '$.max_time.value_as_string')

                    if cur_value[0] is not None:
                        sig_interval_data = [{
                            "type": "mt",
                            "value": cur_value[0],
                            "desc": "终端"
                        }]
                    else:
                        sig_interval_data = []
                    if cur_max_time is False:
                        option_info.append(
                            {"timestamp": cur_key_time[0], option_name: sig_interval_data})
                    else:
                        cur_max_time = utcstr2utctimestamp(cur_max_time[0])
                        option_info.append(
                            {"timestamp": cur_max_time, option_name: sig_interval_data})
                single_media_info[option_name] = option_info
            total_media_info[media_type] = single_media_info

        return True, total_media_info

    def query_mt_recv_info(self):
        """
        查询终端下行信息
        丢包率(mt_medianet)、卡顿(mt_medianet)、时延(mt_medianet)、网络丢帧(mt_media)    暂无 抖动
        :return: dict  {'video':[{},{}], 'audio':[{},{}]}
        """

        mt_media_options = []
        mt_media_net_options = []
        for op in _mt_recv_error_option:
            who_side, media_side, key_word = _mt_recv_error_option_desc.get(op)
            if media_side == 'media':
                mt_media_options.append(op)
            elif media_side == 'medianet':
                mt_media_net_options.append(op)
            else:
                continue

        if len(mt_media_options) > 0:
            info_mt_media = self.query_mt_media_conf_info(mt_media_options)
            if not info_mt_media[0]:
                info_mt_media = {}
            else:
                info_mt_media = info_mt_media[1]
        else:
            info_mt_media = {}

        if len(mt_media_net_options) > 0:
            info_mt_medianet = self.query_mt_media_net_conf_info(
                mt_media_net_options)
            if not info_mt_medianet[0]:
                info_mt_medianet = {}
            else:
                info_mt_medianet = info_mt_medianet[1]
        else:
            info_mt_medianet = {}

        info = {}
        # 合并数据
        for media_type in _allow_media_types:
            mt_media_single_info = info_mt_media.get(media_type)
            mt_media_net_single_info = info_mt_medianet.get(media_type)
            tmp = {}
            if mt_media_single_info is not None:
                tmp.update(mt_media_single_info)
            if mt_media_net_single_info is not None:
                tmp.update(mt_media_net_single_info)
            if len(tmp) == 0:
                info[media_type] = None
                continue

            tmp_time = []
            keys = []
            values = []
            for key, value_list in tmp.items():
                cur_time = [x['timestamp'] for x in value_list]
                cur_key = key
                cur_value = [x[cur_key] for x in value_list]

                keys.append(cur_key)
                tmp_time.append(cur_time)
                values.append(cur_value)

            # 时间戳随机用一个
            t = tmp_time[0]

            # 检查第一个点和最后一个点的时间  解决时间偏移的问题
            # if t[0] < self.start_time:
            #     t[0] = self.start_time
            if t[0] < self.meeting_time[0]["start_time"]:
                t[0] = self.meeting_time[0]["start_time"]
            if t[-1] > self.end_time:
                t[-1] = self.end_time

            values.append(t)
            data_combine = list(zip(*values))
            keys.append('timestamp')

            single_result = [dict(zip(keys, x)) for x in data_combine]
            info[media_type] = single_result
        return info

    def query_conf_actions(self, mt_add_del_info):
        """
        查询会议活动
        :param mt_add_del_info: 会议入会离会活动时间  {'t':{}}
        :return:
        """
        mute_dumbness_data = self.get_dev_mute_dumbness_info()
        if not mute_dumbness_data[0]:
            mute_dumbness_info = {}
        else:
            mute_dumbness_info = self.process_mute_dumbness_data(
                mute_dumbness_data[1])

        speak_chairman_info = self.get_speak_chairman_time()

        keys_set = set(
            mt_add_del_info.keys()) | set(
            mute_dumbness_info.keys()) | set(
            speak_chairman_info.keys())
        keys = sorted(keys_set)

        result = []
        for time_ in keys:
            mt_add_del_action = mt_add_del_info.get(time_, [])
            mute_dumbness_action = mute_dumbness_info.get(time_, [])
            speak_chairman_action = speak_chairman_info.get(time_, [])

            actions = mt_add_del_action + mute_dumbness_action + speak_chairman_action
            result.append({"timestamp": time_, "actions": actions})
        return result

    def get_info_time(self):
        """
        按照要求从终端会议信息中提取数据
        :return:
        """
        if self.types is None:
            option = getBasicInfoOption(self.types)
        else:
            option = self.types.split(',')
            option = [x for x in option if x in getBasicInfoOption(None)]

        if len(option) == 0:
            return True, []

        # first get the meeting time
        meeting_time = self.get_conf_time()
        if not meeting_time[0]:
            logger.error(meeting_time[1])
            return meeting_time
        elif meeting_time[1] is None:
            return True, []
        else:
            self.meeting_time, add_del_actions = meeting_time[1], meeting_time[2]

        if_mt_media_data = None  # 终端侧接收(下行)mt_media是否有数据
        # 如果有查是否有码流
        # # 查询数据  发送: dssworker    接收: media
        if {'3', '4', '5', '6', '7', '8', '12', '13',
                '14', '15', '16', '17'} & set(option):
            bitrate_data = self.query_bitrate_flow_status_data()
            if not bitrate_data[0]:
                return bitrate_data
            else:
                bitrate_data, if_mt_media_data = bitrate_data[1], bitrate_data[2]

        # 如果有查平台媒体数据 提前查询ssrc分布
        if {'18', '19', '20'} & set(option):
            # 查询转发上行码流ssrc
            ssrc_up = QueryDssWorkerSSRC(
                self.conf_id,
                self.mt_e164,
                self.start_time,
                self.end_time,
                'up').query_ssrc()
            if not ssrc_up[0]:
                # 查询ssrc失败
                return ssrc_up
            elif ssrc_up[1] is None:
                # ssrc为空
                pass
            else:
                self.ssrc_up = ssrc_up[1]

        # 如果有查上行异常数据 提前查询上行异常数据
        if {'18', '19', '20'} & set(option):
            send_err_data = self.query_mt_send_info()

        # 如果有查下行异常数据 提前查询下行异常数据
        if {'9', '10', '11'} & set(option):
            # 首先查询终端侧接收mt_media是否有数据
            if if_mt_media_data is None:
                if_mt_media_data = self.query_if_data_mt_media()
            if if_mt_media_data:
                # 查询终端下行异常数据
                recv_err_data = self.query_mt_recv_info()
            else:
                # 如果终端侧接收mt_media是没有数据
                recv_err_data = {}

        info = []
        items = ["name", "description", "data"]
        conf_time_section_num = len(self.meeting_time)   # 入会次数 即会议区间个数
        for type_ in option:
            if type_ == '1':
                # 会议时间
                name, desc = _types_detail.get(type_)
                data = self.meeting_time
                info.append(dict(zip(items, [name, desc, data])))
            elif type_ == '2':
                # 会议活动
                name, desc = _types_detail.get(type_)
                data = self.query_conf_actions(add_del_actions)
                info.append(dict(zip(items, [name, desc, data])))
            elif type_ in ['9', '10', '11']:
                # 异常数据 接收
                if type_ == '9':
                    err_data = recv_err_data.get('video')
                elif type_ == '10':
                    err_data = recv_err_data.get('dualvideo')
                else:
                    err_data = recv_err_data.get('audio')

                name, desc = _types_detail.get(type_)
                if err_data is not None:
                    info.append(dict(zip(items, [name, desc, err_data])))
                else:
                    info.append(dict(zip(items, [name, desc, None])))
            elif type_ in ['18', '19', '20']:
                # 异常数据 发送
                if type_ == '18':
                    err_data = send_err_data.get('video')
                elif type_ == '19':
                    err_data = send_err_data.get('dualvideo')
                else:
                    err_data = send_err_data.get('audio')

                name, desc = _types_detail.get(type_)
                if err_data is not None:
                    info.append(dict(zip(items, [name, desc, err_data])))
                else:
                    info.append(dict(zip(items, [name, desc, None])))
            elif type_ in ['3', '4', '5', '12', '13', '14']:
                # 主视频/辅视频/音频 无码流
                index = ['3', '4', '5', '12', '13', '14'].index(type_)
                name, desc = _types_detail.get(type_)
                data = self.process_no_bitrate(type_, bitrate_data[index * conf_time_section_num:(
                    index + 1) * conf_time_section_num], if_mt_media_data)
                if not data[0]:
                    logger.error(data[1])
                    data = None
                else:
                    data = data[1]
                if data is not None:
                    info.append(dict(zip(items, [name, desc, data])))
                else:
                    info.append(dict(zip(items, [name, desc, None])))
            elif type_ in ['6', '7', '8', '15', '16', '17']:
                # 主视频/辅视频/音频 有码流
                index = ['6', '7', '8', '15', '16', '17'].index(type_)
                name, desc = _types_detail.get(type_)
                data = self.process_bitrate(type_, bitrate_data[index * conf_time_section_num:(
                    index + 1) * conf_time_section_num], if_mt_media_data)
                if not data[0]:
                    logger.error(data[1])
                    data = None
                else:
                    data = data[1]
                if data is not None:
                    info.append(dict(zip(items, [name, desc, data])))
                else:
                    info.append(dict(zip(items, [name, desc, None])))
        return True, info
