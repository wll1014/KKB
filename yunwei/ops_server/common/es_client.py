#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from elasticsearch import Elasticsearch
from elasticsearch import helpers
from common.global_func import get_conf

host = get_conf('elasticsearch', 'hosts')
port = get_conf('elasticsearch', 'port')


class ESClient:
    """
    构建查询客户端
    """

    def __init__(self, **kwargs):
        self.client = Elasticsearch(**kwargs)

    def search(self, index, dsl, **kwargs):
        """
        执行查询
        :param index: ES索引
        :param dsl: ES语句
        :param kwargs:
        :return:
        """
        # scroll_id=None, scroll='2m'
        return self.client.search(index=index, body=dsl, **kwargs)

    def msearch(self, dsl, **kwargs):
        """
        执行批量查询
        :param dsl: ES语句
        :param kwargs:
        :return:
        """
        # scroll_id=None, scroll='2m'
        return self.client.msearch(body=dsl, **kwargs)

    def index(self, index, body):
        return self.client.index(index=index, body=body)

    def bulk(self, actions, *args, **kwargs):
        return helpers.bulk(self.client, actions, *args, **kwargs)


def es_client(**kwargs):
    """
    返回客户端实例
    :param kwargs:
    :return:
    """
    hosts = [{'host': h, 'port': port} for h in host.split(',')]
    kwargs.setdefault("timeout", 10)  # 超时时间
    kwargs.setdefault("http_compress", True)  # http_compress请求压缩
    return ESClient(hosts=hosts, **kwargs)