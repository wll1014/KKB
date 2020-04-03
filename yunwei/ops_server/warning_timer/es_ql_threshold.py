#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

from common.my_elastic import ESIndex

# 磁盘寿命
disk_age_dsl = {
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
                            "gte": "now-30d/m"}}
                }
            }
        },
        "aggs": {
            "status": {
                "terms": {
                    "field": "beat.src_moid.keyword",
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

# 会议协作会议数
dcs_confnum_dsl = {
    'index': ESIndex.NMSDcsIndex.value,
    'dsl': {
        "size": 1,
        "_source": ["source.resinfo.confnum"],
        "query": {
            "bool": {
                "must": [
                    {"match": {"source.eventid": "EV_DCS_RES_INFO"}}
                ],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "gte": "now-30d/m"}}
                }
            }
        },
        "sort": {"@timestamp": {"order": "desc"}}
    }
}

# 会议协作终端数
dcs_mtnum_dsl = {
    'index': ESIndex.NMSDcsIndex.value,
    'dsl': {
        "size": 1,
        "_source": ["source.resinfo.mtnum"],
        "query": {
            "bool": {
                "must": [
                    {"match": {"source.eventid": "EV_DCS_RES_INFO"}}
                ],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "gte": "now-30d/m"}}
                }
            }
        },
        "sort": {"@timestamp": {"order": "desc"}}
    }
}

# 直播观看人数
live_viewer_dsl = {
    'index': ESIndex.NMSVrsIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "source.eventid": "EV_VRS_UPDATE_USER_INFO"
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
        "aggs": {
            "status": {
                "terms": {
                    "field": "source.update_user_info.user_name.keyword"
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
                            "_source": {
                                "includes": [
                                    "source.update_user_info.user_state",
                                    "@timestamp"
                                ]
                            },
                            "size": 1
                        }
                    }
                }
            }
        }
    }
}

# 会议录播
vrs_info_dsl = {
    'index': ESIndex.NMSVrsIndex.value,
    'dsl': {
        "size": 1,
        "_source": ["source.vrs_info.vrs_recroomocp"],
        "query": {
            "bool": {
                "must": [
                    {"match": {"source.eventid": "EV_VRS_INFO"}}
                ],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "gte": "now-30d/m"}}
                }
            }
        },
        "sort": {"@timestamp": {"order": "desc"}}
    }
}

# ap授权
ap_dsl = {
    'index': ESIndex.NMSRmsIndex.value,
    'dsl': {
        "size": 1,
        "_source": [
            "source.ap_info.used",
            "source.ap_info.total"
        ],
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "source.eventid": "EV_RMS_AP_INFO"
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

# mp授权
mp_dsl = {
    'index': ESIndex.NMSRmsIndex.value,
    'dsl': {
        "size": 1,
        "_source": [
            "source.mp_info.used_h264",
            "source.mp_info.used_h265",
            "source.mp_info.total_h264",
            "source.mp_info.total_h265"
        ],
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "source.eventid": "EV_RMS_MP_INFO"
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

# 网卡进口流量
network_in_dsl = {
    'index': ESIndex.MetricBeatIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "metricset.name": "network"
                        }
                    }
                ],
                "must_not": [
                    {
                        "match": {
                            "system.network.name": "lo"
                        }
                    }
                ],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "gte": "now-5m"
                        }
                    }
                }
            }
        },
        "aggs": {
            "machine_terms": {
                "terms": {
                    "field": "beat.eqpid"
                },
                "aggs": {
                    "network_name": {
                        "terms": {
                            "field": "system.network.name"
                        },
                        "aggs": {
                            "time": {
                                "date_histogram": {
                                    "field": "@timestamp",
                                    "interval": "5m",
                                    "format": "yyyy-MM-dd HH:mm:ss",
                                    "time_zone": "+08:00",
                                    "min_doc_count": 0
                                },
                                "aggs": {
                                    "in_bytes": {
                                        "max": {
                                            "field": "system.network.in.bytes"
                                        }
                                    },
                                    "bytes_deriv": {
                                        "derivative": {
                                            "buckets_path": "in_bytes",
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
    }
}

# 网卡出口流量
network_out_dsl = {
    'index': ESIndex.MetricBeatIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "metricset.name": "network"
                        }
                    }
                ],
                "must_not": [
                    {
                        "match": {
                            "system.network.name": "lo"
                        }
                    }
                ],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "gte": "now-5m"
                        }
                    }
                }
            }
        },
        "aggs": {
            "machine_terms": {
                "terms": {
                    "field": "beat.eqpid"
                },
                "aggs": {
                    "network_name": {
                        "terms": {
                            "field": "system.network.name"
                        },
                        "aggs": {
                            "time": {
                                "date_histogram": {
                                    "field": "@timestamp",
                                    "interval": "5m",
                                    "format": "yyyy-MM-dd HH:mm:ss",
                                    "time_zone": "+08:00",
                                    "min_doc_count": 0
                                },
                                "aggs": {
                                    "out_bytes": {
                                        "max": {
                                            "field": "system.network.out.bytes"
                                        }
                                    },
                                    "bytes_deriv": {
                                        "derivative": {
                                            "buckets_path": "out_bytes",
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
    }
}

disk_write_dsl = {
    'index': ESIndex.MetricBeatIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "metricset.name": "diskio"
                        }
                    }
                ],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "gte": "now-5m"
                        }
                    }
                }
            }
        },
        "aggs": {
            "machine_terms": {
                "terms": {
                    "field": "beat.eqpid"
                },
                "aggs": {
                    "network_name": {
                        "terms": {
                            "field": "system.diskio.name"
                        },
                        "aggs": {
                            "time": {
                                "date_histogram": {
                                    "field": "@timestamp",
                                    "interval": "5m",
                                    "format": "yyyy-MM-dd HH:mm:ss",
                                    "time_zone": "+08:00",
                                    "min_doc_count": 0
                                },
                                "aggs": {
                                    "write_bytes": {
                                        "max": {
                                            "field": "system.diskio.write.bytes"
                                        }
                                    },
                                    "bytes_deriv": {
                                        "derivative": {
                                            "buckets_path": "write_bytes",
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
    }
}

# 内存使用率
mem_dsl = {
    'index': ESIndex.MetricBeatIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": {
                    "match": {
                        "metricset.name": "memory"
                    }
                },
                "filter": {
                    "range": {
                        "@timestamp": {
                            "gte": "now-5m"
                        }
                    }
                }
            }
        },
        "aggs": {
            "machine_terms": {
                "terms": {
                    "field": "beat.eqpid"
                },
                "aggs": {
                    "avg_mem": {
                        "avg": {
                            "field": "system.memory.actual.used.pct"
                        }
                    }
                }
            }
        }
    }
}

# 磁盘使用率
filesystem_used_dsl = {
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
                            "gte": "now-5m"
                        }
                    }
                }
            }
        },
        "aggs": {
            "machine_terms": {
                "terms": {
                    "field": "beat.eqpid"
                },
                "aggs": {
                    "status": {
                        "terms": {
                            "field": "system.filesystem.mount_point"
                        },
                        "aggs": {
                            "avg_filesystem_used": {
                                "avg": {
                                    "field": "system.filesystem.used.pct"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

# 各核cpu使用率
cpu_core_idle_dsl = {
    'index': ESIndex.MetricBeatIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "metricset.name": "core"
                        }
                    }
                ],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "gte": "now-5m"
                        }
                    }
                }
            }
        },
        "aggs": {
            "machine_terms": {
                "terms": {
                    "field": "beat.eqpid"
                },
                "aggs": {
                    "status": {
                        "terms": {
                            "field": "system.core.id"
                        },
                        "aggs": {
                            "avg_cpu_core_idle": {
                                "avg": {
                                    "field": "system.core.idle.pct"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

# cpu使用率
cpu_dsl = {
    'index': ESIndex.MetricBeatIndex.value,
    'dsl': {
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
                            "gte": "now-5m"
                        }
                    }
                }
            }
        },
        "aggs": {
            "status": {
                "terms": {
                    "field": "beat.eqpid"
                },
                "aggs": {
                    "avg_cpu_total": {
                        "avg": {
                            "field": "system.cpu.total.pct"
                        }
                    },
                    "avg_core": {
                        "avg": {
                            "field": "system.cpu.cores"
                        }
                    }
                }
            }
        }
    }
}

# mediaresource合成器
mediaresource_vmp_dsl = {
    'index': ESIndex.NMSMediaIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "source.eventid": "EV_MEDIARESOURCE_INFO"
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
        "aggs": {
            "room": {
                "terms": {
                    "field": "beat.roomid.keyword"
                },
                "aggs": {
                    "info": {
                        "top_hits": {
                            "size": 1,
                            "sort": {
                                "@timestamp": {
                                    "order": "desc"
                                }
                            },
                            "_source": [
                                "source.mediaresource_info.total_vmp",
                                "source.mediaresource_info.used_vmp"
                            ]
                        }
                    }
                }
            }
        }
    }
}

# mediaresource混音器
mediaresource_mixer_dsl = {
    'index': ESIndex.NMSMediaIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "source.eventid": "EV_MEDIARESOURCE_INFO"
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
        "aggs": {
            "room": {
                "terms": {
                    "field": "beat.roomid.keyword"
                },
                "aggs": {
                    "info": {
                        "top_hits": {
                            "size": 1,
                            "sort": {
                                "@timestamp": {
                                    "order": "desc"
                                }
                            },
                            "_source": [
                                "source.mediaresource_info.total_mixer",
                                "source.mediaresource_info.used_mixer"
                            ]
                        }
                    }
                }
            }
        }
    }
}

# mps合成器
mps_vmp_dsl = {
    'index': ESIndex.NMSMpsIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "source.eventid": "EV_MPS_INFO"
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
        "aggs": {
            "room": {
                "terms": {
                    "field": "beat.roomid.keyword"
                },
                "aggs": {
                    "info": {
                        "top_hits": {
                            "size": 1,
                            "sort": {
                                "@timestamp": {
                                    "order": "desc"
                                }
                            },
                            "_source": [
                                "source.mps_resource_info.total_vmp",
                                "source.mps_resource_info.used_vmp"
                            ]
                        }
                    }
                }
            }
        }
    }
}

# mps混音器
mps_mixer_dsl = {
    'index': ESIndex.NMSMpsIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "source.eventid": "EV_MPS_INFO"
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
        "aggs": {
            "room": {
                "terms": {
                    "field": "beat.roomid.keyword"
                },
                "aggs": {
                    "info": {
                        "top_hits": {
                            "size": 1,
                            "sort": {
                                "@timestamp": {
                                    "order": "desc"
                                }
                            },
                            "_source": [
                                "source.mps_resource_info.total_mixer",
                                "source.mps_resource_info.used_mixer"
                            ]
                        }
                    }
                }
            }
        }
    }
}

# 直播信息
live_info_dsl = {
    'index': ESIndex.NMSVrsIndex.value,
    'dsl': {
        "size": 1,
        "_source": ["source.vrs_info.vrs_html5lcastocp",
                    "source.vrs_info.vrs_lcastocp"],
        "query": {
            "bool": {
                "must": [
                    {"match": {"source.eventid": "EV_VRS_INFO"}}
                ],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "gte": "now-30d/m"}}
                }
            }
        },
        "sort": {"@timestamp": {"order": "desc"}}
    }
}
