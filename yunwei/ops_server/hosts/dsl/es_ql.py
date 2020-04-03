#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

from common.my_elastic import ESIndex

top_cpu_processes_dsl = {
    'index': ESIndex.MetricBeatIndex.value,
    'dsl': {
        "from": 0,
        "size": 0,
        "query": {
            "bool": {
                "filter": [
                    {
                        "range": {
                            "@timestamp": {
                                "gte": "now-15m/m",
                                "lte": "now"
                            }
                        }
                    }
                ],
                "must": [
                    {
                        "match": {
                            "metricset.name": "process"
                        }
                    }
                ]
            }
        },
        "aggs": {
            "pid": {
                "terms": {
                    "size": "10",
                    "order": {
                        "avg_cpu_pct": "desc"
                    },
                    "field": "system.process.pid"
                },
                "aggs": {
                    "avg_cpu_pct": {
                        "avg": {
                            "field": "system.process.cpu.total.norm.pct"
                        }
                    },
                    "top": {
                        "top_hits": {
                            "size": 1,
                            "_source": [
                                "system.process.name"
                            ]
                        }
                    }
                }
            }
        }
    }
}

top_mem_processes_dsl = {
    'index': ESIndex.MetricBeatIndex.value,
    'dsl': {
        "from": 0,
        "size": 0,
        "query": {
            "bool": {
                "filter": [],
                "must": [
                    {
                        "match": {
                            "metricset.name": "process"
                        }
                    }
                ]
            }
        },
        "aggs": {
            "pid": {
                "terms": {
                    "size": "10",
                    "order": {
                        "avg_mem_pct": "desc"
                    },
                    "field": "system.process.pid"
                },
                "aggs": {
                    "avg_mem_pct": {
                        "avg": {
                            "field": "system.process.memory.rss.pct"
                        }
                    },
                    "top": {
                        "top_hits": {
                            "size": 1,
                            "_source": [
                                "system.process.name"
                            ]
                        }
                    }
                }
            }
        }
    }
}
