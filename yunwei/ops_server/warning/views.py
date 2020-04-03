from django.db.models import Q
from django.http.response import FileResponse, HttpResponse
from django.shortcuts import render
import pickle, csv
import time
import pickle
import os

from django.views.generic import View
from rest_framework.filters import SearchFilter

from common.pagination import ResultsDataSetPaginationOffset
from django.utils import timezone
from datetime import datetime, timedelta

from ops.settings import BASE_DIR, PKS_ROOT
# Create your views here.

import logging
from rest_framework.generics import ListAPIView, CreateAPIView, ListCreateAPIView, RetrieveUpdateAPIView, \
    RetrieveUpdateDestroyAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import connections, transaction
from django_filters.rest_framework import DjangoFilterBackend
from common import global_func
from common.my_elastic import es_client
from warning.models import *
from warning.warning_serializers.warning_serializers import *
from common.keda_baseclass import KedaWarningBaseAPIView, MultiDeleteAPIView, KedaBaseAPIView

logger = logging.getLogger('ops.' + __name__)


class ServerRepairedWarning(KedaWarningBaseAPIView, ListCreateAPIView):
    serializer_class = ServerWarningRepairedSerializer
    pagination_class = ResultsDataSetPaginationOffset
    # 关键字查询
    filter_backends = (DjangoFilterBackend, SearchFilter)
    # 机房moid、设备类型过滤
    filterset_fields = ('machine_room_moid', 'device_type',)
    # 关键字搜索设备名称
    search_fields = ('device_name',)

    # 是否存储pk文件以供导出下载
    # save_pk = True

    def get_queryset(self):
        start = self.request.query_params.get('start_time', str(round((time.time() - 86400) * 1000)))
        end = self.request.query_params.get('end_time', str(round(time.time() * 1000)))
        level = self.request.query_params.get('level', None)
        platform_moid = self.request.query_params.get('platform_moid', None)
        querset = self.serializer_class.Meta.model.objects.all()
        if start.isdigit() and end.isdigit():
            # 时间区间过滤
            start_datetime = datetime.fromtimestamp(int(start) / 1000, tz=timezone.get_current_timezone())
            end_datetime = datetime.fromtimestamp(int(end) / 1000, tz=timezone.get_current_timezone())
            querset = self.serializer_class.Meta.model.objects.filter(start_time__gte=start_datetime).filter(
                start_time__lte=end_datetime).order_by("-start_time")
        if level:
            # 告警等级过滤
            level = level.split(',')
            if len(level) == 1:
                querset = querset.filter(level=level[0])
            elif len(level) == 2:
                querset = querset.filter(Q(level=level[0]) | Q(level=level[1]))
        if platform_moid:
            # 平台域过滤
            with connections['luban'].cursor() as cursor:
                sql = '''
                SELECT machine_room_moid FROM machine_room_info WHERE domain_moid=%s
                '''
                parmas = [platform_moid]
                cursor.execute(sql, parmas)
                fetchall = cursor.fetchall()
                machine_room_moids = [machine_room_moid[0] for machine_room_moid in fetchall]
            querset = querset.filter(machine_room_moid__in=machine_room_moids)
        return querset


class ServerUnrepairedWarning(KedaWarningBaseAPIView, ListCreateAPIView):
    serializer_class = ServerWarningUnrepairedSerializer
    pagination_class = ResultsDataSetPaginationOffset
    # 关键字查询
    filter_backends = (DjangoFilterBackend, SearchFilter)
    # 机房moid、设备类型过滤
    filterset_fields = ('machine_room_moid', 'device_type',)
    # 关键字搜索设备名称
    search_fields = ('device_name',)

    # 是否存储pk文件以供导出下载
    # save_pk = True

    def get_queryset(self):
        start = self.request.query_params.get('start_time', str(round((time.time() - 86400) * 1000)))
        end = self.request.query_params.get('end_time', str(round(time.time() * 1000)))
        level = self.request.query_params.get('level', None)
        platform_moid = self.request.query_params.get('platform_moid', None)
        querset = self.serializer_class.Meta.model.objects.all()
        if isinstance(start, str) and isinstance(end, str) and start.isdigit() and end.isdigit():
            # 时间区间过滤
            start_datetime = datetime.fromtimestamp(int(start) / 1000, tz=timezone.get_current_timezone())
            end_datetime = datetime.fromtimestamp(int(end) / 1000, tz=timezone.get_current_timezone())
            querset = self.serializer_class.Meta.model.objects.filter(start_time__gte=start_datetime).filter(
                start_time__lte=end_datetime).order_by("-start_time")
        if level:
            # 告警等级过滤
            level = level.split(',')
            if len(level) == 1:
                querset = querset.filter(level=level[0])
            elif len(level) == 2:
                querset = querset.filter(Q(level=level[0]) | Q(level=level[1]))
        if platform_moid:
            # 平台域过滤
            with connections['luban'].cursor() as cursor:
                sql = '''
                SELECT machine_room_moid FROM machine_room_info WHERE domain_moid=%s
                '''
                parmas = [platform_moid]
                cursor.execute(sql, parmas)
                fetchall = cursor.fetchall()
                machine_room_moids = [machine_room_moid[0] for machine_room_moid in fetchall]
            querset = querset.filter(machine_room_moid__in=machine_room_moids)

        return querset


class TerminalRepairedWarning(KedaWarningBaseAPIView, ListCreateAPIView):
    serializer_class = TerminalWarningRepairedSerializer
    pagination_class = ResultsDataSetPaginationOffset
    # 关键字查询
    filter_backends = (DjangoFilterBackend, SearchFilter)
    # 用户域moid、设备类型过滤
    filterset_fields = ('device_type', 'domain_moid')
    # 关键字搜索设备名称
    search_fields = ('device_name', 'device_e164', 'device_ip')

    # 是否存储pk文件以供导出下载
    # save_pk = True

    def get_queryset(self):
        start = self.request.query_params.get('start_time', str(round((time.time() - 86400) * 1000)))
        end = self.request.query_params.get('end_time', str(round(time.time() * 1000)))
        level = self.request.query_params.get('level', None)
        platform_moid = self.request.query_params.get('platform_moid', None)
        querset = self.serializer_class.Meta.model.objects.all()
        if isinstance(start, str) and isinstance(end, str) and start.isdigit() and end.isdigit():
            # 时间区间过滤
            start_datetime = datetime.fromtimestamp(int(start) / 1000, tz=timezone.get_current_timezone())
            end_datetime = datetime.fromtimestamp(int(end) / 1000, tz=timezone.get_current_timezone())
            querset = self.serializer_class.Meta.model.objects.filter(start_time__gte=start_datetime).filter(
                start_time__lte=end_datetime).order_by("-start_time")
        if level:
            # 告警等级过滤
            level = level.split(',')
            if len(level) == 1:
                querset = querset.filter(level=level[0])
            elif len(level) == 2:
                querset = querset.filter(Q(level=level[0]) | Q(level=level[1]))

        return querset


class TerminalUnrepairedWarning(KedaWarningBaseAPIView, ListCreateAPIView):
    serializer_class = TerminalWarningUnrepairedSerializer
    pagination_class = ResultsDataSetPaginationOffset
    # 关键字查询
    filter_backends = (DjangoFilterBackend, SearchFilter)
    # 用户域moid、设备类型过滤
    filterset_fields = ('device_type', 'domain_moid')
    # 关键字搜索设备名称
    search_fields = ('device_name', 'device_e164', 'device_ip')

    # 是否存储pk文件以供导出下载
    # save_pk = True

    def get_queryset(self):
        start = self.request.query_params.get('start_time', str(round((time.time() - 86400) * 1000)))
        end = self.request.query_params.get('end_time', str(round(time.time() * 1000)))
        level = self.request.query_params.get('level', None)
        platform_moid = self.request.query_params.get('platform_moid', None)
        querset = self.serializer_class.Meta.model.objects.all()
        if isinstance(start, str) and isinstance(end, str) and start.isdigit() and end.isdigit():
            # 时间区间过滤
            start_datetime = datetime.fromtimestamp(int(start) / 1000, tz=timezone.get_current_timezone())
            end_datetime = datetime.fromtimestamp(int(end) / 1000, tz=timezone.get_current_timezone())
            querset = self.serializer_class.Meta.model.objects.filter(start_time__gte=start_datetime).filter(
                start_time__lte=end_datetime).order_by("-start_time")
        if level:
            # 告警等级过滤
            level = level.split(',')
            if len(level) == 1:
                querset = querset.filter(level=level[0])
            elif len(level) == 2:
                querset = querset.filter(Q(level=level[0]) | Q(level=level[1]))

        return querset


class ServerWarningDevTypes(APIView):
    def get(self, request, *args, **kwargs):
        querysets = []
        dev_types_l = []
        repaired_queryset = ServerWarningRepairedModel.objects.all().values('device_type').distinct()
        if repaired_queryset:
            querysets.append(repaired_queryset)
        unrepaired_queryset = ServerWarningUnrepairedModel.objects.all().values('device_type').distinct()
        if unrepaired_queryset:
            querysets.append(unrepaired_queryset)

        for dev_types in querysets:
            for dev_type in dev_types:
                if dev_type.get('device_type'):
                    dev_types_l.append(dev_type.get('device_type'))

        response = global_func.get_response(data=list(set(dev_types_l)))
        return Response(response)


class TerminalWarningDevTypes(APIView):
    def get(self, request, *args, **kwargs):
        querysets = []
        dev_types_l = []
        repaired_queryset = TerminalWarningRepairedModel.objects.all().values('device_type').distinct()
        if repaired_queryset:
            querysets.append(repaired_queryset)
        unrepaired_queryset = TerminalWarningUnrepairedModel.objects.all().values('device_type').distinct()
        if unrepaired_queryset:
            querysets.append(unrepaired_queryset)

        for dev_types in querysets:
            for dev_type in dev_types:
                if dev_type.get('device_type'):
                    dev_types_l.append(dev_type.get('device_type'))

        response = global_func.get_response(data=list(set(dev_types_l)))
        return Response(response)


class WarningCodes(KedaWarningBaseAPIView, ListAPIView):
    queryset = WarningCodeModel.objects.all()
    serializer_class = WarningCodeSerializer
    # 关键字查询
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('level', 'type',)


class SubWarning(KedaBaseAPIView, ListCreateAPIView, MultiDeleteAPIView):
    queryset = SubWarningCodeModel.objects.all()
    serializer_class = SubWarningCodeSerializer
    lookup_request_data = 'ids'


class SubWarningDetail(KedaBaseAPIView, RetrieveUpdateDestroyAPIView):
    queryset = SubWarningCodeModel.objects.all()
    serializer_class = SubWarningCodeSerializer


class Thresholds(KedaBaseAPIView, ListAPIView):
    queryset = WarningThresholdModel.objects.all()
    serializer_class = WatningThresholdsSerializer


class ThresholdsDetail(KedaBaseAPIView, RetrieveUpdateAPIView):
    queryset = WarningThresholdModel.objects.all()
    serializer_class = WatningThresholdsSerializer


class Rules(KedaBaseAPIView, ListCreateAPIView, MultiDeleteAPIView):
    queryset = WarningNotifyRuleModel.objects.all()
    lookup_request_data = 'ids'

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method == 'POST':
            return RulesDetailCreateSerializer
        else:
            return RulesSerializer


class RulesDetail(KedaBaseAPIView, RetrieveUpdateAPIView):
    queryset = WarningNotifyRuleModel.objects.all()

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method == 'GET':
            return RulesDetailSerializer
        elif self.request.method in ['PUT', 'PATCH']:
            return RulesDetailUpdateSerializer


class ExportWarning(View):
    def get(self, request, *args, **kwargs):
        warning_type = request.GET.get('warning_type', 0)  # 0：服务器告警，1：终端告警
        warning_type = int(warning_type) if isinstance(warning_type, str) and warning_type.isdigit() else warning_type
        file_name = 'warning_data.csv'
        file_path = os.path.join(PKS_ROOT, file_name)
        page_size = 50
        if warning_type:
            viewsets = [TerminalUnrepairedWarning, TerminalRepairedWarning, ]
        else:
            viewsets = [ServerUnrepairedWarning, ServerRepairedWarning, ]

        data = []
        for viewset in viewsets:
            start = 0
            count = page_size
            view = viewset().as_view()
            logger.info(viewset)
            total = page_size
            while True:
                if total > start:
                    # 修改get参数
                    _get = request.GET.copy()
                    _get['start'] = start
                    _get['count'] = count
                    request.GET = _get
                    # 获取接口数据
                    view_data = view(request, *args, **kwargs).data.get('data', {})
                    total = view_data.get('total', 0)
                    info = view_data.get('info', [])
                    for dic in info:
                        if warning_type:
                            try:
                                del dic['id']
                                del dic['device_moid']
                                del dic['domain_moid']
                                del dic['code']
                                del dic['name']
                            except Exception as e:
                                pass
                        else:
                            try:
                                del dic['id']
                                del dic['machine_room_moid']
                                del dic['platform_domain_moid']
                                del dic['code']
                                del dic['name']
                                del dic['device_moid']
                                del dic['guid']
                            except Exception as e:
                                pass
                        if dic.get('start_time'):
                            dic['start_time'] = dic.get('start_time').split('.')[0]
                            dic['start_time'] = '{}\t'.format(
                                dic.get('start_time').replace('T', ' ').replace('+08:00', '')
                            )
                        if dic.get('resolve_time'):
                            dic['resolve_time'] = dic.get('resolve_time').split('.')[0]
                            dic['resolve_time'] = '{}\t'.format(
                                dic.get('resolve_time').replace('T', ' ').replace('+08:00', '')
                            )
                        if dic.get('device_e164'):
                            dic['device_e164'] = '{e164}\t'.format(e164=dic.get('device_e164'))
                        if dic.get('device_name'):
                            dic['device_name'] = '{device_name}\t'.format(device_name=dic.get('device_name'))
                    data.extend(info)
                    logger.info(total)
                    logger.info(start + page_size)
                    start = start + page_size

                else:
                    break
        headers = list(data[0].keys()) if data else []

        with open(file_path, 'w', newline='', encoding='gbk') as f:
            csv_writer = csv.DictWriter(f, headers)
            csv_writer.writeheader()
            csv_writer.writerows(data)

        response = FileResponse(open(file_path, 'rb'))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename={}'.format(file_name)
        # 发送至前端
        return response


def get_warinig_percent(models, start_datetime, end_datetime):
    '''
    获取各告警等级所占百分比
    :param models: model列表，元素只能是终端、服务器已修复、未修复的model
    :param start_datetime: 开始的datetime
    :param end_datetime: 结束的datetime
    :return:
    '''
    ndigits = 2

    total = sum([model.objects.all().filter(start_time__gte=start_datetime).filter(
        start_time__lte=end_datetime).count() for model in models])
    critical_count = sum(
        [model.objects.filter(level='critical').filter(start_time__gte=start_datetime).filter(
            start_time__lte=end_datetime).count() for model in models])
    important_count = sum(
        [model.objects.filter(level='important').filter(start_time__gte=start_datetime).filter(
            start_time__lte=end_datetime).count() for model in models])
    normal_count = sum(
        [model.objects.filter(level='normal').filter(start_time__gte=start_datetime).filter(
            start_time__lte=end_datetime).count() for model in models])
    data = {
        "alert_lvl_pct": {
            "name": "alert_lvl_pct",
            "description": "各告警等级数量占比",
            "data": {
                "critical": round(critical_count / total, ndigits) if total else 0,
                "important": round(important_count / total, ndigits) if total else 0,
                "normal": round(normal_count / total, ndigits) if total else 0
            }
        },
    }

    # 处理百分数相加不为100%问题
    alert_lvl_pct_data = data['alert_lvl_pct']['data']
    total_pct = sum(alert_lvl_pct_data.values())
    difference = round(1 - total_pct, ndigits)
    if difference and difference != 1:
        alert_lvl_pct_data['normal'] += difference
        alert_lvl_pct_data['normal'] = round(alert_lvl_pct_data['normal'], ndigits)

    return data


class ServerWarningPercent(APIView):
    def get(self, request, *args, **kwargs):
        models = [
            # ServerWarningRepairedModel,
            ServerWarningUnrepairedModel
        ]
        try:
            # 开始时间，默认一周之前
            start = request.query_params.get('start_time', str(round((time.time() - 86400 * 7) * 1000)))
            end = request.query_params.get('end_time', str(round(time.time() * 1000)))
            start_datetime = datetime.fromtimestamp(int(start) / 1000, tz=timezone.get_current_timezone())
            end_datetime = datetime.fromtimestamp(int(end) / 1000, tz=timezone.get_current_timezone())

            data = get_warinig_percent(models, start_datetime, end_datetime)
            response = global_func.get_response(data=data)
        except Exception as e:
            logger.error(str(e))
            response = global_func.get_response(0)

        return Response(response)


class TerminalWarningPercent(APIView):
    def get(self, request, *args, **kwargs):
        models = [
            # TerminalWarningRepairedModel,
            TerminalWarningUnrepairedModel
        ]
        try:
            # 开始时间，默认一周之前
            start = request.query_params.get('start_time', str(round((time.time() - 86400 * 7) * 1000)))
            end = request.query_params.get('end_time', str(round(time.time() * 1000)))
            start_datetime = datetime.fromtimestamp(int(start) / 1000, tz=timezone.get_current_timezone())
            end_datetime = datetime.fromtimestamp(int(end) / 1000, tz=timezone.get_current_timezone())

            data = get_warinig_percent(models, start_datetime, end_datetime)

            response = global_func.get_response(data=data)
        except Exception as e:
            logger.error(str(e))
            response = global_func.get_response(0)

        return Response(response)


class IgnoreWarning(APIView):
    def post(self, request, *args, **kwargs):
        warning_type = request.GET.get('warning_type', 0)  # 0：服务器告警，1：终端告警
        warning_type = int(warning_type) if isinstance(warning_type, str) and warning_type.isdigit() else warning_type
        if warning_type:
            viewsets = [TerminalWarningUnrepairedModel, TerminalWarningRepairedModel, ]
        else:
            viewsets = [ServerWarningUnrepairedModel, ServerWarningRepairedModel, ]
        unrepaired_warning_id = request.GET.get('warning_id', 0)
        unrepaired_warning_id = int(unrepaired_warning_id) \
            if isinstance(unrepaired_warning_id, str) and unrepaired_warning_id.isdigit() else unrepaired_warning_id

        if unrepaired_warning_id:
            now = datetime.now(tz=timezone.utc)
            report_time = now + timedelta(hours=8)
            warning_queryset = viewsets[0].objects.filter(pk=unrepaired_warning_id).first()
            if warning_queryset:
                # es伪造网管恢复告警消息
                week_number = now.isocalendar()[1]
                year = now.year
                month = now.month
                utc_format = "%Y-%m-%dT%H:%M:%S.%fZ"
                rpttime_format = "%Y/%m/%d:%H:%M:%S"
                timestamp = now.strftime(utc_format)
                rpttime = report_time.strftime(rpttime_format)
                machine_base_index = 'machine-{platform_moid}-{year}.{month}-{week_number}'
                mt_base_index = 'platform-nmscollector-{platform_moid}-mt-{year}.{month}-{week_number}'

                connections['luban'].close()
                with connections['luban'].cursor() as cursor:
                    sql = '''
                    SELECT domain_moid FROM `machine_room_info` WHERE machine_num>0;
                    '''
                    cursor.execute(sql, )
                    fetchone = cursor.fetchone()
                    platform_moid = fetchone[0]

                if warning_type:
                    # 终端告警
                    # 处理数据库，将忽略的告警变为已修复告警
                    with transaction.atomic():
                        TerminalWarningRepairedModel.objects.create(
                            device_moid=warning_queryset.device_moid,
                            device_name=warning_queryset.device_name,
                            device_type=warning_queryset.device_type,
                            device_ip=warning_queryset.device_ip,
                            device_e164=warning_queryset.device_e164,
                            domain_name=warning_queryset.domain_name,
                            domain_moid=warning_queryset.domain_moid,
                            code=warning_queryset.code,
                            level=warning_queryset.level,
                            description=warning_queryset.description,
                            start_time=warning_queryset.start_time,
                            resolve_time=now,
                        )
                        # 未修复告警表删除数据
                        TerminalWarningUnrepairedModel.objects.filter(
                            device_moid=warning_queryset.device_moid,
                            code=warning_queryset.code
                        ).delete()

                        index = mt_base_index.format(
                            platform_moid=platform_moid,
                            year=year,
                            month=month,
                            week_number=week_number,
                        )

                        body = {
                            "type": "ops",
                            "source": {
                                "rpttime": rpttime,
                                "eventid": "EV_ALARM_MSG",
                                "alarm_info": {
                                    "report_time": rpttime,
                                    "status": 0,
                                    "code_id": warning_queryset.code
                                },
                                "devtype": warning_queryset.device_type,
                                "devid": warning_queryset.device_moid,
                                "msgsrc": "mt"
                            },
                            "@timestamp": timestamp,
                            "beat": {
                                "dev_moid": warning_queryset.device_moid,
                                "name": "nms_collector",
                                "src_type": "mt",
                                "platform_moid": platform_moid
                            }
                        }
                else:
                    # 服务器告警
                    with transaction.atomic():
                        # 已修复告警表添加数据
                        ServerWarningRepairedModel.objects.create(
                            device_moid=warning_queryset.device_moid,
                            guid=warning_queryset.guid,
                            device_name=warning_queryset.device_name,
                            device_type=warning_queryset.device_type,
                            device_ip=warning_queryset.device_ip,
                            machine_room_name=warning_queryset.machine_room_name,
                            machine_room_moid=warning_queryset.machine_room_moid,
                            code=warning_queryset.code,
                            level=warning_queryset.level,
                            description=warning_queryset.description,
                            start_time=warning_queryset.start_time,
                            resolve_time=now,
                        )
                        # 未修复告警表删除数据
                        ServerWarningUnrepairedModel.objects.filter(
                            device_moid=warning_queryset.device_moid,
                            code=warning_queryset.code,
                            device_type=warning_queryset.device_type,
                        ).delete()
                        index = machine_base_index.format(
                            platform_moid=platform_moid,
                            year=year,
                            month=month,
                            week_number=week_number,
                        )

                        body = {
                            "type": "ops",
                            "source": {
                                "rpttime": rpttime,
                                "eventid": "EV_SRV_WARNING_INFO",
                                "devtype": "x86_server",
                                "devid": warning_queryset.device_moid,
                                "warning_info": {
                                    "code": warning_queryset.code,
                                    "status": 0,
                                    "guid": warning_queryset.guid,
                                    "time": rpttime
                                },
                                "msgsrc": "x86_server",
                            },
                            "@timestamp": timestamp,
                            "beat": {
                                "dev_moid": warning_queryset.device_moid,
                                "name": "nms_collector",
                                "src_type": "x86_server",
                                "platform_moid": platform_moid,
                            }
                        }
                try:
                    ret = es_client.index(
                        index=index,
                        body=body
                    )
                    logger.info('index: {}'.format(index))
                    logger.info('body: {}'.format(body))
                    logger.info(ret)
                except Exception as e:
                    logger.error(str(e))
                    response = global_func.get_response(error_code=10002)
                    return Response(response)
                else:
                    data = {
                        'warning_type': warning_type,
                        'warning_info': {'name': warning_queryset.device_name,
                                         'code': warning_queryset.code,
                                         'description': warning_queryset.description}
                    }
                    response = global_func.get_response(data=data)
                    return Response(response)
            else:
                response = global_func.get_response(0, error_code=10404)
                return Response(response)
        else:
            response = global_func.get_response(0, error_code=10008)
            return Response(response)
