#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

import logging
import json
import requests
from common.global_func import get_conf, get_token, get_response
from common.my_redis import my_redis_client
from ops.settings import DEBUG
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse

logger = logging.getLogger('ops.' + __name__)
sso_ip = get_conf('auth', 'ip')
sso_port = get_conf('auth', 'port')
validation_uri = 'apiCore/sso/validationToken'
url = 'http://%s:%s/%s' % (sso_ip, sso_port, validation_uri)
no_sso_url = ['/api/v1/ops/logger/', '/api/v1/ops/login/', '/ops', '/ops/', '/ops/check']
redis_key = 'sso_authenticate'
portalcore_login_uri = '/portalCore/login'
ex = 5


class SSOAuthenticate(MiddlewareMixin):
    def process_request(self, request):
        if request.path not in no_sso_url:
            ssoToken = request.COOKIES.get('SSO_COOKIE_KEY')
            if DEBUG:
                # 测试使用
                sso_auth = {
                    'account': 'administrator',
                    'moid': 'ops_login_debug',
                    'virMachineroomMoid': 'mooooooo-oooo-oooo-oooo-defaultplatf'
                }
                request.META.setdefault('ssoAuth', sso_auth)
            else:
                if not ssoToken:
                    response = get_response(0, data={'url': portalcore_login_uri}, error_code=10003)
                    return JsonResponse(response, json_dumps_params={'ensure_ascii': False}, status=401)
                else:
                    try:
                        is_exists = my_redis_client.exists('%s_%s' % (redis_key, ssoToken))
                    except Exception as e:
                        err = str(e)
                        logger.warning('redis is not connected: %s' % err)
                        is_exists = False

                    if is_exists:
                        sso_auth = my_redis_client.get('%s_%s' % (redis_key, ssoToken))
                        try:
                            sso_auth = sso_auth.decode('utf-8')
                            sso_auth = json.loads(sso_auth)
                        except Exception as e:
                            logger.error(str(e))
                            my_redis_client.delete('%s_%s' % (redis_key, ssoToken))
                            logger.warning('delete %s_%s' % (redis_key, ssoToken))
                        request.META.setdefault('ssoAuth', sso_auth)
                        logger.info(sso_auth)
                    else:
                        account_token = get_token(sso_ip, sso_port)
                        params = {
                            'account_token': account_token,
                            'ssoToken': ssoToken
                        }
                        try:
                            ret = requests.post(url, params=params, timeout=3)
                            sso_auth = json.loads(ret.text)
                        except Exception as e:
                            # 请求结果错误，校验失败
                            logger.warning(str(e))
                            response = get_response(0, data={'url': portalcore_login_uri}, error_code=10003)
                            return JsonResponse(response, json_dumps_params={'ensure_ascii': False}, status=401)
                        else:
                            is_success = sso_auth.get('success')
                            if is_success:
                                # 校验成功
                                sso_auth = sso_auth.get('data', {})
                                logger.debug(sso_auth)
                                request.META.setdefault('ssoAuth', sso_auth)
                                my_redis_client.set('%s_%s' % (redis_key, ssoToken), json.dumps(sso_auth), ex=ex)
                                logger.info('%s is login' % sso_auth.get('account', ''))
                            else:
                                # 校验失败
                                response = get_response(0, data={'url': portalcore_login_uri}, error_code=10003)
                                my_redis_client.delete('%s_%s' % (redis_key, ssoToken))
                                return JsonResponse(response, json_dumps_params={'ensure_ascii': False}, status=401)
