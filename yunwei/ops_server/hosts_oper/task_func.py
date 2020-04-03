#!/usr/bin/env python3
# coding: utf-8

__author__ = 'wanglei_sxcpx@kedacom.com'

import logging
import json
import jsonpath
from django.utils import timezone
from multiprocessing import Process
from django.db import connections

from hosts_oper.models import RealTimeTasksModel, CronTasksModel, DistributionTasksModel

logger = logging.getLogger('ops.' + __name__)


class TaskResult(Process):
    def __init__(self, ansible_task, tasks, now_task_id, task_type='exec', request=None):
        super().__init__()
        self.task_type = task_type
        self.ansible_task = ansible_task
        self.tasks = tasks
        self.now_task_id = now_task_id
        self.request = request

    def func(self):
        if self.task_type in ['exec', 'distribution']:
            return self.get_result_ok_and_failed
        else:
            return self.none_func

    def update_func(self):
        '''
        根据传参获取不同的更新数据库函数
        :return:
        '''
        if self.task_type == 'exec' and self.request:
            # 定时任务表更新
            return self.update_cron_task_table
        elif self.task_type == 'exec' and not self.request:
            # 即时任务表更新
            return self.update_real_time_task_table
        elif self.task_type == 'distribution' and self.request:
            # 文件分发任务表更新
            return self.update_distribution_task_table
        else:
            return self.none_func

    def run(self):
        self.func()()

    def none_func(self):
        pass

    def get_result_ok_and_failed(self):
        host_ok = {}
        host_failed_or_unreachable = {}
        task_result = {'ok': host_ok, 'failed': host_failed_or_unreachable}
        # 关闭 uwsgi 连接的文件描述符， 解决 子进程运行过程中 前端 继续get请求阻塞问题
        import uwsgi
        fd = uwsgi.connection_fd()
        uwsgi.close(fd)
        # 执行 ansible 任务
        ret = self.exec_tasks()
        if ret:
            if ret.host_ok:
                host_ok.update(
                    {ok.get('ip'): {
                        'cmd': ok.get('result').get('cmd') if ok.get('result').get(
                            'cmd') else '',
                        'stdout': ok.get('result').get('stdout') if ok.get('result').get(
                            'stdout') else '',
                        'stderr': ok.get('result').get('stderr') if ok.get('result').get(
                            'stderr') else '',
                        'msg': ok.get('result').get('msg') if ok.get('result').get(
                            'msg') else '',
                        'rc': ok.get('result').get('rc') if isinstance(ok.get('result').get(
                            'rc'), int) else None,
                        'result': ok.get('result')
                    }
                    if ok.get('result') else '' for ok in ret.host_ok}
                )

            if ret.host_failed or ret.host_unreachable:
                host_failed_or_unreachable.update(
                    {failed.get('ip'): {
                        'cmd': failed.get('result').get('cmd') if failed.get('result').get(
                            'cmd') else '',
                        'stdout': failed.get('result').get('stdout') if failed.get('result').get(
                            'stdout') else '',
                        'stderr': failed.get('result').get('stderr') if failed.get('result').get(
                            'stderr') else '',
                        'msg': failed.get('result').get('msg') if failed.get('result').get(
                            'msg') else '',
                        'rc': failed.get('result').get('rc') if isinstance(failed.get('result').get(
                            'rc'), int) else None,
                        'result': failed.get('result')
                    }
                    if failed.get('result') else '' for failed in ret.host_failed}
                )
                host_failed_or_unreachable.update(
                    {unreachable.get('ip'): {
                        'cmd': unreachable.get('result').get('cmd') if unreachable.get('result').get(
                            'cmd') else '',
                        'stdout': unreachable.get('result').get('stdout') if unreachable.get('result').get(
                            'stdout') else '',
                        'stderr': unreachable.get('result').get('stderr') if unreachable.get('result').get(
                            'stderr') else '',
                        'msg': unreachable.get('result').get('msg') if unreachable.get('result').get(
                            'msg') else '',
                        'rc': unreachable.get('result').get('rc') if isinstance(unreachable.get('result').get(
                            'rc'), int) else None,
                        'result': unreachable.get('result')
                    }
                    if unreachable.get('result') else '' for unreachable in ret.host_unreachable}
                )
        logger.info('task_result: %s' % json.dumps(task_result))
        self.update_func()(task_result)
        # if self.request:
        #     # 定时任务表更新
        #     self.update_cron_task_table(task_result)
        # else:
        #     # 即时任务表更新
        #     self.update_real_time_task_table(task_result)
        return task_result

    def update_distribution_task_table(self, task_result):
        connections.close_all()
        DistributionTasksModel.objects.filter(pk=self.now_task_id).update(
            results=json.dumps(task_result),
            status=3 if len(task_result['failed']) else 2,  # '任务状态，1：正在执行，2：执行成功，3：执行失败'
        )

    def update_real_time_task_table(self, task_result):
        connections.close_all()
        task_begin_time = RealTimeTasksModel.objects.filter(pk=self.now_task_id).first().begin_time
        task_begin_time = timezone.datetime.timestamp(task_begin_time)

        stdout_ok = {_: task_result['ok'][_]['stdout'] for _ in task_result['ok']}
        stdout_failed = {_: task_result['failed'][_]['stdout'] for _ in task_result['failed']}
        stderr_ok = {_: task_result['ok'][_]['stderr'] for _ in task_result['ok']}
        stderr_failed = {_: task_result['failed'][_]['stderr'] for _ in task_result['failed']}
        RealTimeTasksModel.objects.filter(pk=self.now_task_id).update(
            stdout=json.dumps({**stdout_ok, **stdout_failed}),
            stderr=json.dumps({**stderr_ok, **stderr_failed}),
            results=json.dumps(task_result),
            status=3 if len(task_result['failed']) else 2,  # 如果有执行失败的机器，那么此任务标识为失败
            duration=timezone.datetime.timestamp(timezone.datetime.now()) - task_begin_time
        )

    def update_cron_task_table(self, task_result):
        connections.close_all()
        if self.request.method == 'DELETE':
            CronTasksModel.objects.filter(pk=self.now_task_id).delete()
        else:
            if self.request.META.get('ssoAuth'):
                last_modify_operator = self.request.META.get('ssoAuth').get('account')
            else:
                last_modify_operator = 'no auth'
            state = jsonpath.jsonpath(task_result['ok'], '$..state')
            logger.debug(state)
            if len(task_result['failed']):
                status = 3
            elif isinstance(state, list) and 'present' in state:
                # 设置定时任务成功
                status = 1
            else:
                status = 2

            CronTasksModel.objects.filter(pk=self.now_task_id).update(
                results=json.dumps(task_result),
                status=status,  # 如果有执行失败的机器，那么此任务标识为失败
                last_modify_time=timezone.datetime.now(tz=timezone.get_current_timezone()),
                last_modify_operator=last_modify_operator,
            )

    def exec_tasks(self):
        try:
            logger.debug(self.tasks)
            ret = self.ansible_task.exec_tasks(self.tasks)
            # 执行成功的返回
            logger.info('ok: %s' % json.dumps(ret.host_ok))
            # 执行失败的返回
            logger.info('failed: %s' % json.dumps(ret.host_failed))
            # 主机不可达的返回
            logger.info('unreachable: %s' % json.dumps(ret.host_unreachable))

        except Exception as e:
            err = str(e)
            logger.error(err)
            ret = None

        return ret


def machine_moid_2_ip(machine_moid_list):
    '''
    返回{moid:ip}结果
    :param machine_moid_list:
    :return:
    '''
    ip_info = {}
    if machine_moid_list:
        with connections['luban'].cursor() as cursor:
            sql = '''
            SELECT mi.machine_moid,ii.ip FROM `ip_info` ii 
            LEFT JOIN machine_info mi ON ii.machine_id=mi.id 
            WHERE ii.flag='1' 
            AND mi.machine_moid in %s
            '''

            params = [machine_moid_list]
            cursor.execute(sql, params=params)
            fetchall = cursor.fetchall()

        if fetchall:
            for fetch in fetchall:
                ip_info[fetch[0]] = fetch[1]

    return ip_info
