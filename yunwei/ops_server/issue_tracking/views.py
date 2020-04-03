from django.shortcuts import render

# Create your views here.

import csv
import codecs
import logging
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework import views
from rest_framework.response import Response
from django.http import HttpResponse
from issue_tracking.models import IssueTracker
from django.db.models import Q
from common.pagination import ResultsSetPaginationOffset1

from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend


logger = logging.getLogger('ops.' + __name__)


class IssueTrackerCreateSerializer(serializers.ModelSerializer):
    """
    创建问题追踪序列化器
    """
    postscript = serializers.CharField(allow_blank=True, required=False)
    detail = serializers.CharField(allow_blank=True, required=False)
    customer = serializers.CharField(allow_blank=True, required=False)
    version = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = IssueTracker
        exclude = ['close_time', ]


class IssueTrackerListSerializer(serializers.ModelSerializer):
    """
    查询/修改 问题追踪序列化器
    """
    postscript = serializers.CharField(allow_blank=True)
    detail = serializers.CharField(allow_blank=True)
    customer = serializers.CharField(allow_blank=True)
    version = serializers.CharField(allow_blank=True)

    class Meta:
        model = IssueTracker
        fields = '__all__'
        read_only_fields = ['creat_time', 'creator', 'close_time']


class IssueTrackerFilter(filters.SearchFilter):
    search_param = 'condition'


class IssueTrackerView(viewsets.ModelViewSet):
    # queryset = IssueTracker.objects.all()
    lookup_field = 'pk'
    pagination_class = ResultsSetPaginationOffset1
    # 关键字查询
    filter_backends = (DjangoFilterBackend, IssueTrackerFilter)
    filterset_fields = ('status', 'priority')
    # 关键字搜索
    search_fields = ('id', 'issue')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            serializer_class = IssueTrackerCreateSerializer
        else:
            serializer_class = IssueTrackerListSerializer
        return serializer_class

    def get_queryset(self):
        conditions = self.request.query_params.dict()
        conditions = dict([(k, v) for k, v in conditions.items() if v])

        begin_time = conditions.get('begin_time')
        end_time = conditions.get('end_time')

        query_filter = {}

        if begin_time and end_time:
            query_filter['creat_time__range'] = (begin_time, end_time)
        elif begin_time:
            query_filter['creat_time__gte'] = begin_time
        elif end_time:
            query_filter['creat_time__lte'] = end_time

        queryset = IssueTracker.objects.filter(**query_filter).order_by('-id')
        return queryset

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except Exception as err:
            logger.error(err)
            return Response({'success': 0, 'error_code': 402, 'msg': err.args[0]})

    def create(self, request, *args, **kwargs):
        try:
            creator = request.META.get('ssoAuth').get('account')
        except Exception as err:
            logger.error(err)
        else:
            if creator is not None:
                request.data['creator'] = creator
        try:
            super().create(request, *args, **kwargs)
        except Exception as err:
            logger.error(err)
            return Response({'success': 0, 'error_code': 402, 'msg': err.args[0]})
        return Response({'success': 1})

    def get_paginated_response(self, data):
        conditions = self.request.query_params.dict()
        conditions = dict([(k, v) for k, v in conditions.items() if v])
        return self.paginator.get_paginated_response(data, **conditions)

    def update(self, request, *args, **kwargs):
        try:
            super().update(request, *args, **kwargs)
        except Exception as err:
            logger.error(err)
            return Response({'success': 0, 'error_code': 402, 'msg': err.args[0]})
        return Response({'success': 1})

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
        except Exception as err:
            logger.error(err)
            return Response({'success': 0, 'error_code': 402, 'msg': err.args[0]})
        return Response({'success': 1, 'data': serializer.data})

    def destroy(self, request, *args, **kwargs):
        try:
            super().destroy(request, *args, **kwargs)
        except Exception as err:
            logger.error(err)
            return Response({'success': 0, 'error_code': 402, 'msg': err.args[0]})
        return Response({'success': 1})

    def delete(self, request, *args, **kwargs):
        ids = request.data.get('ids')
        if isinstance(ids, list):
            try:
                IssueTracker.objects.filter(id__in=ids).delete()
            except Exception as err:
                logger.error(err)
                return Response({'success': 0, 'error_code': 403, 'msg': err.args[0]})
            else:
                return Response({'success': 1})
        else:
            return Response({'success': 0, 'error_code': 403, 'msg': "数据格式错误"})


class IssueTrackerExportView(views.APIView):
    """
    问题追踪记录导出
    """

    def get(self, request, *args, **kwargs):
        # 获取导出数据筛选条件
        filter_condition = request.query_params.get('ids')

        try:
            filter_condition = [int(id_) for id_ in filter_condition.split(',') if id_]
        except Exception as err:
            logger.error(err)
            return Response({'success': 0, 'error_code': 420, 'msg': err.args[0]})

        queryset = IssueTracker.objects.filter(id__in=filter_condition)
        if len(queryset) == 0:
            return Response({'success': 0, 'error_code': 420, 'msg': "数据为空"})
        else:
            # 数据不为空
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=issue_tracking.csv'
            response.write(codecs.BOM_UTF8)
            writer = csv.writer(response)

            dates_series = IssueTrackerListSerializer(instance=queryset, many=True)

            # 标题行
            keys = dates_series.child.fields.fields.keys()
            writer.writerow([str(x) for x in keys])

            for item in dates_series.data:
                writer.writerow([str(x) for x in item.values()])
            return response
