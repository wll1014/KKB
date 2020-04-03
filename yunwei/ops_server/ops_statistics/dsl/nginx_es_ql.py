#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

from common.my_elastic import ESIndex

INDEX = ESIndex.NGINXIndex.value

outline_dsl = {
    'index': INDEX,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [],
                "filter": {
                    "range": {
                        "@timestamp": {}
                    }
                }
            }
        },
        "aggs": {
            "time": {
                "date_histogram": {
                    "field": "@timestamp",
                    "interval": "1d",
                    "extended_bounds": {

                    }
                },
                "aggs": {
                    "uv": {
                        "cardinality": {
                            "field": "remote_addr.keyword"
                        }
                    },
                    "avg_request_time": {
                        "avg": {
                            "field": "request_time"
                        }
                    }
                }
            },
            "avg_bucket_request_time": {
                "avg_bucket": {
                    "buckets_path": "time>avg_request_time"
                }
            },
            "sum_bucket_uv": {
                "sum_bucket": {
                    "buckets_path": "time>uv"
                }
            }
        }
    }
}

request_traffic_dsl = {
    'index': INDEX,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [],
                "filter": {
                    "range": {
                        "@timestamp": {}
                    }
                }
            }
        },
        "aggs": {
            "time": {
                "date_histogram": {
                    "field": "@timestamp",
                    "interval": "30m",
                    "extended_bounds": {}
                },
                "aggs": {
                    "sum_body_bytes_sent": {
                        "sum": {
                            "field": "body_bytes_sent"
                        }
                    }
                }
            }
        }
    }
}

pv_dsl = {
    'index': INDEX,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [],
                "filter": {
                    "range": {
                        "@timestamp": {}
                    }
                }
            }
        },
        "aggs": {
            "time": {
                "date_histogram": {
                    "field": "@timestamp",
                    "interval": "1h",
                    "extended_bounds": {}
                }
            }
        }
    }
}

ip_info_dsl = {
    'index': INDEX,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [],
                "filter": {
                    "range": {
                        "@timestamp": {}
                    }
                }
            }
        },
        "aggs": {
            "remote_addr": {
                "terms": {
                    "field": "remote_addr.keyword",
                    "size": 2147483647
                }
            }
        }
    }
}

slow_responses_or_url_dsl = {
    'index': INDEX,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [],
                "must_not": [],
                "filter": {
                    "range": {
                        "@timestamp": {}
                    }
                }
            }
        },
        "aggs": {
            "uri": {
                "terms": {
                    "field": "request_uri.keyword",
                    "size": 2147483647
                }
            }
        }
    }
}

clients_pct_dsl = {
    'index': INDEX,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [],
                "must_not": [],
                "filter": {
                    "range": {
                        "@timestamp": {}
                    }
                }
            }
        },
        "aggs": {
            "clients": {
                "filters": {
                    "other_bucket_key": "other",
                    "filters": {
                        "firefox": {
                            "bool": {
                                "must": [
                                    {
                                        "match": {
                                            "http_user_agent": "firefox"
                                        }
                                    }
                                ]
                            }
                        },
                        "chrome": {
                            "bool": {
                                "must": [
                                    {
                                        "match": {
                                            "http_user_agent": "chrome"
                                        }
                                    }
                                ]
                            }
                        },
                        "movision": {
                            "bool": {
                                "must": [
                                    {
                                        "match": {
                                            "http_user_agent": "movision"
                                        }
                                    }
                                ]
                            }
                        },
                        "ie": {
                            "bool": {
                                "must": [
                                    {
                                        "bool": {
                                            "should": [
                                                {
                                                    "match": {
                                                        "http_user_agent": "trident"
                                                    }
                                                },
                                                {
                                                    "match": {
                                                        "http_user_agent": "msie"
                                                    }
                                                }
                                            ],
                                            "minimum_should_match": 1
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

clients_dsl = {
    'index': INDEX,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [],
                "must_not": [],
                "filter": {
                    "range": {
                        "@timestamp": {}
                    }
                }
            }
        },
        "aggs": {
            "user_agent": {
                "terms": {
                    "field": "http_user_agent.keyword",
                    "size": 2147483647
                }
            }
        }
    }
}

status_code_dsl = {
    'index': INDEX,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [],
                "filter": {
                    "range": {
                        "@timestamp": {}
                    }
                }
            }
        },
        "aggs": {
            "time": {
                "date_histogram": {
                    "field": "@timestamp",
                    "interval": "1h",
                    "extended_bounds": {}
                },
                "aggs": {
                    "2xx": {
                        "filter": {
                            "range": {
                                "status": {
                                    "gte": 200,
                                    "lt": 300
                                }
                            }
                        }
                    },
                    "3xx": {
                        "filter": {
                            "range": {
                                "status": {
                                    "gte": 300,
                                    "lt": 400
                                }
                            }
                        }
                    },
                    "4xx": {
                        "filter": {
                            "range": {
                                "status": {
                                    "gte": 400,
                                    "lt": 500
                                }
                            }
                        }
                    },
                    "5xx": {
                        "filter": {
                            "range": {
                                "status": {
                                    "gte": 500
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

errors_dsl = {
    'index': INDEX,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "bool": {
                            "filter": {
                                "range": {
                                    "status": {
                                        "gte": 400
                                    }
                                }
                            }
                        }
                    }
                ],
                "filter": {
                    "range": {
                        "@timestamp": {}
                    }
                }
            }
        },
        "aggs": {
            "uri": {
                "terms": {
                    "field": "request_uri.keyword",
                    "size": 2147483647
                },
                "aggs": {
                    "status": {
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
                                "status",
                                "upstream_status"
                            ]
                        }
                    }
                }
            }
        }
    }
}

methods_dsl = {
    'index': INDEX,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "request_method": "GET || PUT || POST || DELETE"
                        }
                    }
                ],
                "filter": {
                    "range": {
                        "@timestamp": {}
                    }
                }
            }
        },
        "aggs": {
            "methods": {
                "terms": {
                    "field": "request_method.keyword",
                    "size": 2147483647
                }
            }
        }
    }
}

modules_dsl = {
    'index': INDEX,
    'dsl': {
        "size": 0,
        "query": {
            "bool": {
                "must_not": [
                    {
                        "match": {
                            "module.keyword": "%{[uri_1]}"
                        }
                    }
                ],
                "must": [],
                "filter": {
                    "range": {
                        "@timestamp": {}
                    }
                }
            }
        },
        "aggs": {
            "modules": {
                "terms": {
                    "field": "module.keyword",
                    "size": 2147483647
                }
            }
        }
    }
}

detail_dsl = {
    'index': INDEX,
    'dsl': {
        "size": 10,
        "from": 0,
        "sort": [
            {
                "@timestamp": {
                    "order": "desc"
                }
            }
        ],
        "_source": {
            "excludes": ["@version", "path", 'tags']
        },
        "query": {
            "bool": {
                "must": [],
                "filter": {
                    "range": {
                        "@timestamp": {}
                    }
                }
            }
        },
        "aggs": {}
    }
}
