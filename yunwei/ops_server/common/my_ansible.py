#!/usr/bin/env python3
# coding: utf-8

__author__ = 'wanglei_sxcpx@kedacom.com'

import json
import shutil
import os
import tempfile
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
import ansible.constants as C

from ops.settings import ANSIBLE_PORT


class ResultCallback(CallbackBase):
    """A sample callback plugin used for performing an action as results come in

    If you want to collect all results into a single object for processing at
    the end of the execution, look into utilizing the ``json`` callback plugin
    or writing your own custom callback plugin
    """

    def __init__(self, *args, **kwargs):
        super(ResultCallback, self).__init__(*args, **kwargs)
        self.host_any = []
        self.error_msg = None
        self.host_ok = []
        self.host_unreachable = []
        self.host_failed = []

    def v2_runner_on_ok(self, result, **kwargs):
        """Print a json representation of the result

        This method could store the result in an instance attribute for retrieval later
        """
        name = result._host.get_name()
        task = result._task.get_name()

        self.error_msg = result._result.get('stderr')
        ret = dict(ip=name, task=task, result=result._result)
        self.host_any.append(ret)
        self.host_ok.append(ret)

    def v2_runner_on_failed(self, result, *args, **kwargs):
        name = result._host.get_name()
        task = result._task.get_name()

        self.error_msg = result._result.get('stderr', '') + result._result.get('msg')
        ret = dict(ip=name, task=task, result=result._result)
        self.host_any.append(ret)
        self.host_failed.append(ret)

    def v2_runner_on_unreachable(self, result, ignore_errors=False):
        name = result._host.get_name()
        task = result._task.get_name()

        self.error_msg = name + ':' + result._result.get('msg', '')
        ret = dict(ip=name, task=task, result=result._result)
        self.host_any.append(ret)
        self.host_unreachable.append(ret)


class AnsibleSameInfoHosts:
    def __init__(self, hosts, port=None, connection=None, ssh_user=None, ssh_pass=None):
        self.hosts = hosts
        self.port = port if port else ANSIBLE_PORT
        self.ansible_connection = connection
        self.ansible_ssh_user = ssh_user
        self.ansible_ssh_pass = ssh_pass
        self.ansible_host_list = []

    def get_ansible_host_list(self):
        '''
        返回AnsibleHost列表
        :return:
        '''
        for host in self.hosts:
            ansible_host = AnsibleHost(
                host,
                self.port,
                self.ansible_connection,
                self.ansible_ssh_user,
                self.ansible_ssh_pass
            )
            self.ansible_host_list.append(ansible_host)

        return self.ansible_host_list


class AnsibleHost:
    def __init__(self, host, port=None, connection=None, ssh_user=None, ssh_pass=None):
        self.host = host
        self.port = port if port else ANSIBLE_PORT
        self.ansible_connection = connection
        self.ansible_ssh_user = ssh_user
        self.ansible_ssh_pass = ssh_pass

    def __str__(self):
        result = 'ansible_ssh_host=' + str(self.host)
        if self.port:
            result += ' ansible_ssh_port=' + str(self.port)
        if self.ansible_connection:
            result += ' ansible_connection=' + str(self.ansible_connection)
        if self.ansible_ssh_user:
            result += ' ansible_ssh_user=' + str(self.ansible_ssh_user)
        if self.ansible_ssh_pass:
            result += ' ansible_ssh_pass=' + str(self.ansible_ssh_pass)
        return result


class AnsibleTask:
    def __init__(self, hosts, extra_vars=None):
        self.hosts = hosts
        self.hosts_file = None
        self._validate()
        self._generate_hosts_file()

        # since API is constructed for CLI it expects certain options to always be set, named tuple 'fakes' the args parsing options object
        Options = namedtuple('Options',
                             ['connection', 'module_path', 'forks', 'become', 'become_method', 'become_user', 'check',
                              'diff', 'host_key_checking', 'listhosts', 'listtasks', 'listtags', 'syntax',
                              'ssh_extra_args'])

        ssh_extra_args = [
            '-o StrictHostKeyChecking=no',  # 解决ssh第一次登录机器的提示问题
            '-o ControlPath=/dev/shm/ansible_control_path',  # 解决docker容器中无法ssh的问题
        ]
        self.options = Options(connection='ssh', module_path=None, forks=100,
                               become=None, become_method=None, become_user=None, check=False, diff=False,
                               host_key_checking=False, listhosts=None, listtasks=None, listtags=None, syntax=None,
                               ssh_extra_args=' '.join(ssh_extra_args))
        # initialize needed objects
        self.loader = DataLoader()  # Takes care of finding and reading yaml, json and ini files
        self.passwords = {}

        # create inventory, use path to host config file as source or hosts in a comma separated string
        self.inventory = InventoryManager(loader=self.loader, sources=[self.hosts_file])
        # variable manager takes care of merging all the different sources to give you a unifed view of variables available in each context
        self.variable_manager = VariableManager(loader=self.loader, inventory=self.inventory)
        if extra_vars:
            self.variable_manager.extra_vars = extra_vars

    def _generate_hosts_file(self):
        self.hosts_file = tempfile.mktemp()
        with open(self.hosts_file, 'w+', encoding='utf-8') as file:
            hosts = []
            for host in self.hosts:
                hosts.append(host.host + ' ' + str(host))
            file.write('\n'.join(hosts))

    def _validate(self):
        if not self.hosts:
            raise Exception('hosts不能为空')
        if not isinstance(self.hosts, list):
            raise Exception('hosts只能为list<AnsibleHost>数组')
        for host in self.hosts:
            if not isinstance(host, AnsibleHost):
                raise Exception('host类型必须为AnsibleHost')

    def get_task(self, module, args):
        return {'action': {'module': module, 'args': args}, 'register': 'shell_out'}

    def SCRIPT(self, cmd):
        return self.get_task(module='script', args=cmd)

    def SHELL(self, cmd):
        return self.get_task(module='shell', args=cmd)

    def COPY(self, src, dest, force='yes', mode='0777', backup='yes', owner='root', group='root'):
        '''
        copy模块的快捷task
        :param src: 本机文件路径
        :param dest: 远程主机路径
        :param force: 是否强制覆盖
        :param mode: 拷贝到远程机器后赋予的权限
        :param backup: 是否备份原同名文件
        :param owner: 拷贝到远程机器后的所属用户
        :param group: 拷贝到远程机器后的所属用户组
        :return:task字典
        '''
        return self.get_task(
            module='copy',
            args='src="{src}" dest="{dest}" force={force} mode={mode} backup={backup} owner={owner} group={group}'.format(
                src=src,
                dest=dest,
                force=force,
                mode=mode,
                backup=backup,
                owner=owner,
                group=group,
            )
        )

    def FETCH(self, src, dest, flat='yes', fail_on_missing='yes'):
        '''
        fetch模块的快捷task
        :param src: 远程主机上的文件路径(This must be a file, not a directory.)
        :param dest: 本机存储拉取文件的路径
        :param flat: 是否覆盖本地同名文件
        :param fail_on_missing:
        :return:task字典
        '''
        return self.get_task(
            module='fetch',
            args='src={src} dest={dest} flat={flat} fail_on_missing={fail_on_missing}'.format(
                src=src,
                dest=dest,
                flat=flat,
                fail_on_missing=fail_on_missing,
            )
        )

    def PING(self):
        return self.get_task(module='ping', args='')

    def CRON(self, cron_name, job, state='present', minute='*', hour='*', day='*', month='*', weekday='*', user='root',
             special_time=None):
        '''
        cron模块快捷task
        :param cron_name: 定时任务名称
        :param job: 任务执行的命令
        :param state: {absent 停止任务|present 开始任务}
        :param minute: Minute when the job should run ( 0-59, *, */2, etc )
        :param hour: Hour when the job should run ( 0-23, *, */2, etc )
        :param day: Day of the month the job should run ( 1-31, *, */2, etc )
        :param month: Month of the year the job should run ( 1-12, *, */2, etc )
        :param weekday: Day of the week that the job should run ( 0-6 for Sunday-Saturday, *, etc )
        :param special_time: Special time specification nickname. (reboot,yearly,annually,monthly,weekly,daily,hourly)
        :return: task字典
        '''
        return self.get_task(
            module='cron',
            args='minute="{minute}" hour="{hour}" day="{day}" month="{month}" weekday="{weekday}"'
                 ' job="{job}" state="{state}" name="{cron_name}" user="{user}"'.format(
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                weekday=weekday,
                job=job,
                state=state,
                cron_name=cron_name,
                user=user,
            ) if not special_time else
            'job="{job}" state="{state}" name="{cron_name}" user="{user}" special_time="{special_time}"'.format(
                job=job,
                state=state,
                cron_name=cron_name,
                user=user,
                special_time=special_time,
            )
        )

    def exec_tasks(self, tasks):
        source = {
            'hosts': 'all',
            'gather_facts': 'no',
            'tasks': tasks
        }
        # Create play object, playbook objects use .load instead of init or new methods,
        # this will also automatically create the task objects from the info provided in play_source
        play = Play().load(source, variable_manager=self.variable_manager, loader=self.loader)
        results_callback = ResultCallback()
        tqm = None
        try:
            tqm = TaskQueueManager(
                inventory=self.inventory,
                variable_manager=self.variable_manager,
                loader=self.loader,
                options=self.options,
                passwords=self.passwords,
                stdout_callback=results_callback
            )
            tqm.run(play)

            return results_callback
        except:
            raise
        finally:
            # we always need to cleanup child procs and the structres we use to communicate with them
            if tqm is not None:
                tqm.cleanup()
            # Remove ansible tmpdir
            shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)

    def exec_playbook(self, playbooks):
        results_callback = ResultCallback()

        playbook = PlaybookExecutor(
            playbooks=playbooks,
            inventory=self.inventory,
            variable_manager=self.variable_manager,
            loader=self.loader,
            options=self.options,
            passwords=self.passwords
        )
        setattr(getattr(playbook, '_tqm'), '_stdout_callback', results_callback)
        playbook.run()

        return results_callback

    def __del__(self):
        if self.hosts_file:
            os.remove(self.hosts_file)


if __name__ == '__main__':
    ip_list = ['172.16.186.208', ]
    hosts = AnsibleSameInfoHosts(ip_list, port=33332)
    ansible_host_list = hosts.get_ansible_host_list()
    ansible_task = AnsibleTask(ansible_host_list)
    try:
        tasks = []
        # tasks.append(ansible_task.get_task(module='shell', args='hostname -I'))
        # tasks.append(ansible_task.COPY('/root/aa.sh', '/root/aaaa.sh'))
        # ret = ansible_task.exec_tasks(tasks)
        playbooks = [os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'diagnose', 'scripts',
                                  'fetch_capture_playbook.yaml')]
        ret = ansible_task.exec_playbook(playbooks)
        # 执行成功的返回
        print('ok', json.dumps(ret.host_ok))
        # 执行失败的返回
        print('failed', json.dumps(ret.host_failed))
        # 主机不可达的返回
        print('unreachable', json.dumps(ret.host_unreachable))
    except Exception as e:
        print(e)
