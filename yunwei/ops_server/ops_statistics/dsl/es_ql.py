#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

from common.my_elastic import ESIndex

# 查询硬件资源topN
# cpu/memory
cpu_memory = {
    "size": 0,
    "query": {
        "bool": {
            "must": [
                {
                    "match": {
                        "metricset.name": "cpu"
                    }
                }
            ],
            "filter": {
                "range": {
                    "@timestamp": {
                        "gte": "2018-01-01",
                    }
                }
            }
        }
    },
    "aggs": {
        "2": {
            "date_histogram": {
                "interval": "2m",
                "field": "@timestamp",
                "time_zone": "+08:00",
                "min_doc_count": 1,
                "format": "epoch_millis",
                "extended_bounds": {
                    "max": "now"
                }
            },
            "aggs": {
                "1": {
                    "avg": {
                        "field": "system.cpu.total.pct"
                    }
                }
            }
        }
    }
}

# 磁盘分区
disk_used = {
    'index': ESIndex.MetricBeatIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": {
                    "match": {
                        "metricset.name": "filesystem"
                    }
                },
                "filter": {
                    "range": {
                        "@timestamp": {
                            "gte": "now-1d"
                        }
                    }
                }
            }
        },
        "aggs": {
            "eqpid": {
                "terms": {
                    "field": "beat.eqpid",
                    "size": 1000
                },
                "aggs": {
                    "mount_point": {
                        "terms": {
                            "field": "system.filesystem.mount_point",
                            "size": 1000
                        },
                        "aggs": {
                            "top_date_hits": {
                                "top_hits": {
                                    "size": 1,
                                    "sort": [
                                        {
                                            "@timestamp": {
                                                "order": "desc"
                                            }
                                        }
                                    ],
                                    "_source": {
                                        "includes": [
                                            "system.filesystem.used.pct",
                                            "beat.eqpid"
                                        ]
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

# 磁盘寿命
diskage = {
    'index': ESIndex.MachineIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {"match": {"source.eventid": "EV_PFMINFO_DISK_AGE"}}
                ],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "gte": "2018-01-01"}}
                }
            }
        },
        "aggs": {
            "status": {
                "terms": {
                    "field": "beat.eqpid.keyword",
                    "size": 10000},
                "aggs": {
                    "top_date_hits": {
                        "top_hits": {
                            "sort": [
                                {"@timestamp": {"order": "desc"}}],
                            "_source": {"includes": ["source.diskage.dev", "source.diskage.age"]},
                            "size": 1
                        }
                    }
                }
            }
        }
    }
}

# 网卡流量
network = {
    'index': ESIndex.MetricBeatIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {"match": {"metricset.name": "network"}}],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "gte": "now-2d"}
                    }
                }
            }

        },
        "aggs": {
            "network_name": {"terms": {"field": "system.network.name",
                                       "size": 10000},
                             "aggs": {
                                 "2": {
                                     "date_histogram": {
                                         "field": "@timestamp",
                                         "interval": "300m",
                                         "format": "yyyy-MM-dd HH:mm:ss",
                                         "time_zone": "+08:00",
                                         "min_doc_count": 1,
                                         "extended_bounds": {
                                             "max": "now"
                                         }
                                     },
                                     "aggs": {
                                         "bytes": {
                                             "max": {"field": "system.network.in.bytes"}
                                         },
                                         "bytes_deriv": {
                                             "derivative": {
                                                 "buckets_path": "bytes",
                                                 "unit": "1s"
                                             }
                                         }
                                     }
                                 }
                             }
                             }
        }
    }
}

# ------------------------------------------------------------------------------------------------
# 正在召开点对点会议
now_p2p_conf = {
    'index': ESIndex.NMSPasIndex.value,
    # 'index': ESIndex.AdsPasP2PIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "filter": {
                    "range": {
                        "@timestamp": {
                            "gte": "2018-01-01"
                        }
                    }
                },
                "must": [
                    {
                        "match": {
                            "source.eventid": "EV_PAS_INFO"
                        }
                    }
                ]
            }
        },
        "aggs": {
            "dev_moid": {
                "terms": {
                    "field": "beat.dev_moid.keyword",
                    "size": 10000
                },
                "aggs": {
                    "top": {
                        "top_hits": {
                            "size": 1,
                            "sort": [
                                {
                                    "@timestamp": {
                                        "order": "desc"
                                    }
                                }
                            ],
                            "_source": [
                                "source.pasinfo.confmtcount"
                            ]
                        }
                    }
                }
            }
        }
    }
}

# 终端在线数量
curr_terminal = {
    'index': ESIndex.NMSPasIndex.value,
    'dsl': {
        "query": {
            "bool": {
                "filter": {
                    "range": {
                        "@timestamp": {
                            "gte": "1564830435000",
                            "lte": "1565089840000"
                        }
                    }
                },
                "must": [
                    {
                        "match": {
                            "source.eventid": "EV_PAS_INFO"
                        }
                    },
                    {
                        "match": {
                            "beat.src_type": "pas"
                        }
                    }
                ]
            }
        },
        "size": 0,
        "aggs": {
            "time": {
                "date_histogram": {
                    "interval": "2165000ms",
                    "format": "epoch_millis",
                    "time_zone": "+08:00",
                    "extended_bounds": {
                        "max": 1565089840000,
                        "min": 1564830435000
                    },
                    "min_doc_count": 1,
                    "field": "@timestamp"
                },
                "aggs": {
                    "dev": {
                        "terms": {
                            "field": "source.devid.keyword",
                            "size": 10000
                        },
                        "aggs": {
                            "h323": {
                                "avg": {
                                    "field": "source.pasinfo.h323onlinecount"
                                }
                            },
                            "sip": {
                                "avg": {
                                    "field": "source.pasinfo.siponlinecount"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

# ------------------------------------------------------------------------------------------------
# 终端呼叫数量
calling_terminal = {
    'index': ESIndex.NMSPasIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "filter": {
                    "range": {
                        "@timestamp": {
                            "gte": "1567258998989",
                            "lte": "1567345800000"
                        }
                    }
                },
                "must": [
                    {
                        "match": {
                            "source.eventid": "EV_PAS_INFO"
                        }
                    },
                    {
                        "match": {
                            "beat.src_type": "pas"
                        }
                    }
                ]
            }
        },
        "aggs": {
            "time": {
                "date_histogram": {
                    "interval": "2170000ms",
                    "field": "@timestamp",
                    "time_zone": "+08:00",
                    "min_doc_count": 0,
                    "format": "epoch_millis",
                    "extended_bounds": {
                        "max": 1567345800000,
                        "min": 1567258998989
                    }
                },
                "aggs": {
                    "dev": {
                        "terms": {
                            "field": "source.devid.keyword",
                            "size": 10000
                        },
                        "aggs": {
                            "callingcount": {
                                "avg": {
                                    "field": "source.pasinfo.callingcount"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

# 接入端口统计
now_ap = {
    'index': ESIndex.NMSRmsIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "source.eventid": "EV_RMS_AP_INFO"
                        }
                    },
                    {
                        "regexp": {
                            "source.ap_info.moid": ".{12}"
                        }
                    }
                ],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "lte": "now"
                        }
                    }
                }
            }
        },
        "aggs": {
            "ap_info_moid": {
                "terms": {
                    "field": "source.ap_info.moid.keyword",
                    "size": 10000
                },
                "aggs": {
                    "top": {
                        "top_hits": {
                            "size": 1,
                            "sort": [
                                {
                                    "@timestamp": {
                                        "order": "desc"
                                    }
                                }
                            ],
                            "_source": [
                                "source.ap_info.total",
                                "source.ap_info.used",
                            ]
                        }
                    }
                }
            }
        }
    }
}

terminals_statistics = {
    'index': ESIndex.NMSPasIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "source.eventid": "EV_PAS_INFO"
                        }
                    }
                ],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "lte": "now"
                        }
                    }
                }
            }
        },
        "aggs": {
            "time": {
                "date_histogram": {
                    "interval": "2160250ms",
                    "field": "@timestamp",
                    "time_zone": "+08:00",
                    "min_doc_count": 0,
                    "format": "epoch_millis",
                    "extended_bounds": {
                        "max": 1567347430000,
                        "min": 1567261030000
                    }
                },
                "aggs": {
                    "pas": {
                        "terms": {
                            "field": "source.devid.keyword",
                            "size": 10000
                        },
                        "aggs": {
                            "curonlinecount": {
                                "avg": {
                                    "field": "source.pasinfo.curonlinecount"
                                }
                            },
                            "callingcount": {
                                "avg": {
                                    "field": "source.pasinfo.callingcount"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

# 转发资源
now_bandwidth = {
    'index': ESIndex.NMSDssMasterIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "source.eventid": "EV_DSS_RESOURCE_NOTIFY"
                        }
                    }
                ],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "lte": "now",
                            "gte": "now-5m/m"
                        }
                    }
                }
            }
        },
        "aggs": {
            "devid": {
                "terms": {
                    "field": "source.devid.keyword",
                    "size": 10000
                },
                "aggs": {
                    "top": {
                        "top_hits": {
                            "size": 1,
                            "_source": [
                                "source.bandwidth"
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

dss_bandwidth = {
    'index': ESIndex.NMSDssMasterIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "source.eventid": "EV_DSS_RESOURCE_NOTIFY"
                        }
                    }
                ],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "lte": "1565764205259",
                            "gte": "1565677805259"
                        }
                    }
                }
            }
        },
        "aggs": {
            "time": {
                "date_histogram": {
                    "interval": "2160000ms",
                    "field": "@timestamp",
                    "time_zone": "+08:00",
                    "min_doc_count": 0,
                    "format": "epoch_millis",
                    "extended_bounds": {
                        "max": 1565764205259,
                        "min": 1565677805259
                    }
                },
                "aggs": {
                    "devid": {
                        "terms": {
                            "field": "source.devid.keyword"
                        },
                        "aggs": {
                            "bandwidth_total": {
                                "avg": {
                                    "field": "source.bandwidth.total"
                                }
                            },
                            "bandwidth_used": {
                                "avg": {
                                    "field": "source.bandwidth.used"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

# 召开的多点会议统计
now_conf_statistics = {
    'index': ESIndex.MQWatcherIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [{
                    "match": {
                        "source.type": "MCU_MAU_CONFLIST_NTF"
                    }
                }],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "lte": "now"
                        }
                    }
                }
            }
        },
        "sort": [
            {
                "@timestamp": {
                    "order": "desc"
                }
            }
        ],
        "aggs": {
            "cmumoid": {
                "terms": {
                    "field": "source.cmumoid.keyword"
                },
                "aggs": {
                    "top": {
                        "top_hits": {
                            "sort": {
                                "@timestamp": {
                                    "order": "desc"
                                }
                            },
                            "size": 1,
                            "_source": [
                                "source.confdatainfo.confE164",
                                "source.confdatainfo.mtnum"
                            ]
                        }
                    }
                }
            }
        }
    }
}
conf_statistics = {
    'index': ESIndex.MQWatcherIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "source.type": "MCU_MAU_CONFLIST_NTF"
                        }
                    }
                ],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "lte": "now"
                        }
                    }
                }
            }
        },
        "aggs": {
            "time": {
                "date_histogram": {
                    "field": "@timestamp",
                    "interval": "2160250ms",
                    "format": "yyyy-MM-dd HH:mm:ss",
                    "time_zone": "+08:00",
                    "min_doc_count": 0,
                    "extended_bounds": {
                        "max": 1564994460000,
                        "min": 1564908050000
                    }
                },
                "aggs": {
                    "cmumoid": {
                        "terms": {
                            "field": "source.cmumoid.keyword"
                        },
                        "aggs": {
                            "confdatainfo_length": {
                                "max": {
                                    "script": {
                                        "source": "doc['source.confdatainfo.confE164.keyword'].values.size()"
                                    }
                                }
                            },
                            "confdatainfo": {
                                "top_hits": {
                                    "size": 1,
                                    "sort": [
                                        {
                                            "@timestamp": {
                                                "order": "desc"
                                            }
                                        }
                                    ],
                                    "_source": {
                                        "includes": "source.confdatainfo.confE164"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

p2p_conf_statistics = {
    'index': ESIndex.NMSPasIndex.value,
    # 'index': ESIndex.AdsPasP2PIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "source.eventid": "EV_PAS_INFO"
                        }
                    }
                ],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "gte": "1564542310000",
                            "lte": "1564628710000"
                        }
                    }
                }
            }
        },
        "aggs": {
            "time": {
                "date_histogram": {
                    "field": "@timestamp",
                    "interval": "2160000ms",
                    "format": "epoch_millis",
                    "time_zone": "+08:00",
                    "min_doc_count": 0,
                    "extended_bounds": {
                        "max": 1564628710000,
                        "min": 1564542310000
                    }
                },
                "aggs": {
                    "pas": {
                        "terms": {
                            "field": "beat.dev_moid.keyword",
                            "size": 10000
                        },
                        "aggs": {
                            "confmtcount": {
                                "avg": {
                                    "field": "source.pasinfo.confmtcount"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

# 创会方式
create_conf_type = {
    'index': ESIndex.MQWatcherIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "source.type": "CM_MAU_CREATECONF_REQ"
                        }
                    }
                ],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "lte": "1564994460000",
                            "gte": "1564908050000"
                        }
                    }
                }
            }
        },
        "sort": {
            "@timestamp": {
                "order": "desc"
            }
        },
        "aggs": {
            "time": {
                "date_histogram": {
                    "field": "@timestamp",
                    "interval": "2160250ms",
                    "format": "yyyy-MM-dd HH:mm:ss",
                    "time_zone": "+08:00",
                    "min_doc_count": 0,
                    "extended_bounds": {
                        "max": 1564994460000,
                        "min": 1564908050000
                    }
                },
                "aggs": {
                    "meetingID": {
                        "terms": {
                            "field": "source.meetingID.keyword",
                            "size": 10000
                        },
                        "aggs": {
                            "requestorigin": {
                                "terms": {
                                    "field": "source.requestorigin.keyword",
                                    "size": 10000
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

# 企业创会方式数量统计详情列表
create_conf_type_num_list = {
    'index': ESIndex.MQWatcherIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "source.type": "CM_MAU_CREATECONF_REQ"
                        }
                    }
                ],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "lte": "1564994460000",
                            "gte": "1560908050000"
                        }
                    }
                }
            }
        },
        "aggs": {
            "domain": {
                "terms": {
                    "field": "source.moid.keyword",
                    "size": 10000
                },
                "aggs": {
                    "meetingID": {
                        "terms": {
                            "field": "source.meetingID.keyword",
                            "size": 10000
                        },
                        "aggs": {
                            "requestorigin": {
                                "terms": {
                                    "field": "source.requestorigin.keyword",
                                    "size": 10000
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

# 企业会议数统计
company_conf_statistics = {
    'index': ESIndex.MQWatcherIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "source.type": "MAU_CM_CREATECONF_ACK"
                        }
                    }
                ],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "gte": "1565695970000",
                            "lte": "1565782380000"
                        }
                    }
                }
            }
        },
        "aggs": {
            "confinfo": {
                "terms": {
                    "field": "source.moid.keyword",
                    "size": 10000
                },
                "aggs": {
                    "meetingID": {
                        "terms": {
                            "field": "source.meetingID.keyword",
                            "size": 10000
                        }
                    }
                }
            }
        }
    }
}

# 用于过滤创会的机房
company_conf_room_statistics = {
    'index': ESIndex.MQWatcherIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "source.type": "MAU_MCU_CREATECONF_REQ"
                        }
                    }
                ],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "gte": "1565695970000",
                            "lte": "1565782380000"
                        }
                    }
                }
            }
        },
        "aggs": {
            "meetingID": {
                "terms": {
                    "field": "source.meetingID.keyword",
                    "size": 10000
                }
            }
        }
    }

}

# 创会耗时统计
create_conf_req2ack_time = {
    'index': ESIndex.MQWatcherIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "source.type": "CM_MAU_CREATECONF_REQ || MAU_CM_CREATECONF_ACK"
                        }
                    }
                ],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "lte": "now",
                            "gte": "now-24h/h"
                        }
                    }
                }
            }
        },
        "aggs": {
            "meetingID": {
                "terms": {
                    "field": "source.meetingID.keyword",
                    "size": 10000
                },
                "aggs": {
                    "correlation_id": {
                        "terms": {
                            "field": "beat.headers.properties.correlation_id.keyword",
                            "size": 10000
                        },
                        "aggs": {
                            "timestamp": {
                                "terms": {
                                    "field": "@timestamp",
                                    "size": 10000
                                }
                            }
                        }
                    },
                    "meeting_info": {
                        "top_hits": {
                            "size": 1,
                            "_source": [
                                "source.confE164",
                                "source.meetingID",
                                "source.confname",
                                "source.type",
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

# 获取最新的结会信息
now_release_conf_statistics = {
    'index': ESIndex.MQWatcherIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "source.type": "MAU_CM_RELEASECONF_NTF"
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
        "aggs": {
            "meetingid": {
                "terms": {
                    "field": "source.meetingID.keyword",
                    "size": 10000
                },
                "aggs": {
                    "confe164": {
                        "terms": {
                            "field": "source.confE164.keyword"
                        }
                    }
                }
            }
        }
    }
}

all_release_conf_count = {
    'index': ESIndex.MQWatcherIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "source.type": "MAU_CM_RELEASECONF_NTF"
                        }
                    }
                ]
            }
        },
        "aggs": {
            "conf_count": {
                "cardinality": {
                    "field": "source.meetingID.keyword"
                }
            }
        }
    }
}

all_create_conf_time_statistics = {
    'index': ESIndex.MQWatcherIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "source.type": "MAU_CM_CREATECONF_ACK"
                        }
                    }
                ],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "lte": "now"
                        }
                    }
                }
            }
        },
        "aggs": {
            "meetingID": {
                "terms": {
                    "field": "source.meetingID.keyword",
                    "size": 10000
                },
                "aggs": {
                    "timestamp": {
                        "terms": {
                            "field": "@timestamp"
                        }
                    },
                    "confE164": {
                        "terms": {
                            "field": "source.confE164.keyword"
                        }
                    }
                }
            }
        }
    }
}

# mediamaster资源
now_mediamaster_resource = {
    'index': [ESIndex.NMSMediaIndex.value, ESIndex.MQWatcherIndex.value],
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "should": [

                ],
                "minimum_should_match": 1,
                "filter": {
                    "range": {
                        "@timestamp": {
                            "lte": "now"
                        }
                    }
                }
            }
        },
        "aggs": {
            "roomid": {
                "terms": {
                    "field": "beat.roomid.keyword",
                    "size": 10000
                },
                "aggs": {
                    "top": {
                        "top_hits": {
                            "size": 1,
                            "sort": [
                                {
                                    "@timestamp": {
                                        "order": "desc"
                                    }
                                },
                                {
                                    "_score": {
                                        "order": "asc"
                                    }
                                }
                            ],
                            "_source": [
                                "source.room_res_info"
                            ]
                        }
                    }
                }
            },
            "cmumoid": {
                "terms": {
                    "field": "source.cmumoid.keyword",
                    "size": 10000
                },
                "aggs": {
                    "cmu_top": {
                        "top_hits": {
                            "size": 1,
                            "sort": [
                                {
                                    "@timestamp": {
                                        "order": "desc"
                                    }
                                },
                                {
                                    "_score": {
                                        "order": "desc"
                                    }
                                }
                            ],
                            "_source": [
                                "source.confdatainfo.confE164",
                                "source.roommoid"
                            ]
                        }
                    }
                }
            }
        }
    }
}

mediamaster_resource = {
    'index': [ESIndex.NMSMediaIndex.value, ESIndex.MQWatcherIndex.value],
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "should": [],
                "must": [],
                "minimum_should_match": 1,
                "filter": {
                    "range": {
                        "@timestamp": {
                            "lte": "1567508736832",
                            "gte": "1567422336832"
                        }
                    }
                }
            }
        },
        "aggs": {
            "time": {
                "date_histogram": {
                    "field": "@timestamp",
                    "interval": "2160000ms",
                    "format": "yyyy-MM-dd HH:mm:ss",
                    "time_zone": "+08:00",
                    "min_doc_count": 0,
                    "extended_bounds": {
                        "max": 1567508736832,
                        "min": 1567422336832
                    }
                },
                "aggs": {
                    "last_one": {
                        "top_hits": {
                            "size": 1,
                            "_source": ["source.room_res_info"],
                            "sort": [
                                {
                                    "_score": {
                                        "order": "asc"
                                    }
                                },
                                {
                                    "@timestamp": {
                                        "order": "desc"
                                    }
                                }
                            ]
                        }
                    },
                    "cmumoid": {
                        "terms": {
                            "field": "source.cmumoid.keyword"
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
                                            "_score": {
                                                "order": "desc"
                                            }
                                        },
                                        {
                                            "@timestamp": {
                                                "order": "desc"
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    },
                }
            }
        }
    }
}

base_vrs_info = {
    'index': ESIndex.NMSVrsIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "source.eventid": "EV_VRS_UPDATE_USER_INFO "
                                              "|| EV_VRS_DESTROY_LIVE_INFO "
                                              "|| EV_VRS_CREATE_LIVE_INFO"
                        }
                    }
                ],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "lte": "now"
                        }
                    }
                }
            }
        },
        "aggs": {
            "conf_e164": {
                "terms": {
                    "field": "source.update_user_info.conf_e164.keyword",
                    "size": 10000
                },
                "aggs": {
                    "user_moid": {
                        "terms": {
                            "field": "source.update_user_info.user_moid.keyword",
                            "size": 10000
                        },
                        "aggs": {
                            "user_state": {
                                "terms": {
                                    "field": "source.update_user_info.user_state",
                                    "size": 10000
                                }
                            }
                        }
                    }
                }
            },
            "destroy_live_conf_e164": {
                "terms": {
                    "field": "source.destroy_live_info.conf_e164.keyword",
                    "size": 10000
                }
            },
            "create_live_conf_e164": {
                "terms": {
                    "field": "source.create_live_info.conf_e164.keyword",
                    "size": 10000
                }
            }
        }
    }
}

base_vrs_resources_info = {
    'index': ESIndex.NMSVrsIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "source.eventid": "EV_VRS_INFO"
                        }
                    }
                ],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "lte": "now"
                        }
                    }
                }
            }
        },
        "aggs": {
            "dev_moid": {
                "terms": {
                    "field": "beat.dev_moid.keyword",
                    "size": 1000
                },
                "aggs": {
                    "top": {
                        "top_hits": {
                            "size": 1,
                            "sort": [
                                {
                                    "@timestamp": {
                                        "order": "desc"
                                    }
                                }
                            ],
                            "_source": {"includes": "source"}
                        }
                    }
                }
            }
        }
    }
}

# rediswatcher采集的媒体资源信息
now_media_resource_from_rediswatcher_dsl = {
    'index': ESIndex.RedisWatcherIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "gte": "now-30m/m",
                            "lte": "now"
                        }
                    }
                }
            }
        },
        "aggs": {
            "room": {
                "terms": {
                    "field": "beat.roomid.keyword",
                    "size": 1000
                },
                "aggs": {
                    "top": {
                        "top_hits": {
                            "size": 1,
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

# 服务器运行数量
service_running_count = {
    "size": 0,
    "aggs": {
        "filtered": {
            "filter": {
                "range": {
                    "@timestamp": {
                        "gte": "now-1h",
                        "lte": "now"
                    }
                }
            },
            "aggs": {
                "ServiceId": {
                    "terms": {
                        "field": "beat.eqpid",
                        "size": 10000
                    }
                }
            }
        }
    }
}
