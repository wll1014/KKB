#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

from django.shortcuts import get_object_or_404
from rest_framework import mixins
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from common import global_func

# 基类，改写response，增加success，data字段
class KedaBaseAPIView(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      GenericAPIView):

    # request.data中object的key
    lookup_request_data = None

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': 1, 'data': serializer.data})

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({'success': 1, 'data': serializer.data})

    def create(self, request, *args, **kwargs):
        '''
        重写create方法，支持传入[{...},{...}]格式数据，批量创建
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        if isinstance(request.data, list):
        # if request.data.get('objs'):
            err_list = []
            for data in request.data:
            # for data in request.data.get('objs'):
                if isinstance(data, dict):
                    data['coordinate_str'] = ''
                    if data.get('coordinate'):
                        data['coordinate_str'] = ','.join(data.get('coordinate'))
                serializer = self.get_serializer(data=data)
                try:
                    serializer.is_valid(raise_exception=True)
                    self.perform_create(serializer)
                except Exception as e:
                    err_list.append({
                        'data':str(data),
                        'error msg': str(e)
                    })
            if err_list:
                response = global_func.get_response(0,error_msg=err_list)
            else:
                response = global_func.get_response()
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            if request.data.get('coordinate'):
                request.data['coordinate_str'] = ','.join(request.data.get('coordinate'))
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            response = global_func.get_response(data=serializer.data)
            return Response(response, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if isinstance(request.data.get('coordinate'), list):
            request.data['coordinate_str'] = ','.join(request.data.get('coordinate'))
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response({'success': 1})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'success': 1}, status=status.HTTP_204_NO_CONTENT)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        if self.lookup_request_data and self.request.data.get(self.lookup_request_data):
            objs = []
            for keda_lookup_request_data in self.request.data.get(self.lookup_request_data):
                filter_kwargs = {self.lookup_field: keda_lookup_request_data}
                obj = get_object_or_404(queryset, **filter_kwargs)
                self.check_object_permissions(self.request, obj)
                objs.append(obj)

            return objs
        else:
            queryset = self.filter_queryset(self.get_queryset())
            lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

            assert lookup_url_kwarg in self.kwargs, (
                    'Expected view %s to be called with a URL keyword argument '
                    'named "%s". Fix your URL conf, or set the `.lookup_field` '
                    'attribute on the view correctly.' %
                    (self.__class__.__name__, lookup_url_kwarg)
            )

            filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
            obj = get_object_or_404(queryset, **filter_kwargs)

            self.check_object_permissions(self.request, obj)

            return obj


class MultiDeleteAPIView(mixins.DestroyModelMixin,
                         GenericAPIView):
    def multi_delete(self, request, *args, **kwargs):
        '''
        批量删除,在类中定义变量lookup_request_data = 'ids'，然后在request.data中传入{"ids":[1,2,3]}
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        instances = self.get_object()
        for instance in instances:
            self.perform_destroy(instance)
        return Response({'success': 1})

    def delete(self, request, *args, **kwargs):
        return self.multi_delete(request, *args, **kwargs)
