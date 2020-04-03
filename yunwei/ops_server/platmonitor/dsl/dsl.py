#!/usr/bin/env python
# -*- coding:utf-8 -*-

#############################################################
# 请注意dsl语句配合filter共同使用，如dsl语句变更请一并修改filter语句 #
#############################################################

# 多点会议创会消息,仅返回会议号和开始时间
conf_multi_create_simple_dsl = {"size": 0, "query": {
    "bool": {"must": [{"match": {"beat.src_type": "cmu"}}, {"match": {"source.eventid": "EV_MCU_CONF_CREATE"}}],
             "filter": {"range": {"@timestamp": {"gte": "2018-01-01"}}}}}, "aggs": {
    "confinfo": {"terms": {"field": "source.confinfo.confe164.keyword", "size": 10000}, "aggs": {
        "begin": {"terms": {"field": "source.confinfo.begintime.keyword", "size": 10000}, "aggs": {"top1": {
            "top_hits": {"sort": [{"@timestamp": {"order": "asc"}}],
                         "_source": {"includes": ["@timestamp", "source.confinfo.endtime"]}, "size": 1}}}}}}}}
conf_multi_create_simple_filter = ["aggregations.confinfo.buckets.key",
                                   "aggregations.confinfo.buckets.begin.buckets.key",
                                   "aggregations.confinfo.buckets.begin.buckets.top1.hits.hits.sort",
                                   "aggregations.confinfo.buckets.begin.buckets.top1.hits.hits._source.source.confinfo.endtime"]

# 多点会议实时会议列表,仅返回会议号和开始时间(从mq消息查询)
conf_multi_real_time_simple_dsl = {"size": 0, "query": {"bool": {
    "must": [{"match": {"source.type": "MCU_MAU_CONFLIST_NTF"}},
             {"match": {"beat.platform_moid": "mooooooo-oooo-oooo-oooo-defaultplatf"}}],
    "filter": {"range": {"@timestamp": {"gte": "now-5m"}}}}}, "aggs": {
    "mcu": {"terms": {"field": "source.cmumoid.keyword", "size": 10000}, "aggs": {"top1": {
        "top_hits": {"size": 1, "sort": [{"@timestamp": {"order": "desc"}}], "_source": {
            "includes": ["source.confdatainfo.confE164", "source.confdatainfo.moid",
                         "source.confdatainfo.starttime"]}}}}}}}

# 多点会议根据会议号和开始时间查询会议类型
conf_multi_conf_type_dsl = {"size": 1, "_source": "source.confinfo.conftype", "query": {"bool": {
    "must": [{"match": {"beat.src_type": "cmu"}}, {"match": {"source.eventid": "EV_MCU_CONF_CREATE"}},
             {"match": {"source.confinfo.confe164": "4440067"}},
             {"match": {"source.confinfo.begintime": '2019-08-31 10:05:34'}}]}}}

# 多点会议创会消息
conf_multi_creat_dsl = {"size": 0, "query": {
    "bool": {"must": [{"match": {"beat.src_type": "cmu"}}, {"match": {"source.eventid": "EV_MCU_CONF_CREATE"}}],
             "must_not": [{"wildcard": {"source.confinfo.confname": "test_*_createmeeting*"}}],
             "filter": {"range": {"@timestamp": {"gte": "2018-01-01"}}}}}, "aggs": {
    "confinfo": {"terms": {"field": "source.confinfo.confe164.keyword", "size": 10000}, "aggs": {
        "begin": {"terms": {"field": "source.confinfo.begintime.keyword", "size": 10000},
                  "aggs": {"top1": {"top_hits": {"sort": [{"@timestamp": {"order": "asc"}}], "size": 1}}}}}}}}
# 会议详情filter
conf_multi_creat_all_filter = ['aggregations.confinfo.buckets.key',
                               'aggregations.confinfo.buckets.begin.buckets.top1.hits.hits']

# 多点会议结会消息endtime
conf_multi_destroy_dsl = {"size": 1, "_source": "@timestamp", "query": {"bool": {
    "must": [{"match": {"beat.src_type": "cmu"}}, {"match": {"source.eventid": "EV_MCU_CONF_DESTROY"}},
             {"match": {"beat.platform_moid": "xx-xx-xx"}}, {"match": {"source.confinfo.confe164": "0513**77"}},
             {"match": {"source.confinfo.conftype": 0}}], "filter": {"range": {"@timestamp": {"gte": "2018-01-01"}}}}},
                          "sort": {"@timestamp": {"order": "asc"}}}
conf_multi_destroy_filter = ['responses.hits.hits']

# 多点会议入会消息 仅返回入会终端e164号码
conf_multi_dev_add_dsl = {"size": 0, "query": {"bool": {
    "must": [{"match": {"source.eventid": "EV_MCU_MT_ADD"}}, {"match": {"source.mtinfo.confe164.keyword": "6660131"}}],
    "filter": {"range": {"@timestamp": {"gte": "1565061003000", "lte": "1565061027000"}}}}}, "aggs": {
    "mttype": {"terms": {"field": "source.mtinfo.mttype", "size": 10000},
               "aggs": {"mtaccount": {"terms": {"field": "source.mtinfo.mtaccount.keyword", "size": 10000}}}}}}
conf_multi_dev_add_filter = ['aggregations.mttype.buckets.key', 'aggregations.mttype.buckets.mtaccount.buckets.key']
confs_multi_dev_add_filter = ['responses.aggregations.mttype.buckets']

# 多点会议终端列表筛选入会终端
conf_multi_dev_filter_add_dsl = {"size": 0, "query": {"bool": {
    "must": [{"match": {"source.eventid": "EV_MCU_MT_ADD"}}, {"match": {"source.mtinfo.confe164.keyword": "6662661"}}],
    "filter": {"range": {"@timestamp": {"gte": "1567582793000", "lte": "now"}}}}}, "aggs": {
    "mtaccount": {"terms": {"field": "source.mtinfo.mtaccount.keyword", "size": 10000}, "aggs": {
        "mtip": {"terms": {"field": "source.mtinfo.mtip.keyword", "size": 10000}, "aggs": {"gggg": {
            "top_hits": {"size": 1, "_source": ["source.mtinfo.mttype", "source.mtinfo.mtip", "source.mtinfo.mtaccount",
                                                "source.mtinfo.mtname", "source.mtinfo.softversion"]}}}}}}}}

# 多点会议终端会议消息 返回最新的会议消息
conf_multi_dev_conf_info_dsl = {"size": 1, "query": {"bool": {
    "must": [{"match": {"source.eventid": "EV_CONF_INFO"}}, {"match": {"source.conf_info.mt_e164": "0512110000831"}},
             {"match": {"source.conf_info.conf_e164": "6662718"}}],
    "filter": {"range": {"@timestamp": {"gte": "2019-01-01", "lte": "now"}}}}},
                                "sort": [{"@timestamp": {"order": "desc"}}]}

# 多点会议终端入会离会时间
conf_multi_dev_add_del_dsl = {"size": 10000, "_source": ["@timestamp", "source.eventid", "source.mtinfo.leavereason"],
                              "query": {"bool": {"must": [{"match": {"beat.src_type": "cmu"}}, {
                                  "match": {"source.eventid": "EV_MCU_MT_ADD || EV_MCU_MT_DEL"}},
                                                          {"match": {"source.mtinfo.confe164": "0513**77"}},
                                                          {"match": {"source.mtinfo.mtaccount": "0000001000048"}}],
                                                 "filter": {"range": {
                                                     "@timestamp": {"gte": "2019-07-01", "lte": "2019-08-01"}}}}},
                              "sort": {"@timestamp": {"order": "asc"}}}

# 多点会议会议码率
conf_multi_bitrate_dsl = {"_source": "source.confinfo.bitrate", "size": 1, "query": {"bool": {
    "must": [{"match": {"beat.src_type": "cmu"}}, {"match": {"source.eventid": "EV_MCU_CONF_CREATE"}},
             {"match": {"source.confinfo.confe164.keyword": "0513**77"}}],
    "filter": {"range": {"@timestamp": {"gte": "2018-01-01", "lte": "2019-09-01"}}}}}}
conf_multi_bitrate_filter = ['hits.hits._source.source.confinfo.bitrate']

# 多点会议终端设备协议类型
conf_multi_dev_prot_dsl = {"size": 1, "_source": ["source.proto_type"], "query": {"bool": {
    "must": [{"match": {"source.eventid": "EV_PAS_ADD_MT_PROTO"}},
             {"match": {"source.devid": "18260240-950d-4594-9ab5-7262e9f97034"}}],
    "filter": {"range": {"@timestamp": {"lte": "2019-07-09"}}}}}, "sort": {"@timestamp": {"order": "desc"}}}
conf_multi_dev_prot_filter = ["responses.hits.hits._source.source.proto_type"]

# 查询点对点会议终端列表
conf_p2p_creat_dsl = {"size": 10000,
                      "_source": ["@timestamp", "source.confinfo.caller.deve164", "source.confinfo.callee.deve164"],
                      "query": {"bool": {
                          "must": [{"match": {"beat.src_type": "pas"}}, {"match": {"beat.platform_moid": "xx-xx-xx"}},
                                   {"match": {"source.eventid": "EV_PAS_P2PCONF_CREATE"}}],
                          "filter": {"range": {"@timestamp": {"gte": "2018-01-01", "lte": "2019-01-01"}}}}},
                      "sort": [{"@timestamp": {"order": "desc"}}]}
# 会议详情filter
conf_p2p_creat_all_filter = ["hits.total", "hits.hits.sort", "hits.hits._source.beat.platform_moid",
                             "hits.hits._source.source.confinfo"]

# 查询点会对会议列表
conf_p2p_create_dsl = {"size": 0, "query": {"bool": {"must": [{"match": {"source.eventid": "EV_PAS_P2PCONF_CREATE"}}, {
    "match": {"beat.platform_moid": "mooooooo-oooo-oooo-oooo-defaultplatf"}}], "filter": {
    "range": {"@timestamp": {"gte": "now-7d", "lte": "now"}}}}}, "aggs": {
    "time": {"terms": {"field": "source.confinfo.time.keyword", "size": 100000, "order": {"_key": "desc"}}, "aggs": {
        "caller": {"terms": {"field": "source.confinfo.caller.deve164.keyword", "size": 100000}, "aggs": {"top1": {
            "top_hits": {"size": 1, "_source": {
                "includes": ["@timestamp", "beat.platform_moid", "source.confinfo.caller",
                             "source.confinfo.callee"]}}}}}}}}}

# 点对点会议结会消息
conf_p2p_destroy_dsl = {"size": 1, "_source": "@timestamp", "query": {"bool": {
    "must": [{"match": {"beat.src_type": "pas"}}, {"match": {"source.eventid": "EV_PAS_P2PCONF_DESTROY"}},
             {"match": {"source.confinfo.callerE164": "051255566"}},
             {"match": {"source.confinfo.calleeE164": "051255567"}}],
    "filter": {"range": {"@timestamp": {"gte": "2018-01-01"}}}}}, "sort": {"@timestamp": {"order": "asc"}}}
conf_p2p_destroy_filter = ['responses.hits.hits']

# 点对点会议终端ip/版本号
conf_p2p_dev_extra_dsl = {"size": 1,
                          "query": {"bool": {"must": [{"match": {"source.eventid": "EV_MT_INFO"}}, {
                              "match": {"source.devid": "18260240-950d-4594-9ab5-7262e9f97034"}}],
                                             "filter": {"range": {"@timestamp": {"lte": "2019-07-09"}}}}},
                          "sort": {"@timestamp": {"order": "desc"}}}
conf_p2p_dev_extra_filter = ["responses.hits.hits"]

# 通过e164号查询upuwatcher信息
mt_upuwatcher_info = {"size": 1, "query": {"bool": {"must": [{"match": {"source.e164": "0512121890992"}}], "filter": {
    "range": {"@timestamp": {"gte": "1567582793000", "lte": "now"}}}}}, "sort": [{"@timestamp": {"order": "desc"}}]}
mt_upuwatcher_info_filter = ["responses.hits.hits"]

# 多点会议离会原因消息
conf_multi_dev_leave_dsl = {"size": 0, "query": {"bool": {
    "must": [{"match": {"source.mtinfo.confe164": "0513**77"}}, {"match": {"source.eventid": "EV_MCU_MT_DEL"}},
             {"match": {"beat.src_type": "cmu"}}, {"terms": {"source.mtinfo.leavereason": [1, 3, 28, 29, 30, 31]}}],
    "filter": {"range": {"@timestamp": {"gte": "2018-01-06", "lte": "2018-01-06"}}}}}, "aggs": {
    "mtaccount": {"terms": {"field": "source.mtinfo.mtaccount.keyword", "size": 10000}}}}
conf_multi_dev_leave_filter = ['responses.aggregations.mtaccount.buckets']

# 会议丢包率消息
conf_pkts_lossrate_dsl = {"size": 0, "query": {"bool": {
    "must": [{"match": {"source.eventid": "EV_CONF_INFO"}}, {"match": {"source.conf_info.conf_e164": "0512111886042"}}],
    "filter": {"range": {"@timestamp": {"gte": "2018-01-01", "lte": "2018-01-01"}}}}}, "aggs": {
    "dev_lossrate": {"terms": {"field": "source.conf_info.mt_e164.keyword", "size": 10000}, "aggs": {
        "privideo_recv_max_lose": {"max": {"field": "source.conf_info.privideo_recv.video_pkts_loserate"}},
        "assvideo_recv_max_lose": {"max": {"field": "source.conf_info.assvideo_recv.video_pkts_loserate"}},
        "audio_recv_max_lose": {"max": {"field": "source.conf_info.audio_recv.audio_pkts_loserate"}}}}}}
conf_pkts_lossrate_filter = ['responses.aggregations.dev_lossrate.buckets']

# 终端会议信息 码流/音频/丢包
dev_conf_info_dsl = {"_source": "source.conf_info", "query": {"bool": {
    "must": [{"match": {"source.conf_info.conf_e164": "0513**77"}},
             {"match": {"source.conf_info.mt_e164": "0000001000048"}}, {"match": {"source.eventid": "EV_CONF_INFO"}}],
    "filter": {"range": {"@timestamp": {"gte": "2018-01-06", "lte": "2018-01-06"}}}}},
                     "sort": {"@timestamp": {"order": "asc"}}}
dev_conf_info_filter = ["hits.hits._source.source.conf_info", "hits.hits.sort"]

# 获取会议发言人
dev_conf_speaker_dsl = {"size": 10000, "_source": ["source.speaker.mtNO", "source.chairman.mtNO"], "query": {"bool": {
    "must": [{"match": {"source.confE164.keyword": "6660030"}}, {"match": {"source.type": "MCU_CM_SIMCONFINFO_NTF"}},
             {"match": {"beat.name": "mqwatcher"}}],
    "filter": {"range": {"@timestamp": {"gte": "2019-07-06", "lte": "2019-07-08"}}}}},
                        "sort": {"@timestamp": {"order": "asc"}}}
dev_conf_speaker_filter = ["hits.hits._source.source.speaker", "hits.hits._source.source.chairman", "hits.hits.sort"]

# 获取终端上报的上下行带宽
dev_bandwidth_dsl = {"size": 0, "query": {"bool": {
    "must": [{"match": {"source.devid": "c3102d7c-bb21-49b3-b7a5-22ff64f0b320"}},
             {"match": {"source.eventid": "EV_BANDWIDTH_MSG"}}],
    "filter": {"range": {"@timestamp": {"gte": "2019-07-18", "lte": "2019-07-19"}}}}}, "aggs": {"2": {
    "date_histogram": {"field": "@timestamp", "interval": "1h", "format": "epoch_millis", "min_doc_count": 0,
                       "extended_bounds": {"min": "1563379200000", "max": "1563465600000"}},
    "aggs": {"1": {"avg": {"field": "source.recv_bandwidth.bandwidth"}}}}}}

# 根据ssrc查询网媒信息
dev_media_ssrc_dsl = {"size": 0, "query": {"bool": {
    "must": [{"match": {"beat.src_type": "mps"}}, {"match": {"source.eventid": "EV_MEDIA_STATIS_NOTIFY"}},
             {"match": {"source.conf_e164": "1110039"}}, {"match": {"source.rtp_info.ssrc": "2222"}}],
    "filter": {"range": {"@timestamp": {"gte": "2019-07-24", "lte": "2019-07-28"}}}}}, "aggs": {
    "type": {"terms": {"field": "source.context.type.keyword", "size": 10000}, "aggs": {"time": {
        "date_histogram": {"field": "@timestamp", "interval": "30s", "format": "epoch_millis", "min_doc_count": 0},
        "aggs": {"result": {"max": {"field": "source.rtp_info.qoe.network.rtt"}}}}}}}}

# 查询终端侧 终端卡顿次数
dev_rebuffer_dsl = {"size": 0, "query": {"bool": {
    "must": [{"match": {"source.devid": "c3102d7c-bb21-49b3-b7a5-22ff64f0b320"}},
             {"match": {"source.eventid": "EV_BLUNT_INFO"}}],
    "filter": {"range": {"@timestamp": {"gte": "2019-07-18", "lte": "2019-07-19"}}}}}, "aggs": {"2": {
    "date_histogram": {"field": "@timestamp", "interval": "1h", "format": "epoch_millis", "min_doc_count": 0,
                       "extended_bounds": {"min": "1563379200000", "max": "1563465600000"}},
    "aggs": {"1": {"avg": {"field": "source.blunt_info.count"}}}}}}

# 查询终端侧 主视频丢包数/丢包率/帧率
dev_conf_inf_dsl = {"size": 0, "query": {"bool": {"must": [{"match": {"source.conf_info.mt_e164": "0512110000202"}},
                                                           {"match": {"source.conf_info.conf_e164": "1118003"}},
                                                           {"match": {"source.eventid": "EV_CONF_INFO"}}], "filter": {
    "range": {"@timestamp": {"gte": "2019-07-25", "lte": "2019-07-31"}}}}}, "aggs": {
    "3": {"terms": {"field": "source.conf_info.privideo_recv.id", "size": 10000}, "aggs": {"2": {
        "date_histogram": {"field": "@timestamp", "interval": "1h", "format": "epoch_millis", "min_doc_count": 0,
                           "extended_bounds": {"min": "1564416000000", "max": "1564469436000"}},
        "aggs": {"1": {"avg": {"field": "source.conf_info.privideo_recv.id"}}}}}}}}

# 码流链路 查询dssworker第一包信息
switch_link_dssw_dsl = {"size": 1, "query": {"bool": {
    "must": [{"match": {"source.eventid": "EV_DSS_PORT_STATIS_NOTIFY"}},
             {"exists": {"field": "source.rtp_info.dst.ip"}}, {"match": {"source.conf_e164": "6660125"}},
             {"match": {"source.context.chan_type": "dualvideo"}},
             {"match": {"source.context.channer.id": "9999991000020"}},
             {"match": {"source.context.chanee.id": "6660125"}}, {"match": {"source.context.channer.local": 1}},
             {"match": {"source.direct": "up"}}, {"exists": {"field": "source.rtp_info.statis.ssrc"}}],
    "filter": {"range": {"@timestamp": {"gte": 1568631333001, "lte": 1568631453001}}}}},
                        "sort": [{"@timestamp": {"order": "asc"}}]}

# 终端ip/协议类型(upuwatcher)
mt_ip_proto_inf_dsl = {"size": 1, "_source": ["source.mtaddr", "source.prototype"], "query": {
    "bool": {"must": [{"match": {"beat.name": "upuwatcher"}}, {"match": {"source.e164": 5555550000009}}],
             "filter": {"range": {"@timestamp": {"lte": "2019-08-22T18:49:46.593Z"}}}}},
                       "sort": [{"@timestamp": {"order": "desc"}}]}

# 查询数据会议状态
conf_dcs_dataconf_stat_dsl = {"size": 1, "_source": "source.eventid", "query": {"bool": {
    "must": [{"match": {"beat.src_type": "dcs"}},
             {"match": {"source.eventid": "EV_DCS_CREATE_CONF_INFO|EV_DCS_DESTROY_CONF_INFO"}}, {"bool": {
            "should": [{"match": {"source.createconf.confe164": "ssssss"}},
                       {"match": {"source.delconf.confe164": "ssssss"}}], "minimum_should_match": 1}}],
    "filter": {"range": {"@timestamp": {"gte": "2019-01-01", "lt": "now"}}}}},
                              "sort": [{"@timestamp": {"order": "desc"}}]}

# 终端性能  外设状态信息
mt_ptm_dsl = {"size": 1, "query": {
    "bool": {"must": [{"match": {"source.eventid": "EV_PFMINFO_MSG"}}, {"match": {"source.devid": "0513**77"}}],
             "filter": {"range": {"@timestamp": {"gte": "2018-01-01", "lte": "2018-01-01"}}}}},
              "sort": {"@timestamp": {"order": "desc"}}}

# 根据时间查询会议质量
conf_quality_by_time_dsl = {"size": 0, "query": {
    "bool": {"filter": {"range": {"@timestamp": {"gte": "now-24h", "lte": "now"}}},
             "must_not": [{"wildcard": {"source.conf_name": "test_*_createmeeting*"}}]}}, "aggs": {
    "conf": {"terms": {"field": "source.confe164.keyword", "size": 10000}, "aggs": {
        "time": {"terms": {"field": "source.begintime.keyword", "size": 10000}, "aggs": {"top1": {
            "top_hits": {"size": 1, "_source": {"includes": ["source.score", "source.conf_name"]},
                         "sort": [{"@timestamp": {"order": "desc"}}]}}}}}}}}

# 根据会议号查询会议质量
conf_quality_by_confid_dsl = {"size": 1, "_source": "source.score", "query": {
    "bool": {"must": [{"match": {"source.confe164": "2220064"}}],
             "filter": {"range": {"@timestamp": {"gte": "now-24h", "lte": "now"}}}}},
                              "sort": [{"@timestamp": {"order": "desc"}}]}
