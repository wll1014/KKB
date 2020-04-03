#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

import redis
from common.global_func import get_conf


pool = redis.ConnectionPool(
    host=get_conf('redis', 'host'),
    port=get_conf('redis', 'port'),
    db=get_conf('redis', 'database'),
    password=get_conf('redis', 'password'),
)
redis_client = redis.Redis(connection_pool=pool)
