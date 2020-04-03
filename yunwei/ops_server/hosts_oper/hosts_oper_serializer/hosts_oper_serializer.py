#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

from rest_framework import serializers
from hosts_oper.models import RealTimeTasksModel, CronTasksModel, DistributionFileModel, DistributionTasksModel
from django.utils import timezone
from hosts.models import MachineInfo
import logging
import json

logger = logging.getLogger('ops.' + __name__)


class RealTimeTasksListSerializer(serializers.ModelSerializer):
    '''
    定时任务list使用的序列化器
    '''

    class Meta:
        # fields = '__all__'
        exclude = ('stdout', 'stderr', 'results',)
        model = RealTimeTasksModel
        depth = 1

    begin_timestamp = serializers.SerializerMethodField()

    def get_begin_timestamp(self, obj):
        return round(timezone.datetime.timestamp(obj.begin_time) * 1000)

    machines = serializers.SerializerMethodField()

    def get_machines(self, obj):
        return obj.machines.split(',')


class RealTimeTasksCreateSerializer(serializers.ModelSerializer):
    '''
    定时任务create使用的序列化器
    '''

    class Meta:
        # fields = '__all__'
        exclude = ('stdout', 'stderr', 'results',)
        model = RealTimeTasksModel

    begin_timestamp = serializers.SerializerMethodField()

    def get_begin_timestamp(self, obj):
        return round(timezone.datetime.timestamp(obj.begin_time) * 1000)


class RealTimeTasksDetailSerializer(serializers.ModelSerializer):
    '''
    定时任务详情使用的序列化器
    '''

    class Meta:
        # fields = '__all__'
        exclude = ('stdout', 'stderr',)
        model = RealTimeTasksModel
        depth = 1

    begin_timestamp = serializers.SerializerMethodField()

    def get_begin_timestamp(self, obj):
        return round(timezone.datetime.timestamp(obj.begin_time) * 1000)

    machines = serializers.SerializerMethodField()

    def get_machines(self, obj):
        values = ['moid', 'name', 'room_name', 'domain_name', 'local_ip']
        machines_moid = obj.machines.split(',')
        machines_info = []
        try:
            results = json.loads(obj.results)
        except:
            results = {'failed': {}, 'ok': {}}

        for machine_moid in machines_moid:
            machine_info = MachineInfo.objects.filter(moid=machine_moid).values(*values).first()
            # 查询results，机器是否执行成功2：成功，3：失败
            if machine_info:
                if machine_info.get('local_ip') in results['failed']:
                    status = 3
                elif machine_info.get('local_ip') in results['ok']:
                    status = 2
                else:
                    status = 1
                machines_info.append(
                    {**machine_info, **{'status': status}}
                )
        return machines_info

    results = serializers.SerializerMethodField()

    def get_results(self, obj):
        try:
            results = json.loads(obj.results)
        except:
            results = {'failed': {}, 'ok': {}}
        return results


class CronTasksCreateSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('results', 'create_time', 'last_modify_time', 'status',)
        model = CronTasksModel


class CronTasksUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('results', 'create_time', 'operator')
        model = CronTasksModel


class CronTasksListSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('results', 'cron_rule')
        model = CronTasksModel
        depth = 1

    create_timestamp = serializers.SerializerMethodField()

    def get_create_timestamp(self, obj):
        return round(timezone.datetime.timestamp(obj.create_time) * 1000)

    last_modify_timestamp = serializers.SerializerMethodField()

    def get_last_modify_timestamp(self, obj):
        return round(timezone.datetime.timestamp(obj.last_modify_time) * 1000)

    machines = serializers.SerializerMethodField()

    def get_machines(self, obj):
        return obj.machines.split(',')


class CronTasksDetailSerializer(serializers.ModelSerializer):
    class Meta:
        # exclude = ('', '')
        fields = '__all__'
        model = CronTasksModel
        depth = 1

    cron_rule = serializers.SerializerMethodField()

    def get_cron_rule(self, obj):
        return json.loads(obj.cron_rule)

    results = serializers.SerializerMethodField()

    def get_results(self, obj):
        try:
            results = json.loads(obj.results)
        except:
            results = {'failed': {}, 'ok': {}}
        return results

    machines = serializers.SerializerMethodField()

    def get_machines(self, obj):
        values = ['moid', 'name', 'room_name', 'domain_name', 'local_ip']
        machines_moid = obj.machines.split(',')
        machines_info = []
        try:
            results = json.loads(obj.results)
        except:
            results = {'failed': {}, 'ok': {}}

        for machine_moid in machines_moid:
            machine_info = MachineInfo.objects.filter(moid=machine_moid).values(*values).first()
            # 查询results，机器是否执行成功1：正在执行，2：暂停执行，3：任务创建失败
            if machine_info:
                if machine_info.get('local_ip') in results['failed']:
                    status = 3
                else:
                    status = obj.status
                machines_info.append(
                    {**machine_info, **{'status': status}}
                )
        return machines_info


class FileDistributionSerializer(serializers.ModelSerializer):
    """
    分发文件管理序列化
    """

    class Meta:
        model = DistributionFileModel
        fields = '__all__'

    size = serializers.IntegerField(source='file.size', read_only=True)
    url = serializers.CharField(source='file.url', read_only=True)
    upload_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)


class DistributionTasksCreateSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = DistributionTasksModel

    # 此任务分发的文件
    file = serializers.SerializerMethodField()

    def get_file(self, obj):
        # logger.debug(dir(obj.distributionfilemodel_set))
        fds = FileDistributionSerializer(obj.distributionfilemodel_set.all(), many=True)
        return fds.data


class DistributionTasksListSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = DistributionTasksModel

    # 此任务分发的文件
    file = serializers.SerializerMethodField()

    def get_file(self, obj):
        fds = FileDistributionSerializer(obj.distributionfilemodel_set.all(), many=True)
        return fds.data

    machines = serializers.SerializerMethodField()

    def get_machines(self, obj):
        machines = []
        try:
            machines = obj.machines.split(',')
        except Exception as e:
            err = str(e)
            logger.error(err)
        return machines


class DistributionTasksRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = DistributionTasksModel

    # 此任务分发的文件
    file = serializers.SerializerMethodField()

    def get_file(self, obj):
        fds = FileDistributionSerializer(obj.distributionfilemodel_set.all(), many=True)
        return fds.data

    results = serializers.SerializerMethodField()

    def get_results(self, obj):
        try:
            results = json.loads(obj.results)
        except:
            results = {'failed': {}, 'ok': {}}
        return results

    machines = serializers.SerializerMethodField()

    def get_machines(self, obj):
        values = ['moid', 'name', 'room_name', 'domain_name', 'local_ip']
        machines_moid = obj.machines.split(',')
        machines_info = []
        try:
            results = json.loads(obj.results)
        except:
            results = {'failed': {}, 'ok': {}}

        for machine_moid in machines_moid:
            machine_info = MachineInfo.objects.filter(moid=machine_moid).values(*values).first()
            # 查询results，机器是否执行成功任务状态，1：正在执行，2：执行成功，3：执行失败
            if machine_info:
                if machine_info.get('local_ip') in results['failed']:
                    status = 3
                else:
                    status = obj.status
                machines_info.append(
                    {**machine_info, **{'status': status}}
                )
        return machines_info


class DistributionTasksUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = DistributionTasksModel
