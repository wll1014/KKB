from django.shortcuts import render

# Create your views here.

import csv
import codecs
import logging
import datetime
from io import BytesIO
from .models import OperationLog
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from common.pagination import ResultsSetPaginationOffset1

logger = logging.getLogger('ops.' + __name__)


def operation_logger(request, detail, status):
    """
    记录操作日志
    :param request: HttpRequest 对象
    :param detail: 操作描述,例如：新增-添加维护记录、修改-修改FAQ记录
    :param status: 操作状态，例如，修改成功、修改失败等
    :return:是否记录成功，布尔值，true/false
    """
    try:
        username = request.META.get('ssoAuth').get('account')
    except Exception as err:
        logger.error(err)
        username = ''

    ip = request.META.get('REMOTE_ADDR', '')

    operation_data = OperationLogSerializers(data=dict(username=username, detail=detail, status=status, ip=ip))
    if operation_data.is_valid():  # 校验数据
        try:
            with transaction.atomic():
                operation_data.save()
        except Exception as err:
            logger.error(err)
            return False
        else:
            return True
    else:
        logger.error(operation_data.errors)
        return False


def json_response(state, **kwargs):
    """
    自定义返回json
    :param state: 操作状态 0：失败   1：成功
    :param kwargs: 自定义返回字段
    :return: 字典
    """
    if state == 0:
        kwargs.setdefault("success", 0)
        return kwargs
    else:
        kwargs.setdefault("success", 1)
        return kwargs


class ChoicesField(serializers.Field):
    def __init__(self, choices, **kwargs):
        self._choices = choices
        super(ChoicesField, self).__init__(**kwargs)

    def to_representation(self, obj):
        for key, value in self._choices:
            if key == obj:
                return value
        return ""

    def to_internal_value(self, data):
        return data


class OperationLogSerializers(serializers.ModelSerializer):
    """
    序列化
    """
    time = serializers.SerializerMethodField(read_only=True)
    opertype = ChoicesField(choices=OperationLog.operation_type)
    operrest = ChoicesField(choices=OperationLog.operation_results)

    class Meta:
        model = OperationLog
        # fields = '__all__'  # 所有字段序列化后返回
        exclude = ('id',)

    def get_time(self, obj):
        """
        时间转换为unix时间戳
        :param obj:
        :return:
        """
        return int(obj.time.timestamp()*1000)


class OperationLogView(APIView):
    """
    处理 api/v1/ops/oplog/ 请求
    """

    def get(self, request, version):
        """
        处理GET请求,返回所有符合条件的操作记录
        :param version: API版本号
        :param request:
        """
        # obtain Conditional query parameter from URL
        params = request.query_params.dict()
        columns_search = ["username"]
        conditions = {key + '__icontains': params.get(key) for key in columns_search if params.get(key)}
        columns_match = ["opertype"]
        conditions.update({key + '__exact': params.get(key) for key in columns_match if params.get(key)})

        start_time = params.get("starttime")
        end_time = params.get("endtime")

        if start_time and end_time:
            try:
                start_time = datetime.datetime.fromtimestamp(int(start_time) / 1000)
                end_time = datetime.datetime.fromtimestamp(int(end_time) / 1000)
            except Exception as err:
                logger.error(err)
            else:
                conditions['time__range'] = (start_time, end_time)

        if not conditions:
            # 无筛选条件返回全部数据
            items = OperationLog.objects.all().order_by('-id')
        else:
            # 有筛选条件返回筛选数据
            items = OperationLog.objects.filter(**conditions).order_by('-id')

        try:
            pagination = ResultsSetPaginationOffset1()  # create pagination object
            pg_res = pagination.paginate_queryset(queryset=items, request=request, view=self)  # get pagination data
            items_series = OperationLogSerializers(instance=pg_res, many=True)
            return pagination.get_paginated_response(items_series.data, **params)
        except Exception as err:
            logger.error(err)
            return JsonResponse(json_response(0, error_code=421, msg='数据库操作失败'))


class ExportOpLog(APIView):
    """
    操作记录导出
    """
    def get(self, request, version):

        response = OperationLogView().get(request=request, version=version)
        response_stat = response.data["success"]
        if response_stat == 0:
            # 读数据失败
            return response
        response_data = response.data['data']['info']
        if len(response_data) == 0:
            # 数据为空
            return JsonResponse(json_response(0, error_code=420, msg='数据为空'))
        else:
            # 数据不为空
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=oplog_data.csv'
            response.write(codecs.BOM_UTF8)
            writer = csv.writer(response)

            keys = response_data[0].keys()
            writer.writerow([str(x) for x in keys])

            for item in response_data:
                item['time'] = datetime.datetime.fromtimestamp(int(item['time']/1000)).strftime("%Y-%m-%dT%H:%M:%S")
                writer.writerow([str(x) for x in item.values()])
            return response
