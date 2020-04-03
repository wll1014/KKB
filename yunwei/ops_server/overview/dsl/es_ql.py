#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

from common.my_elastic import ESIndex

direct_up_video_audio_lost_rate_dsl = {
    'index': ESIndex.NMSDssWorkerIndex.value,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "exists": {
                            "field": "source.rtp_info.statis"
                        }
                    },
                    {
                        "match_phrase": {
                            "source.eventid": {
                                "query": "EV_DSS_PORT_STATIS_NOTIFY"
                            }
                        }
                    },
                    {
                        "match_phrase": {
                            "source.direct": {
                                "query": "up"
                            }
                        }
                    },
                    {
                        "bool": {
                            "should": [
                                {
                                    "match_phrase": {
                                        "source.context.chan_type": "video"
                                    }
                                },
                                {
                                    "match_phrase": {
                                        "source.context.chan_type": "audio"
                                    }
                                }
                            ],
                            "minimum_should_match": 1
                        }
                    },
                    {
                        "range": {
                            "@timestamp": {
                                "gte": "now-15m/m"
                            }
                        }
                    }
                ]
            }
        },
        "aggs": {
            "chan_type": {
                "terms": {
                    "field": "source.context.chan_type.keyword",
                    "size": 2
                },
                "aggs": {
                    "statis": {
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
                                "source.rtp_info.statis.rtp_lose.lose_percent.cur",
                                "source.rtp_info.statis.udp_pkt.bytes_rate.cur"
                            ]
                        }
                    }
                }
            }
        }
    }
}
