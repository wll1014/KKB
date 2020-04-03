#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

from common.my_elastic import ESIndex

terminal_alarm_dsl = {
    'index': ESIndex.NMSMTIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "source.eventid": "EV_ALARM_MSG"
                        }
                    }
                ],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "gt": "now-1m/m"
                        }
                    }
                }
            }
        },
        "aggs": {
            "dev_moid": {
                "terms": {
                    "field": "beat.dev_moid.keyword",
                    "size": 10000
                },
                "aggs": {
                    "top_date_hits": {
                        "top_hits": {
                            "sort": [
                                {
                                    "@timestamp": {
                                        "order": "asc"
                                    }
                                }
                            ],
                            "_source": {
                                "includes": [
                                    "source.devtype",
                                    "source.alarm_info",
                                    "beat.platform_moid",
                                    "beat.src_type",
                                    "@timestamp",
                                ]
                            },
                            "size": 100
                        }
                    }
                }
            }
        }
    }
}
