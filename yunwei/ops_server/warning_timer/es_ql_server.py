#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

from common.my_elastic import ESIndex

server_alarm_dsl = {
    'index': ESIndex.MachineIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "source.eventid": "EV_SRV_WARNING_INFO"
                        }
                    }
                ],
                "filter": {
                    "range": {
                        "beat.estimestamp": {
                            "gt": "now-1m/m",
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
                    "guid": {
                        "terms": {
                            "field": "source.warning_info.guid.keyword",
                            "size": 10000
                        },
                        "aggs": {
                            "top_date_hits": {
                                "top_hits": {
                                    "sort": [
                                        {
                                            "source.warning_info.timestamp": {
                                                "order": "asc"
                                            }
                                        }
                                    ],
                                    "_source": {
                                        "includes": [
                                            "source.devtype",
                                            "source.warning_info",
                                            "beat.platform_moid",
                                            "beat.src_type",
                                            "@timestamp"
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
    }
}
