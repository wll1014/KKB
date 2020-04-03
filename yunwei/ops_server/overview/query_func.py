#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

import os
import time
import json
import jsonpath
import logging
from common.my_elastic import es_client, ESIndex
from common.my_redis import my_redis_client as redis_client

logger = logging.getLogger('ops.' + __name__)


def get_terminal_online_status(terminal_moid, cache_time=300):
    now = time.time()
    redis_key = 'terminal_online_info'
    cache = {'terminal_status': {}, 'time': now}
    try:
        if redis_client.exists(redis_key):
            try:
                cache_bytes = redis_client.get(redis_key)
                cache = json.loads(cache_bytes.decode())
            except Exception as e:
                err = str(e)
                logger.error(err)

            if cache.get('time') and cache.get('time') < now - cache_time:
                # 如果大于缓存时间，则重新查询
                terminal_status = es_search_terminal_status()
                cache['time'] = now
                cache['terminal_status'] = terminal_status

                try:
                    redis_client.set(redis_key, json.dumps(cache), ex=cache_time)
                except Exception as e:
                    err = str(e)
                    logger.error(err)

                return cache.get('terminal_status').get(terminal_moid)
            else:
                return cache.get('terminal_status').get(terminal_moid)
        else:
            terminal_status = es_search_terminal_status()
            cache['time'] = now
            cache['terminal_status'] = terminal_status
            try:
                redis_client.set(redis_key, json.dumps(cache))
            except Exception as e:
                err = str(e)
                logger.error(err)

            return cache.get('terminal_status').get(terminal_moid)
    except Exception as e:
        err = str(e)
        logger.error(err)
        return cache.get('terminal_status').get(terminal_moid)


def es_search_terminal_status():
    dsl = {
        'index': ESIndex.NMSMTIndex.value,
        'dsl': {
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "source.eventid": "EV_DEV_ONLINE || EV_DEV_OFFLINE"
                            }
                        },
                        {
                            "match": {
                                "source.msgsrc": "mt || bridge26 || bridge48"
                            }
                        }
                    ],
                    "filter": {
                        "range": {
                            "@timestamp": {
                                "gte": "2018-01-01"
                            }
                        }
                    }
                }
            },
            "size": 0,
            "aggs": {
                "status": {
                    "terms": {
                        "size": 10000,
                        "field": "beat.dev_moid.keyword"
                    },
                    "aggs": {
                        "top_date_hits": {
                            "top_hits": {
                                "sort": [
                                    {
                                        "@timestamp": {
                                            "order": "desc"
                                        }
                                    }
                                ],
                                # "_source": ["source"],
                                "_source": ["source.eventid"],
                                "size": 1
                            }
                        }
                    }
                }
            }
        }
    }
    dsls = [dsl]
    m_body = es_client.get_index_header_m_body(*dsls)

    try:
        terminal_status_response = es_client.msearch(m_body)['responses'][0]
    except Exception as e:
        err = str(e)
        logger.error(err)
        terminal_status_response = {}

    status = {}
    if terminal_status_response:
        status_buckets = jsonpath.jsonpath(terminal_status_response, '$..status.buckets')
        if status_buckets:
            status_buckets = status_buckets[0]
            for status_bucket in status_buckets:
                # print(status_bucket)
                terminal_moid = status_bucket.get('key')
                last_status = jsonpath.jsonpath(status_bucket, '$..eventid')
                if 'EV_DEV_ONLINE' in last_status:
                    status[terminal_moid] = 'EV_DEV_ONLINE'
                else:
                    status[terminal_moid] = 'EV_DEV_OFFLINE'
    logger.info('重写终端上下线缓存...')
    return status


if __name__ == '__main__':
    x = es_search_terminal_status()
    print(x)
