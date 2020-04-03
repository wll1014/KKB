#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

import logging
import copy

import jsonpath

from platmonitor.dsl import es_ql
from common.my_elastic import es_client
from common.my_elastic import OpsException

logger = logging.getLogger('ops.' + __name__)


def get_conf_actions(request, conf_id):
    '''
    获取某会议的会议事件
    :param request:
    :param conf_id: 会议号码
    :return: {
            'create_destroy_conf': [[时间戳1,flag],[时间戳2,flag]......],
            'set_cancel_chairman': [[时间戳1,flag],[时间戳2,flag]......]
            }
    '''

    # mq消息中的source.type 转换义 和 转换flag 1：创会/设置/打开/恢复，0：结会/取消/关闭/暂停
    mqtype2actions = {
        'MAU_CM_CREATECONF_ACK': ['create_destroy_conf', 1],
        # 'MAU_CM_RELEASECONF_ACK': ['create_destroy_conf', 0],
        'MAU_CM_RELEASECONF_NTF': ['create_destroy_conf', 0],
        'CMU_CM_SETCHAIRMAN_ACK': ['set_cancel_chairman', 1],
        'CMU_CM_CANCELCHAIRMAN_ACK': ['set_cancel_chairman', 0],
        'CMU_CM_SETSPEAKER_ACK': ['set_cancel_speaker', 1],
        'CMU_CM_CANCELSPEAKER_ACK': ['set_cancel_speaker', 0],
        'CM_CMU_STARTPOLL_CMD': ['set_cancel_poll', 1],
        'CM_CMU_STOPPOLL_CMD': ['set_cancel_poll', 0],
        'CM_CMU_RESUMEPOLL_CMD': ['resume_pause_poll', 1],
        'CM_CMU_PAUSEPOLL_CMD': ['resume_pause_poll', 0],
        'CMU_CM_STARTMIX_ACK': ['set_cancel_mix', 1],
        'CMU_CM_STOPMIX_ACK': ['set_cancel_mix', 0],
        'CMU_CM_STARTVMP_ACK': ['set_cancel_vmp', 1],
        'CMU_CM_STOPVMP_ACK': ['set_cancel_vmp', 0],
        # 原始消息id为 EV_MCU_CONF_MANAGER_CHANGE
        'EV_MCU_CONF_MANAGER_CHANGE_SET': ['set_cancel_chairman', 1],
        'EV_MCU_CONF_MANAGER_CHANGE_CANCEL': ['set_cancel_chairman', 0],
        # 原始消息id为 EV_MCU_CONF_SPEAKER_CHANGE
        'EV_MCU_CONF_SPEAKER_CHANGE_SET': ['set_cancel_speaker', 1],
        'EV_MCU_CONF_SPEAKER_CHANGE_CANCEL': ['set_cancel_speaker', 0],
    }
    dsl = copy.deepcopy(es_ql.conf_actions_dsl)
    start_time = request.query_params.get('start_time')
    end_time = request.query_params.get('end_time')
    conf_id_filter = {"match": {"source.confE164": conf_id}}
    nms_conf_id_filter = {"match": {"source.confinfo.confe164": conf_id}}
    should = [conf_id_filter, nms_conf_id_filter]
    must = {
        "bool": {
            "should": should,
            "minimum_should_match": 1
        }
    }
    dsl_bool = dsl['dsl']['query']['bool']
    dsl_bool['must'].append(must)
    dsl_bool['filter']['range']['@timestamp']['gte'] = start_time
    dsl_bool['filter']['range']['@timestamp']['lte'] = end_time if end_time else 'now'

    dsls = [dsl]
    m_body = es_client.get_index_header_m_body(*dsls)
    logger.info(m_body)
    try:
        responses = es_client.msearch(m_body)['responses']
    except Exception as e:
        logger.exception(e)
        raise OpsException(code='10002')
    else:
        conf_actions_response = responses[0]
        conf_actions = {}
        source_type_buckets = jsonpath.jsonpath(conf_actions_response, '$..source_type.buckets')
        source_type_buckets = source_type_buckets[0] if source_type_buckets else []
        eventid_buckets = jsonpath.jsonpath(conf_actions_response, '$..eventid.buckets')
        eventid_buckets = eventid_buckets[0] if eventid_buckets else []

        total_buckets = source_type_buckets + eventid_buckets

        for source_type_bucket in total_buckets:
            action = source_type_bucket.get('key')
            time_buckets = jsonpath.jsonpath(source_type_bucket, '$..time.buckets')
            time_buckets = time_buckets[0] if time_buckets else []
            if action == 'MAU_CM_RELEASECONF_NTF':
                # 结会通知消息会有多个，均表示此次结会，只取一个就可以
                timestamp = time_buckets[0].get('key')
                info = [timestamp, mqtype2actions[action][1]]
                if not conf_actions.get(mqtype2actions[action][0]):
                    conf_actions[mqtype2actions[action][0]] = []
                conf_actions[mqtype2actions[action][0]].append(info)
            else:
                for time_bucket in time_buckets:
                    # 循环时间桶，将所有事件的每次时间戳都记录
                    timestamp = time_bucket.get('key')
                    if time_bucket.get('top'):
                        # eventid聚合的时间桶才有top
                        # 获取发言人、管理方
                        manager = jsonpath.jsonpath(time_bucket, '$..source.confinfo.manager')
                        speaker = jsonpath.jsonpath(time_bucket, '$..source.confinfo.speaker')
                        if manager:
                            if manager[0]:
                                action = 'EV_MCU_CONF_MANAGER_CHANGE_SET'
                            else:
                                # manager为空字符串，则为取消管理方
                                action = 'EV_MCU_CONF_MANAGER_CHANGE_CANCEL'
                        if speaker:
                            if speaker[0]:
                                action = 'EV_MCU_CONF_SPEAKER_CHANGE_SET'
                            else:
                                # speaker为空字符串，则为取消发言人
                                action = 'EV_MCU_CONF_SPEAKER_CHANGE_CANCEL'
                    info = [timestamp, mqtype2actions[action][1]]
                    if not conf_actions.get(mqtype2actions[action][0]):
                        conf_actions[mqtype2actions[action][0]] = []
                    conf_actions[mqtype2actions[action][0]].append(info)

        return conf_actions
