#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

from common.my_elastic import ESIndex

auto_buckets_count = 200

# 并发会议数量峰值
concurrent_confs_peak_num_dsl = {
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
                            "lte": "now/m",
                            "gte": "now-24h/m"
                        }
                    }
                }
            }
        },
        "aggs": {
            "time": {
                "auto_date_histogram": {
                    "field": "@timestamp",
                    "buckets": auto_buckets_count,
                    "time_zone": "+08:00"
                },
                "aggs": {
                    "dev": {
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
                            }
                        }
                    }
                }
            }
        }
    }
}

# 在线终端数量峰值
online_terminals_peak_num_dsl = {
    'index': ESIndex.NMSPasIndex.value,
    'dsl': {
        "query": {
            "bool": {
                "filter": {
                    "range": {
                        "@timestamp": {
                            "lte": "now/m",
                            "gte": "now-24h/m"
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
                "auto_date_histogram": {
                    "field": "@timestamp",
                    "buckets": auto_buckets_count,
                    "time_zone": "+08:00"
                },
                "aggs": {
                    "dev": {
                        "terms": {
                            "field": "source.devid.keyword",
                            "size": 100
                        },
                        "aggs": {
                            "curonlinecount": {
                                "max": {
                                    "field": "source.pasinfo.curonlinecount"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

# 呼叫终端数量峰值
calls_terminals_peak_num_dsl = {
    'index': ESIndex.NMSPasIndex.value,
    'dsl': {
        "query": {
            "bool": {
                "filter": {
                    "range": {
                        "@timestamp": {
                            "lte": "now/m",
                            "gte": "now-24h/m"
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
                "auto_date_histogram": {
                    "field": "@timestamp",
                    "buckets": auto_buckets_count,
                    "time_zone": "+08:00"
                },
                "aggs": {
                    "dev": {
                        "terms": {
                            "field": "source.devid.keyword",
                            "size": 100
                        },
                        "aggs": {
                            "callingcount": {
                                "max": {
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

# cpu 使用率 top服务器
cpu_top_machines_dsl = {
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
                            "lte": "now/m",
                            "gte": "now-24h/m"
                        }
                    }
                }
            }
        },
        "aggs": {
            "eqpid": {
                "terms": {
                    "field": "beat.eqpid",
                    "size": 100
                },
                "aggs": {
                    "time": {
                        "auto_date_histogram": {
                            "field": "@timestamp",
                            "buckets": auto_buckets_count,
                            "time_zone": "+08:00"
                        },
                        "aggs": {
                            "avg_idle": {
                                "avg": {
                                    "field": "system.cpu.idle.pct"
                                }
                            },
                            "avg_cores": {
                                "avg": {
                                    "field": "system.cpu.cores"
                                }
                            },
                            "used_pct": {
                                "bucket_script": {
                                    "buckets_path": {
                                        "idle_pct": "avg_idle",
                                        "cores": "avg_cores"
                                    },
                                    "script": "1 - (params.idle_pct / params.cores)"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

# 内存使用率 top服务器
mem_top_machines_dsl = {
    'index': ESIndex.MetricBeatIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "metricset.name": "memory"
                        }
                    }
                ],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "lte": "now/m",
                            "gte": "now-24h/m"
                        }
                    }
                }
            }
        },
        "aggs": {
            "eqpid": {
                "terms": {
                    "field": "beat.eqpid",
                    "size": 10000
                },
                "aggs": {
                    "actual_used_pct": {
                        "max": {
                            "field": "system.memory.actual.used.pct"
                        }
                    }
                }
            }
        }
    }
}

# 分区使用率 top服务器
disk_top_machines_dsl = {
    'index': ESIndex.MetricBeatIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "metricset.name": "filesystem"
                        }
                    }
                ],
                "must_not": [
                    {
                        "match": {
                            "system.filesystem.type": "overlay"
                        }
                    },
                    {
                        "match": {
                            "system.filesystem.type": "fuse.glusterfs"
                        }
                    }
                ],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "lte": "now/m",
                            "gte": "now-24h/m"
                        }
                    }
                }
            }
        },
        "aggs": {
            "eqpid": {
                "terms": {
                    "field": "beat.eqpid",
                    "size": 10000
                },
                "aggs": {
                    "mount_point": {
                        "terms": {
                            "field": "system.filesystem.mount_point"
                        },
                        "aggs": {
                            "filesystem_used_pct": {
                                "max": {
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

# 转发资源使用率统计
transmit_resource_dsl = {
    'index': ESIndex.NMSDssMasterIndex.value,
    'dsl': {
        "aggs": {
            "time": {
                "auto_date_histogram": {
                    "field": "@timestamp",
                    "buckets": auto_buckets_count,
                    "time_zone": "+08:00"
                },
                "aggs": {
                    "bandwidth_used": {
                        "avg": {
                            "field": "source.bandwidth.used"
                        }
                    },
                    "bandwidth_total": {
                        "avg": {
                            "field": "source.bandwidth.total"
                        }
                    },
                    "bandwidth_used_pct": {
                        "bucket_script": {
                            "buckets_path": {
                                "bandwidth_used": "bandwidth_used",
                                "bandwidth_total": "bandwidth_total"
                            },
                            "script": "params.bandwidth_used / params.bandwidth_total"
                        }
                    }
                }
            }
        },
        "size": 0,
        "stored_fields": [
            "*"
        ],
        "docvalue_fields": [
            {
                "field": "@timestamp",
                "format": "date_time"
            }
        ],
        "query": {
            "bool": {
                "must": [],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "lte": "now/m",
                            "gte": "now-24h/m"
                        }
                    }
                }
            }
        }
    }
}


# 时间范围内的会议列表
total_confs_dsl = {
    'index': ESIndex.NMSCmuIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "source.eventid": "EV_MCU_CONF_CREATE || EV_MCU_MT_ADD || EV_MCU_MT_DEL"
                        }
                    }
                ],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "gte": "now-24h/m",
                            "lte": "now"
                        }
                    }
                }
            }
        },
        "aggs": {
            "mt_conf_e164": {
                "terms": {
                    "field": "source.mtinfo.confe164.keyword",
                    "size": 100000
                },
                "aggs": {
                    "eventid": {
                        "terms": {
                            "field": "source.eventid.keyword",
                            "size": 100000
                        }
                    }
                }
            },
            "conf_conf_e164": {
                "terms": {
                    "field": "source.confinfo.confe164.keyword",
                    "size": 100000
                },
                "aggs": {
                    "timestamp": {
                        "terms": {
                            "field": "source.confinfo.begintime.keyword",
                            "size": 100000
                        },
                        "aggs": {
                            "confinfo": {
                                "top_hits": {
                                    "size": 1,
                                    "_source": {
                                        "includes": [
                                            "source.confinfo"
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

total_confs_end_time_dsl = {
    'index': ESIndex.NMSCmuIndex.value,
    'dsl': {
        "size": 1,
        "_source": ['source.confinfo'],
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "source.eventid": "EV_MCU_CONF_DESTROY"
                        }
                    }
                ],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "gte": "1575423008000"
                        }
                    }
                }
            }
        },
        "sort": [
            {
                "@timestamp": {
                    "order": "asc"
                }
            }
        ]
    }
}
