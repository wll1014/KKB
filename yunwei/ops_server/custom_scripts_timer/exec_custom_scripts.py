#!/usr/bin/env python3
# coding: utf-8

__author__ = 'wanglei_sxcpx@kedacom.com'

import os
import re
import threading
import queue
import subprocess
import datetime
import json
import copy
import logging

logger = logging.getLogger('custom-scripts')


class ScriptsHandler:
    def __init__(self):
        self.default_interval = 30
        self.run_timeout = 10
        self.base_es_index = 'ops-custom-scripts-{year}.{month}'

        self.base_path = '/opt/data/ops/media/custom_scripts/'
        self.conf_file_path = os.path.join(self.base_path, 'conf')
        if not os.path.exists(self.conf_file_path):
            os.makedirs(self.conf_file_path)
        self.is_enable_conf_file_path = os.path.join(self.conf_file_path, 'is-enable')
        self.is_running_conf_file_path = os.path.join(self.conf_file_path, 'is-running')
        self.ops_version_file_path = os.path.abspath('/opt/ops/ops_server/version')
        # 校验文件是否存在
        self._validate_conf_files()
        # 过滤.conf结尾的文件
        self.custom_conf_files = list(
            filter(lambda conf_file: re.match(r'.*\.conf$', conf_file), os.listdir(self.conf_file_path)))

        self.msg_queue = queue.Queue()

    def _validate_conf_files(self):
        if not os.path.isfile(self.is_enable_conf_file_path):
            raise Exception('%s is not a file' % self.is_enable_conf_file_path)
        # 获取功能开关
        with open(self.is_enable_conf_file_path, 'r', encoding='utf-8') as f:
            is_enable = f.read()
            is_enable = is_enable.strip()
            if is_enable.isdigit():
                self.is_enable = bool(int(is_enable.strip()))
            else:
                raise Exception('Please set %s as 0:close or 1:open' % self.is_enable_conf_file_path)
        if not os.path.isfile(self.is_running_conf_file_path):
            raise Exception('%s is not a file' % self.is_running_conf_file_path)
        if not os.path.isfile(self.ops_version_file_path):
            raise Exception('%s is not a file' % self.ops_version_file_path)
        with open(self.ops_version_file_path, 'r', encoding='utf-8') as f:
            ops_version = f.read()
            self.ops_version = ops_version.strip()

    def get_key_conf(self):
        """
        获取key配置
        :return: {'ops.xxx': '/opt/data/ops/media/custom_scripts/scripts/ops_test.sh'}
        """
        key_conf = {}
        if self.custom_conf_files:
            for custom_conf_file in self.custom_conf_files:
                # 循环读取所有配置文件
                with open(os.path.join(self.conf_file_path, custom_conf_file), 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        # 正确配置为 UserParameter= 开头
                        try:
                            if re.match(r'^UserParameter=.*', line):
                                line_split = line.split('=', maxsplit=1)
                                key = line_split[1].split(',', maxsplit=1)[0]
                                cmdline = line_split[1].split(',', maxsplit=1)[1]
                                key_conf = {**key_conf, **{key: cmdline}}
                        except Exception as e:
                            raise Exception(
                                '%s, %s配置错误' % (e.args, os.path.join(self.conf_file_path, custom_conf_file)))
        return key_conf

    def get_run_conf(self, key_conf):
        """
        获取运行配置
        :return: {'ops.check': {'interval': 60, 'cmdline': '/opt/ops/ops_server/ops_check.sh', 'params': ['1']}}
        """
        run_conf = []
        with open(self.is_running_conf_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not re.match(r'^#.*', line):
                    # 过滤空行和注释行
                    params = []
                    interval = self.default_interval
                    if '[' in line and ']' in line:
                        # 有参数的key
                        try:
                            re_match = re.match(r'((\w+\.?)+)\[(.*)\]\s?(\d*)', line)
                            key = re_match.group(1)
                            params = re_match.group(3).split(',')
                            if re_match.group(4):
                                # 间隔时间最小为30s
                                interval = int(re_match.group(4))
                        except Exception as e:
                            raise Exception('%s, %s配置错误' % (e.args, self.is_running_conf_file_path))
                    else:
                        # 无参数的key
                        try:
                            re_match = re.match(r'((\w+\.?)+)\s?(\d*)', line)
                            key = re_match.group(1)
                            if re_match.group(3):
                                interval = int(re_match.group(3))
                        except Exception as e:
                            raise Exception('%s, %s配置错误' % (e.args, self.is_running_conf_file_path))
                    if key in key_conf.keys():
                        cmdline = key_conf[key]
                        interval = interval if interval >= self.default_interval else self.default_interval
                        run_conf.append({key: {'cmdline': cmdline, 'params': params, 'interval': interval}})
        return run_conf

    def exec_cmdline(self, key, interval, cmdline, params):
        """
        在服务器执行命令，并将结果投入队列
        :param key: 执行命令的key
        :param interval: 时间间隔
        :param cmdline: 命令
        :param params: 命令参数
        :return:
        """
        start_timestamp = datetime.datetime.now().timestamp() * 1000
        res = subprocess.Popen(
            '{cmdline} {params}'.format(cmdline=cmdline, params=params),
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            preexec_fn=os.setsid  # 将产生的所有子进程放入进程组
        )
        pid = res.pid
        try:
            # 脚本执行的超时时间为10s
            res.wait(self.run_timeout)
        except subprocess.TimeoutExpired:
            # 如果超时，杀死进程组内所有的子进程，并将返回值设置为200
            os.killpg(os.getpgid(pid), 9)
            status = 200
        except Exception as e:
            logger.exception(e)
            status = 201
        else:
            status = res.returncode
        stdout = res.stdout.read().decode('utf-8').strip()
        stderr = res.stderr.read().decode('utf-8').strip()
        # 读取输出后再统计时间，才是真正的脚本/命令执行时间
        end_timestamp = datetime.datetime.now().timestamp() * 1000
        run_time = end_timestamp - start_timestamp

        put_info = {
            'key': key,
            'cmdline': cmdline,
            'interval': interval,
            'params': params,
            'pid': pid,
            'stderr': stderr,
            'stdout': stdout,
            'stdout_to_num': 0,
            'status': status,
            '@timestamp': self.format_timestamp(end_timestamp / 1000),
            'start_timestamp': start_timestamp,
            'end_timestamp': end_timestamp,
            'run_time': run_time,
            'ops_version': self.ops_version,
        }
        if stdout.isdigit():
            # 如果输出为整数或小数，则写入stdout_to_num
            put_info['stdout_to_num'] = int(stdout)
        else:
            try:
                put_info['stdout_to_num'] = float(stdout)
            except ValueError:
                pass

        self.msg_queue.put_nowait(put_info)
        return put_info

    @staticmethod
    def msg_formatter(msg):
        """
        格式化消息
        :param msg:
        :return: 格式化消息
        """
        result = {
            '@timestamp': msg.get('@timestamp'),
            'metricset': {
                'name': msg.get('key'),  # 自定义脚本的键
                'module': 'ops_custom_scripts'  # 固定值，表明是自定义脚本功能存储的内容
            },
            'beat': {
                'version': msg.get('ops_version')  # ops版本号
            },
            'ops_custom_scripts': {
                'script': {
                    'cmdline': msg.get('cmdline'),  # 执行的命令（可能为脚本或shell命令）
                    'params': msg.get('params'),  # 脚本执行的传参
                    'status': msg.get('status'),  # 脚本执行的返回值
                    'stdout': {
                        'text': msg.get('stdout'),  # 脚本的标准输出
                        'long': msg.get('stdout_to_num')  # 脚本的标准输出转换数字，非数字则为0
                    },
                    'stderr': msg.get('stderr'),  # 脚本的错误输出
                    'pid': msg.get('pid'),  # 脚本执行的进程号pid
                    'run_time': {
                        's': round(msg.get('run_time') / 1000, 3),  # 脚本的执行耗时（单位s）
                        'ms': round(msg.get('run_time'), 3)  # 脚本的执行耗时（单位ms）
                    }
                }
            }
        }

        return result

    @staticmethod
    def format_timestamp(time):
        d = datetime.datetime.fromtimestamp(time, tz=datetime.timezone.utc)
        utc_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        timestamp = d.strftime(utc_format)

        return timestamp

    def save(self, save_to='kafka'):
        """
        收queue消息，储存json文档至指定位置
        :return:
        """
        save_func = getattr(self, 'save_to_%s' % save_to, self.save_to_kafka)
        save_func()

    def save_to_kafka(self, topic='ods.ops.custom.scripts'):
        if not self.msg_queue.empty():
            for i in range(self.msg_queue.qsize()):
                msg = self.msg_queue.get_nowait()
                result = self.msg_formatter(msg)
                logger.info(json.dumps(result))
                logger.info(topic)

    def save_to_es(self):
        all_results = []
        if not self.msg_queue.empty():
            for i in range(self.msg_queue.qsize()):
                msg = self.msg_queue.get_nowait()
                result = self.msg_formatter(msg)
                all_results.append(result)
        if all_results:
            now_timestamp = datetime.datetime.now().timestamp()
            bulk_data = self.get_bulk_data(now_timestamp, all_results)
            try:
                self.post_data_to_elasticsearch(bulk_data)
            except Exception as e:
                logger.exception(e)

    def get_bulk_data(self, t, all_data):
        """
        获取elasticsearch bulk格式的数据
        :param t: time.time()
        :param all_data: 要写入elasticsearch的数据列表
        :return: elasticsearch bulk格式的数据
        """
        now_datetime = datetime.datetime.fromtimestamp(t)
        year = now_datetime.year
        month = now_datetime.month

        index = copy.deepcopy(self.base_es_index).format(
            year=year,
            month=month,
        )
        bulk_data = ''
        bulk_method = 'index'
        bulk_header = {bulk_method: {'_index': index, '_type': '_doc'}}
        bulk_header = json.dumps(bulk_header, separators=(',', ':'))
        for data in all_data:
            bulk_data += bulk_header
            bulk_data += '\n'
            bulk_data += json.dumps(data, separators=(',', ':'))
            bulk_data += '\n'

        return bulk_data

    @staticmethod
    def post_data_to_elasticsearch(bulk_data):
        """
        写入文档
        :param bulk_data: 符合elasticsearch bulk接口数据格式的数据
        :return: 创建结果
        """
        from common.my_elastic import es_client
        try:
            return es_client.bulk(body=bulk_data)
        except Exception as e:
            logger.exception(e)
            raise e

    def get_jobs(self, run_conf):
        """
        获取任务定时器
        :param run_conf: self.get_run_conf()返回值
        :return: {key1: timer1, key2: timer2}
        """
        jobs = []
        for run in run_conf:
            for key, script_info in run.items():
                interval = script_info.get('interval')
                cmdline = script_info.get('cmdline')
                if os.path.isfile(cmdline):
                    # 如果为脚本，则赋权755
                    os.chmod(cmdline, 0o0755)
                params = ' '.join(script_info.get('params'))

                loop_timer = LoopTimer(interval, self.exec_cmdline, [key, interval, cmdline, params])
                jobs.append({key: loop_timer})
        if jobs:
            # 如果有定时任务，则创建存储定时器，从队列中获取执行结果，写入存储中
            save_interval = 0.1
            save_loop_timer = LoopTimer(save_interval, self.save, ['es'])
            jobs.append({'default.save.func': save_loop_timer})
        return jobs

    @staticmethod
    def run_all(jobs):
        """
        开始执行全部job
        :param jobs: jobs字典
        :return:
        """
        for job in jobs:
            if job.values():
                for timer in job.values():
                    timer.start()

    @staticmethod
    def cancel_all(jobs):
        """
        取消执行全部job
        :param jobs: jobs字典
        :return:
        """
        for job in jobs:
            if job.values():
                for timer in job.values():
                    timer.start()


class LoopTimer(threading.Timer):
    def __init__(self, interval, function, args=None, kwargs=None):
        threading.Timer.__init__(self, interval, function, args, kwargs)

    def run(self):
        """
        重新run函数，按照interval时间，循环执行self.function
        :return:
        """
        while True:
            if self.finished.is_set():
                self.finished.set()
                break
            self.function(*self.args, **self.kwargs)
            # 改为执行完函数后等待
            self.finished.wait(self.interval)


def main():
    s = ScriptsHandler()
    if not s.is_enable:
        logger.info('This function is not enabled. '
                    'Please check the enable config file: %s. Exit 2' % s.is_enable_conf_file_path)
        exit(2)
    key_conf = s.get_key_conf()
    run_conf = s.get_run_conf(key_conf)
    jobs = s.get_jobs(run_conf)
    logger.info(jobs)
    s.run_all(jobs)


if __name__ == '__main__':
    main()
