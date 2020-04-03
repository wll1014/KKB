#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

import os
from common.global_func import get_conf
from ops.settings import BASE_DIR
import redis

pool = redis.ConnectionPool(
    host=get_conf('redis_platform','host'),
    port=get_conf('redis_platform','port'),
    db=get_conf('redis_platform','database'),
    password=get_conf('redis_platform','password'),
)

my_pool = redis.ConnectionPool(
    host=get_conf('redis','host'),
    port=get_conf('redis','port'),
    db=get_conf('redis','database'),
    password=get_conf('redis','password'),
)

# 平台同步的redis客户端
redis_client = redis.Redis(connection_pool=pool)
# 自用redis客户端
my_redis_client = redis.Redis(connection_pool=my_pool)

if __name__ == '__main__':
    import time

    starttime = time.time()
    script_path = os.path.join(BASE_DIR, 'overview', 'lua', 'get_conf_mt_e164.lua')
    with open(script_path, 'r')as f:
        script_content = f.read()

    in_meeting_terminals = []
    try:
        in_meeting_terminals = redis_client.eval(script_content, 0)
        in_meeting_terminals = [in_meeting_terminal.decode('utf-8') for in_meeting_terminal in in_meeting_terminals]
    except Exception as e:
        err = str(e)
        print(err)

    print(time.time() - starttime)