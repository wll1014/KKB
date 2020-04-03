from django.db import connections
from django.shortcuts import render

# Create your views here.

import time
import copy
import logging
import jsonpath
import os
import re
import shutil
import json
import datetime

from django.http import FileResponse
from django.db.models.query_utils import Q
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, ListCreateAPIView, RetrieveUpdateAPIView, \
    RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from redis.client import parse_list_of_dicts

from common.my_elastic import es_client
from common import global_func, pagination
from diagnose.dsl import es_ql
from diagnose import query_func
from diagnose.models import SnapshotTaskModel, QuickCaptureTaskModel, CustomCaptureTaskModel, CustomCaptureItemsModel
from diagnose.diagnose_serializers import diagnose_serializers
from common.keda_baseclass import KedaWarningBaseAPIView
from common.my_redis import redis_client

from ops.settings import MEDIA_ROOT, BASE_DIR

from diagnose.models import LinkCheckerModel
from diagnose.links import CreateConf, ConfLinkChecker, CallLinkFunctionsAdapter
from common.pagination import ResultsSetPaginationOffset1
from warning.models import ServerWarningUnrepairedModel, TerminalWarningUnrepairedModel
from common.my_exception import OpsException
from diagnose import terminal

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
        kwargs.setdefault("success", 1)
        return kwargs


class SnapShot(APIView):
    def post(self, request, *args, **kwargs):
        apps = request.query_params.get('apps', '')
        key = request.query_params.get('key', '')
        # 毫秒级时间戳
        now = time.time() * 1000
        # 判断是否有导出进程正在进行
        task_queryset = SnapshotTaskModel.objects.filter(is_complete=0).first()
        if task_queryset:
            err = '有未完成的任务： [task_id:%s]' % task_queryset.pk
            logger.info(err)
            response = global_func.get_response(0, error_msg=err)
            try:
                start_time = float(task_queryset.start_time)
            except Exception as e:
                err = str(e)
                logger.error(err)
                start_time = 0

            if now - start_time > 60 * 60 * 1000:
                # 如果上次任务距离现在大于1小时，则认为上次任务失败，停止所有任务相关进程，可开始下一次任务
                query_func.kill_all_task(task_queryset.pk)
                task_queryset.is_complete = 2
                task_queryset.save()
                logger.warning('stop last task which time over 60min...')
            else:
                return Response(response)

        data = {
            'key': key,
            'apps': apps,
            'start_time': now,
        }
        ds = diagnose_serializers.SnapShotSerializer(data=data)
        if ds.is_valid():
            new_queryset = ds.save()

            # 执行导出函数
            is_success, msg = query_func.get_es_data(request, new_queryset.pk)
            if is_success:
                if not key:
                    key = 'nokey'
                new_queryset.filename = '%s_%s.tar.gz' % (new_queryset.pk, key)
                new_queryset.pids = ';'.join(msg)
                new_queryset.is_complete = '0'
                new_queryset.save()
                query_func.check_dump_process(task_id=new_queryset.pk)
                response = global_func.get_response(data={'task_id': new_queryset.pk})
            else:
                new_queryset.err_msg = ';'.join(msg)
                new_queryset.is_complete = '2'
                new_queryset.save()
                response = global_func.get_response(0, error_msg=';'.join(msg))
        else:
            response = global_func.get_response(0, error_msg=ds.errors)
        return Response(response)

    def delete(self, request, *args, **kwargs):
        task_querysets = SnapshotTaskModel.objects.filter(is_complete=0)
        for task_queryset in task_querysets:
            query_func.kill_all_task(task_queryset.pk)
            task_queryset.is_complete = 2
            task_queryset.save()

        response = global_func.get_response()
        return Response(response)


class LogAppTypes(APIView):
    # 日志的app类型
    def get(self, request, *args, **kwargs):
        dsl = copy.deepcopy(es_ql.log_app_types)
        dsls = [dsl]
        m_body = es_client.get_index_header_m_body(*dsls)
        logger.debug(m_body)
        try:
            log_app_types_response = es_client.msearch(m_body)['responses'][0]
        except Exception as e:
            err = str(e)
            logger.error(err)
            log_app_types_response = {}

        apps = []
        if log_app_types_response:
            log_app_type_buckets = jsonpath.jsonpath(log_app_types_response, '$..app_types.buckets')[0]
            if log_app_type_buckets:
                for log_app_type_bucket in log_app_type_buckets:
                    app = log_app_type_bucket.get('key')
                    apps.append(app)
        data = apps

        response = global_func.get_response(data=data)
        return Response(response)


class SnapShotList(KedaWarningBaseAPIView, ListAPIView):
    queryset = SnapshotTaskModel.objects.all()
    serializer_class = diagnose_serializers.SnapShotSerializer
    pagination_class = pagination.ResultsDataSetPaginationOffset


class SnapShotTask(KedaWarningBaseAPIView, RetrieveAPIView):
    serializer_class = diagnose_serializers.SnapShotSerializer
    queryset = SnapshotTaskModel.objects.all()


class Download(APIView):
    def get(self, request, *args, **kwargs):
        task_id = request.query_params.get('task_id', '')
        download_type = request.query_params.get('type', 'snapshot')
        allow_download_type = ['snapshot', 'mtinfo', 'custom_capture']
        if not task_id.isdigit():
            response = global_func.get_response(0, error_msg='参数错误')
            return Response(response)

        if download_type in allow_download_type:
            if download_type == 'snapshot':
                # 快照文件下载
                queryset = SnapshotTaskModel.objects.filter(pk=task_id).first()
            elif download_type == 'mtinfo':
                # 快捷抓包文件下载
                queryset = QuickCaptureTaskModel.objects.filter(pk=task_id).first()
            elif download_type == 'custom_capture':
                # 自定义抓包文件下载
                queryset = CustomCaptureTaskModel.objects.filter(pk=task_id).first()
            else:
                queryset = None

            if queryset:
                file_path = queryset.filename
            else:
                file_path = None
            if file_path:
                full_file_path = os.path.join(MEDIA_ROOT, download_type, file_path)
                if os.path.exists(full_file_path):
                    file = open(full_file_path, 'rb')
                    response = FileResponse(file)
                    # 文件名称
                    response['Content-Disposition'] = 'attachment;filename={}'.format(
                        os.path.basename(full_file_path))
                else:
                    response = global_func.get_response(0, error_msg='文件不存在')
                    response = Response(response)
            else:
                response = global_func.get_response(0, error_msg='参数错误')
                response = Response(response)
        else:
            response = global_func.get_response(
                0, error_msg='type:%s only allow %s' % (download_type, allow_download_type)
            )
            response = Response(response)
        return response


class Link(APIView):
    """
    链路检测
    包括会议链路和呼叫链路
    """

    def get(self, request, version):
        try:
            items = LinkCheckerModel.objects.all()
            pagination = ResultsSetPaginationOffset1()
            pg_res = pagination.paginate_queryset(queryset=items, request=request, view=self)
            items_series = diagnose_serializers.LinkSerializer(instance=pg_res, many=True)
            return pagination.get_paginated_response(items_series.data)
        except Exception as err:
            logger.error(err)
            return Response(json_response(0, error_code=421, msg='数据库操作失败'))

    def post(self, request, version):
        """
        创建链路检测
        :param request:
        :param version:
        :return:
        """
        try:
            creator = request.META.get('ssoAuth').get('account')
        except Exception as err:
            logger.error(err)
            return Response(json_response(0, error_code=422, msg='授权信息错误'))

        try:
            user = request.data.get('user')
            password = request.data.get('password')
            mt_id = request.data.get('mt_id')

            if user is None or password is None:
                return Response(json_response(0, error_code=403, msg='用户名或密码不能为空'))
            mt_id = mt_id if mt_id is not None else ""
        except Exception as err:
            logger.error(err)
            return Response(json_response(0, error_code=404, msg='数据格式错误'))

        try:
            active_task = LinkCheckerModel.objects.filter(is_complete=0)
        except Exception as err:
            logger.error(err)
            return Response(json_response(0, error_code=421, msg='数据库操作失败'))

        if len(active_task) >= 1:
            for a_t in active_task:
                if int(time.time() * 1000) - int(a_t.start_time) > 130000:
                    end_time = int(a_t.start_time) + 130000
                    # 任务超过2min 强制结束
                    a_t.is_complete = 1
                    a_t.need_del = 1
                    a_t.end_time = end_time
                    a_t.save(update_fields=['is_complete', 'need_del', 'end_time'])
            real_active_num = LinkCheckerModel.objects.filter(is_complete=0).count()
            if real_active_num >= 1:
                return Response(json_response(0, error_code=402, msg='任务数量已达上限,请稍后重试'))

        task_info = [[task.user, task.mt_id] for task in active_task]
        task_hash = [hash(str(task[0]) + str(task[1])) for task in task_info]
        if hash(str(user) + str(mt_id)) in task_hash:
            return Response(json_response(0, error_code=401, msg='任务已经创建或有其它类型的链路检测任务正在运行'))

        link_type = 1 if mt_id == "" else 2
        create_time = int(time.time() * 1000)
        data = {"creator": creator, "user": user, "link_type": link_type, "mt_id": mt_id, 'start_time': create_time}
        data_serializer = diagnose_serializers.LinkSerializer(data=data)

        if data_serializer.is_valid():
            try:
                new_obj = data_serializer.save()
            except Exception as err:
                logger.error(err)
                return Response(json_response(0, error_code=421, msg='数据库操作失败'))
        else:
            err = data_serializer.errors
            logger.error(str(err))
            return Response(json_response(0, error_code=405, msg=err))

        # 新开进程开始任务
        link_task = CreateConf(user, password, new_obj.task_id)
        # link_task.daemon = False
        link_task.start()

        # 主线程返回
        task_id = new_obj.task_id
        return Response(json_response(1, task_id=task_id))


class LinkDetail(APIView):
    def get(self, request, version, task_id):
        try:
            item = LinkCheckerModel.objects.get(task_id=task_id)
        except (LinkCheckerModel.DoesNotExist, LinkCheckerModel.MultipleObjectsReturned) as err:
            logger.error(err)
            return Response(data=json_response(0, error_code=424, msg='请求信息不存在'))
        except Exception as err:
            logger.error(err)
            return Response(json_response(0, error_code=421, msg='数据库操作失败'))
        else:
            start_time = int(item.start_time)
            if int(time.time() * 1000) - start_time > 130000:
                end_time = start_time + 130000
                # 任务超过2min 强制结束
                item.is_complete = 1
                item.need_del = 1
                item.end_time = end_time
                item.save(update_fields=['is_complete', 'need_del', 'end_time'])
                item.refresh_from_db()
            item_data = diagnose_serializers.LinkSerializer(item, many=False).data

        conf_id = item_data['conf_id']
        conf_name = item_data['conf_name']
        if not (conf_id or conf_name):
            item_data['points'] = []
            item_data['info'] = []
            return Response(json_response(1, data=item_data))

        end_time = item.end_time
        if not end_time:
            end_time = int(time.time() * 1000)

        if conf_id:
            conf = conf_id
            conf_tp = 'id'
        else:
            conf = conf_name
            conf_tp = 'name'

        info = ConfLinkChecker(conf, conf_tp, start_time, end_time).check()
        item_data['points'] = info[0]
        item_data['info'] = info[1]
        return Response(json_response(1, data=item_data))


class LinkCallID(APIView):
    """
    query call_id
    """

    def get(self, request, version, task_id):
        try:
            item = LinkCheckerModel.objects.get(task_id=task_id)
        except (LinkCheckerModel.DoesNotExist, LinkCheckerModel.MultipleObjectsReturned) as err:
            logger.error(err.args)
            return Response(data=json_response(0, error_code=424, msg='请求信息不存在'))
        except Exception as err:
            logger.error(err.args)
            return Response(json_response(0, error_code=421, msg='数据库操作失败'))

        start_time = item.start_time
        end_time = item.end_time
        mt_id = item.mt_id
        conf_id = item.conf_id
        is_complete = int(item.is_complete)
        link_type = item.link_type

        if mt_id == "":
            return Response(json_response(0, error_code=421, msg='链路类型错误'))

        end_time_ins = end_time if end_time else str(time.time() * 1000)
        call_id = CallLinkFunctionsAdapter.get_call_id(mt_id, start_time, end_time_ins, conf_id)

        data = {'task_id': task_id, 'link_type': link_type, 'is_complete': is_complete, 'mt_id': mt_id,
                'start_time': start_time, 'end_time': end_time, 'info': call_id}
        return Response(json_response(1, data=data))


class LinkCallIDMethods(APIView):
    """
    query methods for call_id
    """

    def get(self, request, version, call_id):
        params = request.query_params.dict()
        params = dict([(k, v) for k, v in params.items() if v])
        start_time = params.get('start_time')
        end_time = params.get('end_time')
        call_type = params.get("call_type")

        try:
            start_time = int(start_time)
            end_time = int(end_time)
        except Exception as err:
            logger.error(err.args)
            return Response(json_response(0, error_code=30002, msg='参数格式错误'))

        methods = CallLinkFunctionsAdapter.get_call_id_methods(call_type, call_id, start_time, end_time)
        params["call_id"] = call_id
        params["info"] = methods
        return Response(json_response(1, data=params))


class LinkCallDetail(APIView):
    """
    pass
    """

    def get(self, request, version, call_id):
        params = request.query_params.dict()
        params = dict([(k, v) for k, v in params.items() if v])
        start_time = params.get('start_time')
        end_time = params.get('end_time')
        call_type = params.get("call_type")

        try:
            start_time = int(start_time)
            end_time = int(end_time) if end_time else int(time.time() * 1000)
        except Exception as err:
            logger.error(err.args)
            return Response(json_response(0, error_code=30002, msg='参数格式错误'))

        points, info = CallLinkFunctionsAdapter.get_call_link_info(call_type, call_id, start_time, end_time)

        data = dict(zip(['call_id', 'start_time', 'end_time', 'points', 'info'],
                        [call_id, start_time, end_time, points, info]))
        return Response(json_response(1, data=data))


class LinkCallAllMessages(APIView):
    def get(self, request, version, call_id):
        params = request.query_params.dict()
        params = dict([(k, v) for k, v in params.items() if v])
        start_time = params.get('start_time')
        end_time = params.get('end_time')
        call_type = params.get("call_type")
        start = params.get('start')
        count = params.get('count')
        method = params.get('method')

        try:
            start_time = int(start_time)
            end_time = int(end_time) if end_time else int(time.time() * 1000)
            start = int(start) if start is not None else 0
            count = int(count) if count is not None else 20
        except Exception as err:
            logger.error(err.args)
            return Response(json_response(0, error_code=30002, msg='参数格式错误'))

        call_data = CallLinkFunctionsAdapter.get_all_call_msg(call_type, call_id, start_time, end_time, start, count, method)
        total, info = call_data
        params['total'] = total
        params['info'] = info
        return Response(json_response(1, data=params))


class QuickCaptureTaskDetailRetrieveAPIView(KedaWarningBaseAPIView):
    # 重写retrieve方法，供一键抓包返回错误使用
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        logger.info(response.data)
        if response.data.get('success') == 0:
            logger.info(response.data.get('success'))
            return response
        is_complete = response.data.get('data', {}).get('is_complete', 1)
        conf_e164 = response.data.get('data', {}).get('conf_e164', '')
        mt_e164 = response.data.get('data', {}).get('mt_e164', '')
        if is_complete in [0, 1]:
            # 正常返回
            logger.info(response.data.get('success'))
            return response
        elif is_complete == 2:
            # 脚本参数错误
            logger.info(response.data.get('success'))
            raise OpsException(code='10013', detail='脚本参数错误')
        elif is_complete == 3:
            logger.info(response.data.get('success'))
            raise OpsException(code='10013', detail='redis 连接失败')
        elif is_complete == 4:
            logger.info(response.data.get('success'))
            raise OpsException(code='10013', detail='请确认会议%s是否存在' % conf_e164)
        elif is_complete == 5:
            logger.info(response.data.get('success'))
            raise OpsException(code='10013', detail='%s未加入会议' % mt_e164)
        elif is_complete == 100:
            logger.info(response.data.get('success'))
            raise OpsException(code='10013', detail='抓包文件打包错误')
        else:
            logger.info(response.data.get('success'))
            raise OpsException(code='10013')


class QuickCaptureTaskDetail(QuickCaptureTaskDetailRetrieveAPIView, RetrieveAPIView):
    queryset = QuickCaptureTaskModel.objects.all()
    serializer_class = diagnose_serializers.QuickCaptureSerializer


class QuickCaptureTask(KedaWarningBaseAPIView, ListAPIView):
    queryset = QuickCaptureTaskModel.objects.all().order_by('-id')
    serializer_class = diagnose_serializers.QuickCaptureSerializer
    pagination_class = pagination.ResultsDataSetPaginationOffset

    def post(self, request, *args, **kwargs):
        conf_e164 = request.data.get('conf_e164', '')
        mt_e164 = request.data.get('mt_e164', '')
        if not all([conf_e164, mt_e164]):
            raise OpsException(code='10010')
        # 毫秒级时间戳
        now = time.time() * 1000
        # 距现在多久可以认为前一次未完成的任务失败，并开始新任务(ms时间戳)
        max_time = 60 * 60 * 1000
        # 判断是否有导出进程正在进行
        task_queryset = QuickCaptureTaskModel.objects.filter(is_complete=0).first()
        if task_queryset:
            err_msg = '有任务正在执行...'
            try:
                start_time = float(task_queryset.start_time)
            except Exception as e:
                err = str(e)
                logger.error(err)
                start_time = 0

            if now - start_time > max_time:
                # 如果上次任务距离现在大于 max_time，则认为上次任务失败，停止所有任务相关进程，可开始下一次任务
                query_func.kill_all_task(task_queryset.pk)
                task_queryset.is_complete = '2'
                task_queryset.save()
                logger.warning('stop last task which time over %ss...' % (max_time / 1000))
            else:
                raise OpsException(code='10013', detail=err_msg)

        data = {
            'conf_e164': conf_e164,
            'mt_e164': mt_e164,
            'start_time': now,
        }
        ds = diagnose_serializers.QuickCaptureSerializer(data=data)
        if ds.is_valid():
            new_queryset = ds.save()
            # 执行抓包函数
            p_get_quick_capture_result = query_func.TaskResult(request, new_queryset.pk)
            p_get_quick_capture_result.start()
            response = global_func.get_response(data={'task_id': new_queryset.pk})
        else:
            logger.error(ds.errors)
            raise OpsException(code='10013')
        return Response(response)


class CustomCaptureTask(KedaWarningBaseAPIView, ListAPIView):
    '''
    自定义抓包
    '''
    queryset = CustomCaptureTaskModel.objects.all().order_by('-id')
    serializer_class = diagnose_serializers.CustomCaptureListSerializer
    pagination_class = pagination.ResultsDataSetPaginationOffset


class CustomCaptureTaskDetail(KedaWarningBaseAPIView, RetrieveUpdateAPIView):
    queryset = CustomCaptureTaskModel.objects.all()
    serializer_class = diagnose_serializers.CustomCaptureRetrieveSerializer
    pagination_class = pagination.ResultsDataSetPaginationOffset


class CustomCaptureItem(KedaWarningBaseAPIView, ListCreateAPIView):
    queryset = CustomCaptureItemsModel.objects.all().order_by('-id')
    serializer_class = diagnose_serializers.CustomCaptureItemsSerializer
    pagination_class = pagination.ResultsDataSetPaginationOffset

    def post(self, request, *args, **kwargs):
        data = request.data
        task = CustomCaptureTaskModel.objects.all().first()
        if task:
            data['task'] = task.pk
        devtype = ''
        if str(data.get('item_type', 1)) == '2':
            # 判断抓包终端是否支持抓包
            moid = data.get('moid', '')
            if moid:
                dsl = copy.deepcopy(es_ql.mttype_online_offline)
                dsl['dsl']['query']['bool']['must'].append({'match_phrase': {'source.devid': moid}})
                dsls = [dsl]
                m_body = es_client.get_index_header_m_body(*dsls)
                logger.debug(m_body)
                try:
                    mt_response = es_client.msearch(m_body)['responses'][0]
                except Exception as e:
                    err = str(e)
                    logger.error(err)
                    mt_response = {}
                if mt_response:
                    source = jsonpath.jsonpath(mt_response, '$..source')
                    if source:
                        source = source[0]
                        devtype = source.get('devtype', '')
                        eventid = source.get('eventid', '')
                        if eventid == 'EV_DEV_OFFLINE':
                            response = global_func.get_response(0, error_msg='该终端未注册网管')
                            return Response(response)
                        if 'truelink' in devtype.lower() or 'windows' in devtype.lower():
                            response = global_func.get_response(0, error_msg='该终端不支持抓包')
                            return Response(response)
                    else:
                        response = global_func.get_response(0, error_msg='该终端未注册网管')
                        return Response(response)
                else:
                    response = global_func.get_response(0, error_code=10001)
                    return Response(response)
        request.data['dev_type'] = devtype
        return super().post(request, *args, **kwargs)


class CustomCaptureItemDetail(KedaWarningBaseAPIView, RetrieveUpdateDestroyAPIView):
    queryset = CustomCaptureItemsModel.objects.all()
    serializer_class = diagnose_serializers.CustomCaptureItemsRetrieveSerializer
    pagination_class = pagination.ResultsDataSetPaginationOffset


class MachineCards(APIView):
    def get(self, request, *args, **kwargs):
        machine_moid = kwargs.get('machine_moid')
        network_card_info = query_func.get_luban_machines_network_card_info([machine_moid])
        logger.debug(network_card_info)
        if network_card_info:
            cards = network_card_info.get(machine_moid, {}).get('cards', [])
            machine_name = network_card_info.get(machine_moid, {}).get('machine_name')
            data = {'machine_moid': machine_moid, 'machine_name': machine_name, 'cards': cards}
            response = global_func.get_response(data=data)
        else:
            response = global_func.get_response(0, error_msg='machine_moid not found')
        return Response(response)


class CustomCaptureTaskHandler(APIView):
    def post(self, request, *args, **kwargs):
        '''
        开始抓包
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        task = CustomCaptureTaskModel.objects.all().first()
        if not task:
            response = global_func.get_response(0, error_msg='任务错误')
            return Response(response)
        if float(task.start_time) > (time.time() - 60 * 20) * 1000:
            # 开始时间在 二十分钟之内，则判断是否有未结束的任务
            for item in task.customcaptureitemsmodel_set.all():
                if item.is_complete == 0:
                    response = global_func.get_response(0, error_msg='任务暂未结束')
                    return Response(response)
        task_id = task.pk
        # filename置空
        CustomCaptureTaskModel.objects.filter(pk=task_id).update(start_time=time.time() * 1000, filename='')
        # 所有任务改为未完成状态
        task.customcaptureitemsmodel_set.all().update(is_complete=0)
        # 删除旧文件
        custom_capture_path = os.path.join(MEDIA_ROOT, 'custom_capture')
        shutil.rmtree(custom_capture_path, ignore_errors=True)
        os.makedirs(custom_capture_path, exist_ok=True)
        # 开始抓包、打包进程
        p_start_server_custom_capture = query_func.TaskResult(request, task_id, task_type='start_server_custom_capture')
        p_start_terminal_custom_capture = query_func.TaskResult(request, task_id,
                                                                task_type='start_terminal_custom_capture')
        p_check_terminal_capture_status = query_func.TaskResult(request, task_id,
                                                                task_type='check_terminal_capture_status')
        p_compress_capture_files = query_func.TaskResult(request, task_id, task_type='compress_capture_files')
        p_start_server_custom_capture.start()
        p_start_terminal_custom_capture.start()
        p_check_terminal_capture_status.start()
        p_compress_capture_files.start()

        response = global_func.get_response()
        return Response(response)

    def put(self, request, *args, **kwargs):
        '''
        结束抓包
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        task = CustomCaptureTaskModel.objects.all().first()
        if not task:
            response = global_func.get_response(0, error_msg='任务错误')
            return Response(response)
        if all([item.is_complete for item in task.customcaptureitemsmodel_set.all()]):
            # 所有任务都不是“正在执行”状态
            response = global_func.get_response(0, error_msg='任务暂未开始')
            return Response(response)

        task_id = task.pk
        incomplete_server_count = task.customcaptureitemsmodel_set.filter(Q(item_type=1) & Q(is_complete=0)).count()
        incomplete_terminal_count = task.customcaptureitemsmodel_set.filter(Q(item_type=2) & Q(is_complete=0)).count()
        if incomplete_server_count:
            p_stop_server_custom_capture = query_func.TaskResult(request, task_id,
                                                                 task_type='stop_server_custom_capture')
            p_stop_server_custom_capture.start()
            logger.info('stop server capture')

        if incomplete_terminal_count:
            p_stop_terminal_custom_capture = query_func.TaskResult(request, task_id,
                                                                   task_type='stop_terminal_custom_capture')
            p_stop_terminal_custom_capture.start()
            logger.info('stop terminal capture')

        response = global_func.get_response()
        return Response(response)

    def delete(self, request, *args, **kwargs):
        '''
        清空对象及抓包文件
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        task = CustomCaptureTaskModel.objects.all().first()
        if not task:
            response = global_func.get_response(0, error_msg='任务错误')
            return Response(response)
        if task.customcaptureitemsmodel_set.filter(is_complete=0).exists():
            response = global_func.get_response(0, error_msg='任务未完成')
            return Response(response)
        try:
            task.customcaptureitemsmodel_set.all().delete()
            response = global_func.get_response()
        except Exception as e:
            err = str(e)
            logger.error(err)
            response = global_func.get_response(0, error_msg=err)
        else:
            custom_capture_path = os.path.join(MEDIA_ROOT, 'custom_capture')
            shutil.rmtree(custom_capture_path, ignore_errors=True)
            os.makedirs(custom_capture_path, exist_ok=True)

        return Response(response)


class AppsCheck(APIView):
    # 应用检测
    def post(self, request, *args, **kwargs):
        check_type = kwargs.get('check_type')
        if check_type:
            p = query_func.CheckAppsProcess(request, 1, 'check_%s' % check_type)
        else:
            p = query_func.CheckAppsProcess(request, 1, 'check_all')
        if p.is_running:
            response = global_func.get_response(0, error_msg='正在检测，请稍后')
            return Response(response)
        if not p.is_conf_ok:
            response = global_func.get_response(0, error_msg='读取配置有误，请查询luban数据库是否可用')
            return Response(response)
        p.start()
        response = global_func.get_response()
        return Response(response)

    def get(self, request, *args, **kwargs):
        check_type = kwargs.get('check_type')
        if check_type:
            p = query_func.CheckAppsProcess(request, 1, 'check_%s' % check_type)
            data = p.get_result(check_type)
        else:
            p = query_func.CheckAppsProcess(request, 1, 'check_all')
            data = p.get_all_result()

        response = global_func.get_response(data=data)
        return Response(response)


class AppsCheckExport(APIView):
    # 应用检测结果文件导出
    def get(self, request, *args, **kwargs):
        file_format = 'tar.gz'
        base_name = 'check_apps'
        file_name = base_name + '.' + file_format
        base_path = os.path.join(MEDIA_ROOT, 'check_apps')
        file_path = os.path.join(base_path, base_name)
        full_path = os.path.join(base_path, file_name)
        if os.path.exists(full_path):
            os.remove(full_path)
        try:
            export_file_path = shutil.make_archive(base_name=file_path, format='gztar',
                                                   root_dir=os.path.dirname(file_path),
                                                   logger=logger)
        except Exception as e:
            err = str(e)
            logger.error(err)
            response = global_func.get_response(0, error_msg='压缩文件失败')
            response = Response(response)
            return response

        if os.path.exists(export_file_path):
            file = open(export_file_path, 'rb')
            response = FileResponse(file)
            # 文件名称
            response['Content-Disposition'] = 'attachment;filename={}'.format(
                os.path.basename(export_file_path))
        else:
            response = global_func.get_response(0, error_msg='文件不存在')
            response = Response(response)

        return response


class AppsCheckLog(APIView):
    # 应用检测结果文件导出
    def get(self, request, *args, **kwargs):
        check_type = kwargs.get('check_type')
        section = kwargs.get('section')
        log = query_func.CheckAppsProcess(request, 1).get_log(check_type, section)
        data = {'log': log, 'check_type': check_type, 'section': section}
        response = global_func.get_response(data=data)

        return Response(response)


class ConfTopologyRooms(APIView):
    # 获取会议拓扑的机房
    def get(self, request, *args, **kwargs):
        machine_room_moid = request.query_params.get('machine_room_moid', '')
        try:
            with connections['luban'].cursor() as cursor:
                all_used_room_sql = '''
                SELECT mri.machine_room_moid,mri.machine_room_name,mri.machine_room_type,di.domain_moid,di.domain_name
                FROM machine_room_info mri 
                LEFT JOIN domain_info di 
                ON mri.domain_moid=di.domain_moid 
                WHERE mri.machine_num>=0 
                '''

                if machine_room_moid:
                    all_used_room_sql += ' AND mri.machine_room_moid=\'%s\'' % machine_room_moid
                all_used_room_sql += ' ORDER BY mri.id'
                cursor.execute(all_used_room_sql, )
                all_used_rooms = cursor.fetchall()

            data = []
            manager_rooms = [used_room[0] for used_room in all_used_rooms if used_room[2] == 1]
            for used_room in all_used_rooms:
                data.append({
                    'machine_room_moid': used_room[0],
                    'machine_room_name': used_room[1],
                    'machine_room_type': used_room[2],
                    'domain_moid': used_room[3],
                    'domain_name': used_room[4],
                    'status': 1 if ServerWarningUnrepairedModel.objects.filter(
                        machine_room_moid=used_room[0]).exists() else 0,  # 机房状态是否正常：0：正常，1：不正常
                    'link': [{'machine_room_moid': manager_room, 'detail': {}} for manager_room in manager_rooms if
                             manager_room != used_room[0]]  # detail 字段备用
                })
        except Exception as e:
            err = str(e)
            logger.error(err)
            response = global_func.get_response(0, error_msg=err)
            return Response(response)
        else:
            response = global_func.get_response(data=data)
            return Response(response)


class ConfTopologyRoomConfs(APIView):
    # 获取会议列表，支持过滤机房、会议号
    def get(self, request, *args, **kwargs):
        machine_room_moid = request.query_params.get('machine_room_moid', '')
        keywords = request.query_params.get('keywords', '')
        data = {}
        try:
            script_path = os.path.join(BASE_DIR, 'lua', 'get_real_conf_list_mt_list.lua')
            with open(script_path, 'r') as f:
                script_content = f.read()
            result = redis_client.eval(script_content, 0, machine_room_moid)
            if machine_room_moid:
                data['machine_room_moid'] = machine_room_moid
            confs = parse_list_of_dicts(result)
            no_mts_confs = []
            for conf in confs:
                mts = parse_list_of_dicts(conf.get('mts'))
                conf['mts'] = mts
                conf_copy = conf.copy()
                del conf_copy['mts']
                no_mts_confs.append(conf_copy)
            filtered_confs = []
            if keywords:
                for i, conf in enumerate(confs):
                    conf_e164 = conf.get('e164', b'').decode()
                    conf_name = conf.get('name', b'').decode()
                    conf_creator_name = conf.get('creatorname', b'').decode()
                    mt_e164 = ' '.join([mt.get('e164', b'').decode() for mt in conf.get('mts', [])])
                    mt_name = ' '.join([mt.get('mtalias', b'').decode() for mt in conf.get('mts', [])])

                    if re.search(r'.*%s.*' % keywords,
                                 ' '.join([conf_e164, conf_name, conf_creator_name, mt_e164, mt_name])):
                        filtered_confs.append(no_mts_confs[i])
                no_mts_confs = filtered_confs
            data['keywords'] = keywords
            # 按照开始时间排序，前端渲染保证顺序不变
            confs = sorted(no_mts_confs, key=lambda conf: conf['real_start_time'], reverse=True)

        except Exception as e:
            logger.exception(e)
            response = global_func.get_response(0, error_msg=';'.join(e.args))
            return Response(response)
        else:
            data['info'] = confs
            response = global_func.get_response(data=data)

            return Response(response)


class ConfTopologyConfDetail(APIView):
    # 获取会议详情
    def get(self, request, *args, **kwargs):
        e164 = kwargs.get('e164')
        script_path = os.path.join(BASE_DIR, 'lua', 'get_conf_mts_info.lua')
        with open(script_path, 'r') as f:
            script_content = f.read()
        try:
            data = {'e164': e164, 'info': []}
            result = redis_client.eval(script_content, 0, e164)

            mts = parse_list_of_dicts(result)
            mts_e164 = [mt['e164'] for mt in mts]
            if mts_e164:
                with connections['movision'].cursor() as cursor:
                    sql = '''
                    SELECT e164,moid FROM user_info
                    WHERE isdeleted = '0' AND account_type != '9' AND 
                    (device_type IS NULL or device_type NOT IN ('519','524','530','531')) AND
                    binded='0' AND account IS NOT NULL AND e164 IN %s
                    '''
                    params = [mts_e164]
                    cursor.execute(sql, params)
                    fetchall = cursor.fetchall()

                e164tomoid = {fetch[0]: fetch[1] for fetch in fetchall}
                mt_info = query_func.query_mt_addr([mt_e164.decode('utf-8') for mt_e164 in mts_e164])
                for mt in mts:
                    mt['status'] = 1 if TerminalWarningUnrepairedModel.objects.filter(
                        device_moid=e164tomoid.get(mt['e164'])).exists() else 0  # 机房状态是否正常：0：正常，1：不正常
                    # 查询终端本机地址
                    if hasattr(mt['e164'], 'decode'):
                        now_mt_e164 = mt['e164'].decode('utf-8')
                    else:
                        now_mt_e164 = mt['e164']
                    mt['ip'] = mt_info.get(now_mt_e164, {}).get('mtaddr', '')

                data['info'] = mts
        except Exception as e:
            logger.exception(e)
            raise OpsException()
        else:
            response = global_func.get_response(data=data)
            return Response(response)


class TerminalAccountsSearch(APIView):
    # 终端诊断  搜索终端
    def get(self, request, *args, **kwargs):
        params = request.query_params.dict()
        keyword = params.get("keyword")
        if keyword is None:
            raise OpsException(code='30001')

        results = terminal.AccountsTerminalSearch(keyword).search()
        params["info"] = results
        return Response(json_response(1, data=params))


class TerminalAccountInfo(APIView):
    # 终端诊断  获取账号信息
    def get(self, request, *args, **kwargs):
        e164 = kwargs.get("e164")

        results = terminal.AccountTerminalInfo(e164).get_account_info()
        kwargs["info"] = results
        return Response(json_response(1, data=kwargs))


class AccountTerminalsList(APIView):
    # 终端诊断  获取账号下的所有终端
    def get(self, request, *args, **kwargs):
        e164 = kwargs.get("e164")

        results = terminal.AccountTerminals(e164).get_terminals()
        kwargs["info"] = results
        return Response(json_response(1, data=kwargs))


class TerminalConnectInfo(APIView):
    # 终端诊断  获取终端连接信息
    def get(self, request, *args, **kwargs):
        e164 = kwargs.get("e164")
        dev_type = kwargs.get("terminal")

        results = terminal.TerminalConnect(e164, dev_type).get_connect()
        kwargs["info"] = results
        return Response(json_response(1, data=kwargs))


class TerminalStatusInfo(APIView):
    # 终端诊断  获取设备状态信息
    def get(self, request, *args, **kwargs):
        e164 = kwargs.get("e164")
        dev_type = kwargs.get("terminal")

        results = terminal.TerminalStatus(e164, dev_type).get_status()
        kwargs["info"] = results
        return Response(json_response(1, data=kwargs))


class TerminalStatisticInfo(APIView):
    # 终端诊断  获取设备统计信息
    def get(self, request, *args, **kwargs):
        e164 = kwargs.get("e164")
        dev_type = kwargs.get("terminal")

        results = terminal.TerminalStatistic(e164, dev_type).get_statistic()
        kwargs["info"] = results
        return Response(json_response(1, data=kwargs))


class TerminalPeripheralInfo(APIView):
    # 终端诊断  获取设备外设信息
    def get(self, request, *args, **kwargs):
        e164 = kwargs.get("e164")
        dev_type = kwargs.get("terminal")

        results = terminal.TerminalPeripheral(e164, dev_type).get_peripheral()
        kwargs["info"] = results
        return Response(json_response(1, data=kwargs))


class TerminalCrucialProcessesInfo(APIView):
    # 终端诊断  获取设备关键进程信息
    def get(self, request, *args, **kwargs):
        e164 = kwargs.get("e164")
        dev_type = kwargs.get("terminal")

        results = terminal.TerminalCrucialProcesses(e164, dev_type).get_crucial_processes()
        kwargs["info"] = results
        return Response(json_response(1, data=kwargs))


class TerminalCallRecordsInfo(APIView):
    # 终端诊断  获取设备呼叫信息
    def get(self, request, *args, **kwargs):
        params = request.query_params.dict()
        start = params.get("start", 0)
        count = params.get("count", 20)

        e164 = kwargs.get("e164")
        dev_type = kwargs.get("terminal")

        total, results = terminal.TerminalCallRecords(e164, dev_type, start, count).get_call_records()
        kwargs["total"] = total
        kwargs["info"] = results
        kwargs.update(params)
        return Response(json_response(1, data=kwargs))
