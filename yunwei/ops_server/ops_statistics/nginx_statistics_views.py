#!/usr/bin/env python3
# coding: utf-8
from django.http.request import HttpRequest

__author__ = 'wanglei_sxcpx@kedacom.com'

import logging
import os
import csv
import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from django.http.response import FileResponse

from ops_statistics import nginx_statistics_query_func
from ops.settings import MEDIA_ROOT
from common import global_func
from common.my_exception import OpsException

logger = logging.getLogger('ops.' + __name__)


class OutLine(APIView):
    def get(self, request, *args, **kwargs):
        params = nginx_statistics_query_func.from_request_get_common_params(request)
        outline_info = nginx_statistics_query_func.get_outline_pv_uv_request_time(request)
        data = {
            "end_time": params.get('end_time'),
            "start_time": params.get('start_time'),
            "room_moid": params.get('room_moid'),
            "platform_moid": params.get('platform_moid'),
            "info": outline_info
        }

        response = global_func.get_response(data=data)
        return Response(response)


class RequestTraffic(APIView):
    def get(self, request, *args, **kwargs):
        params = nginx_statistics_query_func.from_request_get_common_params(request)
        request_traffic_info = nginx_statistics_query_func.get_time_aggs_request_traffic(request)
        data = {
            "end_time": params.get('end_time'),
            "start_time": params.get('start_time'),
            "interval": params.get('interval'),
            "room_moid": params.get('room_moid'),
            "platform_moid": params.get('platform_moid'),
            "info": request_traffic_info
        }

        response = global_func.get_response(data=data)
        return Response(response)


class PV(APIView):
    def get(self, request, *args, **kwargs):
        params = nginx_statistics_query_func.from_request_get_common_params(request)
        pv_info = nginx_statistics_query_func.get_time_aggs_pv(request)
        data = {
            "end_time": params.get('end_time'),
            "start_time": params.get('start_time'),
            "interval": params.get('interval'),
            "room_moid": params.get('room_moid'),
            "platform_moid": params.get('platform_moid'),
            "info": pv_info
        }

        response = global_func.get_response(data=data)
        return Response(response)


class IP(APIView):
    def get(self, request, *args, **kwargs):
        params = nginx_statistics_query_func.from_request_get_common_params(request)
        ip_info = nginx_statistics_query_func.get_ip_info(request)
        data = {
            "end_time": params.get('end_time'),
            "start_time": params.get('start_time'),
            "room_moid": params.get('room_moid'),
            "platform_moid": params.get('platform_moid'),
            "start": params.get('start'),
            "count": params.get('count'),
            "total": len(ip_info),
            "info": ip_info[params.get('start'):(params.get('start') + params.get('count'))]
        }

        response = global_func.get_response(data=data)
        return Response(response)


class SlowResponses(APIView):
    def get(self, request, *args, **kwargs):
        params = nginx_statistics_query_func.from_request_get_common_params(request)
        slow_responses_info = nginx_statistics_query_func.get_slow_responses_info(request)
        data = {
            "end_time": params.get('end_time'),
            "start_time": params.get('start_time'),
            "room_moid": params.get('room_moid'),
            "platform_moid": params.get('platform_moid'),
            "start": params.get('start'),
            "count": params.get('count'),
            "total": len(slow_responses_info),
            "slow_time_threshold": params.get('slow_time_threshold'),
            "info": slow_responses_info[params.get('start'):(params.get('start') + params.get('count'))]
        }

        response = global_func.get_response(data=data)
        return Response(response)


class URLs(APIView):
    def get(self, request, *args, **kwargs):
        params = nginx_statistics_query_func.from_request_get_common_params(request)
        url_info = nginx_statistics_query_func.get_url_info(request)
        data = {
            "end_time": params.get('end_time'),
            "start_time": params.get('start_time'),
            "room_moid": params.get('room_moid'),
            "platform_moid": params.get('platform_moid'),
            "start": params.get('start'),
            "count": params.get('count'),
            "total": len(url_info),
            "info": url_info[params.get('start'):(params.get('start') + params.get('count'))]
        }

        response = global_func.get_response(data=data)
        return Response(response)


class ClientsPct(APIView):
    def get(self, request, *args, **kwargs):
        params = nginx_statistics_query_func.from_request_get_common_params(request)
        clients_pct_info = nginx_statistics_query_func.get_clients_pct_info(request)
        data = {
            "end_time": params.get('end_time'),
            "start_time": params.get('start_time'),
            "room_moid": params.get('room_moid'),
            "platform_moid": params.get('platform_moid'),
            "info": clients_pct_info
        }

        response = global_func.get_response(data=data)
        return Response(response)


class Clients(APIView):
    # 暂未完成
    def get(self, request, *args, **kwargs):
        params = nginx_statistics_query_func.from_request_get_common_params(request)
        clients_info = nginx_statistics_query_func.get_clients_info(request)
        data = {
            "end_time": params.get('end_time'),
            "start_time": params.get('start_time'),
            "room_moid": params.get('room_moid'),
            "platform_moid": params.get('platform_moid'),
            "client": params.get('client'),
            "start": params.get('start'),
            "count": params.get('count'),
            "total": len(clients_info),
            "info": clients_info[params.get('start'):(params.get('start') + params.get('count'))]
        }

        response = global_func.get_response(data=data)
        return Response(response)


class StatusCode(APIView):
    def get(self, request, *args, **kwargs):
        params = nginx_statistics_query_func.from_request_get_common_params(request)
        status_code_info = nginx_statistics_query_func.get_time_aggs_status_code(request)
        data = {
            "end_time": params.get('end_time'),
            "start_time": params.get('start_time'),
            "interval": params.get('interval'),
            "room_moid": params.get('room_moid'),
            "platform_moid": params.get('platform_moid'),
            "info": status_code_info
        }

        response = global_func.get_response(data=data)
        return Response(response)


class Errors(APIView):
    def get(self, request, *args, **kwargs):
        params = nginx_statistics_query_func.from_request_get_common_params(request)
        url_info = nginx_statistics_query_func.get_error_info(request)
        data = {
            "end_time": params.get('end_time'),
            "start_time": params.get('start_time'),
            "room_moid": params.get('room_moid'),
            "platform_moid": params.get('platform_moid'),
            "start": params.get('start'),
            "count": params.get('count'),
            "total": len(url_info),
            "info": url_info[params.get('start'):(params.get('start') + params.get('count'))]
        }

        response = global_func.get_response(data=data)
        return Response(response)


class Methods(APIView):
    def get(self, request, *args, **kwargs):
        params = nginx_statistics_query_func.from_request_get_common_params(request)
        methods_info = nginx_statistics_query_func.get_methods_info(request)
        data = {
            "end_time": params.get('end_time'),
            "start_time": params.get('start_time'),
            "room_moid": params.get('room_moid'),
            "platform_moid": params.get('platform_moid'),
            "info": methods_info
        }

        response = global_func.get_response(data=data)
        return Response(response)


class Modules(APIView):
    def get(self, request, *args, **kwargs):
        params = nginx_statistics_query_func.from_request_get_common_params(request)
        methods_info = nginx_statistics_query_func.get_modules(request)
        data = {
            "end_time": params.get('end_time'),
            "start_time": params.get('start_time'),
            "room_moid": params.get('room_moid'),
            "platform_moid": params.get('platform_moid'),
            "info": methods_info
        }

        response = global_func.get_response(data=data)
        return Response(response)


class Detail(APIView):
    def get(self, request, *args, **kwargs):
        params = nginx_statistics_query_func.from_request_get_common_params(request)
        detail_info, total = nginx_statistics_query_func.get_detail_info(request)

        data = {
            "end_time": params.get('end_time'),
            "start_time": params.get('start_time'),
            "room_moid": params.get('room_moid'),
            "platform_moid": params.get('platform_moid'),
            "start": params.get('start'),
            "count": params.get('count'),
            "total": total,
            "key": params.get('key'),
            "client": params.get('client'),
            "status_code": params.get('status_code'),
            "module": params.get('module'),
            "slow_time_threshold": params.get('slow_time_threshold'),
            "info": detail_info
        }

        response = global_func.get_response(data=data)
        return Response(response)


class Export(APIView):
    def get(self, request, *args, **kwargs):
        params = nginx_statistics_query_func.from_request_get_common_params(request)
        export_type = params.get('export_type')  # 导出文档的类型
        file_name = '%s_%s.csv' % (export_type, int(datetime.datetime.now().timestamp() * 1000))  # 文件名：类型_时间戳.csv
        file_path = os.path.join(MEDIA_ROOT, 'nginx_statistics', file_name)
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
        query_params = request.query_params
        request = HttpRequest()
        request.query_params = query_params

        allow_export_type = ['ip', 'slow_responses', 'urls', 'clients', 'errors', 'detail']
        if export_type in allow_export_type:
            if export_type == allow_export_type[0]:
                viewset = IP
                headers = ['ip', 'count']
            elif export_type == allow_export_type[1]:
                viewset = SlowResponses
                headers = ['urls', 'count']
            elif export_type == allow_export_type[2]:
                viewset = URLs
                headers = ['urls', 'count']
            elif export_type == allow_export_type[3]:
                viewset = Clients
                headers = ['clients', 'count']
            elif export_type == allow_export_type[4]:
                viewset = Errors
                headers = ['urls', 'count', 'status', 'upstream_status']
            else:
                viewset = Detail
                headers = ['@timestamp', 'request', 'module', 'request_method', 'request_time', 'http_user_agent',
                           'args', 'host', 'upstream_response_time', 'status', 'http_referer', 'request_uri',
                           'beat', 'type', 'server_name', 'upstream_status', 'remote_user', 'scheme',
                           'http_x_forwarded_for', 'server_port', 'server_addr',
                           'body_bytes_sent', 'remote_addr', 'remote_port', 'upstream_addr', 'uri',
                           'hostname', 'https', 'time_local']
        else:
            raise OpsException(code='10010')
        # 获取接口数据
        start = 0
        count = total = page_size = 1000

        with open(file_path, 'w', newline='', encoding='gbk') as f:
            # 写入csv
            csv_writer = csv.DictWriter(f, headers)
            csv_writer.writeheader()
            while total > start:
                # 翻页查询全部文档
                data = []
                query_params = request.query_params.copy()
                query_params['start'] = start
                query_params['count'] = count
                request.query_params = query_params
                # 调用视图函数获得不同的导出内容
                view_data = viewset().get(request, *args, **kwargs)
                total = view_data.data.get('data', {}).get('total', 0)
                data_info = view_data.data.get('data', {}).get('info', [])
                if export_type == allow_export_type[4]:
                    # error内容
                    for dic in data_info:
                        data.append({headers[0]: dic[0], headers[1]: dic[1], headers[2]: dic[2], headers[3]: dic[3]})
                elif export_type == allow_export_type[5]:
                    # detail内容
                    data.extend(data_info)
                else:
                    for dic in data_info:
                        data.append({headers[0]: dic[0], headers[1]: dic[1]})
                start = start + page_size

                csv_writer.writerows(data)

        response = FileResponse(open(file_path, 'rb'))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename={}'.format(file_name)
        # 发送至前端
        return response
