import requests
from django.db.models.query_utils import Q
from django.shortcuts import render

# Create your views here.

import logging
import json
import os
from .models import ScriptFiles, DistributionFileModel, DistributionTasksModel, RealTimeTasksModel, CronTasksModel
from django.db import transaction
from django.http import JsonResponse
from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from common.pagination import ResultsSetPaginationOffset1
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver

from datetime import datetime
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView, RetrieveDestroyAPIView
from rest_framework import filters
from django.utils import timezone

from hosts_oper.hosts_oper_serializer.hosts_oper_serializer import RealTimeTasksListSerializer, \
    RealTimeTasksCreateSerializer, RealTimeTasksDetailSerializer, \
    CronTasksCreateSerializer, CronTasksDetailSerializer, CronTasksListSerializer, CronTasksUpdateSerializer, \
    FileDistributionSerializer, DistributionTasksListSerializer, DistributionTasksRetrieveSerializer, \
    DistributionTasksCreateSerializer, DistributionTasksUpdateSerializer
from common.keda_baseclass import KedaWarningBaseAPIView, MultiDeleteAPIView
from common.pagination import ResultsDataSetPaginationOffset
from common import global_func
from common.my_ansible import AnsibleTask, AnsibleSameInfoHosts
from hosts_oper import task_func
from ops.settings import MEDIA_ROOT

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


# 数据库删除脚本时连同文件一起删除
@receiver(pre_delete, sender=ScriptFiles)
def script_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.file.delete(False)


# 数据库删除分发文件时连同文件一起删除
@receiver(pre_delete, sender=DistributionFileModel)
def distribution_file_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.file.delete(False)


class ScriptSerializers(serializers.ModelSerializer):
    """
    脚本管理序列化
    """
    size = serializers.IntegerField(source='file.size', read_only=True)
    url = serializers.CharField(source='file.url', read_only=True)
    upload_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = ScriptFiles
        fields = ('id', 'filename', 'size', 'upload_time', 'uploader', 'postscript', 'url')


class ScriptFileHandler(APIView):
    """
    处理 api/v1/ops/hosts_oper/scripts/ 请求
    """

    def get(self, request, version):
        """
        处理GET请求
        :param request:
        :param version: API版本号
        :return:
        """
        params = request.query_params.dict()
        # obtain Conditional query parameter from URL

        # fuzzy search
        columns = ["filename"]
        conditions = {key + '__icontains': params.get(key) for key in columns if params.get(key)}

        # exact search
        uploader_condition = params.get("uploader")
        if uploader_condition is not None:
            conditions['uploader__exact'] = uploader_condition

        start_time = params.get("starttime")
        end_time = params.get("endtime")
        if start_time and end_time:
            conditions['upload_time__range'] = (start_time, end_time)

        if not conditions:
            # 无筛选条件返回全部数据
            items = ScriptFiles.objects.all().order_by('-id')
        else:
            # 有筛选条件返回筛选数据
            items = ScriptFiles.objects.filter(**conditions).order_by('-id')

        try:
            if items:
                # 数据不为空正常返回数据
                pagination = ResultsSetPaginationOffset1()  # create pagination object
                pg_res = pagination.paginate_queryset(queryset=items, request=request, view=self)  # get pagination data
                items_series = ScriptSerializers(instance=pg_res, many=True)
                return pagination.get_paginated_response(items_series.data, **params)
            else:
                # 数据为空返回空列表
                return Response(data={'success': 1, 'data': {"total": 0, "start": 0, "count": 0, "info": []}})
        except Exception as err:
            logger.error(err)
            return JsonResponse(json_response(0, error_code=421, msg='数据库操作失败'))

    def post(self, request, version):
        """
        处理POST请求，上传文件
        一次只上传一个文件
        :param request:
        :param version: API版本号
        """

        try:
            uploader = request.META.get('ssoAuth').get('account')
        except Exception as err:
            logger.error(err)
            return JsonResponse(json_response(0, error_code=422, msg='授权为空'))
        else:
            if len(request.FILES) == 0:
                # 文件为空，返回失败
                return JsonResponse(json_response(0, error_code=422, msg='数据为空'))

        for file in request.FILES.values():
            size = file.size
            name = file.name
            if size > 2097152:
                # 文件最大2M，即 2097152 byte
                return JsonResponse(json_response(0, filename=name, eror_code=422, msg='数据最大为2M'))  # 一次只上传一个文件

            data = {'file': file, 'uploader': uploader, 'filename': name}
            front_data = ScriptSerializers(data=data)
            if front_data.is_valid():
                try:
                    with transaction.atomic():
                        ScriptFiles.objects.create(**data)
                        # front_data.save()
                except Exception as err:
                    logger.error(err)
                    return JsonResponse(json_response(0, filename=name, eror_code=421, msg='数据库操作失败'))
                else:
                    return JsonResponse(json_response(1, filename=name))
            else:
                logger.error(front_data.errors)
                return JsonResponse(json_response(0, filename=name, eror_code=422, msg='数据格式错误'))

    def delete(self, request, version):
        """
        处理DELETE请求
        delete items
        :param request:
        :param version: API版本号
        """

        # 获取待删除数据id的数组
        try:
            ids = json.loads(request.body.decode()).get('ids')
        except Exception as err:
            logger.error(err)
            return JsonResponse(json_response(0, error_code=422, msg='数据格式错误'))
        else:
            if not all([isinstance(x, int) for x in ids]):
                return JsonResponse(json_response(0, error_code=422, msg='数据格式错误'))

        # 执行删除
        try:
            with transaction.atomic():
                ScriptFiles.objects.filter(id__in=ids).delete()
        except Exception as err:
            logger.error(err)
            return JsonResponse(json_response(0, error_code=421, msg='数据库操作失败'))
        else:
            return JsonResponse(json_response(1))


class ScriptFileHandlerDetail(APIView):
    """
    处理 api/v1/ops/hosts_oper/scripts/{id}/ 请求
    """

    def get(self, request, version, ids):
        """
        处理GET请求,查询一条脚本信息
        :param request:
        :param version: API版本号
        :param ids: 待查询记录的id
        :return:
        """

        try:
            item = ScriptFiles.objects.get(id=ids)
        except (ScriptFiles.DoesNotExist, ScriptFiles.MultipleObjectsReturned) as err:
            logger.error(err)
            # 没有获取到指定ID的数据数据则返回空列表
            return Response(data={'success': 1, 'data': {"total": 0, "start": 0, "count": 0, "info": []}})
        except Exception as err:
            logger.error(err)
            JsonResponse(json_response(0, error_code=421, msg='数据库操作失败'))
        else:
            item_series = ScriptSerializers(item, many=False)
            return Response(
                data={'success': 1, 'data': {"total": 1, "start": 0, "count": 1, "info": [item_series.data]}})

    def put(self, request, version, ids):
        """
        处理PUT请求
        alter one item
        :param request:
        :param version: API版本号
        :param ids: 待修改记录的id
        """

        try:
            # 先查询得到要修改的记录
            item = ScriptFiles.objects.get(id=ids)
        except (ScriptFiles.DoesNotExist, ScriptFiles.MultipleObjectsReturned) as err:
            logger.error(err)
            return Response(data=json_response(0, error_code=424, msg='请求信息不存在'))
        except Exception as err:
            logger.error(err)
            JsonResponse(json_response(0, error_code=421, msg='数据库操作失败'))
        else:
            # 修改记录
            # 仅支持修改备注
            postscript = request.data.get('postscript')
            if postscript is not None:
                front_data = ScriptSerializers(instance=item, data={'postscript': postscript}, partial=True)
            else:
                return JsonResponse(json_response(0, error_code=422, msg='数据格式错误'))
            if front_data.is_valid():  # 校验数据
                try:
                    with transaction.atomic():
                        front_data.save()
                except Exception as err:
                    logger.error(err)
                    JsonResponse(json_response(0, error_code=421, msg='数据库操作失败'))
                else:
                    return JsonResponse(json_response(1))
            else:
                logger.error(front_data.errors)
                return JsonResponse(json_response(0, error_code=422, msg='数据格式错误'))


class ScriptUploader(APIView):
    """
    处理 api/v1/ops/hosts_oper/scripts/uploader/ 请求
    """

    def get(self, request, version):
        """
        处理GET请求，查询所有上传人员
        :param request:
        :param version: API版本号
        :return:
        """
        try:
            items = ScriptFiles.objects.values_list('uploader', flat=True).distinct()
        except Exception as err:
            logger.error(err)
            return JsonResponse(json_response(0, error_code=421, msg='数据库操作失败'))
        return Response(data={'success': 1, 'data': items})


# ---------------------------- 即时任务 ----------------------------

class RealTimeTasksList(KedaWarningBaseAPIView, ListAPIView):
    '''
    处理 api/v1/ops/hosts_oper/oper_tasks/real_time_tasks/ 请求
    '''
    queryset = RealTimeTasksModel.objects.all()
    serializer_class = RealTimeTasksListSerializer
    # 关键字查询
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ('status', 'operator')
    # 关键字搜索
    search_fields = ('task_name',)
    pagination_class = ResultsDataSetPaginationOffset
    ordering_fields = ('begin_time', 'id')

    def get_queryset(self):
        start = self.request.query_params.get('start_time', '')
        end = self.request.query_params.get('end_time', '')

        if start.isdigit() and end.isdigit():
            # 时间区间过滤
            start_datetime = datetime.fromtimestamp(int(start) / 1000, tz=timezone.get_current_timezone())
            end_datetime = datetime.fromtimestamp(int(end) / 1000, tz=timezone.get_current_timezone())
            return RealTimeTasksModel.objects.filter(
                begin_time__gte=start_datetime).filter(begin_time__lte=end_datetime).order_by("-id")
        return RealTimeTasksModel.objects.all().order_by("-id")

    def post(self, request, *args, **kwargs):
        data = request.data
        if isinstance(data.get('machines'), list):
            data['machines'] = ','.join(data.get('machines'))
        username = request.META.get('ssoAuth').get('account')
        data['operator'] = username
        rttcs = RealTimeTasksCreateSerializer(data=data)
        if rttcs.is_valid(raise_exception=False):
            new_task = rttcs.save()
            logger.info(rttcs.data)
        else:
            logger.error(rttcs.errors)
            if 'unique' in str(rttcs.errors):
                response = global_func.get_response(0, error_code='10006', error_msg='任务名称重复')
            elif 'not be null' in str(rttcs.errors):
                response = global_func.get_response(0, error_code='10007')
            else:
                response = global_func.get_response(0, error_code='10005')
            return Response(response)

        # 脚本路径
        script_path = os.path.join(MEDIA_ROOT, new_task.script.file.path)
        script_params = new_task.script_params
        # 主机moid列表
        machine_moid_list = new_task.machines.split(',')

        ip_list = task_func.machine_moid_2_ip(machine_moid_list).values()
        logger.debug('ip_list: %s' % ip_list)
        logger.debug('script_path: %s' % script_path)

        if ip_list:
            # ip_list = ['172.16.186.204', '172.16.186.208', '10.67.16.101']
            hosts = AnsibleSameInfoHosts(ip_list)
            ansible_host_list = hosts.get_ansible_host_list()
            ansible_task = AnsibleTask(ansible_host_list)
            # tasks = [ansible_task.get_task(module='shell', args='chmod +x %s;%s' % (script_path, script_path))]
            tasks = [ansible_task.get_task(module='script', args='%s %s' % (script_path, script_params))]

            p_get_task_ok_and_failed = task_func.TaskResult(ansible_task, tasks, new_task.pk)
            p_get_task_ok_and_failed.start()

            response = global_func.get_response(data={'task_id': new_task.pk})
            return Response(response)
        else:
            response = global_func.get_response(0, error_msg='主机%s错误' % machine_moid_list)
            return Response(response)


class RealTimeTasksRetrieve(KedaWarningBaseAPIView, RetrieveAPIView):
    queryset = RealTimeTasksModel.objects.all()
    serializer_class = RealTimeTasksDetailSerializer


class RealTimeTaskOperators(APIView):
    '''
    处理 api/v1/ops/hosts_oper/oper_tasks/real_time_task_operators/?search=ad 请求
    '''

    def get(self, request, *args, **kwargs):
        search = request.query_params.get('search', '')
        operators_queryset = RealTimeTasksModel.objects.filter(operator__icontains=search).distinct().values('operator')
        operators = [operator.get('operator') for operator in operators_queryset]

        response = global_func.get_response(data=operators)
        return Response(response)


# ---------------------------- 定时任务 ----------------------------

class CronTasksList(KedaWarningBaseAPIView, ListAPIView):
    queryset = CronTasksModel.objects.all().order_by('-id')
    serializer_class = CronTasksListSerializer
    # 关键字查询
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ('status', 'operator', 'last_modify_operator')
    # 关键字搜索
    search_fields = ('task_name', 'script__filename')
    pagination_class = ResultsDataSetPaginationOffset
    ordering_fields = ('create_time', 'last_modify_time', 'id')

    def post(self, request, *args, **kwargs):
        '''
        创建定时任务
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        data = request.data
        if isinstance(data.get('machines'), list):
            data['machines'] = ','.join(data.get('machines'))
        if isinstance(data.get('cron_rule'), dict):
            data['cron_rule'] = json.dumps(data.get('cron_rule'))

        username = request.META.get('ssoAuth').get('account')
        data['operator'] = username
        data['last_modify_operator'] = username
        ctcs = CronTasksCreateSerializer(data=data)

        if ctcs.is_valid(raise_exception=False):
            new_task = ctcs.save()
            logger.info(ctcs.data)
        else:
            logger.error(ctcs.errors)
            if 'unique' in str(ctcs.errors):
                response = global_func.get_response(0, error_code='10006')
            elif 'not be null' in str(ctcs.errors):
                response = global_func.get_response(0, error_code='10007')
            else:
                response = global_func.get_response(0, error_code='10005')
            return Response(response)

        # 脚本路径
        script_path = os.path.join(MEDIA_ROOT, new_task.script.file.path)
        script_params = new_task.script_params
        # 主机moid列表
        machine_moid_list = new_task.machines.split(',')

        ip_list = task_func.machine_moid_2_ip(machine_moid_list).values()
        # 定时任务规则
        cron_rule = json.loads(new_task.cron_rule)

        special = cron_rule.get('special', None)

        minute = cron_rule.get('minute', {}).get('rule_str')
        hour = cron_rule.get('hour', {}).get('rule_str')
        day = cron_rule.get('day', {}).get('rule_str')
        month = cron_rule.get('month', {}).get('rule_str')
        weekday = cron_rule.get('weekday', {}).get('rule_str')

        logger.debug('ip_list: %s' % ip_list)
        logger.debug('script_path: %s' % script_path)
        logger.debug('cron rule: %s' % cron_rule)

        if ip_list:
            hosts = AnsibleSameInfoHosts(ip_list)
            ansible_host_list = hosts.get_ansible_host_list()
            ansible_task = AnsibleTask(ansible_host_list)
            logger.debug(os.path.dirname(script_path) + '/')
            tasks = [
                ansible_task.COPY(src=script_path, dest=os.path.dirname(script_path) + '/'),  # 目录结尾加 '/'可以自动创建目录
                ansible_task.CRON(
                    cron_name='%s_%s' % (new_task.pk, new_task.task_name),
                    job='%s %s' % (script_path, script_params),
                    minute=minute,
                    hour=hour,
                    day=day,
                    month=month,
                    weekday=weekday,
                    special_time=special,
                )
            ]

            p_get_task_ok_and_failed = task_func.TaskResult(ansible_task, tasks, new_task.pk, request=request)
            p_get_task_ok_and_failed.start()

            response = global_func.get_response(data={'task_id': new_task.pk})
            return Response(response)

        response = global_func.get_response(0, error_msg='主机%s错误' % machine_moid_list)
        return Response(response)


class CronTasksRetrieve(KedaWarningBaseAPIView, RetrieveDestroyAPIView):
    queryset = CronTasksModel.objects.all()
    serializer_class = CronTasksDetailSerializer

    def delete(self, request, *args, **kwargs):
        '''
        暂未考虑离线主机，以及被luban删除主机的异常情况处理
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        pk = kwargs.get('pk')
        task_queryset = CronTasksModel.objects.filter(pk=pk).first()
        if task_queryset:
            machine_moid_list = task_queryset.machines.split(',')
            script_path = os.path.join(MEDIA_ROOT, task_queryset.script.file.path)
            script_params = task_queryset.script_params
        else:
            response = global_func.get_response(0, error_msg='Not found.')
            return Response(response)

        ip_list = task_func.machine_moid_2_ip(machine_moid_list).values()
        hosts = AnsibleSameInfoHosts(ip_list)
        ansible_host_list = hosts.get_ansible_host_list()
        if ansible_host_list:
            ansible_task = AnsibleTask(ansible_host_list)

            logger.debug(os.path.dirname(script_path) + '/')
            tasks = [
                ansible_task.SHELL(cmd='rm -f %s' % script_path),  # 删除远端脚本文件
                ansible_task.CRON(
                    cron_name='%s_%s' % (task_queryset.pk, task_queryset.task_name),
                    job='%s %s' % (script_path, script_params),
                    state='absent'
                )  # 取消定时任务
            ]
            p_get_task_ok_and_failed = task_func.TaskResult(ansible_task, tasks, task_queryset.pk, request=request)
            p_get_task_ok_and_failed.start()

        return super().delete(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        data = request.data
        task_id = kwargs.get('pk')

        queryset = CronTasksModel.objects.filter(pk=task_id).first()
        if not queryset:
            response = global_func.get_response(0, error_msg='Not found.')
            return Response(response)

        if isinstance(data.get('machines'), list):
            data['machines'] = ','.join(data.get('machines'))
        if isinstance(data.get('cron_rule'), dict):
            data['cron_rule'] = json.dumps(data.get('cron_rule'))
        # 修改前的主机moid列表
        last_machine_moid_list = queryset.machines.split(',')
        username = request.META.get('ssoAuth').get('account')
        data['last_modify_operator'] = username
        data['operator'] = queryset.operator
        data['last_modify_time'] = timezone.datetime.now(tz=timezone.get_current_timezone())
        data['status'] = data.get('status', queryset.status)

        ctus = CronTasksUpdateSerializer(queryset, data=data)
        if ctus.is_valid(raise_exception=False):
            ctus.save()
            logger.info(ctus.data)
            logger.debug(CronTasksModel.objects.filter(pk=task_id).first().cron_rule)
        else:
            logger.error(ctus.errors)
            if 'unique' in str(ctus.errors):
                response = global_func.get_response(0, error_code='10006')
            elif 'not be null' in str(ctus.errors):
                response = global_func.get_response(0, error_code='10007')
            else:
                response = global_func.get_response(0, error_code='10005')
            return Response(response)

        if (data.get('status') and data.get('status') in [1, 2] and data.get('status') != queryset.status) \
                or (data.get('cron_rule')) or set(last_machine_moid_list) != set(queryset.machines.split(',')):
            # 状态与当前定时任务状态不同，或参数传入定时任务规则，则触发修改定时任务
            # 脚本路径
            script_path = os.path.join(MEDIA_ROOT, queryset.script.file.path)
            script_params = queryset.script_params
            # 主机moid列表
            machine_moid_list = queryset.machines.split(',')

            ip_list = task_func.machine_moid_2_ip(machine_moid_list).values()
            last_ip_list = task_func.machine_moid_2_ip(last_machine_moid_list).values()
            # 定时任务规则
            cron_rule = json.loads(queryset.cron_rule)

            special = cron_rule.get('special', None)

            minute = cron_rule.get('minute', {}).get('rule_str')
            hour = cron_rule.get('hour', {}).get('rule_str')
            day = cron_rule.get('day', {}).get('rule_str')
            month = cron_rule.get('month', {}).get('rule_str')
            weekday = cron_rule.get('weekday', {}).get('rule_str')

            logger.debug('ip_list: %s' % ip_list)
            logger.debug('script_path: %s' % script_path)
            logger.debug('cron rule: %s' % cron_rule)

            if ip_list:
                hosts = AnsibleSameInfoHosts(ip_list)
                last_hosts = AnsibleSameInfoHosts(last_ip_list)

                ansible_host_list = hosts.get_ansible_host_list()
                last_ansible_host_list = last_hosts.get_ansible_host_list()

                ansible_task = AnsibleTask(ansible_host_list)
                last_hosts_ansible_task = AnsibleTask(last_ansible_host_list)

                logger.debug(os.path.dirname(script_path) + '/')
                tasks = [
                    last_hosts_ansible_task.SHELL(cmd='rm -f %s' % script_path),
                    last_hosts_ansible_task.CRON(
                        cron_name='%s_%s' % (queryset.pk, queryset.task_name),
                        job='%s %s' % (script_path, script_params),
                        state='absent'
                    ),  # 先取消所有任务
                    ansible_task.COPY(src=script_path, dest=os.path.dirname(script_path) + '/'),  # 目录结尾加 '/'可以自动创建目录
                    ansible_task.CRON(
                        cron_name='%s_%s' % (queryset.pk, queryset.task_name),
                        job='%s %s' % (script_path, script_params),
                        state='present' if data['status'] == 1 else 'absent',
                        minute=minute,
                        hour=hour,
                        day=day,
                        month=month,
                        weekday=weekday,
                        special_time=special,
                    )
                ]

                p_get_task_ok_and_failed = task_func.TaskResult(ansible_task, tasks, queryset.pk, request=request)
                p_get_task_ok_and_failed.start()

        response = global_func.get_response()
        return Response(response)


class CronTaskOperators(APIView):
    '''
    处理 api/v1/ops/hosts_oper/oper_tasks/cron_task_operators/?search=ad 请求
    '''

    def get(self, request, *args, **kwargs):
        search = request.query_params.get('search', '')
        operators_queryset = CronTasksModel.objects.filter(operator__icontains=search).distinct().values('operator')
        operators = [operator.get('operator') for operator in operators_queryset]

        response = global_func.get_response(data=operators)
        return Response(response)


class CronTaskLastModifyOperators(APIView):
    '''
    处理 api/v1/ops/hosts_oper/oper_tasks/cron_task_last_modify_operators/?search=ad 请求
    '''

    def get(self, request, *args, **kwargs):
        search = request.query_params.get('search', '')
        operators_queryset = CronTasksModel.objects.filter(last_modify_operator__icontains=search).distinct().values(
            'last_modify_operator')
        operators = [operator.get('last_modify_operator') for operator in operators_queryset]

        response = global_func.get_response(data=operators)
        return Response(response)


# ---------------------------- 文件分发 ----------------------------
class DistributionFile(KedaWarningBaseAPIView, ListAPIView, MultiDeleteAPIView):
    """
    处理 api/v1/ops/hosts_oper/oper_tasks/distribution_file/ 请求
    """
    queryset = DistributionFileModel.objects.all().order_by('-id')
    serializer_class = FileDistributionSerializer
    # 关键字查询
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filterset_fields = ('uploader',)
    # 关键字搜索
    search_fields = ('filename',)
    pagination_class = ResultsDataSetPaginationOffset
    lookup_request_data = 'ids'

    def post(self, request, *args, **kwargs):
        """
        处理POST请求，上传文件
        一次只上传一个文件
        :param request:
        """

        try:
            uploader = request.META.get('ssoAuth').get('account')
        except Exception as err:
            logger.error(err)
            response = global_func.get_response(0, error_msg='授权为空')
            return Response(response)
        else:
            if len(request.FILES) == 0:
                # 文件为空，返回失败
                response = global_func.get_response(0, error_msg='文件为空')
                return Response(response)
        # 文件最大50M，即 52,428,800‬ byte
        max_file_size = 52428800
        for file in request.FILES.values():
            size = file.size
            name = file.name
            if size > max_file_size:
                response = global_func.get_response(0, error_msg='数据最大为50M')
                return Response(response)
            task_id = request.POST.get('task_id')
            # task = DistributionTasksModel.objects.filter(pk=task_id).first()
            # logger.debug(task)

            data = {
                'file': file,
                'uploader': uploader,
                'filename': name,
                'task': task_id
            }
            fds = FileDistributionSerializer(data=data)
            if fds.is_valid(raise_exception=False):
                try:
                    new_file = fds.save()
                except Exception as e:
                    err = str(e)
                    logger.error(err)
                    logger.error(fds.errors)
                    if 'unique' in str(fds.errors):
                        response = global_func.get_response(0, error_code='10006')
                    elif 'not be null' in str(fds.errors):
                        response = global_func.get_response(0, error_code='10007')
                    else:
                        response = global_func.get_response(0, error_code='10005')
                    return Response(response)
                else:
                    response = global_func.get_response(data={'id': new_file.pk, 'filename': new_file.filename})
                    return Response(response)

            else:
                logger.error(fds.errors)
                if 'unique' in str(fds.errors):
                    response = global_func.get_response(0, error_code='10006')
                elif 'not be null' in str(fds.errors):
                    response = global_func.get_response(0, error_code='10007')
                else:
                    response = global_func.get_response(0, error_code='10005')
                return Response(response)


class DistributionFileDetail(KedaWarningBaseAPIView, RetrieveDestroyAPIView):
    queryset = DistributionFileModel.objects.all().order_by('-id')
    serializer_class = FileDistributionSerializer


class DistributionTasksList(KedaWarningBaseAPIView, ListAPIView):
    # 不返回machines为null的任务
    queryset = DistributionTasksModel.objects.all().filter(~Q(machines='null')).order_by('-id')
    serializer_class = DistributionTasksListSerializer
    # 关键字查询
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filterset_fields = ('operator', 'status')
    # 关键字搜索
    search_fields = ('task_name', 'distributionfilemodel__filename')
    pagination_class = ResultsDataSetPaginationOffset

    def get(self, request, *args, **kwargs):
        three_days_ago = timezone.datetime.now(tz=timezone.get_current_timezone()) - timezone.timedelta(3)
        three_days_ago_no_machine_tasks = self.serializer_class.Meta.model.objects.all().filter(
            Q(machines='null') & Q(create_time__lt=three_days_ago)
        )
        if three_days_ago_no_machine_tasks.all().count():
            logger.info('删除[%s]前的空数据：%s' % (three_days_ago, three_days_ago_no_machine_tasks.all()))
            three_days_ago_no_machine_tasks.delete()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = request.data
        before_upload_files = data.get('before_upload_files', 0)
        username = request.META.get('ssoAuth').get('account')
        data['operator'] = username

        if before_upload_files:
            # 上传文件之前创建一个待修改的分发任务，以供与文件绑定
            data['machines'] = 'null'
            data['task_name'] = '文件分发-' + str(
                timezone.datetime.now(tz=timezone.get_current_timezone()).replace(microsecond=0, tzinfo=None))
        else:
            if isinstance(data.get('machines'), list):
                data['machines'] = ','.join(data.get('machines'))

        logger.debug(data)
        dts = DistributionTasksCreateSerializer(data=data)
        if dts.is_valid(raise_exception=False):
            new_task = dts.save()
        else:
            if 'unique' in str(dts.errors):
                response = global_func.get_response(0, error_code='10006')
            elif 'not be null' in str(dts.errors):
                response = global_func.get_response(0, error_code='10007')
            else:
                response = global_func.get_response(0, error_code='10005')
            return Response(response)

        response = global_func.get_response(data={'task_id': new_task.pk})
        return Response(response)


class DistributionTasksRetrieve(KedaWarningBaseAPIView, RetrieveUpdateDestroyAPIView):
    queryset = DistributionTasksModel.objects.all()
    serializer_class = DistributionTasksRetrieveSerializer

    def put(self, request, *args, **kwargs):
        self.serializer_class = DistributionTasksUpdateSerializer
        data = request.data
        pk = kwargs.get('pk')
        begin_distribution_task = data.get('begin_distribution_task', 0)
        username = request.META.get('ssoAuth').get('account')
        data['operator'] = username
        if isinstance(data.get('machines'), list):
            data['machines'] = ','.join(data.get('machines'))

        if not data.get('remote_path'):
            response = global_func.get_response(0, error_msg='路径错误')
            return Response(response)

        response = super().put(request, *args, **kwargs)
        if begin_distribution_task:
            # 如果携带开始分发任务标识，则开始文件分发
            queryset = DistributionTasksModel.objects.filter(pk=pk).first()
            # 主机moid列表
            machine_moid_list = queryset.machines.split(',')

            ip_list = task_func.machine_moid_2_ip(machine_moid_list).values()
            remote_path = queryset.remote_path
            local_files = [_ for _ in queryset.distributionfilemodel_set.all()]
            logger.debug(local_files)
            logger.debug(machine_moid_list)
            logger.debug(ip_list)
            if ip_list:
                hosts = AnsibleSameInfoHosts(ip_list)
                ansible_host_list = hosts.get_ansible_host_list()
                ansible_task = AnsibleTask(ansible_host_list)
                logger.info('文件分发远端路径：%s，服务器列表：%s' % (remote_path + '/', ip_list))
                tasks = [
                    ansible_task.SHELL(cmd='mkdir -p %s' % (remote_path + '/')),
                ]
                tasks.extend(
                    [
                        ansible_task.COPY(
                            src=local_file.file.path,
                            dest=(remote_path + '/') + local_file.filename) for local_file in local_files
                    ]
                )
                p_get_task_ok_and_failed = task_func.TaskResult(
                    ansible_task, tasks, queryset.pk,
                    request=request, task_type='distribution'
                )
                p_get_task_ok_and_failed.start()

        return response


class DistributionTaskOperators(APIView):
    '''
    处理 api/v1/ops/hosts_oper/oper_tasks/distribution_task_operators/?search=ad 请求
    '''

    def get(self, request, *args, **kwargs):
        search = request.query_params.get('search', '')
        operators_queryset = DistributionTasksModel.objects.filter(operator__icontains=search).distinct().values(
            'operator')
        operators = [operator.get('operator') for operator in operators_queryset]

        response = global_func.get_response(data=operators)
        return Response(response)
