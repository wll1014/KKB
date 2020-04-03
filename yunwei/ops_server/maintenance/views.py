from django.shortcuts import render

# Create your views here.

import json
import logging
from django.db import transaction
from .models import MaintenanceRecords
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from common.pagination import ResultsSetPaginationOffset1

logger = logging.getLogger('ops.' + __name__)


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


class MaintenanceRecordSerializers(serializers.ModelSerializer):
    """
    序列化
    """
    # 修改maintenance_time字段返回前端的时间格式
    maintenance_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    creat_time = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = MaintenanceRecords
        # exclude = ('record_id', 'creat_time',)
        fields = '__all__'  # 所有字段序列化后返回


class RecordView(APIView):
    """
    处理 api/v1/ops/maintenance/ 请求
    """

    def post(self, request, version):
        """
        处理POST请求
        add one record item
        :param request:
        :param version: API版本号
        :return:
        """

        # 从request.META中获取创建人
        try:
            creator = request.META.get('ssoAuth').get('account')
        except Exception as err:
            logger.error(err)
            return JsonResponse(json_response(0, error_code=422, msg='授权信息错误'))

        data = request.data
        data['creator'] = creator
        front_data = MaintenanceRecordSerializers(data=data)  # 序列化
        if front_data.is_valid():  # 校验数据
            try:
                with transaction.atomic():
                    front_data.save()
            except Exception as err:
                logger.error(err)
                return JsonResponse(json_response(0, error_code=421, msg='数据库操作失败'))
            else:
                return JsonResponse(json_response(1))
        else:
            logger.error(front_data.errors)
            return JsonResponse(json_response(0, error_code=422, msg='数据格式错误'))

    def get(self, request, version):
        """
        处理GET请求
        query all items
        :param version: API版本号
        :param request:
        """
        params = request.query_params.dict()
        # obtain Conditional query parameter from URL
        columns = ["platform", "operating_models"]
        conditions = {key+'__icontains': params.get(key) for key in columns if params.get(key)}
        start_time = params.get("starttime")
        end_time = params.get("endtime")
        if start_time and end_time:
            conditions['maintenance_time__range'] = (start_time, end_time)

        if not conditions:
            # 无筛选条件返回全部数据
            items = MaintenanceRecords.objects.all().order_by('-record_id')
        else:
            # 有筛选条件返回筛选数据
            items = MaintenanceRecords.objects.filter(**conditions).order_by('-record_id')

        try:
            if items:
                # 数据不为空正常返回数据
                pagination = ResultsSetPaginationOffset1()  # create pagination object
                pg_res = pagination.paginate_queryset(queryset=items, request=request, view=self)  # get pagination data
                items_series = MaintenanceRecordSerializers(instance=pg_res, many=True)
                return pagination.get_paginated_response(items_series.data, **params)
            else:
                # 数据为空返回空列表
                return Response(data={'success': 1, 'data': {"total": 0, "start": 0, "count": 0, "info": []}})
        except Exception as err:
            logger.error(err)
            return JsonResponse(json_response(0, error_code=421, msg='数据库操作失败'))

    def delete(self, request, version):
        """
        处理DELETE请求
        delete items
        :param request:
        :param version: API版本号
        """

        # 获取待删除数据id的数组
        try:
            ids = json.loads(request.body.decode()).get('ids')
        except Exception as err:
            logger.error(err)
            return JsonResponse(json_response(0, error_code=422, msg='数据格式错误'))
        else:
            if not all([isinstance(x, int) for x in ids]):
                return JsonResponse(json_response(0, error_code=422, msg='数据格式错误'))

        # 执行删除
        try:
            with transaction.atomic():
                MaintenanceRecords.objects.filter(record_id__in=ids).delete()
        except Exception as err:
            logger.error(err)
            return JsonResponse(json_response(0, error_code=421, msg='数据库操作失败'))
        else:
            return JsonResponse(json_response(1))


class RecordDetailView(APIView):
    """
    处理 api/v1/ops/maintenance/id/ 请求
    """

    def get(self, request, version, ids):
        """
        处理GET请求
        query one item
        :param request:
        :param version: API版本号
        :param ids: 待查询记录的id
        :return:
        """

        try:
            item = MaintenanceRecords.objects.get(record_id=ids)
        except (MaintenanceRecords.DoesNotExist, MaintenanceRecords.MultipleObjectsReturned) as err:
            logger.error(err)
            # 没有获取到指定ID的数据数据则返回空列表
            return Response(data={'success': 1, 'data': {"total": 0, "start": 0, "count": 0, "info": []}})
        except Exception as err:
            logger.error(err)
            JsonResponse(json_response(0, error_code=421, msg='数据库操作失败'))
        else:
            item_series = MaintenanceRecordSerializers(item, many=False)
            return Response(data={'success': 1, 'data': {"total": 1, "start": 0, "count": 1, "info": [item_series.data]}})

    def put(self, request, version, ids):
        """
        处理PUT请求
        alter one item
        :param request:
        :param version: API版本号
        :param ids: 待修改记录的id
        """

        try:
            # 先查询得到要修改的记录
            item = MaintenanceRecords.objects.get(record_id=ids)
        except (MaintenanceRecords.DoesNotExist, MaintenanceRecords.MultipleObjectsReturned) as err:
            logger.error(err)
            return Response(data=json_response(0, error_code=424, msg='请求信息不存在'))
        except Exception as err:
            logger.error(err)
            JsonResponse(json_response(0, error_code=421, msg='数据库操作失败'))
        else:
            # 修改记录
            if request.data.get('creator'):
                # 'creator'属性创建后禁止修改
                request.data.pop('creator')

            front_data = MaintenanceRecordSerializers(instance=item, data=request.data, partial=True)
            if front_data.is_valid():  # 校验数据
                try:
                    with transaction.atomic():
                        front_data.save()
                except Exception as err:
                    logger.error(err)
                    JsonResponse(json_response(0, error_code=421, msg='数据库操作失败'))
                else:
                    return JsonResponse(json_response(1))
            else:
                logger.error(front_data.errors)
                return JsonResponse(json_response(0, error_code=422, msg='数据格式错误'))
