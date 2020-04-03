# Create your views here.

import os
import logging
import datetime

from redis.client import pairs_to_dict
from common.my_redis import redis_client
from common.my_exception import OpsException
from common import global_func
from ops.settings import BASE_DIR
from common.conf_params_enum import ConfEndTimeType, ConfType, ConfStat
from rest_framework.views import APIView
from rest_framework.response import Response
from platmonitor.dsl import es_query
from common.pagination import ResultsSetPaginationOffset1
from diagnose.links import CallLinkFunctionsAdapter
from platmonitor.dsl import DevConfMediaInfo
from platmonitor.dsl import DevConfBasicInfo
from platmonitor.dsl import confDevList
from platmonitor.query_func import get_conf_actions

logger = logging.getLogger('ops.' + __name__)


def json_response(state, **kwargs):
    """
    自定义返回json
    :param state: 操作状态 0：失败   1：成功
    :param kwargs: 自定义返回字段
    :return: 字典
    """
    if state == 0:
        kwargs.setdefault("success", 0)
        return kwargs
    else:
        return {"success": 1, "data": kwargs}


class ConferencesQuality(APIView):
    """
    处理 /api/v1/ops/confs/summary-quality/ 请求
    计算会议质量相关计信息
    """

    def get(self, request, version):
        """
        处理GET请求，返回用户体验各等级会议所占比例
        :param request:
        :param version:
        :return:
        """
        params = request.query_params
        params = dict([(k, v) for k, v in params.items() if v])
        conf_type = params.get('conf_type')
        conf_status = params.get('conf_status')
        start_time = params.get("start_time")
        end_time = params.get("end_time")

        try:
            if end_time:
                end_time = int(end_time)
            else:
                end_time = int((datetime.datetime.now()).timestamp() * 1000)
            params['end_time'] = end_time

            if start_time:
                start_time = int(start_time)
            else:
                start_time = end_time - 12 * 60 * 60 * 1000
            params['start_time'] = start_time

            if conf_type is not None:
                conf_type = int(conf_type)
                if conf_type not in ConfType.values():
                    return Response(json_response(0, error_code=400, msg="conf_type参数错误"))
                else:
                    params['conf_type'] = conf_type
            if conf_status is not None:
                conf_status = int(conf_status)
                if conf_status not in ConfStat.values():
                    return Response(json_response(0, error_code=400, msg="conf_status参数错误"))
                else:
                    params['conf_status'] = conf_status
        except Exception as err:
            logger.error(err)
            return Response(json_response(0, error_code=400, msg="参数错误"))

        level = [1, 2, 3, 4]
        desc = {1: "体验不好",
                2: "体验一般",
                3: "体验良好",
                4: "体验优秀"}

        try:
            quality_obj = es_query.ConfQuality(**params)
            quality = quality_obj.get_quality()
        except Exception as err:
            logger.error(err)
            return Response(json_response(0, error_code=400, msg=err.args))

        if not quality[0]:
            return Response(json_response(0, error_code=400, msg=quality[1]))
        quality = quality[1]

        total = len(quality)
        info = []

        level_count = [(i, quality.count(i)) for i in level]
        if total != 0:
            level_count.sort(key=lambda x: x[1])
            percent_total = 0
            for lv, count in level_count[:-1]:
                description = desc.get(lv)
                percent = round(count / total, 2)
                info.append({"count": count, "level": lv, "description": description, "percent": percent})
                percent_total += percent
            # 最后一个百分比用1减 防止总百分比超过100
            info.append({"count": level_count[-1][1],
                         "level": level_count[-1][0],
                         "description": desc.get(level_count[-1][0]),
                         "percent": round(1 - percent_total, 2)})
        else:
            for i in level:
                description = desc[i]
                info.append({"count": 0, "level": i, "description": description, "percent": 0})
        params["total"] = total
        params["info"] = info
        return Response(json_response(1, **params))


class ConferencesInfoList(APIView):
    """
    处理 /api/v1/ops/confs/ 请求
    返回会议信息
    """

    def get(self, request, version):
        """
        处理GET请求，返回会议信息列表
        :param request:
        :param version:
        :return:
        """
        params = request.query_params.dict()
        params = dict([(k, v) for k, v in params.items() if v])

        conf_type = params.get('conf_type')
        conf_status = params.get('conf_status')
        level = params.get('level')
        count = params.get('count')
        start = params.get('start')
        start_time = params.get('start_time')
        end_time = params.get('end_time')
        # platform_moid = params.get('platform_moid')
        # domain_moid = params.get('domain_moid')
        # keywords = params.get('keywords')

        try:
            if int(conf_type) in ConfType.values():
                conf_type = int(conf_type)
                params['conf_type'] = conf_type
            else:
                return Response(json_response(0, error_code=400, msg="conf_type参数错误"))
            if conf_status is not None:
                if int(conf_status) in ConfStat.values():
                    params['conf_status'] = int(conf_status)
                else:
                    return Response(json_response(0, error_code=400, msg="conf_status参数错误"))
            if level is not None:
                if int(level) in [1, 2, 3, 4]:
                    params['level'] = int(level)
                else:
                    return Response(json_response(0, error_code=400, msg="level参数错误"))
            if count:
                params['count'] = int(count)
            else:
                params['count'] = 20
            if start:
                params['start'] = int(start)
            else:
                params['start'] = 0
            if start_time:
                params['start_time'] = int(start_time)
            if end_time:
                params['end_time'] = int(end_time)
        except Exception as err:
            return Response(json_response(0, error_code=400, msg=err.args[0]))

        # 返回服务器当前时间
        params['curr_time'] = int(datetime.datetime.now().timestamp() * 1000)

        if conf_type in [ConfType.TRADITION, ConfType.PORT, ConfType.MULTI]:
            # Multipoint Conference
            try:
                stat, result = es_query.MultiConfList(**params).get_conference()  # 会议详情列表
            except Exception as err:
                logger.exception(err)
                return Response(json_response(0, error_code=400, msg=err.args[0]))
            if not stat:
                return Response(json_response(0, error_code=400, msg=result))
            else:
                result, total = result[0], result[1]
                if result is None:
                    # 会议列表为空
                    result = []

            params['count'] = len(result)
            params['total'] = total
            params['info'] = result
            return Response({'success': 1, 'data': params})
        elif conf_type == ConfType.P2P:
            # One Point Conference
            try:
                stat, result = es_query.P2PConfList(**params).get_conference()  # 会议详情列表
            except Exception as err:
                logger.error(err)
                return Response(json_response(0, error_code=400, msg=err.args[0]))
            if not stat:
                return Response(json_response(0, error_code=400, msg=result))
            elif result is None:
                # 会议列表为空
                result = []

            pagination = ResultsSetPaginationOffset1()  # create pagination object
            pg_res = pagination.paginate_queryset(queryset=result, request=request, view=self)  # get pagination data
            return pagination.get_paginated_response(pg_res, **params)
        else:
            return Response(json_response(0, error_code=400, msg="conf_type参数错误"))


class ConferencesExtendInfo(APIView):
    """
    处理 /api/v1/ops/confs/{conf_id}/extend/ 请求 获取实时会议额外信息
    发言人/管理方/双流源/录像状态/直播状态/协作状态
    """

    def get(self, request, version, conf_id):
        """
        处理GET请求，返回会议信息列表
        :param conf_id:
        :param request:
        :param version:
        :return:
        """
        params = request.query_params.dict()
        params = dict([(k, v) for k, v in params.items() if v])
        start_time = params.get('start_time')

        if start_time is not None:
            start_time = int(start_time)
        else:
            return Response(json_response(0, error_code=400, msg="start_time不能为空"))

        try:
            stat, result = es_query.MultiConfExtendInfo([[conf_id, start_time]]).get_conference_info()
        except Exception as err:
            logger.error(err)
            return Response(json_response(0, error_code=400, msg=err.args))
        if not stat:
            return Response(json_response(0, error_code=400, msg=result))

        params['conf_id'] = conf_id
        params['start_time'] = start_time
        params['info'] = result
        return Response(json_response(1, **params))


class ConfDevlist(APIView):
    """
    处理 /api/v1/ops/confs/{conf_id}/mts/
    获取会议终端列表
    """

    def get(self, request, version, conf_id):
        params = request.query_params.dict()
        params = dict([(k, v) for k, v in params.items() if v])
        start_time = params.get('start_time')
        end_time = params.get('end_time')
        conf_type = params.get('conf_type')
        conf_status = params.get('conf_status')
        condition = params.get('condition')
        if not all([conf_type, start_time, end_time, conf_status]):
            return Response(json_response(0, error_code=400, msg="参数错误"))

        conf_type, start_time, conf_status = int(conf_type), int(start_time), int(conf_status)
        if end_time.isdigit():
            end_time = int(end_time)
        elif end_time == ConfEndTimeType.REALTIME.name or end_time == ConfEndTimeType.MANUAL.name:
            end_time = int((datetime.datetime.now()).timestamp() * 1000)
        elif end_time == ConfEndTimeType.ABEND.name:
            # 异常结会按会议时长2小时计算
            end_time = start_time + 7200000

        if conf_type not in ConfType.values():
            return Response(json_response(0, error_code=400, msg="conf_type参数错误"))
        if conf_status not in ConfType.values():
            return Response(json_response(0, error_code=400, msg="conf_status参数错误"))

        conf_info = conf_id, start_time, end_time, conf_status, condition
        if conf_type in [ConfType.TRADITION, ConfType.PORT, ConfType.MULTI]:
            # 多点会议
            try:
                stat, result = confDevList.MultiConfDevList(conf_info).get_dev_info()  # 会议终端详情列表
            except Exception as err:
                logger.error(err)
                return Response(json_response(0, error_code=400, msg=err.args))
            if not stat:
                # 获取失败
                return Response(json_response(0, error_code=400, msg=result))
        else:
            # 点对点会议
            try:
                stat, result = confDevList.P2PConfDevList(conf_info).get_dev_info()  # 会议终端详情列表
            except Exception as err:
                logger.error(err)
                return Response(json_response(0, error_code=400, msg=err.args))
            if not stat:
                # 获取失败
                return Response(json_response(0, error_code=400, msg=result))

        params['conf_id'] = conf_id
        params['conf_type'] = conf_type
        params['conf_status'] = conf_status
        params['start_time'] = start_time
        params['end_time'] = end_time

        pagination = ResultsSetPaginationOffset1()  # create pagination object
        pg_res = pagination.paginate_queryset(queryset=result, request=request, view=self)  # get pagination data
        return pagination.get_paginated_response(pg_res, **params)


class ConfDevChannel(APIView):
    """
    处理  /api/v1/ops/confs/{conf_id}/mts/{mt_e164}/channel/
    获取会议终端通道信息
    """

    def get(self, request, *args, **kwargs):
        params = request.query_params.dict()
        params = dict([(k, v) for k, v in params.items() if v])
        conf_status = params.get('conf_status')
        start_time = params.get('start_time')
        end_time = params.get('end_time')

        conf_id = kwargs.get('conf_id')
        mt_e164 = kwargs.get('mt_e164')

        if not all([conf_status, start_time, end_time]):
            return Response(json_response(0, error_code=400, msg="参数错误"))

        conf_status, start_time = int(conf_status), int(start_time)
        if end_time.isdigit():
            end_time = int(end_time)
        elif end_time == ConfEndTimeType.REALTIME.name or end_time == ConfEndTimeType.MANUAL.name:
            end_time = int((datetime.datetime.now()).timestamp() * 1000)
        elif end_time == ConfEndTimeType.ABEND.name:
            # 异常结会按会议时长2小时计算
            end_time = start_time + 7200000

        if conf_status not in ConfStat.values():
            return Response(json_response(0, error_code=400, msg="conf_status参数错误"))

        params['conf_id'] = conf_id
        params['mt_e164'] = mt_e164
        params['conf_status'] = conf_status
        params['start_time'] = start_time
        params['end_time'] = end_time

        param_use = [conf_id, start_time, end_time, conf_status, mt_e164]
        try:
            stat, dev_info = confDevList.MultiConfDevChannelInfo(param_use).get_channel_info()  # 会议终端通道信息
        except Exception as err:
            logger.error(err)
            return Response(json_response(0, error_code=400, msg=err))
        if not stat:
            # 获取失败
            return Response(json_response(0, error_code=400, msg=dev_info))
        if len(dev_info) == 0:
            params['info'] = []
        else:
            params['info'] = [dev_info]
        return Response(json_response(1, **params))


class ConfDevTopology(APIView):
    """
    处理  /api/v1/ops/confs/{conf_id}/mts/{mt_e164}/topology/
    获取会议终端通道信息
    """

    def get(self, request, *args, **kwargs):
        params = request.query_params.dict()
        params = dict([(k, v) for k, v in params.items() if v])
        conf_status = params.get('conf_status')
        start_time = params.get('start_time')
        end_time = params.get('end_time')

        conf_id = kwargs.get('conf_id')
        mt_e164 = kwargs.get('mt_e164')

        if not all([conf_status, start_time, end_time]):
            return Response(json_response(0, error_code=400, msg="参数错误"))

        conf_status, start_time = int(conf_status), int(start_time)
        if end_time.isdigit():
            end_time = int(end_time)
        elif end_time == ConfEndTimeType.REALTIME.name or end_time == ConfEndTimeType.MANUAL.name:
            end_time = int((datetime.datetime.now()).timestamp() * 1000)
        elif end_time == ConfEndTimeType.ABEND.name:
            # 异常结会按会议时长2小时计算
            end_time = start_time + 7200000

        if conf_status not in ConfStat.values():
            return Response(json_response(0, error_code=400, msg="conf_status参数错误"))

        params['conf_id'] = conf_id
        params['mt_e164'] = mt_e164
        params['conf_status'] = conf_status
        params['start_time'] = start_time
        params['end_time'] = end_time

        param_use = [conf_id, start_time, end_time, conf_status, mt_e164]
        try:
            stat, dev_info = confDevList.MultiConfDevTopologyInfo(param_use).get_topology_info()  # 会议终端拓扑信息
        except Exception as err:
            logger.error(err)
            return Response(json_response(0, error_code=400, msg=err))
        if not stat:
            # 获取失败
            return Response(json_response(0, error_code=400, msg=dev_info))

        params['info'] = dev_info
        return Response(json_response(1, **params))


class ConfDevInfo(APIView):
    """
    处理  /api/v1/ops/confs/{conf_id}/mts/{mt_e164}/conf_info/
    获取会议终端概况
    """

    def get(self, request, version, conf_id, mt_e164):
        params = request.query_params.dict()
        params = dict([(k, v) for k, v in params.items() if v])
        conf_type = params.get('conf_type')
        conf_status = params.get('conf_status')
        start_time = params.get('start_time')
        end_time = params.get('end_time')
        time_on = params.get('time_on')

        if not all([conf_type, conf_status, start_time, end_time, time_on]):
            return Response(json_response(0, error_code=400, msg="参数错误"))

        conf_type, conf_status, start_time, time_on = int(conf_type), int(conf_status), int(start_time), int(time_on)
        if end_time.isdigit():
            end_time = int(end_time)
        elif end_time == ConfEndTimeType.REALTIME.name or end_time == ConfEndTimeType.MANUAL.name:
            end_time = int((datetime.datetime.now()).timestamp() * 1000)
        elif end_time == ConfEndTimeType.ABEND.name:
            # 异常结会按会议时长2小时计算
            end_time = start_time + 7200000

        if conf_type not in ConfType.values():
            return Response(json_response(0, error_code=400, msg="conf_type参数错误"))
        if conf_status not in ConfStat.values():
            return Response(json_response(0, error_code=400, msg="conf_status参数错误"))

        params['conf_id'] = conf_id
        params['mt_e164'] = mt_e164
        params['conf_type'] = conf_type
        params['conf_status'] = conf_status
        params['start_time'] = start_time
        params['end_time'] = end_time
        params['time_on'] = time_on

        try:
            stat, dev_info = DevConfBasicInfo.DevConfBasicInfo(**params).get_info_time()  # 会议终端概况
        except Exception as err:
            logger.error(err)
            return Response(json_response(0, error_code=400, msg=err))
        if not stat:
            # 获取失败
            return Response(json_response(0, error_code=400, msg=dev_info))

        params['info'] = dev_info
        return Response(json_response(1, **params))


class ConfDevMediaInfo(APIView):
    """
    处理 /api/v1/ops/confs/{conf_id}/mts/{mt_e164}/media_info/
    获取会议终端网媒信息
    """

    def get(self, request, version, conf_id, mt_e164):
        params = request.query_params.dict()
        params = dict([(k, v) for k, v in params.items() if v])
        tp = params.get('type')
        start_time = params.get('start_time')
        end_time = params.get('end_time')
        interval = params.get('interval')
        option = params.get('option')
        if not all([start_time, end_time, tp, option]):
            return Response(json_response(0, error_code=400, msg="参数错误"))

        try:
            start_time = int(start_time)
            option = int(option)
            if end_time.isdigit():
                end_time = int(end_time)
            elif end_time == ConfEndTimeType.REALTIME.name or end_time == ConfEndTimeType.MANUAL.name:
                end_time = int((datetime.datetime.now()).timestamp() * 1000)
            elif end_time == ConfEndTimeType.ABEND.name:
                # 异常结会按会议时长2小时计算
                end_time = start_time + 7200000
        except Exception as err:
            logger.error(err)
            return Response(json_response(0, error_code=400, msg="参数错误"))

        use_params = dict(zip(['conf_id', 'mt_e164', 'start_time', 'end_time', 'type', 'option'],
                              [conf_id, mt_e164, start_time, end_time, tp, option]))

        if interval is not None and interval.isdigit():
            use_params['interval'] = int(interval)

        try:
            stat, data_info = DevConfMediaInfo.DevConfMediaInfo(**use_params).get_data()  # 会议终端概况
        except Exception as err:
            logger.error(err)
            return Response(json_response(0, error_code=400, msg=err))
        if not stat:
            # 获取失败
            return Response(json_response(0, error_code=400, msg=data_info))

        params.update(use_params)
        params['info'] = data_info
        return Response(json_response(1, **params))


class ConfDevMediaInfoOptions(APIView):
    """
    处理 /api/v1/ops/confs/{conf_id}/mts/{mt_e164}/media_info/options/
    获取会议终端网媒类型信息
    """

    def get(self, request, version, conf_id, mt_e164):
        params = request.query_params.dict()
        params = dict([(k, v) for k, v in params.items() if v])
        start_time = params.get('start_time')
        end_time = params.get('end_time')
        if not all([start_time, end_time]):
            return Response(json_response(0, error_code=400, msg="参数错误"))

        try:
            start_time = int(start_time)
            if end_time.isdigit():
                end_time = int(end_time)
            elif end_time == ConfEndTimeType.REALTIME.name or end_time == ConfEndTimeType.MANUAL.name:
                end_time = int((datetime.datetime.now()).timestamp() * 1000)
            elif end_time == ConfEndTimeType.ABEND.name:
                # 异常结会按会议时长2小时计算
                end_time = start_time + 7200000
        except Exception as err:
            logger.error(err)
            return Response(json_response(0, error_code=400, msg="参数错误"))

        use_params = dict(zip(['conf_id', 'mt_e164', 'start_time', 'end_time'],
                              [conf_id, mt_e164, start_time, end_time]))

        try:
            stat, data_info = DevConfMediaInfo.get_options(**use_params)  # 会议终端概况
        except Exception as err:
            logger.error(err)
            return Response(json_response(0, error_code=400, msg=err))
        if not stat:
            # 获取失败
            return Response(json_response(0, error_code=400, msg=data_info))

        params.update(use_params)
        params['info'] = data_info
        return Response(json_response(1, **params))


class ConfDevSwitchInfo(APIView):
    """
    处理 /api/v1/ops/confs/{conf_id}/mts/{mt_e164}/switch/
    获取会议终码流链路
    """

    def get(self, request, *args, **kwargs):
        params = request.query_params.dict()
        params = dict([(k, v) for k, v in params.items() if v])
        conf_id = kwargs.get("conf_id")
        mt_e164 = kwargs.get("mt_e164")
        type_ = params.get('type')
        time_ = params.get('time')
        conf_status = params.get('conf_status')
        if not all([conf_id, mt_e164, type_, time_, conf_status]):
            return Response(json_response(0, error_code=400, msg="参数错误"))

        try:
            time_ = int(time_)
            type_ = int(type_)
            conf_status = int(conf_status)
            use_params = dict(zip(['conf_id', 'mt_e164', 'type', 'time', "conf_status"],
                                  [conf_id, mt_e164, type_, time_, conf_status]))
        except Exception as err:
            logger.error(err.args)
            return Response(json_response(0, error_code=400, msg="参数错误"))

        try:
            stat, data_info = es_query.SwitchLink(**use_params).get_data()  # 码流链路
        except Exception as err:
            logger.error(err.args)
            return Response(json_response(0, error_code=400, msg=err.args))
        if not stat:
            # 获取失败
            return Response(json_response(0, error_code=400, msg=data_info))

        params.update(use_params)
        params['info'] = data_info
        return Response(json_response(1, **params))


class ConfDevCallID(APIView):
    """
    query call_id
    """

    def get(self, request, version, conf_id, mt_e164):
        params = request.query_params.dict()
        params = dict([(k, v) for k, v in params.items() if v])
        start_time = params.get('start_time')
        end_time = params.get('end_time')

        if not all([start_time, end_time]):
            return Response(json_response(0, error_code=30002, msg="参数格式错误"))

        try:
            start_time = int(start_time)
            if end_time.isdigit():
                end_time = int(end_time)
            elif end_time == ConfEndTimeType.REALTIME.name or end_time == ConfEndTimeType.MANUAL.name:
                end_time = int((datetime.datetime.now()).timestamp() * 1000)
            elif end_time == ConfEndTimeType.ABEND.name:
                # 异常结会按会议时长2小时计算
                end_time = start_time + 7200000
        except Exception as err:
            logger.error(err.args)
            return Response(json_response(0, error_code=30002, msg='参数格式错误'))

        call_id = CallLinkFunctionsAdapter.get_call_id(mt_e164, start_time, end_time, conf_id)
        params["info"] = call_id
        return Response(json_response(1, **params))


class ConfDevCallIDMethods(APIView):
    """
    query methods for call_id
    """

    def get(self, request, *args, **kwargs):
        params = request.query_params.dict()
        params = dict([(k, v) for k, v in params.items() if v])
        start_time = params.get('start_time')
        end_time = params.get('end_time')
        call_type = params.get("call_type")
        call_id = kwargs.get("call_id")

        if not all([start_time, end_time, call_type]):
            return Response(json_response(0, error_code=30002, msg="参数格式错误"))

        try:
            start_time = int(start_time)
            if end_time.isdigit():
                end_time = int(end_time)
            elif end_time == ConfEndTimeType.REALTIME.name or end_time == ConfEndTimeType.MANUAL.name:
                end_time = int((datetime.datetime.now()).timestamp() * 1000)
            elif end_time == ConfEndTimeType.ABEND.name:
                # 异常结会按会议时长2小时计算
                end_time = start_time + 7200000
        except Exception as err:
            logger.error(err.args)
            return Response(json_response(0, error_code=30002, msg="参数格式错误"))

        methods = CallLinkFunctionsAdapter.get_call_id_methods(call_type, call_id, start_time, end_time)
        params.update(kwargs)
        params["info"] = methods
        return Response(json_response(1, **params))


class ConfDevCallDetail(APIView):

    def get(self, request, *args, **kwargs):
        params = request.query_params.dict()
        params = dict([(k, v) for k, v in params.items() if v])
        start_time = params.get("start_time")
        end_time = params.get("end_time")
        call_type = params.get("call_type")
        call_id = kwargs.get("call_id")

        if not all([start_time, end_time, call_type]):
            return Response(json_response(0, error_code=30002, msg="参数格式错误"))

        try:
            start_time = int(start_time)
            if end_time.isdigit():
                end_time = int(end_time)
            elif end_time == ConfEndTimeType.REALTIME.name or end_time == ConfEndTimeType.MANUAL.name:
                end_time = int((datetime.datetime.now()).timestamp() * 1000)
            elif end_time == ConfEndTimeType.ABEND.name:
                # 异常结会按会议时长2小时计算
                end_time = start_time + 7200000
        except Exception as err:
            logger.error(err.args)
            return Response(json_response(0, error_code=30002, msg="参数格式错误"))

        points, info = CallLinkFunctionsAdapter.get_call_link_info(call_type, call_id, start_time, end_time)
        params.update(kwargs)
        params["points"] = points
        params["info"] = info
        return Response(json_response(1, **params))


class ConfDevCallAllMessages(APIView):
    def get(self, request, *args, **kwargs):
        params = request.query_params.dict()
        params = dict([(k, v) for k, v in params.items() if v])
        start_time = params.get('start_time')
        end_time = params.get('end_time')
        call_type = params.get("call_type")
        start = params.get('start')
        count = params.get('count')
        method = params.get('method')
        call_id = kwargs.get("call_id")

        if not all([start_time, end_time, call_type]):
            return Response(json_response(0, error_code=30002, msg="参数格式错误"))

        try:
            start_time = int(start_time)
            if end_time.isdigit():
                end_time = int(end_time)
            elif end_time == ConfEndTimeType.REALTIME.name or end_time == ConfEndTimeType.MANUAL.name:
                end_time = int((datetime.datetime.now()).timestamp() * 1000)
            elif end_time == ConfEndTimeType.ABEND.name:
                # 异常结会按会议时长2小时计算
                end_time = start_time + 7200000
            start = int(start) if start is not None else 0
            count = int(count) if count is not None else 20
        except Exception as err:
            logger.error(err.args)
            return Response(json_response(0, error_code=30002, msg="参数格式错误"))

        total, info = CallLinkFunctionsAdapter.get_all_call_msg(call_type, call_id, start_time, end_time, start, count, method)
        params.update(kwargs)
        params["total"] = total
        params["info"] = info
        return Response(json_response(1, **params))


class RealTimeStatus(APIView):
    def get(self, request, *args, **kwargs):
        conf_id = kwargs.get('conf_id', '')
        mt_e164 = kwargs.get('mt_e164', '')
        logger.info(conf_id)
        logger.info(mt_e164)
        script_path = os.path.join(BASE_DIR, 'lua', 'get_conf_mt_real_time_status.lua')
        with open(script_path, 'r', encoding='utf8') as f:
            script_content = f.read()
        try:
            status_script = redis_client.register_script(script_content)
            status_result = status_script(args=[conf_id, mt_e164])
            if not status_result:
                raise OpsException(code='10012')
            status_dict = pairs_to_dict(status_result, decode_keys=True)
            for status in status_dict:
                if isinstance(status_dict[status], bytes) and status_dict[status].decode('utf-8').isdigit():
                    status_dict[status] = int(status_dict[status].decode('utf-8'))
                else:
                    status_dict[status] = 0
        except OpsException as e:
            raise e
        except Exception as e:
            logger.exception(e)
            raise OpsException(code='10011')
        else:
            response = global_func.get_response(data=status_dict)
            return Response(response)


class ConferencesActions(APIView):
    '''
    会议事件
    '''

    def get(self, request, *args, **kwargs):
        conf_id = kwargs.get('conf_id')
        start_time = request.query_params.get('start_time', '')
        end_time = request.query_params.get('end_time', '')

        if not start_time:
            raise OpsException(code='10010')
        if end_time and isinstance(end_time, str) and not end_time.isdigit():
            raise OpsException(code='10010')

        # 获取会议事件
        conf_actions = get_conf_actions(request, conf_id)

        # 最终返回前端的格式，info.data按时间正序排序
        data = {
            "conf_id": conf_id,
            "start_time": start_time,
            "end_time": end_time,
            "info": [
                {
                    "name": "create_destroy_conf",
                    "data": sorted(conf_actions.get('create_destroy_conf', []), key=lambda x: x[0]),
                    "description": "开会/结会"
                },
                {
                    "name": "set_cancel_chairman",
                    "data": sorted(conf_actions.get('set_cancel_chairman', []), key=lambda x: x[0]),
                    "description": "设置/取消管理方"
                },
                {
                    "name": "set_cancel_speaker",
                    "data": sorted(conf_actions.get('set_cancel_speaker', []), key=lambda x: x[0]),
                    "description": "设置/取消发言方"
                },
                {
                    "name": "set_cancel_poll",
                    "data": sorted(conf_actions.get('set_cancel_poll', []), key=lambda x: x[0]),
                    "description": "设置/取消轮询"
                },
                {
                    "name": "resume_pause_poll",
                    "data": sorted(conf_actions.get('resume_pause_poll', []), key=lambda x: x[0]),
                    "description": "恢复/暂停轮询"
                },
                {
                    "name": "set_cancel_mix",
                    "data": sorted(conf_actions.get('set_cancel_mix', []), key=lambda x: x[0]),
                    "description": "设置/取消混音"
                },
                {
                    "name": "set_cancel_vmp",
                    "data": sorted(conf_actions.get('set_cancel_vmp', []), key=lambda x: x[0]),
                    "description": "设置/取消画面合成"
                }
            ]
        }

        response = global_func.get_response(data=data)
        return Response(response)
