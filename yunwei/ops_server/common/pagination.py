#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.response import Response


class ResultsSetPaginationOffset(LimitOffsetPagination):
    """
    自定义分页格式, 采用偏移量分页
    """
    limit_query_param = 'count'  # 每页记录数参数标识
    offset_query_param = 'start'  # 偏移数参数标识
    default_limit = 20  # 默认每页记录数
    max_limit = 50  # 最大每页记录数

    def get_paginated_response(self, data):
        """
        定义返回前端的数据格式
        :param data: 待返回数据
        :return: a instance of class Response
        """
        return Response(
            {
                'success': 1,
                'total': self.count,
                'data': data
            }
        )


class ResultsSetPaginationOffset1(ResultsSetPaginationOffset):
    """
    自定义分页格式1, 采用偏移量分页
    """
    def get_paginated_response(self, data, **params):
        """
        定义返回前端的数据格式
        :param data: 待返回数据
        :param params: 查询参数
        :return: a instance of class Response
        """
        params['start'] = self.offset
        params['count'] = len(data)
        params['total'] = self.count
        params['info'] = data
        return Response(
            {
                'success': 1,
                'data': params
            }
        )


class ResultsSetPaginationDefault(PageNumberPagination):
    """
    自定义分页格式, 默认分页
    """
    page_query_param = 'page'  # 页参数标识
    page_size_query_param = 'size'  # 记录数参数标识
    page_size = 5  # 每页记录数
    max_page_size = 50  # 最大每页记录数

    def get_paginated_response(self, data):
        """
        定义返回前端的数据格式
        :param data: 待返回数据
        :return: a instance of Response class
        """
        return Response(
            {
                'success': 1,
                'total': self.page.paginator.count,
                'data': data
            }
        )


class ResultsDataSetPaginationOffset(LimitOffsetPagination):
    """
    自定义分页格式, 采用偏移量分页
    """
    limit_query_param = 'count'  # 每页记录数参数标识
    offset_query_param = 'start'  # 偏移数参数标识
    default_limit = 5  # 默认每页记录数
    max_limit = 50  # 最大每页记录数

    def get_paginated_response(self, data):
        """
        定义返回前端的数据格式
        :param data: 待返回数据
        :return: a instance of class Response
        """
        response = data
        response['data']['total'] = self.count
        response['data']['count'] = self.limit
        response['data']['start'] = self.offset
        return Response(response)
