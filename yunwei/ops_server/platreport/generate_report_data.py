#!/usr/bin/env python3
# coding: utf-8
import requests

__author__ = 'wanglei_sxcpx@kedacom.com'
import os
import re
import logging
import datetime
import json
import jsonpath
import copy

import django
from rest_framework.request import HttpRequest
from django.utils.timezone import get_current_timezone
from django.db import connections, close_old_connections
from django.db.models import Count

from common.my_elastic import MyElastic, hosts, port
from platreport.dsl import es_ql
from platmonitor.dsl.es_query import ConfQuality, MtVideoResolutionRedisDesc

os.environ['DJANGO_SETTINGS_MODULE'] = 'ops.settings'
django.setup()
logger = logging.getLogger('ops_info.' + __name__)

from ops_statistics.views import CompanyInfo, TerminalInfo, ConfResourcesStatistics, ConfTime
from platmonitor.views import ConferencesQuality
from warning.models import ServerWarningRepairedModel, ServerWarningUnrepairedModel, \
    TerminalWarningRepairedModel, TerminalWarningUnrepairedModel
from platreport.platreport_serializer.platreport_serializer import DailyReportSerializers, DailyReportModel


class ReportDateGenerator:
    platform_report_type = [
        'machine_num',  # 服务器数量统计
        'machine_type',  # 服务器类型统计
    ]
    conference_report_type = [
        'concurrent_confs_peak_num',  # 会议并发峰值
        'total_confs',  # 会议总数
        'bad_experience_top_confs',  # 会议体验最差 top会议
        'conf_quality',  # 会议质量饼图
        'conf_time',  # 会议时长饼图
        'conf_resolution',  # 会议码率帧率类型饼图
    ]
    resource_report_type = [
        'media_resource',  # 媒体资源
        'transmit_resource',  # 转发资源
    ]
    terminals_report_type = [
        'online_terminals_peak_num',  # 终端在线数量峰值
        'calls_terminals_peak_num',  # 终端呼叫数量峰值
    ]
    enable_disable_report_type = [
        'enable_disable_companies',  # 企业启用、停用统计
        'enable_disable_terminals',  # 终端启用、停用统计
    ]
    machines_report_type = [
        'cpu_top_machines',  # cpu使用率 top机器
        'mem_top_machines',  # 内存使用率 top机器
        'disk_top_machines',  # 分区使用率 top机器
    ]
    warning_report_type = [
        'server_warning',  # 服务器告警统计
        'terminal_warning',  # 终端告警统计
    ]
    all_report_types = platform_report_type + conference_report_type + resource_report_type + terminals_report_type + \
                       enable_disable_report_type + machines_report_type + warning_report_type

    # 常用时间相关
    now = datetime.datetime.now(tz=get_current_timezone())
    yesterday = now - datetime.timedelta(1)
    replace = {'hour': 0, 'minute': 0, 'second': 0, 'microsecond': 0}
    today_0_datetime = now.replace(**replace)  # 当天0点的datetime
    today_0_timestamp = int(today_0_datetime.timestamp() * 1000)
    yesterday_0_timestamp = int((today_0_datetime - datetime.timedelta(1)).timestamp() * 1000)
    week_ago_0_timestamp = int((today_0_datetime - datetime.timedelta(7)).timestamp() * 1000)

    # top 数量相关
    cpu_top_count = 3
    mem_top_count = 3
    disk_top_count = 3
    bad_experience_conf_top_count = 10

    def __init__(self, excludes=None, includes=None, es_timeout=600, es_max_retries=3):
        '''

        :param includes: 包含列表，includes与excludes同时传入时，只有includes生效
        :param excludes: 排除列表，includes与excludes同时传入时，只有includes生效
        :param es_timeout:  elasticsearch的查询超时时间
        :param es_max_retries: elasticsearch的查询失败重试时间
        '''
        close_old_connections()
        self.includes = includes
        self.excludes = excludes
        self.report_type_list = []
        self.total_confs_list = []
        if self.includes:
            # 传入indclues
            for include in self.includes:
                if include in self.all_report_types:
                    self.report_type_list.append(include)
        elif self.excludes:
            # 传入excludes
            self.report_type_list = self.all_report_types
            for exclude in self.excludes:
                if exclude in self.all_report_types:
                    self.report_type_list.remove(exclude)
        else:
            self.report_type_list = self.all_report_types

        self.luban_cursor = connections['luban'].cursor()
        self.movision_cursor = connections['movision'].cursor()

        self.hosts_list = ({'host': host, 'port': port} for host in hosts.split(','))
        self.es_client = MyElastic(
            self.hosts_list,
            http_compress=True,  # http_compress请求压缩
            timeout=es_timeout,  # 请求超时时间，官方默认为10s
            max_retries=es_max_retries  # 最大重试次数，官方默认为3
        )

    def __del__(self):
        try:
            connections.close_all()
        except Exception as e:
            logger.exception(e)

    def _reset_daily_report_data(self, date):
        try:
            DailyReportModel.objects.filter(date=date).delete()
        except Exception as e:
            logger.exception(e)

    def generate_handler(self):
        self.daily_report(cover=True)

    def daily_report(self, cover=False):
        import time
        st = time.time()
        start_time = self.yesterday_0_timestamp
        # start_time = int((self.today_0_datetime - datetime.timedelta(2)).timestamp() * 1000)
        end_time = self.today_0_timestamp
        # end_time = self.yesterday_0_timestamp
        date = self.yesterday.date()
        # date = (self.now - datetime.timedelta(2)).date()
        if cover:
            self._reset_daily_report_data(date)
        if not DailyReportModel.objects.filter(date=date).exists():
            for report_type in self.report_type_list:
                if hasattr(self, report_type):
                    func = getattr(self, report_type)
                    logger.info('begin %s' % func.__name__)
                    try:
                        result = func(start_time, end_time)
                    except Exception as e:
                        logger.exception(e)
                    else:
                        try:
                            result = json.dumps(result)
                        except:
                            pass
                        data = {
                            'date': date,
                            'platform_moid': '',
                            'platform_name': '',
                            'report_type': func.__name__,
                            'report_data': result
                        }
                        drs = DailyReportSerializers(data=data)
                        if drs.is_valid():
                            drs.save()
                        else:
                            logger.error(drs.errors)
        logger.info('生成日报耗时：%ss' % (time.time() - st))

    # def weekly_report(self):
    #     start_time = self.week_ago_0_timestamp
    #     end_time = self.today_0_timestamp

    def machine_num(self, start_time=yesterday_0_timestamp, end_time=today_0_timestamp):
        '''
        机器数量
        :param start_time:
        :param end_time:
        :return: 数量：int
        '''
        machine_num = 0
        try:
            sql = '''
            SELECT count(*) FROM machine_info;
            '''
            self.luban_cursor.execute(sql)
            fetchone = self.luban_cursor.fetchone()
            machine_num = fetchone[0]
        except Exception as e:

            logger.exception(e)

        return machine_num

    def machine_type(self, start_time=yesterday_0_timestamp, end_time=today_0_timestamp):
        '''
        机器类型
        :param start_time:
        :param end_time:
        :return: {类型：数量}
        '''
        machine_type = {}
        try:
            sql = '''
            SELECT machine_type,COUNT(machine_type) AS `count` FROM `machine_info` GROUP BY machine_type;
            '''
            self.luban_cursor.execute(sql)
            fetchall = self.luban_cursor.fetchall()
            machine_type.update({x[0]: x[1] for x in fetchall})
        except Exception as e:
            logger.exception(e)

        return machine_type

    def concurrent_confs_peak_num(self, start_time=yesterday_0_timestamp, end_time=today_0_timestamp):
        '''
        并发会议数量峰值
        :param start_time:
        :param end_time:
        :return: 数量：int
        '''
        dsl = es_ql.concurrent_confs_peak_num_dsl
        index, body = dsl.get('index'), dsl.get('dsl')
        timestamp_field = body["query"]["bool"]["filter"]["range"]["@timestamp"]
        timestamp_field['gte'], timestamp_field['lte'] = start_time, end_time
        filter_path = {'filter_path': 'aggregations.time.buckets.dev.buckets.confdatainfo_length.value'}
        concurrent_confs_peak_num = 0
        items = []
        try:
            es_response = self.es_client.search(
                body=body,
                index=index,
                params=filter_path
            )

            jsonpath_result = jsonpath.jsonpath(es_response, '$..dev.buckets')
            if jsonpath_result:
                for item in jsonpath_result:
                    items.append(sum(jsonpath.jsonpath(item, '$..value') if jsonpath.jsonpath(item, '$..value') else 0))
                    concurrent_confs_peak_num = max(items) if items else 0

        except Exception as e:
            logger.exception(e)

        return concurrent_confs_peak_num

    def total_confs(self, start_time=yesterday_0_timestamp, end_time=today_0_timestamp):
        '''
        指定时间段内会议总数
        :param start_time:
        :param end_time:
        :return: [{name,domain_name,bandwidth,start_time,end_time,terminal_num}]
        '''
        dsl = es_ql.total_confs_dsl
        index, body = dsl.get('index'), dsl.get('dsl')
        timestamp_field = body["query"]["bool"]["filter"]["range"]["@timestamp"]
        timestamp_field['gte'], timestamp_field['lte'] = start_time, end_time
        total_confs = []
        terminal_count_info = {}
        description = ['conf_e164', 'domain_moid', 'domain_name', 'conf_name', 'conf_type', 'resolution', 'frame_rate',
                       'bitrate', 'start_time', 'end_time', 'terminal_count']

        try:
            user_domain_name_sql = '''
            SELECT user_domain_moid,user_domain_name FROM user_domain;
            '''
            self.movision_cursor.execute(user_domain_name_sql)
            user_domain_name = self.movision_cursor.fetchall()
            user_domain_moid2name = {_[0]: _[1] for _ in user_domain_name}
            es_response = self.es_client.search(
                body=body,
                index=index,
            )
            mt_conf_e164_buckets = es_response.get('aggregations', {}).get('mt_conf_e164', {}).get('buckets', [])
            m_search_dsls = []
            for mt_conf_e164_bucket in mt_conf_e164_buckets:
                conf_e164 = mt_conf_e164_bucket.get('key')
                eventid_buckets = mt_conf_e164_bucket.get('eventid', {}).get('buckets', [])
                add_count = 0
                del_count = 0
                for eventid_bucket in eventid_buckets:
                    if eventid_bucket.get('key') == 'EV_MCU_MT_ADD':
                        add_count += eventid_bucket.get('doc_count')
                    if eventid_bucket.get('key') == 'EV_MCU_MT_DEL':
                        del_count += eventid_bucket.get('doc_count')
                terminal_count = add_count - del_count if (add_count - del_count) > 0 else 0
                terminal_count_info.update({conf_e164: terminal_count})  # 重复会议号将导致终端数量不正确
            conf_conf_e164_buckets = es_response.get('aggregations', {}).get('conf_conf_e164', {}).get('buckets', [])
            for conf_conf_e164_bucket in conf_conf_e164_buckets:
                conf_e164 = conf_conf_e164_bucket.get('key')
                confinfo = jsonpath.jsonpath(conf_conf_e164_bucket, '$..source.confinfo')
                for info in confinfo:
                    domain_moid = info.get('domainmoid')
                    domain_name = user_domain_moid2name.get(domain_moid)
                    conf_name = info.get('confname')
                    if re.match('test_(.*)_createmeeting\d?', conf_name):
                        # 测试会议，不展示
                        continue
                    conf_type = 'port' if info.get('conftype', 0) else 'traditional'  # 0:传统会议 1:端口会议
                    resolution = info.get('resolution')
                    resolution = MtVideoResolutionRedisDesc.get(resolution, '')
                    frame_rate = info.get('frame')
                    bitrate = info.get('bitrate')
                    start_time = info.get('begintime')
                    end_time = info.get('endtime')
                    try:
                        start_timestamp = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S').timestamp() * 1000
                        end_time_dsl = copy.deepcopy(es_ql.total_confs_end_time_dsl)
                        dsl_bool = end_time_dsl['dsl']['query']['bool']
                        dsl_bool['must'].append({
                            "match": {
                                "source.confinfo.confe164": conf_e164
                            }
                        })
                        dsl_bool['filter']['range']['@timestamp']['gte'] = start_timestamp
                        m_search_dsls.append(end_time_dsl)
                    except Exception as e:
                        logger.exception(e)

                    terminal_count = terminal_count_info.get(conf_e164, 0)
                    conf = [conf_e164, domain_moid, domain_name, conf_name, conf_type, resolution, frame_rate, bitrate,
                            start_time, end_time, terminal_count]
                    total_confs.append(dict(zip(description, conf)))
            try:
                m_body = self.es_client.get_index_header_m_body(*m_search_dsls)
                end_time_es_responses = self.es_client.msearch(m_body)['responses']
                for i, end_time_es_response in enumerate(end_time_es_responses):
                    real_end_time = jsonpath.jsonpath(end_time_es_response, '$..confinfo.endtime')
                    real_end_time_e164 = jsonpath.jsonpath(end_time_es_response, '$..confinfo.confe164')
                    if real_end_time:
                        real_end_time = real_end_time[0]
                        real_end_time_e164 = real_end_time_e164[0]
                        if total_confs[i]['conf_e164'] == real_end_time_e164:
                            total_confs[i]['end_time'] = real_end_time
            except Exception as e:
                logger.exception(e)

            total_confs.sort(key=lambda conf: (-conf.get('terminal_count'), conf.get('start_time')))
        except Exception as e:
            logger.exception(e)
        self.total_confs_list = total_confs
        return total_confs

    def bad_experience_top_confs(self, start_time=yesterday_0_timestamp, end_time=today_0_timestamp):
        '''
        top 差会议体验会议
        :param start_time:
        :param end_time:
        :return:
        '''
        conf_quality = ConfQuality(start_time=start_time, end_time=end_time)
        bad_experience_confs = conf_quality.get_quality(detail=True)
        bad_confs = []
        if bad_experience_confs[0]:
            bad_experience_confs = [
                bad_experience_top_conf for bad_experience_top_conf in bad_experience_confs[1]
                if len(bad_experience_top_conf[1]) == 7  # 多点会议号长度为7
            ]
            bad_experience_confs.sort(key=lambda quality: quality[0])
        else:
            bad_experience_confs = []

        if bad_experience_confs:
            top_bad_experience_confs = bad_experience_confs[:self.bad_experience_conf_top_count]
            top_bad_experience_conf_e164 = [conf[1] for conf in top_bad_experience_confs]
            conf_info = self.total_confs_list
            for conf in conf_info:
                if conf.get('conf_e164') in top_bad_experience_conf_e164:
                    index = top_bad_experience_conf_e164.index(conf.get('conf_e164'))
                    conf['quality'] = top_bad_experience_confs[index][0]
                    conf['quality_desc'] = self._get_quality_desc(conf['quality'])
                else:
                    conf['quality'] = 4
            conf_info.sort(key=lambda _conf: (_conf['quality'], _conf['start_time']))

            for conf in conf_info:
                if conf.get('quality', 4) != 4:
                    bad_confs.append(conf)
        return bad_confs

    def _get_quality_desc(self, score):
        desc = ["体验不好", "体验一般", "体验良好", "体验优秀"]
        try:
            return desc[score - 1]
        except:
            return desc[3]

    def media_resource(self, start_time=yesterday_0_timestamp, end_time=today_0_timestamp):
        request = HttpRequest()
        request.query_params = {'start_time': start_time, 'end_time': end_time}
        statistics_data = ConfResourcesStatistics().get(request).data.get('data', {}).get('info', [])
        return statistics_data

    def transmit_resource(self, start_time=yesterday_0_timestamp, end_time=today_0_timestamp):
        '''
        转发资源统计
        :param start_time:
        :param end_time:
        :return:
        '''
        dsl = es_ql.transmit_resource_dsl
        index, body = dsl.get('index'), dsl.get('dsl')
        timestamp_field = body["query"]["bool"]["filter"]["range"]["@timestamp"]
        timestamp_field['gte'], timestamp_field['lte'] = start_time, end_time
        filter_path = {'filter_path': 'aggregations.time.buckets'}
        transmit_resource = []
        try:
            es_response = self.es_client.search(
                body=body,
                index=index,
                params=filter_path
            )
            buckets = jsonpath.jsonpath(es_response, '$..time.buckets')
            if buckets:
                buckets = buckets[0]
                for bucket in buckets:
                    transmit_resource.append(
                        [bucket.get('key'), round(bucket.get('bandwidth_used_pct', {}).get('value', 0), 4)]
                    )
        except Exception as e:
            logger.exception(e)

        return transmit_resource

    def online_terminals_peak_num(self, start_time=yesterday_0_timestamp, end_time=today_0_timestamp):
        '''
        在线终端数量峰值
        :param start_time:
        :param end_time:
        :return: 数量：int
        '''
        dsl = es_ql.online_terminals_peak_num_dsl
        index, body = dsl.get('index'), dsl.get('dsl')
        timestamp_field = body["query"]["bool"]["filter"]["range"]["@timestamp"]
        timestamp_field['gte'], timestamp_field['lte'] = start_time, end_time
        filter_path = {'filter_path': 'aggregations.time.buckets.dev.buckets.curonlinecount.value'}
        online_terminals_peak_num = 0
        items = []
        try:
            es_response = self.es_client.search(
                body=body,
                index=index,
                params=filter_path
            )

            jsonpath_result = jsonpath.jsonpath(es_response, '$..dev.buckets')
            if jsonpath_result:
                for item in jsonpath_result:
                    items.append(sum(jsonpath.jsonpath(item, '$..value') if jsonpath.jsonpath(item, '$..value') else 0))
                    online_terminals_peak_num = max(items) if items else 0

        except Exception as e:
            logger.exception(e)

        return online_terminals_peak_num

    def calls_terminals_peak_num(self, start_time=yesterday_0_timestamp, end_time=today_0_timestamp):
        '''
        呼叫终端数量峰值
        :param start_time:
        :param end_time:
        :return: 数量：int
        '''
        dsl = es_ql.calls_terminals_peak_num_dsl
        index, body = dsl.get('index'), dsl.get('dsl')
        timestamp_field = body["query"]["bool"]["filter"]["range"]["@timestamp"]
        timestamp_field['gte'], timestamp_field['lte'] = start_time, end_time
        filter_path = {'filter_path': 'aggregations.time.buckets.dev.buckets.callingcount.value'}
        calls_terminals_peak_num = 0
        items = []
        try:
            es_response = self.es_client.search(
                body=body,
                index=index,
                params=filter_path
            )

            jsonpath_result = jsonpath.jsonpath(es_response, '$..dev.buckets')
            if jsonpath_result:
                for item in jsonpath_result:
                    items.append(sum(jsonpath.jsonpath(item, '$..value') if jsonpath.jsonpath(item, '$..value') else 0))
                    calls_terminals_peak_num = max(items) if items else 0

        except Exception as e:
            logger.exception(e)

        return calls_terminals_peak_num

    def enable_disable_companies(self, start_time=yesterday_0_timestamp, end_time=today_0_timestamp):
        request = HttpRequest()
        request.query_params = {}
        enable_disable_terminals = CompanyInfo().get(request)
        data = enable_disable_terminals.data.get('data')
        if 'platform_moid' in data:
            data.pop('platform_moid')

        return data

    def enable_disable_terminals(self, start_time=yesterday_0_timestamp, end_time=today_0_timestamp):
        request = HttpRequest()
        request.query_params = {}
        enable_disable_terminals = TerminalInfo().get(request)
        data = enable_disable_terminals.data.get('data')
        if 'platform_moid' in data:
            data.pop('platform_moid')
        if 'user_domain_moid' in data:
            data.pop('user_domain_moid')

        return data

    @property
    def _machine_moid2name(self):
        '''
        机器名称
        :return:
        '''
        machine_name = {}
        sql = '''
        SELECT machine_moid,machine_name FROM machine_info
        '''
        params = []
        try:
            self.luban_cursor.execute(sql, params)
            fetchall = self.luban_cursor.fetchall()
            machine_name = {fetch[0]: fetch[1] for fetch in fetchall}
        except Exception as e:
            logger.exception(e)
        return machine_name

    def cpu_top_machines(self, start_time=yesterday_0_timestamp, end_time=today_0_timestamp):
        '''
        top cpu机器
        :param start_time:
        :param end_time:
        :return:
        '''
        dsl = es_ql.cpu_top_machines_dsl
        index, body = dsl.get('index'), dsl.get('dsl')
        timestamp_field = body["query"]["bool"]["filter"]["range"]["@timestamp"]
        timestamp_field['gte'], timestamp_field['lte'] = start_time, end_time
        filter_path = {'filter_path': 'aggregations.eqpid.buckets'}
        cpu_top_machines = []
        try:
            es_response = self.es_client.search(
                body=body,
                index=index,
                params=filter_path
            )
            jsonpath_result = jsonpath.jsonpath(es_response, '$..buckets')
            if jsonpath_result:
                buckets = jsonpath_result[0]
                for bucket in buckets:
                    moid = bucket.get('key', '')
                    used_pct_value = [sbucket for sbucket in bucket.get('time', {}).get('buckets', [])]
                    # cpu使用率最高的机器
                    max_used_pct_value = sorted(
                        used_pct_value,
                        key=lambda item: item.get('used_pct', {}).get('value', 0)
                    )[-1]

                    cpu_top_machines.append({
                        'moid': moid,
                        'value': max_used_pct_value.get('used_pct', {}).get('value', 0)
                    })

                cpu_top_machines.sort(key=lambda bucket: bucket.get('value', 0), reverse=True)
                cpu_top_machines = cpu_top_machines[:self.cpu_top_count]
                for cpu_top_machine in cpu_top_machines:
                    moid = cpu_top_machine.get('moid')
                    cpu_top_machine['name'] = self._machine_moid2name.get(moid, '')

        except Exception as e:
            logger.exception(e)

        return cpu_top_machines

    def mem_top_machines(self, start_time=yesterday_0_timestamp, end_time=today_0_timestamp):
        '''
        top 内存机器
        :param start_time:
        :param end_time:
        :return:
        '''
        dsl = es_ql.mem_top_machines_dsl
        index, body = dsl.get('index'), dsl.get('dsl')
        timestamp_field = body["query"]["bool"]["filter"]["range"]["@timestamp"]
        timestamp_field['gte'], timestamp_field['lte'] = start_time, end_time
        filter_path = {'filter_path': 'aggregations.eqpid.buckets'}
        mem_top_machines = []
        try:
            es_response = self.es_client.search(
                body=body,
                index=index,
                params=filter_path
            )
            jsonpath_result = jsonpath.jsonpath(es_response, '$..buckets')
            if jsonpath_result:
                buckets = jsonpath_result[0]
                mem_top_machines = [
                    {'moid': bucket.get('key', ''),
                     'value': round(bucket.get('actual_used_pct', {}).get('value', 0), 4)
                     } for bucket in buckets
                ]
                mem_top_machines.sort(key=lambda bucket: bucket.get('value', 0), reverse=True)
                mem_top_machines = mem_top_machines[:self.mem_top_count]
                for mem_top_machine in mem_top_machines:
                    moid = mem_top_machine.get('moid')
                    mem_top_machine['name'] = self._machine_moid2name.get(moid, '')

        except Exception as e:
            logger.exception(e)

        return mem_top_machines

    def disk_top_machines(self, start_time=yesterday_0_timestamp, end_time=today_0_timestamp):
        '''
        top 分区使用率机器
        :param start_time:
        :param end_time:
        :return:
        '''
        dsl = es_ql.disk_top_machines_dsl
        index, body = dsl.get('index'), dsl.get('dsl')
        timestamp_field = body["query"]["bool"]["filter"]["range"]["@timestamp"]
        timestamp_field['gte'], timestamp_field['lte'] = start_time, end_time
        filter_path = {'filter_path': 'aggregations.eqpid.buckets'}
        disk_top_machines = []
        try:
            es_response = self.es_client.search(
                body=body,
                index=index,
                params=filter_path
            )

            jsonpath_result = jsonpath.jsonpath(es_response, '$..buckets')

            if jsonpath_result:
                buckets = jsonpath_result[0]
                for bucket in buckets:
                    moid = bucket.get('key', '')
                    mount_point_value = [sbucket for sbucket in bucket.get('mount_point', {}).get('buckets', [])]
                    # 使用率最高的分区
                    max_mount_point_value = sorted(
                        mount_point_value,
                        key=lambda item: item.get('filesystem_used_pct', {}).get('value')
                    )[-1]

                    disk_top_machines.append({
                        'moid': moid,
                        'mount_point': max_mount_point_value.get('key'),
                        'value': max_mount_point_value.get('filesystem_used_pct', {}).get('value')
                    })

                disk_top_machines.sort(key=lambda bucket: bucket.get('value', 0), reverse=True)
                disk_top_machines = disk_top_machines[:self.disk_top_count]

                for disk_top_machine in disk_top_machines:
                    moid = disk_top_machine.get('moid')
                    disk_top_machine['name'] = self._machine_moid2name.get(moid, '')

        except Exception as e:
            logger.exception(e)

        return disk_top_machines

    def server_warning(self, start_time=yesterday_0_timestamp, end_time=today_0_timestamp):
        server_warning = {
            'unrepaired': {'critical': 0, 'important': 0, 'normal': 0},
            'repaired': {'critical': 0, 'important': 0, 'normal': 0},
        }
        try:
            # 未修复告警
            unrepaired_count = ServerWarningUnrepairedModel.objects.filter(
                start_time__lte=datetime.datetime.fromtimestamp(end_time / 1000, tz=get_current_timezone()),
                start_time__gte=datetime.datetime.fromtimestamp(start_time / 1000, tz=get_current_timezone())
            ).values_list('level').annotate(Count('id'))
            unrepaired_count = dict(unrepaired_count)
            server_warning['unrepaired']['critical'] = unrepaired_count.get('critical', 0)
            server_warning['unrepaired']['important'] = unrepaired_count.get('important', 0)
            server_warning['unrepaired']['normal'] = unrepaired_count.get('normal', 0)
            # 已修复告警
            repaired_count = ServerWarningRepairedModel.objects.filter(
                start_time__lte=datetime.datetime.fromtimestamp(end_time / 1000, tz=get_current_timezone()),
                start_time__gte=datetime.datetime.fromtimestamp(start_time / 1000, tz=get_current_timezone())
            ).values_list('level').annotate(Count('id'))
            repaired_count = dict(repaired_count)
            server_warning['repaired']['critical'] = repaired_count.get('critical', 0)
            server_warning['repaired']['important'] = repaired_count.get('important', 0)
            server_warning['repaired']['normal'] = repaired_count.get('normal', 0)
        except Exception as e:
            logger.exception(e)
        return server_warning

    def terminal_warning(self, start_time=yesterday_0_timestamp, end_time=today_0_timestamp):
        terminal_warning = {
            'unrepaired': {'critical': 0, 'important': 0, 'normal': 0},
            'repaired': {'critical': 0, 'important': 0, 'normal': 0},
        }
        try:
            # 未修复告警
            unrepaired_count = TerminalWarningUnrepairedModel.objects.filter(
                start_time__lte=datetime.datetime.fromtimestamp(end_time / 1000, tz=get_current_timezone()),
                start_time__gte=datetime.datetime.fromtimestamp(start_time / 1000, tz=get_current_timezone())
            ).values_list('level').annotate(Count('id'))
            unrepaired_count = dict(unrepaired_count)
            terminal_warning['unrepaired']['critical'] = unrepaired_count.get('critical', 0)
            terminal_warning['unrepaired']['important'] = unrepaired_count.get('important', 0)
            terminal_warning['unrepaired']['normal'] = unrepaired_count.get('normal', 0)
            # 已修复告警
            repaired_count = TerminalWarningRepairedModel.objects.filter(
                start_time__lte=datetime.datetime.fromtimestamp(end_time / 1000, tz=get_current_timezone()),
                start_time__gte=datetime.datetime.fromtimestamp(start_time / 1000, tz=get_current_timezone())
            ).values_list('level').annotate(Count('id'))
            repaired_count = dict(repaired_count)
            terminal_warning['repaired']['critical'] = repaired_count.get('critical', 0)
            terminal_warning['repaired']['important'] = repaired_count.get('important', 0)
            terminal_warning['repaired']['normal'] = repaired_count.get('normal', 0)
        except Exception as e:
            logger.exception(e)
        return terminal_warning

    def conf_time(self, start_time=yesterday_0_timestamp, end_time=today_0_timestamp):
        request = HttpRequest()
        request.query_params = {'start_time': start_time, 'end_time': end_time}
        conf_time = ConfTime().get(request).data.get('data', {}).get('info', [])
        return conf_time

    def conf_quality(self, start_time=yesterday_0_timestamp, end_time=today_0_timestamp):
        request = HttpRequest()
        request.query_params = {'start_time': start_time, 'end_time': end_time}
        conf_quality = ConferencesQuality().get(request, version='v1').data.get('data', {}).get('info', [])
        return conf_quality

    def conf_resolution(self, start_time=yesterday_0_timestamp, end_time=today_0_timestamp):
        conf_resolution = {}
        for conf in self.total_confs_list:
            resolution = conf.get('resolution', '')
            frame_rate = conf.get('frame_rate', '30')
            key = '%s_%s' % (resolution, frame_rate)
            if conf_resolution.get(key):
                conf_resolution[key] += 1
            else:
                conf_resolution[key] = 1

        return conf_resolution


if __name__ == '__main__':
    rdg = ReportDateGenerator()
    rdg.daily_report()
