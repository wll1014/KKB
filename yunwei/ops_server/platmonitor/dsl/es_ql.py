#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

from common.my_elastic import ESIndex

conf_actions_dsl = {
    'index': [ESIndex.MQWatcherIndex.value, ESIndex.NMSCmuIndex.value],
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [],
                "filter": {
                    "range": {
                        "@timestamp": {
                            "gte": "1582601237699",
                            "lte": "now"
                        }
                    }
                },
                "should": [
                    {
                        "match": {
                            "source.type": "MAU_CM_CREATECONF_ACK"  # 创会
                        }
                    },
                    {
                        "match": {
                            "source.type": "MAU_CM_RELEASECONF_NTF"  # 结会通知
                        }
                    },
                    {
                        "match": {
                            "source.type": "CMU_CM_SETCHAIRMAN_ACK"  # 设置管理方
                        }
                    },
                    {
                        "match": {
                            "source.type": "CMU_CM_CANCELCHAIRMAN_ACK"  # 取消管理方
                        }
                    },
                    {
                        "match": {
                            "source.type": "CMU_CM_SETSPEAKER_ACK"  # 设置发言人
                        }
                    },
                    {
                        "match": {
                            "source.type": "CMU_CM_CANCELSPEAKER_ACK"  # 取消发言人
                        }
                    },
                    {
                        "match": {
                            "source.type": "CM_CMU_STARTPOLL_CMD"  # 开始轮询
                        }
                    },
                    {
                        "match": {
                            "source.type": "CM_CMU_RESUMEPOLL_CMD"  # 恢复轮询
                        }
                    },
                    {
                        "match": {
                            "source.type": "CM_CMU_STOPPOLL_CMD"  # 停止轮询
                        }
                    },
                    {
                        "match": {
                            "source.type": "CM_CMU_PAUSEPOLL_CMD"  # 暂停轮询
                        }
                    },
                    {
                        "match": {
                            "source.type": "CMU_CM_STARTVMP_ACK"  # 开始画面合成
                        }
                    },
                    {
                        "match": {
                            "source.type": "CMU_CM_STOPVMP_ACK"  # 停止画面合成
                        }
                    },
                    {
                        "match": {
                            "source.type": "CMU_CM_STARTMIX_ACK"  # 开始混音
                        }
                    },
                    {
                        "match": {
                            "source.type": "CMU_CM_STOPMIX_ACK"  # 停止混音
                        }
                    },
                    {
                        "match": {
                            "source.eventid": "EV_MCU_CONF_MANAGER_CHANGE"  # 管理方切换
                        }
                    },
                    {
                        "match": {
                            "source.eventid": "EV_MCU_CONF_SPEAKER_CHANGE"  # 发言人切换
                        }
                    }
                ],
                "minimum_should_match": 1
            }
        },
        "aggs": {
            "source_type": {
                "terms": {
                    "field": "source.type.keyword",
                    "size": 2147483647
                },
                "aggs": {
                    "time": {
                        "terms": {
                            "size": 2147483647,
                            "field": "@timestamp"
                        }
                    }
                }
            },
            "eventid": {
                "terms": {
                    "size": 2147483647,
                    "field": "source.eventid.keyword"
                },
                "aggs": {
                    "time": {
                        "terms": {
                            "size": 2147483647,
                            "field": "@timestamp"
                        },
                        "aggs": {
                            "top": {
                                "top_hits": {
                                    "size": 1,
                                    "_source": ["source.confinfo.manager", "source.confinfo.speaker"],
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
    }
}

conf_media_type_dsl = {
    'index': ESIndex.MQWatcherIndex.value,
    'dsl': {
        "size": 0,
        "_source": "@timestamp",
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
                            "gte": "1582624835000",
                            "lte": "1582625137000"
                        }
                    }
                }
            }
        },
        "aggs": {
            "time": {
                "terms": {
                    "field": "@timestamp",
                    "size": 2147483647
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
                                "source.media_master.roommoid",
                                "source.confroommoid"
                            ]
                        }
                    }
                }
            }
        }
    }
}
