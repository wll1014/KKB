#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

import logging
import math
import json
import time
import copy
from enum import Enum, unique

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q, A
from elasticsearch_dsl.response import Response
from elasticsearch.client.utils import query_params

from common.global_func import get_conf
from common.my_exception import OpsException

logger = logging.getLogger('ops.' + __name__)

hosts = get_conf('elasticsearch', 'hosts')
port = get_conf('elasticsearch', 'port')
timeout = get_conf('elasticsearch', 'timeout')
max_retries = get_conf('elasticsearch', 'max_retries')


class MyElastic(Elasticsearch):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields_dic = {
            'cpu': [
                'system.cpu.total.pct',
                'system.cpu.idle.pct',
                'system.cpu.iowait.pct',
                'system.cpu.irq.pct',
                'system.cpu.nice.pct',
                'system.cpu.softirq.pct',
                'system.cpu.steal.pct',
                'system.cpu.system.pct',
                'system.cpu.user.pct',
                'system.cpu.cores'
            ],
            'core': [
                'system.core.system.pct',
                'system.core.idle.pct',
                'system.core.softirq.pct',
                'system.core.iowait.pct',
                'system.core.user.pct',
                'system.core.steal.pct',
                'system.core.nice.pct',
                'system.core.irq.pct',
            ],
            'memory': [
                'system.memory.total',
                'system.memory.actual.free',
                'system.memory.actual.used.bytes',
                'system.memory.actual.used.pct'
            ],
            'load': [
                'system.load.1',
                'system.load.5',
                'system.load.15'
            ],
            'filesystem': [
                'system.filesystem.free',
                'system.filesystem.used.bytes',
                'system.filesystem.used.pct',
                'system.filesystem.total'
            ],
            'diskage': [
                'system.diskage.count'
            ],
            'network': [
                'system.network.in.bytes',
                'system.network.out.bytes'
            ],
            'uptime': [
                'system.uptime.duration.ms'
            ]
        }

    def get_start_time(self, start_time):
        '''
        将开始时间向下取整
        :param start_time: ms级开始时间
        :return: ms级时间
        '''
        return round(round(start_time) / 10000) * 10000

    def get_end_time(self, end_time):
        '''
        将结束时间向上取整
        :param end_time: ms级结束时间
        :return: ms级时间
        '''
        return math.ceil(round(end_time) / 10000) * 10000

    def get_interval_time(self, start_time, end_time=time.time()*1000, point=90):
        '''
        输入时间范围，返回时间间隔 ms级
        :param start_time:ms级开始时间utc时间戳
        :param end_time: ms级结束时间utc时间戳
        :return: ms级时间间隔
        '''
        try:
            start_time, end_time = float(start_time), float(end_time)
        except:
            pass
        if not (isinstance(start_time, (float, int)) and isinstance(end_time, (float, int))):
            logger.error('time must be a digital type %s %s' % (start_time, end_time))
            raise OpsException(code='10010')
        elif end_time < start_time:
            logger.error('end_time must greater than start_time %s %s' % (start_time, end_time))
            raise OpsException(code='10010')
        interval_time = str(round((self.get_end_time(end_time) - self.get_start_time(start_time)) // point / 10) * 10)
        if int(interval_time) < 10000:
            interval_time = '10000'

        return interval_time + 'ms'

    def get_time_info(self, request):
        '''
        获取开始、结束时间，及时间间隔
        :param request:
        :return:
        '''
        if request.query_params.get('start_time') and request.query_params.get('end_time'):
            start_time = request.query_params.get('start_time')
            end_time = request.query_params.get('end_time')
            try:
                start_time = int(start_time)
                end_time = int(end_time)
                interval = self.get_interval_time(start_time, end_time)
            except Exception as e:
                start_time = 'now-24h/m'
                end_time = 'now/m'
                interval = '960000ms'
                logger.warning(str(e))
        else:
            # 默认返回最近24h的数据，时间间隔为960000ms
            start_time = 'now-24h/m'
            end_time = 'now/m'
            interval = '960000ms'

        if request.query_params.get('interval'):
            interval = request.query_params.get('interval')

        return start_time, end_time, interval

    def get_es_data(self, request, es_client, _query, _filter, _aggs,
                    _sort=None, _source=None, _size=10, index='metricbeat-*', doc_type='doc', *args, **kwargs):
        '''
        生成dsl查询语句并执行es的查询
        :param request: 请求对象
        :param es_client: es客户端对象
        :param _query: query过滤条件
        :param _filter: filter过滤条件
        :param _aggs: 聚合查询条件,包含'bucket'和'metric'两个列表的字典
        :param _sort: 是否倒序
        :param _size: 返回hits的数量
        :param index: es中的索引名称，默认为'metricbeat-*'
        :param doc_type: es中的文档类型名称，默认为'doc'
        :param args:
        :param kwargs:
        :return: 查询es得到的Response对象
        '''
        s = Search(using=es_client, index=index)

        '''
        参数数据格式：
        _filter = [
            ['range', {'@timestamp': {"gte": "now-24h/m", "lte": "now/m"}}]
        ]
        _query = [
            ['match', {'metricset.name': 'cpu'}],
            ['match', {'beat.machine_moid': '9ef403ca-0f04-11e9-b9f7-a3f569b0ab2b'}]
        ]
        _aggs = [
            {
                'bucket': ['by_time', 'date_histogram', {'field': '@timestamp', 'interval': '360000ms', 'time_zone': '+08:00', 'format': 'yyyy-MM-dd HH:mm:ss', 'min_doc_count': 0}], 
                'metric': [
                    ['system_cpu_total_pct', 'avg', {'field': 'system.cpu.total.pct'}],
                    ['system_cpu_idle_pct', 'avg', {'field': 'system.cpu.idle.pct'}],
                    ]
                'pipeline': []
            }
        ]
        '''

        try:
            for f in _filter:
                s = s.filter(f[0], **f[1])
            for q in _query:
                s = s.query(q[0], **q[1])

            for a in _aggs:
                if a['bucket']:
                    s.aggs.bucket(a['bucket'][0], a['bucket'][1], **a['bucket'][2])
                    for m in a['metric']:
                        s.aggs[a['bucket'][0]].metric(m[0], m[1], **m[2])
                    for p in a['pipeline']:
                        s.aggs[a['bucket'][0]].pipeline(p[0], p[1], **p[2])
                else:
                    for m in a['metric']:
                        s.aggs.metric(m[0], m[1], **m[2])

            if _sort:
                s = s.sort(_sort)

            if _source:
                s = s.source(_source)

            s = s[0:_size]
        except Exception as e:
            logger.error(str(e))

        '''
                s = Search(using=es_client, index='metricbeat-*') \
                    .filter('range',**{'@timestamp':{"gte": "now-24h/m", "lte": "now/m"}}) \
                    .query('match', **{'metricset.name': 'cpu'}) \
                    .query('match', **{'beat.machine_moid': '9ef403ca-0f04-11e9-b9f7-a3f569b0ab2b'}) \

                s.aggs.bucket('by_time','date_histogram', **{
                                "field": "@timestamp",
                                "interval": "360000ms",
                                "time_zone": "+08:00",
                                "format": "yyyy-MM-dd HH:mm:ss",
                                "min_doc_count": 0
                            }).metric('total_pct','avg',field='system.cpu.total.pct') \
                            .metric('idle_pct', 'avg', field='system.cpu.idle.pct')
            上述对象操作可生成如下dsl语句
            >>
                {
                    "query": {
                        "bool": {
                            "filter": [
                                {
                                    "range": {
                                        "@timestamp": {
                                            "gte": "now-24h/m",
                                            "lte": "now/m"
                                        }
                                    }
                                }
                            ],
                            "must": [
                                {
                                    "match": {
                                        "metricset.name": "cpu"
                                    }
                                },
                                {
                                    "match": {
                                        "beat.machine_moid": "9ef403ca-0f04-11e9-b9f7-a3f569b0ab2b"
                                    }
                                }
                            ]
                        }
                    },
                    "aggs": {
                        "by_time": {
                            "date_histogram": {
                                "field": "@timestamp",
                                "interval": "360000ms",
                                "time_zone": "+08:00",
                                "format": "yyyy-MM-dd HH:mm:ss",
                                "min_doc_count": 0
                            },
                            "aggs": {
                                "total_pct": {
                                    "avg": {
                                        "field": "system.cpu.total.pct"
                                    }
                                },
                                "idle_pct": {
                                    "avg": {
                                        "field": "system.cpu.idle.pct"
                                    }
                                }
                            }
                        }
                    },
                    "from": 0,
                    "size": 0
                }
        '''
        logger.debug('dsl_body: %s' % json.dumps(s.to_dict()))
        try:
            response = s.execute()
        except Exception as e:
            logger.error(str(e))
            return None
        return response

    @query_params('_source', '_source_exclude', '_source_include',
                  'allow_no_indices', 'allow_partial_search_results', 'analyze_wildcard',
                  'analyzer', 'batched_reduce_size', 'default_operator', 'df',
                  'docvalue_fields', 'expand_wildcards', 'explain', 'from_',
                  'ignore_unavailable', 'lenient', 'max_concurrent_shard_requests',
                  'pre_filter_shard_size', 'preference', 'q', 'request_cache', 'routing',
                  'scroll', 'search_type', 'size', 'sort', 'stats', 'stored_fields',
                  'suggest_field', 'suggest_mode', 'suggest_size', 'suggest_text',
                  'terminate_after', 'timeout', 'track_scores', 'track_total_hits',
                  'typed_keys', 'version')
    def search(self, index='platform-nmscollector-*', body=None, params=None):
        return super().search(index=index, body=body, params=params)

    def get_m_body(self, *args):
        m_body = '{}\n'
        for index, value in enumerate(args):
            m_body += json.dumps(value)
            if index == len(args) - 1:
                m_body += '\n'
            else:
                m_body += '\n{}\n'
        return m_body

    def get_index_header_m_body(self, *args):
        m_body = ''
        for args_index, arg in enumerate(args):
            index = arg['index']
            body = arg['dsl']
            if index == len(args) - 1:
                m_body += '\n'
            else:
                m_body += '%s\n%s\n' % (json.dumps({'index': index}), json.dumps(body))
        return m_body

    def get_every_time_dsls(self, base_dsl, start_time, end_time, interval, infos):
        '''
        用于非实时上报数据，生成绘制曲线图的dsl，并将时间戳写入返回信息的info['data']
        :param base_dsl: 基础dsl
        :param start_time: 开始时间
        :param end_time: 结束时间
        :param interval: 间隔时间
        :param infos: 多个返回信息info组成的列表infos
        :return: 每个数据点获取数据的dsl组成的列表dsls, 多个返回信息info组成的列表infos
        '''
        dsls = []
        curr_time = int(end_time)
        timestamps = [curr_time]
        while True:
            curr_time -= int(interval.split('ms')[0])
            timestamps.append(curr_time)
            if curr_time <= int(start_time):
                break
        timestamps.sort()
        for timestamp in timestamps:
            tmp_dsl = copy.deepcopy(base_dsl)
            tmp_dsl['dsl']['query']['bool']['filter'] = {
                "range": {
                    "@timestamp": {
                        "lte": timestamp
                    }
                }
            }
            dsls.append(tmp_dsl)
            for info in infos:
                info['data'].append([timestamp])

        return dsls, infos


hosts_list = ({'host': host, 'port': port} for host in hosts.split(','))
es_client = MyElastic(
    hosts_list,
    http_compress=True,  # http_compress请求压缩
    timeout=timeout,  # 请求超时时间，官方默认为10
    max_retries=max_retries  # 最大重试次数，官方默认为3
)


@unique
class ESIndex(Enum):
    # beat数据索引
    MetricBeatIndex = "metricbeat-*"
    SIPProtoIndex = "packetbeat-*"
    H323ProtoIndex = "platform-ads.h323-*"
    # 日志数据索引
    APPLogIndex = "log-*"
    # watcher数据索引
    UpuWatcherIndex = "upuwatcher-*"
    MQWatcherIndex = "mqwatcher-*"
    RedisWatcherIndex = "rediswatcher-*"
    # 网管数据索引
    NMSMTIndex = "platform-*mt*"
    NMSPasIndex = "platform-*pas*"
    NMSRmsIndex = "platform-*rms*"
    NMSMediaIndex = "platform-*media*"
    NMSMpsIndex = "platform-*mps*"
    NMSVrsIndex = "platform-*vrs*"
    NMSDcsIndex = "platform-*dcs*"
    NMSCmuIndex = "platform-*cmu*"
    NMSDssMasterIndex = "platform-*dss*master*"
    NMSDssWorkerIndex = "platform-*dss*worker*"
    MachineIndex = "machine-*"
    # 流计算特殊逻辑处理数据索引
    AdsPasP2PIndex = "platform-ads.nms.pas-p2p-meeting*"
    # nginx日志数据索引
    NGINXIndex = "nginx-*"
