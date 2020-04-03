#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
import jsonpath
from common.es_client import es_client
from copy import deepcopy
from common.timeFormatConverter import utcstr2utctimestamp

logger = logging.getLogger('ops.' + __name__)

dev_dssw_ssrc_dsl = {
    "size": 0, "query": {
        "bool": {
            "must": [
                {
                    "match": {
                        "source.eventid": "EV_DSS_PORT_STATIS_NOTIFY"}}, {
                    "match": {
                        "source.conf_e164": "0001370"}}, {
                    "match": {
                        "source.context.channer.local": 1}}, {
                    "match": {
                        "source.context.channer.id": "0512121880144"}}, {
                    "match": {
                        "source.context.chanee.id": "0001370"}}, {
                    "match": {
                        "source.direct": "up"}}], "must_not": [
                {
                    "match": {
                        "source.rtp_info.statis.ssrc": 0}}], "filter": {
                "range": {
                    "@timestamp": {
                        "gte": 0, "lte": "now"}}}}}, "aggs": {
        "chantype": {
            "terms": {
                "field": "source.context.chan_type.keyword", "size": 10000}, "aggs": {
                "ssrc": {
                    "terms": {
                        "field": "source.rtp_info.statis.ssrc", "size": 10000, "order": {
                            "min_time": "asc"}}, "aggs": {
                        "max_time": {
                            "max": {
                                "field": "@timestamp"}}, "min_time": {
                            "min": {
                                "field": "@timestamp"}}}}}}}}


class QueryDssWorkerSSRC:
    """
    查询 转发 ssrc分布时间段 用于查询媒体上报的会议信息
    """

    def __init__(self, conf_id, mt_e164, start_time, end_time, flow_direction):
        """
        :param flow_direction: 码流方向 up/down
        :param conf_id:
        :param mt_e164:
        :param start_time:
        :param end_time:
        """
        self.flow_direction = flow_direction
        self.conf_id = conf_id
        self.mt_e164 = mt_e164
        self.start_time = start_time
        self.end_time = end_time
        if self.flow_direction not in ['up', 'down']:
            raise ValueError('flow_direction 参数错误')

    def query_ssrc(self):
        """
        查询 转发 ssrc分布时间段 用于查询媒体会议信息
        :return: (true/false) ((dict/none)/err)
        """
        dsl_ = self.make_ssrc_dsl()
        es = es_client()
        index = "platform-nmscollector-*dss*worker*"
        try:
            results = es.search(index=index, dsl=dsl_)
        except Exception as err:
            logger.error(err)
            return False, err.args
        else:
            results = results["aggregations"]["chantype"]["buckets"]

        if len(results) == 0:
            return True, None

        ssrc = {}
        for result in results:
            chan_type = result['key']
            # if chan_type not in self.dss_chan_type:
            #     continue
            cur_ssrc = []
            for info in result["ssrc"]["buckets"]:
                ssrc_key = jsonpath.jsonpath(info, '$..key')
                ssrc_min_time = jsonpath.jsonpath(
                    info, '$..min_time.value_as_string')
                ssrc_max_time = jsonpath.jsonpath(
                    info, '$..max_time.value_as_string')
                if not (ssrc_key and ssrc_min_time and ssrc_max_time):
                    continue
                ssrc_min_time = utcstr2utctimestamp(ssrc_min_time[0])
                ssrc_max_time = utcstr2utctimestamp(ssrc_max_time[0])
                ssrc_key = ssrc_key[0]
                cur_ssrc.append([ssrc_key, ssrc_min_time, ssrc_max_time])
            if len(cur_ssrc) == 0:
                continue
            else:
                ssrc[chan_type] = cur_ssrc
        if len(ssrc) == 0:
            return True, None
        else:
            return True, ssrc

    def make_ssrc_dsl(self):
        """
        构建从dssworker查询ssrc分布的dsl语句
        :return:
        """
        dsl_ = deepcopy(dev_dssw_ssrc_dsl)
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

        # 将过滤条件加入
        must_block.append(
            {"match": {"source.conf_e164": "{}".format(self.conf_id)}})
        # 时间
        dsl_['query']['bool']['filter']['range']['@timestamp'] = {
            "gte": self.start_time, "lte": self.end_time}
        if self.flow_direction == "up":
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
        return dsl_
