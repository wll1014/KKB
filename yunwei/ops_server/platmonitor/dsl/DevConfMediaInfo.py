#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
终端网媒信息, 包括终端上报信息、转发上报信息、媒体上报信息

网口带宽： 进/出 终端上报数据    5min/per
丢包率：
    终端丢包率

码率:
media->frame里面的码率，统一除1024再乘8，单位为kb/s      他原始单位是Bps  目前终端和平台码率用的meida上的
转发上的码率，统一除1024再乘8 单位未kb/s    他原始单位是Bps
medianet上的码率，统一除1024，单位未kb/s   他原始单位是bps

"""

import datetime
import json
import logging
import jsonpath
from django.db import connections
from collections import OrderedDict
from copy import deepcopy
from common.es_client import es_client
from platmonitor.dsl.confPublicFunc import QueryDssWorkerSSRC

from common.conf_params_enum import *

logger = logging.getLogger('ops.' + __name__)

# 支持的请求类型
_allow_types = OrderedDict(
    [('dssworker', '转发'), ('mediaworker', '平台媒体'), ('mt', '终端')])

# 支持的请求的选项
_allow_options = {
    1: '丢包率',
    3: '卡顿次数',
    4: '时延',
    5: '抖动',
    6: '码率',
    7: '帧率',
    8: '网络丢帧',
    9: '媒体丢帧',
    10: '最大帧大小',
    11: '关键帧频率',
    12: '宽/高',
    13: "媒体错误",
    14: "帧总数",
    15: '网口带宽',
}

_type_options = {
    'mt': [1, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14],  # 终端暂不支持查询 网口带宽/抖动
    'dssworker': [6, 1],
    'mediaworker': [1, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14],  # 平套暂不支持查询 抖动
}

# 返回数据点数
_POINTS_NUM = 90

# 转发  码流类型  只关注 chan_type 是这些类型的消息
dss_chan_type = ['video', 'dualvideo', 'audio']
dss_chan_type_desc = {
    'video': '主视频',
    'dualvideo': '辅视频',
    'audio': '音频'
}
# 媒体  码流类型  只关注 media_type 是这些类型的消息
mda_media_type = ['vmp', 'vbas', 'port', 'portbas', 'abas', 'mixer']
mda_media_type_desc = {
    'vmp': "合成",
    'vbas': "适配",
    'port': "端口",
    'portbas': "端口适配",
    'abas': "适配",
    'mixer': "混音"
}

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
                        "gte": 1569396965000,
                        "lte": 1569397565000}}}}},
    "aggs": {
        "date": {
            "date_histogram": {
                "field": "@timestamp",
                "interval": "5m",
                "format": "epoch_millis",
                "min_doc_count": 0,
                "extended_bounds": {
                    "min": 1569396965000,
                    "max": 1569397565000}},
            "aggs": {
                "data": {
                    "max": {
                        "field": "source.rtp_info.qoe.fraction_lost"}}}},
        "max": {
            "max": {
                "field": "@timestamp"}}}}

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
                        "gte": 1569396965000,
                        "lte": 1569397565000}}}}},
    "aggs": {
        "date": {
            "date_histogram": {
                "field": "@timestamp",
                "interval": "5m",
                "format": "epoch_millis",
                "min_doc_count": 0,
                "extended_bounds": {
                    "min": 1569396965000,
                    "max": 1569397565000}},
            "aggs": {
                "data": {
                    "max": {
                        "field": "source.rtp_info.qoe.fraction_lost"}}}},
        "max": {
            "max": {
                "field": "@timestamp"}}}}

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
                                "field": "source.rtp_info.qoe.thruput.pps"}}}},
                "max": {
                    "max": {
                        "field": "@timestamp"}}}}}}

platform_media_dsl = {
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
                                "field": "source.rtp_info.qoe.thruput.pps"}}}},
                "max": {
                    "max": {
                        "field": "@timestamp"}}}}}}

dss_dsl = {"size": 0, "query": {"bool": {
    "must": [{"match": {"source.eventid": "EV_DSS_PORT_STATIS_NOTIFY"}}, {"match": {"source.conf_e164": "0001370"}},
             {"match": {"source.context.channer.local": 1}}, {"match": {"source.context.channer.id": "0512121880144"}},
             {"match": {"source.context.chanee.id": "0001370"}}, {"match": {"source.direct": "up"}},
             {"match": {"source.context.chan_type": "video"}}],
    "filter": {"range": {"@timestamp": {"gte": 1569496991000, "lte": 1569553266081}}}}}, "aggs": {"date": {
    "date_histogram": {"field": "@timestamp", "interval": "1m", "format": "epoch_millis", "min_doc_count": 0,
                       "extended_bounds": {"min": 1569496991000, "max": 1569553266081}},
    "aggs": {"data": {"max": {"field": "source.rtp_info.statis.rtp_lose.lose_percent.cur"}}}}, "max": {
    "max": {"field": "@timestamp"}}}}

dev_bandwidth_dsl = {"size": 0, "query": {"bool": {
    "must": [{"match": {"source.devid": "c3102d7c-bb21-49b3-b7a5-22ff64f0b320"}},
             {"match": {"source.eventid": "EV_BANDWIDTH_MSG"}}],
    "filter": {"range": {"@timestamp": {"gte": "2019-07-18", "lte": "2019-07-19"}}}}}, "aggs": {"2": {
    "date_histogram": {"field": "@timestamp", "interval": "1h", "format": "epoch_millis", "min_doc_count": 0,
                       "extended_bounds": {"min": "1563379200000", "max": "1563465600000"}},
    "aggs": {"1": {"avg": {"field": "source.recv_bandwidth.bandwidth"}}}}}}


def get_options(**kwargs):
    """
    获取网媒类型及类型选项信息
    :return:
    """
    param_keys = ['type', 'description', 'data']
    info = []
    for type_, description in _allow_types.items():
        data = []
        options = _type_options.get(type_)
        for option in options:
            data.append(dict(zip(["option", 'description'], [
                option, _allow_options.get(option)])))
        info.append(dict(zip(param_keys, [type_, description, data])))
    return True, info


def deal_agg_histogram_data(
        data,
        latest_data_time=None,
        start_time=None,
        end_time=None):
    """
    处理聚合数据
    如果 latest_data_time 为None 不做任何改变, 直接返回原始值
    如果 latest_data_time 不为None 则把第一个数据点的时间戳替换成start_time,最后一个数据的时间戳
        替换成latest_data_time,并在末尾追加一个数据点(end_time, None)
    :param end_time: option
    :param start_time: option
    :param latest_data_time: int, unix timestamp
    :param data: list of tuple
    :type data: list
    :return:
    """
    if latest_data_time is None:
        return data
    else:
        if start_time is not None:
            data[0][0] = start_time
        data[-1][0] = latest_data_time

        if end_time is not None and latest_data_time != end_time:
            data.append((end_time, None))
        return data


def media_net_fields_options(op_type):
    """
    MediaNet媒体字段，包括终端侧和平台侧数据

    'down' 即接收->下载
    'up' 即发送-> 上传
    :param op_type:
    """
    option2field = {
        3: ['mt', 'video', 'down', "source.rtp_info.qoe.fraction_lost"],
        4: ['mt', 'dualvideo', 'down', "source.rtp_info.qoe.fraction_lost"],

        5: ['mt', 'video', 'down', "source.rtp_info.qoe.rebuffer"],
        6: ['mt', 'dualvideo', 'down', "source.rtp_info.qoe.rebuffer"],

        7: ['mt', 'video', 'down', "source.rtp_info.qoe.rtt"],
        8: ['mt', 'dualvideo', 'down', "source.rtp_info.qoe.rtt"],

        # 抖动暂无数据
        9: ['mt', 'video', 'down', ""],
        10: ['mt', 'dualvideo', 'down', ""],

        46: ['plfm', 'video', 'down', "source.rtp_info.qoe.fraction_lost"],
        47: ['plfm', 'dualvideo', 'down', "source.rtp_info.qoe.fraction_lost"],

        48: ['plfm', 'video', 'down', "source.rtp_info.qoe.rebuffer"],
        49: ['plfm', 'dualvideo', 'down', "source.rtp_info.qoe.rebuffer"],

        50: ['plfm', 'video', 'down', "source.rtp_info.qoe.rtt"],
        51: ['plfm', 'dualvideo', 'down', "source.rtp_info.qoe.rtt"],

        # 抖动暂无数据
        52: ['plfm', 'video', 'down', ""],
        53: ['plfm', 'dualvideo', 'down', ""],

        # 87: ['mt', 'video', 'up', "source.rtp_info.qoe.fraction_lost"],
        # 88: ['mt', 'dualvideo', 'up', "source.rtp_info.qoe.fraction_lost"],
        #
        # 89: ['mt', 'video', 'up', "source.rtp_info.qoe.rebuffer"],
        # 90: ['mt', 'dualvideo', 'up', "source.rtp_info.qoe.rebuffer"],
        #
        # 91: ['mt', 'video', 'up', "source.rtp_info.qoe.rtt"],
        # 92: ['mt', 'dualvideo', 'up', "source.rtp_info.qoe.rtt"],

        # 终端抖动暂无数据
        # 93: ['mt', 'video', 'up', ""],
        # 94: ['mt', 'dualvideo', 'up', ""],

        # 124: ['plfm', 'video', 'up', "source.rtp_info.qoe.fraction_lost"],
        # 125: ['plfm', 'dualvideo', 'up', "source.rtp_info.qoe.fraction_lost"],
        #
        # 126: ['plfm', 'video', 'up', "source.rtp_info.qoe.rebuffer"],
        # 127: ['plfm', 'dualvideo', 'up', "source.rtp_info.qoe.rebuffer"],
        #
        # 128: ['plfm', 'video', 'up', "source.rtp_info.qoe.rtt"],
        # 129: ['plfm', 'dualvideo', 'up', "source.rtp_info.qoe.rtt"],

        # 平台抖动暂无数据
        # 130: ['plfm', 'video', 'up', ""],
        # 131: ['plfm', 'dualvideo', 'up', ""],
    }
    return option2field.get(op_type, None)


def media_fields_options(op_type):
    """
    Media媒体字段，包括终端侧和平台侧数据

    'down' 即接收->下载
    'up' 即发送-> 上传
    :param op_type:
    """
    option2field = {
        11: ['mt', 'video', 'down', "source.frame.bitrate"],
        12: ['mt', 'dualvideo', 'down', "source.frame.bitrate"],
        95: ['mt', 'audio', 'down', "source.frame.bitrate"],

        13: ['mt', 'video', 'down', "source.frame.fps"],
        14: ['mt', 'dualvideo', 'down', "source.frame.fps"],
        99: ['mt', 'audio', 'down', "source.frame.fps"],

        15: ['mt', 'video', 'down', "source.frame.medianet_lost"],
        16: ['mt', 'dualvideo', 'down', "source.frame.medianet_lost"],
        17: ['mt', 'audio', 'down', "source.frame.medianet_lost"],

        18: ['mt', 'video', 'down', "source.media_lost"],
        19: ['mt', 'dualvideo', 'down', "source.media_lost"],
        20: ['mt', 'audio', 'down', "source.media_lost"],

        21: ['mt', 'video', 'down', "source.frame.max_size"],
        22: ['mt', 'dualvideo', 'down', "source.frame.max_size"],
        23: ['mt', 'audio', 'down', "source.frame.max_size"],

        24: ['mt', 'video', 'down', "source.frame.I_frame_rate"],
        25: ['mt', 'dualvideo', 'down', "source.frame.I_frame_rate"],

        27: ['mt', 'video', 'down', "source.frame.width"],
        28: ['mt', 'dualvideo', 'down', "source.frame.width"],
        29: ['mt', 'video', 'down', "source.frame.height"],
        30: ['mt', 'dualvideo', 'down', "source.frame.height"],

        31: ['mt', 'video', 'down', "source.last_error"],
        32: ['mt', 'dualvideo', 'down', "source.last_error"],
        33: ['mt', 'audio', 'down', "source.last_error"],

        81: ['mt', 'video', 'down', "source.frame.total_frames"],
        82: ['mt', 'dualvideo', 'down', "source.frame.total_frames"],
        83: ['mt', 'audio', 'down', "source.frame.total_frames"],

        54: ['plfm', 'video', 'down', "source.frame.bitrate"],
        55: ['plfm', 'dualvideo', 'down', "source.frame.bitrate"],
        56: ['plfm', 'audio', 'down', "source.frame.bitrate"],

        57: ['plfm', 'video', 'down', "source.frame.fps"],
        58: ['plfm', 'dualvideo', 'down', "source.frame.fps"],
        59: ['plfm', 'audio', 'down', "source.frame.fps"],

        60: ['plfm', 'video', 'down', "source.frame.medianet_lost"],
        61: ['plfm', 'dualvideo', 'down', "source.frame.medianet_lost"],
        62: ['plfm', 'audio', 'down', "source.frame.medianet_lost"],

        63: ['plfm', 'video', 'down', "source.media_lost"],
        64: ['plfm', 'dualvideo', 'down', "source.media_lost"],
        65: ['plfm', 'audio', 'down', "source.media_lost"],

        66: ['plfm', 'video', 'down', "source.frame.max_size"],
        67: ['plfm', 'dualvideo', 'down', "source.frame.max_size"],
        68: ['plfm', 'audio', 'down', "source.frame.max_size"],

        69: ['plfm', 'video', 'down', "source.frame.I_frame_rate"],
        70: ['plfm', 'dualvideo', 'down', "source.frame.I_frame_rate"],

        71: ['plfm', 'video', 'down', "source.frame.width"],
        72: ['plfm', 'dualvideo', 'down', "source.frame.width"],
        73: ['plfm', 'video', 'down', "source.frame.height"],
        74: ['plfm', 'dualvideo', 'down', "source.frame.height"],

        75: ['plfm', 'video', 'down', "source.last_error"],
        76: ['plfm', 'dualvideo', 'down', "source.last_error"],
        77: ['plfm', 'audio', 'down', "source.last_error"],

        84: ['plfm', 'video', 'down', "source.frame.total_frames"],
        85: ['plfm', 'dualvideo', 'down', "source.frame.total_frames"],
        86: ['plfm', 'audio', 'down', "source.frame.total_frames"],

        96: ['mt', 'video', 'up', "source.frame.bitrate"],
        97: ['mt', 'dualvideo', 'up', "source.frame.bitrate"],
        98: ['mt', 'audio', 'up', "source.frame.bitrate"],

        100: ['mt', 'video', 'up', "source.frame.fps"],
        101: ['mt', 'dualvideo', 'up', "source.frame.fps"],
        102: ['mt', 'audio', 'up', "source.frame.fps"],

        103: ['mt', 'video', 'up', "source.frame.medianet_lost"],
        104: ['mt', 'dualvideo', 'up', "source.frame.medianet_lost"],
        105: ['mt', 'audio', 'up', "source.frame.medianet_lost"],

        106: ['mt', 'video', 'up', "source.media_lost"],
        107: ['mt', 'dualvideo', 'up', "source.media_lost"],
        108: ['mt', 'audio', 'up', "source.media_lost"],

        109: ['mt', 'video', 'up', "source.frame.max_size"],
        110: ['mt', 'dualvideo', 'up', "source.frame.max_size"],
        111: ['mt', 'audio', 'up', "source.frame.max_size"],

        112: ['mt', 'video', 'up', "source.frame.I_frame_rate"],
        113: ['mt', 'dualvideo', 'up', "source.frame.I_frame_rate"],

        114: ['mt', 'video', 'up', "source.frame.width"],
        115: ['mt', 'dualvideo', 'up', "source.frame.width"],
        116: ['mt', 'video', 'up', "source.frame.height"],
        117: ['mt', 'dualvideo', 'up', "source.frame.height"],

        118: ['mt', 'video', 'up', "source.last_error"],
        119: ['mt', 'dualvideo', 'up', "source.last_error"],
        120: ['mt', 'audio', 'up', "source.last_error"],

        121: ['mt', 'video', 'up', "source.frame.total_frames"],
        122: ['mt', 'dualvideo', 'up', "source.frame.total_frames"],
        123: ['mt', 'audio', 'up', "source.frame.total_frames"],

        132: ['plfm', 'video', 'up', "source.frame.bitrate"],
        133: ['plfm', 'dualvideo', 'up', "source.frame.bitrate"],
        134: ['plfm', 'audio', 'up', "source.frame.bitrate"],

        135: ['plfm', 'video', 'up', "source.frame.fps"],
        136: ['plfm', 'dualvideo', 'up', "source.frame.fps"],
        137: ['plfm', 'audio', 'up', "source.frame.fps"],

        138: ['plfm', 'video', 'up', "source.frame.medianet_lost"],
        139: ['plfm', 'dualvideo', 'up', "source.frame.medianet_lost"],
        140: ['plfm', 'audio', 'up', "source.frame.medianet_lost"],

        141: ['plfm', 'video', 'up', "source.media_lost"],
        142: ['plfm', 'dualvideo', 'up', "source.media_lost"],
        143: ['plfm', 'audio', 'up', "source.media_lost"],

        144: ['plfm', 'video', 'up', "source.frame.max_size"],
        145: ['plfm', 'dualvideo', 'up', "source.frame.max_size"],
        146: ['plfm', 'audio', 'up', "source.frame.max_size"],

        147: ['plfm', 'video', 'up', "source.frame.I_frame_rate"],
        148: ['plfm', 'dualvideo', 'up', "source.frame.I_frame_rate"],

        149: ['plfm', 'video', 'up', "source.frame.width"],
        150: ['plfm', 'dualvideo', 'up', "source.frame.width"],
        151: ['plfm', 'video', 'up', "source.frame.height"],
        152: ['plfm', 'dualvideo', 'up', "source.frame.height"],

        78: ['plfm', 'video', 'up', "source.last_error"],
        79: ['plfm', 'dualvideo', 'up', "source.last_error"],
        80: ['plfm', 'audio', 'up', "source.last_error"],

        153: ['plfm', 'video', 'up', "source.frame.total_frames"],
        154: ['plfm', 'dualvideo', 'up', "source.frame.total_frames"],
        155: ['plfm', 'audio', 'up', "source.frame.total_frames"],
    }
    return option2field.get(op_type, None)


def dssworker_fields_option(op_type):
    """
    转发侧媒体字段
    :param op_type:
    """
    option2switchfield = {
        34: ['dss', 'video', "up", "source.rtp_info.statis.rtp_lose.lose_percent.cur"],
        35: ['dss', 'dualvideo', "up", "source.rtp_info.statis.rtp_lose.lose_percent.cur"],
        36: ['dss', 'audio', "up", "source.rtp_info.statis.rtp_lose.lose_percent.cur"],
        37: ['dss', 'video', "down", "source.rtp_info.statis.rtp_lose.lose_percent.cur"],
        38: ['dss', 'dualvideo', "down", "source.rtp_info.statis.rtp_lose.lose_percent.cur"],
        39: ['dss', 'audio', "down", "source.rtp_info.statis.rtp_lose.lose_percent.cur"],

        40: ['dss', 'video', "up", "source.rtp_info.statis.udp_pkt.bytes_rate.cur"],
        41: ['dss', 'dualvideo', "up", "source.rtp_info.statis.udp_pkt.bytes_rate.cur"],
        42: ['dss', 'audio', "up", "source.rtp_info.statis.udp_pkt.bytes_rate.cur"],
        43: ['dss', 'video', "down", "source.rtp_info.statis.udp_pkt.bytes_rate.cur"],
        44: ['dss', 'dualvideo', "down", "source.rtp_info.statis.udp_pkt.bytes_rate.cur"],
        45: ['dss', 'audio', "down", "source.rtp_info.statis.udp_pkt.bytes_rate.cur"]
    }
    return option2switchfield.get(op_type, None)


class DevConfMediaInfo:
    """
    查询终端会议网媒相关信息
    """

    def __init__(self, **kwargs):
        self.conf_id = kwargs.get('conf_id')
        self.mt_e164 = kwargs.get('mt_e164')
        self.start_time = kwargs.get('start_time')
        self.end_time = kwargs.get('end_time')
        self.tp = kwargs.get('type')
        self.option = kwargs.get('option')
        self.interval = kwargs.get('interval')
        self.ssrc_up = None
        self.ssrc_down = None
        self.params_init()

    def params_init(self):
        """
        处理异常查询条件
        :return:
        """
        if self.tp is None:
            raise ValueError("type 参数不能为空")
        elif self.tp not in _allow_types:
            raise ValueError("type 参数错误")

        self.start_time = int(self.start_time)

        if self.end_time == ConfEndTimeType.REALTIME.name or self.end_time == ConfEndTimeType.MANUAL.name:
            self.end_time = int(datetime.datetime.now().timestamp() * 1000)
        elif self.end_time == ConfEndTimeType.ABEND.name:
            # 异常结会按会议时长2小时计算
            self.end_time = self.start_time + 7200000
        else:
            self.end_time = int(self.end_time)

        if self.end_time <= self.start_time:
            raise ValueError("time 参数错误")

        if self.interval is None:
            self.interval = str(
                (self.end_time - self.start_time) // _POINTS_NUM) + "ms"
        else:
            self.interval = str(self.interval) + "ms"

        if self.option is None:
            raise ValueError("option 参数不能为空")
        elif self.option not in _type_options.get(self.tp):
            raise ValueError("option 参数错误")

    def query_dev_moid(self):
        """
        根据终端e164号码查询终端moid
        :return:
        """
        sql = "SELECT moid FROM user_info WHERE e164 = %s AND binded='0'"
        with connections['movision'].cursor() as cursor:
            cursor.execute(sql, [self.mt_e164])
            moid = cursor.fetchone()
        if moid is None:
            # 没有查到moid
            return None
        else:
            return moid[0]

    def make_platform_media_net_dsl(self, op_type):
        """
        根据dssworker中查询的ssrc时间段构建 平台侧 medianet 网媒信息dsl语句
        :param op_type: 待查询网媒字段的枚举类型
        :return: None/dsl
        """
        field_key = media_net_fields_options(op_type)
        if field_key is None:
            return None
        else:
            who, media_type, direct, key_field = field_key

        dsl_ = deepcopy(platform_media_net_dsl)

        if direct == "up":
            ssrc = self.ssrc_down
        else:
            ssrc = self.ssrc_up
        if ssrc is None:
            return None

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
        if len(ssrc_info) == 0:
            return None

        # 时间间隔
        dsl_['aggs']['mediatype']['aggs']['date']['date_histogram']['interval'] = self.interval
        dsl_['aggs']['mediatype']['aggs']['date']['date_histogram']['extended_bounds'] = {
            "min": self.start_time, "max": self.end_time}
        # 查询字段
        dsl_['aggs']['mediatype']['aggs']['date']['aggs']['data']['max']['field'] = key_field

        should_block = dsl_['query']['bool']['should']
        for single_ssrc_info in ssrc_info:
            must = []
            must.append(
                {"match": {"source.context.conf_e164": "{}".format(self.conf_id)}})
            must.append(
                {"match": {"source.eventid": "OPS_PLATFORM_MEDIANET_INFO_NOTIFY"}})
            must.append(
                {"match": {"source.rtp_info.ssrc": single_ssrc_info[0]}})
            must.append({"range": {"@timestamp": {
                "gte": single_ssrc_info[1], "lte": single_ssrc_info[2]}}})

            # 1.0 卡顿 后端规避数值过大问题 临时方案
            # if op_type in [5, 6, 48, 49]:
            #     must.append({"range": {key_field: {"lt": 1000}}})

            should = {"bool": {"must": must}}
            should_block.append(should)

        dsl_['query']['bool']['should'] = should_block
        return dsl_

    def make_platform_media_dsl(self, op_type):
        """
        根据dssworker中查询的ssrc时间段构建 平台侧 media 网媒信息dsl语句
        :param op_type: 待查询网媒字段的枚举类型
        :return: None/dsl
        """
        field_key = media_fields_options(op_type)
        if field_key is None:
            return None
        else:
            who, media_type, direct, key_field = field_key

        dsl_ = deepcopy(platform_media_dsl)

        if direct == "up":
            # 平台发送 即 下行
            ssrc = self.ssrc_down
        else:
            # 平台接收 即 上行
            ssrc = self.ssrc_up
        if ssrc is None:
            return None

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
        if len(ssrc_info) == 0:
            return None

        # 时间间隔
        dsl_['aggs']['mediatype']['aggs']['date']['date_histogram']['interval'] = self.interval
        dsl_['aggs']['mediatype']['aggs']['date']['date_histogram']['extended_bounds'] = {
            "min": self.start_time, "max": self.end_time}
        # 查询字段
        dsl_['aggs']['mediatype']['aggs']['date']['aggs']['data']['max']['field'] = key_field

        should_block = dsl_['query']['bool']['should']
        for single_ssrc_info in ssrc_info:
            must = []
            must.append(
                {"match": {"source.context.conf_e164": "{}".format(self.conf_id)}})
            must.append(
                {"match": {"source.eventid": "OPS_PLATFORM_MEDIA_INFO_NOTIFY"}})
            must.append({"match": {"source.frame.ssrc": single_ssrc_info[0]}})
            must.append({"range": {"@timestamp": {
                "gte": single_ssrc_info[1], "lte": single_ssrc_info[2]}}})

            # # 1.0 网络丢帧 后端规避数值过大问题 临时方案
            # if op_type in [15, 16, 17, 60, 61, 62]:
            #     must.append({"range": {key_field: {"lt": 1000}}})
            # # 1.0 码率 后端规避数值过大问题 临时方案
            # elif op_type in [11, 12, 54, 55, 56]:
            #     must.append({"range": {key_field: {"lt": 10000000}}})

            should = {"bool": {"must": must}}
            should_block.append(should)

        dsl_['query']['bool']['should'] = should_block
        return dsl_

    def make_mt_media_net_dsl(self, op_type):
        """
        构建查询终端侧medianet信息的dsl语句
        :param op_type: 待查询网媒字段的枚举类型
        :return: None/dsl
        """
        field_key = media_net_fields_options(op_type)
        if field_key is None:
            return None
        else:
            who, media_type, direct, key_field = field_key

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

        # 1.0 卡顿 后端规避数值过大问题 临时方案
        # if op_type in [5, 6, 48, 49]:
        #     dsl_['query']['bool']['filter'] = [{"range": {key_field: {"lt": 1000}}},
        #                                        {"range": {
        #                                            "@timestamp": {"gte": self.start_time, "lte": self.end_time}}}]
        # else:

        # 时间
        dsl_['query']['bool']['filter']['range']['@timestamp'] = {
            "gte": self.start_time, "lte": self.end_time}

        # 聚合
        # 时间间隔
        dsl_['aggs']['date']['date_histogram']['interval'] = self.interval
        dsl_['aggs']['date']['date_histogram']['extended_bounds'] = {
            "min": self.start_time, "max": self.end_time}
        # 查询字段
        dsl_['aggs']['date']['aggs']['data']['max']['field'] = key_field
        return dsl_

    def make_mt_media_dsl(self, op_type):
        """
        构建查询终端侧media信息的dsl语句
        :param op_type: 待查询网媒字段的枚举类型
        :return: None/dsl
        """
        field_key = media_fields_options(op_type)
        if field_key is None:
            return None
        else:
            who, media_type, direct, key_field = field_key

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

        # # 1.0 网络丢帧 后端规避数值过大问题 临时方案
        # if op_type in [15, 16, 17, 60, 61, 62]:
        #     dsl_['query']['bool']['filter'] = [{"range": {key_field: {"lt": 1000}}},
        #                                        {"range": {
        #                                            "@timestamp": {"gte": self.start_time, "lte": self.end_time}}}]
        # # 1.0 码率 后端规避数值过大问题 临时方案
        # elif op_type in [11, 12, 54, 55, 56]:
        #     dsl_['query']['bool']['filter'] = [{"range": {key_field: {"lt": 10000000}}},
        #                                        {"range": {
        #                                            "@timestamp": {"gte": self.start_time, "lte": self.end_time}}}]
        # else:

        # 时间
        dsl_['query']['bool']['filter']['range']['@timestamp'] = {
            "gte": self.start_time, "lte": self.end_time}

        # 聚合
        # 时间间隔
        dsl_['aggs']['date']['date_histogram']['interval'] = self.interval
        dsl_['aggs']['date']['date_histogram']['extended_bounds'] = {
            "min": self.start_time, "max": self.end_time}
        # 查询字段
        dsl_['aggs']['date']['aggs']['data']['max']['field'] = key_field
        return dsl_

    def make_bandwidth_dsl(self, moid, op_type):
        """
        构建网口带宽查询的dsl语句
        :param op_type: 选项
        :param moid: 终端moid
        :return:
        """
        if op_type == ConfMTMediaInfo.Mt_bond_in:
            field_condiition = "source.recv_bandwidth.bandwidth"
        elif op_type == ConfMTMediaInfo.Mt_bond_out:
            field_condiition = "source.send_bandwidth.bandwidth"
        else:
            return None

        dsl_ = deepcopy(dev_bandwidth_dsl)
        must_block = dsl_['query']['bool']['must']
        # 先将模板中条件删除
        for item in must_block[::-1]:
            if 'source.devid' in item['match']:
                must_block.remove(item)
                break

        # 将moid过滤条件加入
        must_block.append({"match": {"source.devid": "{}".format(moid)}})
        # 时间
        dsl_['query']['bool']['filter']['range']['@timestamp'] = {
            "gte": self.start_time, "lte": self.end_time}
        # 聚合
        dsl_['aggs']['2']['date_histogram']['interval'] = self.interval
        dsl_['aggs']['2']['date_histogram']['extended_bounds'] = {
            "max": self.end_time, "min": self.start_time}
        dsl_['aggs']['2']['aggs']['1']['avg']['field'] = field_condiition
        return dsl_

    def make_dssworker_dsl(self, op_type):
        """
        :param op_type: 查询类型枚举值
        构建转发 丢包率/码率 查询的dsl语句
        从dssworker上报信息中查询
        """

        key = dssworker_fields_option(op_type)
        if key is None:
            return None
        who, media_type, direct, key_word = key

        dsl_ = deepcopy(dss_dsl)

        must_block = dsl_['query']['bool']['must']
        # 先将模板中条件删除
        for item in must_block[::-1]:
            if 'source.conf_e164' in item['match']:
                must_block.remove(item)
                continue
            if 'source.context.channer.id' in item['match']:
                must_block.remove(item)
                continue
            if 'source.context.chanee.id' in item['match']:
                must_block.remove(item)
                continue
            if 'source.direct' in item['match']:
                must_block.remove(item)
                continue
            if 'source.context.chan_type' in item['match']:
                must_block.remove(item)
                continue

        # 将过滤条件加入
        must_block.append(
            {"match": {"source.conf_e164": "{}".format(self.conf_id)}})
        must_block.append(
            {"match": {"source.context.chan_type": "{}".format(media_type)}})
        must_block.append({"exists": {"field": "source.rtp_info"}})
        # 时间
        dsl_['query']['bool']['filter']['range']['@timestamp'] = {
            "gte": self.start_time, "lte": self.end_time}
        # 聚合
        dsl_['aggs']['date']['date_histogram']['interval'] = self.interval
        dsl_['aggs']['date']['date_histogram']['extended_bounds'] = {
            "max": self.end_time, "min": self.start_time}
        dsl_['aggs']['date']['aggs']['data']['max']['field'] = key_word

        # 码流方向
        if direct == "down":
            # 转发发送 即 下行
            must_block.append(
                {"match": {"source.context.channer.id": "{}".format(self.conf_id)}})
            must_block.append(
                {"match": {"source.context.chanee.id": "{}".format(self.mt_e164)}})
            must_block.append({"match": {"source.direct": "down"}})
        else:
            # 转发接收 即 上行
            must_block.append(
                {"match": {"source.context.channer.id": "{}".format(self.mt_e164)}})
            must_block.append(
                {"match": {"source.context.chanee.id": "{}".format(self.conf_id)}})
            must_block.append({"match": {"source.direct": "up"}})

        return dsl_

    def query_bandwidth(self):
        """
        查询网口进出口带宽
        :return:
        """
        # 网口带宽所有数据字段
        options = [ConfMTMediaInfo.Mt_bond_in, ConfMTMediaInfo.Mt_bond_out]

        option = options

        info = []
        param_keys = ['name', 'description', 'data']

        moid = self.query_dev_moid()  # 查询终端moid

        if moid is None:
            return True, info

        m_dsl = ""
        for op in option:
            dsl_ = self.make_bandwidth_dsl(moid, op)
            if dsl_ is None:
                option.remove(op)
                continue
            m_dsl += '{}\n' + json.dumps(dsl_) + '\n'

        if not m_dsl:
            return True, info

        es = es_client()
        index = "platform-nmscollector-*mt*"
        try:
            results = es.msearch(index=index, dsl=m_dsl)
        except Exception as err:
            logger.error(err)
            return False, err.args

        for count, result in enumerate(results['responses']):
            name = option[count].name
            description = ConfMTMediaInfoDesc.get(option[count].value)

            if result['hits']['total'] == 0:
                info.append(dict(zip(param_keys, [name, description, None])))
                continue

            time_key = jsonpath.jsonpath(result, '$.aggregations..key')
            data_val = jsonpath.jsonpath(result, '$.aggregations..value')
            if time_key is False or data_val is False:
                # 没有数据返回None
                info.append(dict(zip(param_keys, [name, description, None])))
                continue

            # latest_data_time = jsonpath.jsonpath(result, '$.aggregations.max.value_as_string')  # 最新的一条数据的的时间戳
            # latest_data_time = utcstr2utctimestamp(latest_data_time[0])
            data = [list(x) for x in zip(time_key, data_val)]
            # data = deal_agg_histogram_data(data, latest_data_time, self.start_time, self.end_time)
            info.append(dict(zip(param_keys, [name, description, data])))
        return True, info

    def query_platform_media_net_conf_info(self, options):
        """
        查询平台侧meidanet上报的会议信息
        :param options:
        :return:
        """
        info = []
        param_keys = ['name', 'description', 'data']

        m_dsl = ""
        for op in options[:]:
            dsl_ = self.make_platform_media_net_dsl(op)
            if dsl_ is None:
                options.remove(op)
                continue
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

        for count, result in enumerate(results['responses']):
            name = options[count].name
            description = ConfMTMediaInfoDesc.get(options[count].value)

            if result['hits']['total'] == 0:
                info.append(dict(zip(param_keys, [name, description, None])))
                continue

            for sig_media_type_result in result['aggregations']['mediatype']['buckets']:
                cur_media_tpye = sig_media_type_result["key"]
                if cur_media_tpye not in mda_media_type:
                    continue

                # name 字段添加媒体合成适配等标识
                cur_media_tpye_name = mda_media_type_desc.get(cur_media_tpye)
                cur_description = description + "-" + cur_media_tpye_name

                time_key = jsonpath.jsonpath(
                    sig_media_type_result, '$.date.buckets..key')
                data_val = jsonpath.jsonpath(
                    sig_media_type_result, '$.date.buckets..value')
                if time_key is False or data_val is False:
                    # 没有数据返回None
                    info.append(
                        dict(zip(param_keys, [name, cur_description, None])))
                    continue
                # medianet上码率统一除1024
                if self.option == 6:
                    data_val = [
                        round(
                            x / 1024,
                            2) if x is not None else None for x in data_val]
                # latest_data_time = jsonpath.jsonpath(sig_media_type_result, '$.max.value_as_string')  # 最新的一条数据的的时间戳
                # latest_data_time = utcstr2utctimestamp(latest_data_time[0])
                data = [list(x) for x in zip(time_key, data_val)]
                # data = deal_agg_histogram_data(data, latest_data_time, self.start_time, self.end_time)
                info.append(
                    dict(zip(param_keys, [name, cur_description, data])))
        return True, info

    def query_platform_media_conf_info(self, options):
        """
        查询平台侧meida上报的会议信息
        :param options:
        :return:
        """
        info = []
        param_keys = ['name', 'description', 'data']

        m_dsl = ""
        for op in options[:]:
            dsl_ = self.make_platform_media_dsl(op)
            if dsl_ is None:
                options.remove(op)
                continue
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

        for count, result in enumerate(results['responses']):
            name = options[count].name
            description = ConfMTMediaInfoDesc.get(options[count].value)

            if result['hits']['total'] == 0:
                info.append(dict(zip(param_keys, [name, description, None])))
                continue

            for sig_media_type_result in result['aggregations']['mediatype']['buckets']:
                cur_media_tpye = sig_media_type_result["key"]
                if cur_media_tpye not in mda_media_type:
                    continue

                # name 字段添加媒体合成适配等标识
                cur_media_tpye_name = mda_media_type_desc.get(cur_media_tpye)
                cur_description = description + "-" + cur_media_tpye_name

                time_key = jsonpath.jsonpath(
                    sig_media_type_result, '$.date.buckets..key')
                data_val = jsonpath.jsonpath(
                    sig_media_type_result, '$.date.buckets..value')
                if time_key is False or data_val is False:
                    # 没有数据返回None
                    info.append(
                        dict(zip(param_keys, [name, cur_description, None])))
                    continue
                # media-frame里码率统一除1024再乘8
                if self.option == 6:
                    data_val = [
                        round(
                            x / 128,
                            2) if x is not None else None for x in data_val]
                # latest_data_time = jsonpath.jsonpath(sig_media_type_result, '$.max.value_as_string')  # 最新的一条数据的的时间戳
                # latest_data_time = utcstr2utctimestamp(latest_data_time[0])
                data = [list(x) for x in zip(time_key, data_val)]
                # data = deal_agg_histogram_data(data, latest_data_time, self.start_time, self.end_time)
                info.append(
                    dict(zip(param_keys, [name, cur_description, data])))
        return True, info

    def query_mt_media_net_conf_info(self, options):
        """
        查询终端侧medianet上报的会议信息
        :param options:
        :return:
        """
        info = []
        param_keys = ['name', 'description', 'data']

        m_dsl = ""
        for op in options[:]:
            dsl_ = self.make_mt_media_net_dsl(op)
            if dsl_ is None:
                options.remove(op)
                continue
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

        for count, result in enumerate(results['responses']):
            name = options[count].name
            description = ConfMTMediaInfoDesc.get(options[count].value)

            if result['hits']['total'] == 0:
                info.append(dict(zip(param_keys, [name, description, None])))
                continue

            time_key = jsonpath.jsonpath(
                result, '$.aggregations.date.buckets..key')
            data_val = jsonpath.jsonpath(
                result, '$.aggregations.date.buckets..value')
            if time_key is False or data_val is False:
                # 没有数据返回None
                info.append(dict(zip(param_keys, [name, description, None])))
                continue
            # medianet上码率统一除1024
            if self.option == 6:
                data_val = [
                    round(
                        x / 1024,
                        2) if x is not None else None for x in data_val]
            # latest_data_time = jsonpath.jsonpath(result, '$.aggregations.max.value_as_string')  # 最新的一条数据的的时间戳
            # latest_data_time = utcstr2utctimestamp(latest_data_time[0])
            data = [list(x) for x in zip(time_key, data_val)]
            # data = deal_agg_histogram_data(data, latest_data_time, self.start_time, self.end_time)
            info.append(dict(zip(param_keys, [name, description, data])))
        return True, info

    def query_mt_media_conf_info(self, options):
        """
        查询终端侧media上报的会议信息
        :param options:
        :return:
        """
        info = []
        param_keys = ['name', 'description', 'data']

        m_dsl = ""
        for op in options[:]:
            dsl_ = self.make_mt_media_dsl(op)
            if dsl_ is None:
                options.remove(op)
                continue
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

        for count, result in enumerate(results['responses']):
            name = options[count].name
            description = ConfMTMediaInfoDesc.get(options[count].value)

            if result['hits']['total'] == 0:
                info.append(dict(zip(param_keys, [name, description, None])))
                continue

            time_key = jsonpath.jsonpath(
                result, '$.aggregations.date.buckets..key')
            data_val = jsonpath.jsonpath(
                result, '$.aggregations.date.buckets..value')
            if time_key is False or data_val is False:
                # 没有数据返回None
                info.append(dict(zip(param_keys, [name, description, None])))
                continue
            # media-frame里码率统一除1024再乘8
            if self.option == 6:
                data_val = [
                    round(
                        x / 128,
                        2) if x is not None else None for x in data_val]
            # latest_data_time = jsonpath.jsonpath(result, '$.aggregations.max.value_as_string')  # 最新的一条数据的的时间戳
            # latest_data_time = utcstr2utctimestamp(latest_data_time[0])
            data = [list(x) for x in zip(time_key, data_val)]
            # data = deal_agg_histogram_data(data, latest_data_time, self.start_time, self.end_time)
            info.append(dict(zip(param_keys, [name, description, data])))
        return True, info

    def query_medianet_conf_info(self, options):
        """
        查询medianet信息， 包括平台侧和终端侧
        :param options:
        :return:
        """
        mt_medianet_options = []
        plfm_medianet_options = []
        for op in options:
            option_inf = media_net_fields_options(op)
            if option_inf is None:
                continue
            else:
                who, media_type, direction, keyword = option_inf

            if who == 'mt':
                # 平台侧
                mt_medianet_options.append(op)
            elif who == 'plfm':
                # 终端侧
                plfm_medianet_options.append(op)
            else:
                continue

        if len(mt_medianet_options) > 0:
            info_mt_medianet = self.query_mt_media_net_conf_info(
                mt_medianet_options)
            if not info_mt_medianet[0]:
                info_mt_medianet = []
            else:
                info_mt_medianet = info_mt_medianet[1]
        else:
            info_mt_medianet = []

        if len(plfm_medianet_options) > 0:
            info_plfm_medianet = self.query_platform_media_net_conf_info(
                plfm_medianet_options)
            if not info_plfm_medianet[0]:
                info_plfm_medianet = []
            else:
                info_plfm_medianet = info_plfm_medianet[1]
        else:
            info_plfm_medianet = []

        result = info_mt_medianet + info_plfm_medianet
        return True, result

    def query_media_conf_info(self, options):
        """
        查询media信息， 包括平台侧和终端侧
        :param options:
        :return:
        """
        mt_media_options = []
        plfm_media_options = []
        for op in options:
            option_inf = media_fields_options(op)
            if option_inf is None:
                continue
            else:
                who, media_type, direction, keyword = option_inf

            if who == 'mt':
                # 平台侧
                mt_media_options.append(op)
            elif who == 'plfm':
                # 终端侧
                plfm_media_options.append(op)
            else:
                continue

        if len(mt_media_options) > 0:
            info_mt_media = self.query_mt_media_conf_info(mt_media_options)
            if not info_mt_media[0]:
                info_mt_media = []
            else:
                info_mt_media = info_mt_media[1]
        else:
            info_mt_media = []

        if len(plfm_media_options) > 0:
            info_plfm_media = self.query_platform_media_conf_info(
                plfm_media_options)
            if not info_plfm_media[0]:
                info_plfm_media = []
            else:
                info_plfm_media = info_plfm_media[1]
        else:
            info_plfm_media = []

        result = info_mt_media + info_plfm_media
        return True, result

    def query_platform_conf_info(self):
        """
        查询平台上报会议数据
        :return:
        """
        option_choose = {
            # 丢包率
            1: [ConfMTMediaInfo.PlfmMedianet_recv_privideo_loss_rate,
                ConfMTMediaInfo.PlfmMedianet_recv_assvideo_loss_rate,
                # ConfMTMediaInfo.PlfmMedianet_send_privideo_loss_rate,
                # ConfMTMediaInfo.PlfmMedianet_send_assvideo_loss_rate
                ],
            # 卡顿次数
            3: [ConfMTMediaInfo.PlfmMedianet_recv_privideo_rebuffer,
                ConfMTMediaInfo.PlfmMedianet_recv_assvideo_rebuffer,
                # ConfMTMediaInfo.PlfmMedianet_send_privideo_rebuffer,
                # ConfMTMediaInfo.PlfmMedianet_send_assvideo_rebuffer
                ],
            # 时延
            4: [ConfMTMediaInfo.PlfmMedianet_recv_privideo_rtt,
                ConfMTMediaInfo.PlfmMedianet_recv_assvideo_rtt,
                # ConfMTMediaInfo.PlfmMedianet_send_privideo_rtt,
                # ConfMTMediaInfo.PlfmMedianet_send_assvideo_rtt
                ],
            # 抖动
            5: [ConfMTMediaInfo.PlfmMedianet_recv_video_shake,
                ConfMTMediaInfo.PlfmMedianet_recv_dualvideo_shake,
                # ConfMTMediaInfo.PlfmMedianet_send_video_shake,
                # ConfMTMediaInfo.PlfmMedianet_send_dualvideo_shake
                ],
            # 码率
            6: [ConfMTMediaInfo.PlfmMedia_recv_privideo_bitrate,
                ConfMTMediaInfo.PlfmMedia_recv_assvideo_bitrate,
                ConfMTMediaInfo.PlfmMedia_recv_audio_bitrate,
                ConfMTMediaInfo.PlfmMedia_send_privideo_bitrate,
                ConfMTMediaInfo.PlfmMedia_send_assvideo_bitrate,
                ConfMTMediaInfo.PlfmMedia_send_audio_bitrate
                ],
            # 帧率
            7: [ConfMTMediaInfo.PlfmMedia_recv_privideo_framerate,
                ConfMTMediaInfo.PlfmMedia_recv_assvideo_framerate,
                ConfMTMediaInfo.PlfmMedia_recv_audio_framerate,
                ConfMTMediaInfo.PlfmMedia_send_privideo_framerate,
                ConfMTMediaInfo.PlfmMedia_send_assvideo_framerate,
                ConfMTMediaInfo.PlfmMedia_send_audio_framerate
                ],
            # 网络丢帧
            8: [ConfMTMediaInfo.PlfmMedia_recv_privideo_medianet_lost,
                ConfMTMediaInfo.PlfmMedia_recv_assvideo_medianet_lost,
                ConfMTMediaInfo.PlfmMedia_recv_audio_medianet_lost,
                # ConfMTMediaInfo.PlfmMedia_send_privideo_medianet_lost,
                # ConfMTMediaInfo.PlfmMedia_send_assvideo_medianet_lost,
                # ConfMTMediaInfo.PlfmMedia_send_audio_medianet_lost
                ],
            # 媒体丢帧
            9: [ConfMTMediaInfo.PlfmMedia_recv_privideo_media_lost,
                ConfMTMediaInfo.PlfmMedia_recv_assvideo_media_lost,
                ConfMTMediaInfo.PlfmMedia_recv_audio_media_lost,
                # ConfMTMediaInfo.PlfmMedia_send_privideo_media_lost,
                # ConfMTMediaInfo.PlfmMedia_send_assvideo_media_lost,
                # ConfMTMediaInfo.PlfmMedia_send_audio_media_lost
                ],
            # 最大帧大小
            10: [ConfMTMediaInfo.PlfmMedia_recv_privideo_max_size,
                 ConfMTMediaInfo.PlfmMedia_recv_assvideo_max_size,
                 ConfMTMediaInfo.PlfmMedia_recv_audio_max_size,
                 ConfMTMediaInfo.PlfmMedia_send_privideo_max_size,
                 ConfMTMediaInfo.PlfmMedia_send_assvideo_max_size,
                 ConfMTMediaInfo.PlfmMedia_send_audio_max_size
                 ],
            # 关键帧频率
            11: [ConfMTMediaInfo.PlfmMedia_recv_privideo_fps,
                 ConfMTMediaInfo.PlfmMedia_recv_assvideo_fps,
                 ConfMTMediaInfo.PlfmMedia_send_privideo_fps,
                 ConfMTMediaInfo.PlfmMedia_send_assvideo_fps
                 ],
            # 宽/高
            12: [ConfMTMediaInfo.PlfmMedia_recv_privideo_width,
                 ConfMTMediaInfo.PlfmMedia_recv_assvideo_width,
                 ConfMTMediaInfo.PlfmMedia_recv_privideo_height,
                 ConfMTMediaInfo.PlfmMedia_recv_assvideo_height,
                 ConfMTMediaInfo.PlfmMedia_send_privideo_width,
                 ConfMTMediaInfo.PlfmMedia_send_assvideo_width,
                 ConfMTMediaInfo.PlfmMedia_send_privideo_height,
                 ConfMTMediaInfo.PlfmMedia_send_assvideo_height
                 ],
            # 媒体错误
            13: [ConfMTMediaInfo.PlfmMedia_recv_privideo_last_error,
                 ConfMTMediaInfo.PlfmMedia_recv_assvideo_last_error,
                 ConfMTMediaInfo.PlfmMedia_recv_audio_last_error,
                 ConfMTMediaInfo.PlfmMedia_send_privideo_last_error,
                 ConfMTMediaInfo.PlfmMedia_send_assvideo_last_error,
                 ConfMTMediaInfo.PlfmMedia_send_audio_last_error
                 ],
            # 帧总数
            14: [ConfMTMediaInfo.PlfmMedia_recv_privideo_total_frames,
                 ConfMTMediaInfo.PlfmMedia_recv_assvideo_total_frames,
                 ConfMTMediaInfo.PlfmMedia_recv_audio_total_frames,
                 ConfMTMediaInfo.PlfmMedia_send_privideo_total_frames,
                 ConfMTMediaInfo.PlfmMedia_send_assvideo_total_frames,
                 ConfMTMediaInfo.PlfmMedia_send_audio_total_frames
                 ]
        }

        option = option_choose.get(self.option)

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

        # if self.option == 13:
        # 查询转发下行码流ssrc
        ssrc_down = QueryDssWorkerSSRC(self.conf_id, self.mt_e164, self.start_time, self.end_time,
                                       'down').query_ssrc()
        if not ssrc_down[0]:
            # 查询ssrc失败
            return ssrc_down
        elif ssrc_down[1] is None:
            # ssrc为空
            pass
        else:
            self.ssrc_down = ssrc_down[1]

        if self.option in [1, 3, 4, 5]:
            info_media = self.query_medianet_conf_info(option)
        else:
            info_media = self.query_media_conf_info(option)

        if not info_media[0]:
            info_media = []
        else:
            info_media = info_media[1]

        return True, info_media

    def query_mt_conf_info(self):
        """
        查询终端上报会议数据
        :return:
        """
        option_choose = {
            # 丢包率
            1: [ConfMTMediaInfo.MtMedianet_recv_privideo_loss_rate,
                ConfMTMediaInfo.MtMedianet_recv_assvideo_loss_rate,
                # ConfMTMediaInfo.MtMedianet_send_privideo_loss_rate,
                # ConfMTMediaInfo.MtMedianet_send_assvideo_loss_rate
                ],
            # 卡顿次数
            3: [ConfMTMediaInfo.MtMedianet_recv_video_rebuffer,
                ConfMTMediaInfo.MtMedianet_recv_dualvideo_rebuffer,
                # ConfMTMediaInfo.MtMedianet_send_video_rebuffer,
                # ConfMTMediaInfo.MtMedianet_send_dualvideo_rebuffer
                ],
            # 时延
            4: [ConfMTMediaInfo.MtMedianet_recv_video_rtt,
                ConfMTMediaInfo.MtMedianet_recv_dualvideo_rtt,
                # ConfMTMediaInfo.MtMedianet_send_video_rtt,
                # ConfMTMediaInfo.MtMedianet_send_dualvideo_rtt
                ],
            # 抖动
            5: [ConfMTMediaInfo.MtMedianet_recv_video_shake,
                ConfMTMediaInfo.MtMedianet_recv_dualvideo_shake,
                # ConfMTMediaInfo.MtMedianet_send_video_shake,
                # ConfMTMediaInfo.MtMedianet_send_dualvideo_shake
                ],
            # 码率
            6: [ConfMTMediaInfo.MtMedia_recv_privideo_bitrate,
                ConfMTMediaInfo.MtMedia_recv_assvideo_bitrate,
                ConfMTMediaInfo.MtMedia_recv_audio_bitrate,
                # ConfMTMediaInfo.MtMedia_send_privideo_bitrate,
                # ConfMTMediaInfo.MtMedia_send_assvideo_bitrate,
                # ConfMTMediaInfo.MtMedia_send_audio_bitrate
                ],
            # 帧率
            7: [ConfMTMediaInfo.MtMedia_recv_privideo_framerate,
                ConfMTMediaInfo.MtMedia_recv_assvideo_framerate,
                ConfMTMediaInfo.MtMedia_recv_audio_framerate,
                # ConfMTMediaInfo.MtMedia_send_privideo_framerate,
                # ConfMTMediaInfo.MtMedia_send_assvideo_framerate,
                # ConfMTMediaInfo.MtMedia_send_audio_framerate,
                ],
            # 网络丢帧
            8: [ConfMTMediaInfo.MtMedia_recv_video_medianet_lost,
                ConfMTMediaInfo.MtMedia_recv_dualvideo_medianet_lost,
                ConfMTMediaInfo.MtMedia_recv_audio_medianet_lost,
                # ConfMTMediaInfo.MtMedia_send_video_medianet_lost,
                # ConfMTMediaInfo.MtMedia_send_dualvideo_medianet_lost,
                # ConfMTMediaInfo.MtMedia_send_audio_medianet_lost
                ],
            # 媒体丢帧
            9: [ConfMTMediaInfo.MtMedia_recv_video_media_lost,
                ConfMTMediaInfo.MtMedia_recv_dualvideo_media_lost,
                ConfMTMediaInfo.MtMedia_recv_audio_media_lost,
                # ConfMTMediaInfo.MtMedia_send_video_media_lost,
                # ConfMTMediaInfo.MtMedia_send_dualvideo_media_lost,
                # ConfMTMediaInfo.MtMedia_send_audio_media_lost
                ],
            # 最大帧大小
            10: [ConfMTMediaInfo.MtMedia_recv_video_max_size,
                 ConfMTMediaInfo.MtMedia_recv_dualvideo_max_size,
                 ConfMTMediaInfo.MtMedia_recv_audio_max_size,
                 # ConfMTMediaInfo.MtMedia_send_video_max_size,
                 # ConfMTMediaInfo.MtMedia_send_dualvideo_max_size,
                 # ConfMTMediaInfo.MtMedia_send_audio_max_size
                 ],
            # 关键帧频率
            11: [ConfMTMediaInfo.MtMedia_recv_video_fps,
                 ConfMTMediaInfo.MtMedia_recv_dualvideo_fps,
                 # ConfMTMediaInfo.MtMedia_send_video_fps,
                 # ConfMTMediaInfo.MtMedia_send_dualvideo_fps
                 ],
            # 宽/高
            12: [ConfMTMediaInfo.MtMedia_recv_privideo_width,
                 ConfMTMediaInfo.MtMedia_recv_assvideo_width,
                 ConfMTMediaInfo.MtMedia_recv_privideo_height,
                 ConfMTMediaInfo.MtMedia_recv_assvideo_height,
                 # ConfMTMediaInfo.MtMedia_send_privideo_width,
                 # ConfMTMediaInfo.MtMedia_send_assvideo_width,
                 # ConfMTMediaInfo.MtMedia_send_privideo_height,
                 # ConfMTMediaInfo.MtMedia_send_assvideo_height
                 ],
            # 媒体错误
            13: [ConfMTMediaInfo.MtMedia_recv_video_last_error,
                 ConfMTMediaInfo.MtMedia_recv_dualvideo_last_error,
                 ConfMTMediaInfo.MtMedia_recv_audio_last_error,
                 # ConfMTMediaInfo.MtMedia_send_video_last_error,
                 # ConfMTMediaInfo.MtMedia_send_dualvideo_last_error,
                 # ConfMTMediaInfo.MtMedia_send_audio_last_error
                 ],
            # 帧总数
            14: [ConfMTMediaInfo.MtMedia_recv_video_total_frames,
                 ConfMTMediaInfo.MtMedia_recv_dualvideo_total_frames,
                 ConfMTMediaInfo.MtMedia_recv_audio_total_frames,
                 # ConfMTMediaInfo.MtMedia_send_video_total_frames,
                 # ConfMTMediaInfo.MtMedia_send_dualvideo_total_frames,
                 # ConfMTMediaInfo.MtMedia_send_audio_total_frames
                 ],
            # 网口带宽
            15: [ConfMTMediaInfo.Mt_bond_in,
                 ConfMTMediaInfo.Mt_bond_out],
        }

        option = option_choose.get(self.option)

        if self.option in [1, 3, 4, 5]:
            info_media = self.query_medianet_conf_info(option)
        elif self.option == 15:
            info_media = self.query_bandwidth()
        else:
            info_media = self.query_media_conf_info(option)

        if not info_media[0]:
            info_media = []
        else:
            info_media = info_media[1]

        return True, info_media

    def query_dssworker_conf_info(self):
        """
        查询转发上报会议数据
        :return:
        """
        option_choose = {
            # 丢包率
            1: [ConfMTMediaInfo.Dss_send_video_loss_rate,
                ConfMTMediaInfo.Dss_send_dualvideo_loss_rate,
                ConfMTMediaInfo.Dss_send_audio_loss_rate,
                ConfMTMediaInfo.Dss_recv_video_loss_rate,
                ConfMTMediaInfo.Dss_recv_dualvideo_loss_rate,
                ConfMTMediaInfo.Dss_recv_audio_loss_rate],
            # 码率
            6: [ConfMTMediaInfo.Dss_send_video_bitrate,
                ConfMTMediaInfo.Dss_send_dualvideo_bitrate,
                ConfMTMediaInfo.Dss_send_audio_bitrate,
                ConfMTMediaInfo.Dss_recv_video_bitrate,
                ConfMTMediaInfo.Dss_recv_dualvideo_bitrate,
                ConfMTMediaInfo.Dss_recv_audio_bitrate]
        }

        option = option_choose.get(self.option)

        info = []
        param_keys = ['name', 'description', 'data']

        m_dsl = ""
        for op in option[:]:
            dsl_ = self.make_dssworker_dsl(op)
            if dsl_ is None:
                option.remove(op)
                continue
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

        for count, result in enumerate(results['responses']):
            name = option[count].name
            description = ConfMTMediaInfoDesc.get(option[count].value)

            if result['hits']['total'] == 0:
                info.append(dict(zip(param_keys, [name, description, None])))
                continue

            time_key = jsonpath.jsonpath(
                result, '$.aggregations.date.buckets..key')
            data_val = jsonpath.jsonpath(
                result, '$.aggregations.date.buckets..value')
            if time_key is False or data_val is False:
                # 没有数据返回None
                info.append(dict(zip(param_keys, [name, description, None])))
                continue
            # 转发上码率统一除1024再乘8
            if self.option == 6:
                data_val = [
                    round(
                        x / 128,
                        2) if x is not None else None for x in data_val]
            # latest_data_time = jsonpath.jsonpath(result, '$.aggregations.max.value_as_string')  # 最新的一条数据的的时间戳
            # latest_data_time = utcstr2utctimestamp(latest_data_time[0])
            data = [list(x) for x in zip(time_key, data_val)]
            # data = deal_agg_histogram_data(data, latest_data_time, self.start_time, self.end_time)
            info.append(dict(zip(param_keys, [name, description, data])))
        return True, info

    def get_data(self):
        if self.tp == 'mt':
            # 终端上报数据
            info = self.query_mt_conf_info()
        elif self.tp == "dssworker":
            # 平台转发上报数据
            info = self.query_dssworker_conf_info()
        elif self.tp == "mediaworker":
            # 平台媒体上报数据
            info = self.query_platform_conf_info()
        else:
            info = False, "请求类型错误"
        return info
