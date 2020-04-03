#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'


from common.my_elastic import ESIndex
# sip信令包获取
sip_packet = {
    'index': ESIndex.SIPProtoIndex.value,
    'dsl': {
        "query": {
            "bool": {
                "must": [],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "lte": "now"
                        }
                    }
                }
            }
        }
    }
}

# 日志获取
logs = {
    'index': ESIndex.APPLogIndex.value,
    'dsl': {
        "query": {
            "bool": {
                "filter": {
                    "range": {
                        "@timestamp": {
                            "lte": "1566199820000",
                            "gte": "1565849800000"
                        }
                    }
                },
                "must": []
            }
        }
    }
}

# 日志类型获取
log_app_types = {
    'index': ESIndex.APPLogIndex.value,
    'dsl': {
        "size": 0,
        "aggs": {
            "app_types": {
                "terms": {
                    "field": "beat.name.keyword",
                    "size": 10000
                }
            }
        }
    }
}

# 终端上下线状态及终端类型获取
mttype_online_offline = {
    'index': ESIndex.NMSMTIndex.value,
    'dsl': {
        "size": 1,
        "_source": ["source.devtype", "source.eventid", "source.collector_moid"],
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "source.eventid": "EV_DEV_OFFLINE || EV_DEV_ONLINE"
                        }
                    }
                ],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "gte": "now-30d/m"
                        }
                    }
                }
            }
        },
        "sort": {
            "@timestamp": {
                "order": "desc"
            }
        }
    }
}

# upuwatcher中查询终端信息
mt_info = {
    'index': ESIndex.UpuWatcherIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [],
                "filter": [
                    {
                        "range": {
                            "@timestamp": {
                                "gte": "now-1w/m"
                            }
                        }
                    }
                ]
            }
        },
        "aggs": {
            "mt_e164": {
                "terms": {
                    "field": "source.e164.keyword",
                    "size": 100000
                },
                "aggs": {
                    "top": {
                        "top_hits": {
                            "size": 1,
                            "_source": [
                                "source"
                            ],
                            "sort": [
                                {
                                    "@timestamp": {
                                        "order": "desc"
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }
    }
}
