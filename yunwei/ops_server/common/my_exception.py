#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

import logging
from rest_framework.exceptions import APIException
from rest_framework import exceptions, status
from rest_framework.views import set_rollback
from rest_framework.response import Response

from django.http import Http404,HttpResponseServerError
from django.core.exceptions import PermissionDenied

from common import global_func
from common.global_func import ERROR

logger = logging.getLogger('ops.' + __name__)


class OpsException(APIException):
    '''
    自定义错误，供统一错误返回处理
    '''
    status_code = status.HTTP_200_OK
    default_code = '10000'
    code = None

    def __init__(self, detail=None, code=None):
        if not code:
            self.code = self.default_code
            code = self.default_code
        else:
            self.code = code
        self.default_detail = ERROR.get(code, ERROR.get('10000'))
        super().__init__(detail=detail, code=code)


def exception_handler(exc, context):
    '''
    重写原错误处理方法，修改返回内容格式
    :param exc:
    :param context:
    :return:
    '''
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    if isinstance(exc, exceptions.APIException):
        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['Retry-After'] = '%d' % exc.wait

        error_msg = exc.detail
        if getattr(exc, 'code', None):
            error_code = exc.code
        else:
            error_code = exc.default_code
        response = global_func.get_response(0, error_code=error_code, error_msg=error_msg)
        set_rollback()
        return Response(response, status=exc.status_code, headers=headers)

    return None

def ops_exception_handler(exc, context):
    '''
    调用更改后的错误处理方法，如为未捕获到的错误，统一处理为未知错误的json返回
    :param exc:
    :param context:
    :return:
    '''
    response = exception_handler(exc, context)
    default_error_code = '10000'
    headers = {}
    status_code = status.HTTP_200_OK
    logger.exception(exc)
    if response is None:
        response = global_func.get_response(0, error_code=default_error_code)
        return Response(response, status=status_code, headers=headers)
    return response