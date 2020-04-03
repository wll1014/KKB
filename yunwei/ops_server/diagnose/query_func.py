#!/usr/bin/env python3
# coding: utf-8
import jsonpath

__author__ = 'wanglei_sxcpx@kedacom.com'

import copy
import logging
import subprocess
import json
import os
import re
import sys
import shutil
import time
import requests
from configparser import ConfigParser
from django.db import connections
from django.db.models.query_utils import Q
from multiprocessing import Process
from ops.settings import MEDIA_ROOT, BASE_DIR, ANSIBLE_PORT, CUSTOM
from diagnose.dsl import es_ql
from diagnose.models import SnapshotTaskModel, QuickCaptureTaskModel, CustomCaptureTaskModel, CustomCaptureItemsModel
from common.my_elastic import es_client
from common.my_redis import my_redis_client
from common import global_func, my_ansible, my_rabbitmq
from ops_statistics.query_func import get_filter_dsl
from common.my_exception import OpsException

logger = logging.getLogger('ops.' + __name__)
scripts_path = os.path.join(BASE_DIR, 'diagnose', 'scripts')


def redis_rdb_dump2json(conf_e164, file_path):
    """
    从redis的dump文件中提取会议号相关信息，存为json文件，以供导出
    :return:
    """
    # 组件组提供的redis dump的rdb文件解析脚本
    PYTHONPATH = os.path.join(os.path.dirname(BASE_DIR), 'ops_python3', 'lib', 'python3.5', 'site-packages')
    script_path = os.path.join(BASE_DIR, 'diagnose', 'scripts', 'rdb_to_json.py')
    # redis dump的rdb文件固定的绝对路径
    rdb_path = os.path.abspath('/opt/data/redis/dump7380.rdb')
    # 导出conf/ 开头的会议相关key命令
    conf_cmd = 'PYTHONPATH={PYTHONPATH} '.format(
        PYTHONPATH=PYTHONPATH) + script_path + ' ' + '--command json -k "conf/{conf_e164}/*" {rdb_path}'.format(
        conf_e164=conf_e164, rdb_path=rdb_path
    )
    # 导出confex/ 开头的会议相关key命令
    conf_ex_cmd = 'PYTHONPATH={PYTHONPATH} '.format(
        PYTHONPATH=PYTHONPATH) + script_path + ' ' + '--command json -k "confex/{conf_e164}/*" {rdb_path}'.format(
        conf_e164=conf_e164, rdb_path=rdb_path
    )
    logger.info('conf_cmd: %s' % conf_cmd)
    logger.info('conf_ex_cmd: %s' % conf_ex_cmd)
    conf_status, conf_output = subprocess.getstatusoutput(conf_cmd)
    conf_ex_status, conf_ex_output = subprocess.getstatusoutput(conf_ex_cmd)

    try:
        conf_file_path = os.path.join(file_path, 'conf.json')
        conf_ex_file_path = os.path.join(file_path, 'confex.json')
        with open(conf_file_path, 'w', encoding='utf-8') as f:
            json.dump(json.loads(conf_output), f, indent=2)
        with open(conf_ex_file_path, 'w', encoding='utf-8') as f:
            json.dump(json.loads(conf_ex_output), f, indent=2)
    except Exception as e:
        logger.error(conf_output)
        logger.error(conf_ex_output)
        logger.exception(e)


def get_es_data(request, task_id):
    key = request.query_params.get('key', '*')
    apps = request.query_params.get('apps', '')
    if apps:
        apps = apps.split(';')

    if not os.path.exists(os.path.join(MEDIA_ROOT, 'snapshot')):
        os.mkdir(os.path.join(MEDIA_ROOT, 'snapshot'))
    es_hosts = global_func.get_conf('elasticsearch', 'hosts').split(',')
    es_port = global_func.get_conf('elasticsearch', 'port')
    if not es_hosts and es_port:
        raise Exception('elasticsearch addr/port error!')

    # sip 查询语句
    sip_dsl = copy.deepcopy(es_ql.sip_packet)
    query_key_dict = {
        "query_string": {
            "fields": [
                "sip.from",
                "sip.to"
            ],
            "query": "*{key}*".format(key=key)
        }
    }
    sip_dsl['dsl']['query']['bool']['must'].append(query_key_dict)

    # log 查询语句
    log_dsl = copy.deepcopy(es_ql.logs)
    query_key_dict = {
        "query_string": {
            "query": ' OR '.join(apps + [key]) if apps else key,
            "analyze_wildcard": True,
            "default_field": "*"
        }
    }
    log_dsl['dsl']['query']['bool']['must'].append(query_key_dict)
    dsls = [sip_dsl, log_dsl]
    dsls = get_filter_dsl(request, dsls, includes=['start_time', 'end_time', 'platform_moid', 'room_moid'])

    if key == '*':
        key = 'nokey'

    pids = []
    errs = []

    snapshot_path = os.path.join(MEDIA_ROOT, 'snapshot', '%s_%s' % (task_id, key))
    if os.path.exists(os.path.join(MEDIA_ROOT, 'snapshot', '%s_%s' % (task_id, key))):
        logger.warning(
            '%s already exists, overwrite it' % snapshot_path)
        shutil.rmtree(snapshot_path)

    for dsl in dsls:
        # 通过es_dump脚本导出sip和logs内容，存入
        if dsl is sip_dsl:
            dump_file_name = 'sip_packets'
            output_file_path = '%s_%s/elasticsearch/packets/%s.json' % (task_id, key, dump_file_name)
        elif dsl is log_dsl:
            dump_file_name = 'logs'
            output_file_path = '%s_%s/elasticsearch/log/%s.json' % (task_id, key, dump_file_name)
        else:
            dump_file_name = 'xx'
            output_file_path = '%s_%s/elasticsearch/xx/%s.json' % (task_id, key, dump_file_name)
        dump_input = 'http://{es_host}:{es_port}/{dump_input_index}'.format(es_host=es_hosts[0], es_port=es_port,
                                                                            dump_input_index=dsl['index'])
        dump_output = os.path.join(MEDIA_ROOT, 'snapshot', output_file_path)
        os.makedirs(os.path.dirname(dump_output), exist_ok=True)
        dump_type = 'data'
        dump_search_body = json.dumps(dsl['dsl'], separators=(',', ':'))

        script_path = os.path.join(scripts_path, 'es_dump.sh')
        cmd = '/bin/bash {script_path} \'{dump_input}\' \'{dump_output}\' \'{dump_type}\' \'{dump_search_body}\' \'{dump_file_name}\''.format(
            script_path=script_path,
            dump_input=dump_input,
            dump_output=dump_output,
            dump_type=dump_type,
            dump_search_body=dump_search_body,
            dump_file_name=dump_file_name
        )
        logger.info('start dump %s...' % dump_file_name)
        status, stdout = subprocess.getstatusoutput(cmd)
        logger.info(cmd)
        logger.info('%s: %s' % (status, stdout))

        if status == 0:
            pid = stdout.split(':')[1]
            pids.append(pid)
        else:
            err_msg = stdout
            errs.append(err_msg)

    # redis快照导出
    if re.match(r'^\d{7}$', key):
        output_file_path = '%s_%s/redis/' % (task_id, key)
        file_path = os.path.join(MEDIA_ROOT, 'snapshot', output_file_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        try:
            redis_rdb_dump2json(key, file_path)
        except Exception as e:
            logger.exception(e)
    else:
        logger.info('the key: %s is not a conf_e164，no redis info' % key)

    # 会议号存在
    # 增加cmu/mps等打印
    if key != "nokey":
        snapshot_script_path = os.path.join(scripts_path, 'real_conf_business_snapshot.sh')
        # 如果配置了定制脚本则优先使用定制脚本  定制脚本存放在特定路径 配置文件--custom--ConfSnapShot
        # 否则使用通用脚本
        if CUSTOM is not None and CUSTOM.get('ConfSnapShot') is not None:
            custom_snapshot_script_path = CUSTOM.get('ConfSnapShot')
            if os.path.exists(custom_snapshot_script_path):
                snapshot_script_path = custom_snapshot_script_path

        # 确保所需配置文件存在  /opt/data/ops/media/check_apps/conf/ip_info.ini
        CheckAppsProcess(request, None)

        redis_platform_password = global_func.get_conf('redis_platform', 'password')
        ssh_port = ANSIBLE_PORT
        output_file_path = '%s_%s/business/curr_mtinfo' % (task_id, key)
        dump_output = os.path.join(MEDIA_ROOT, 'snapshot', output_file_path)
        script_path = os.path.join(scripts_path, 'exec_script.sh')

        cmd = '/bin/bash {script_path} {custom_script} {conf_e164} \'\' {redis_platform_password} {ssh_port} ' \
              '{dump_output}'.format(
            script_path=script_path,  # executor
            custom_script=snapshot_script_path,  # 真正要执行的脚本
            conf_e164=key,
            redis_platform_password=redis_platform_password,
            ssh_port=ssh_port,
            dump_output=dump_output,
        )

        logger.info('start run %s...' % snapshot_script_path)
        status, stdout = subprocess.getstatusoutput(cmd)
        logger.info(cmd)
        logger.info('%s: %s' % (status, stdout))

        if status == 0:
            pid = stdout.split(':')[1]
            pids.append(pid)
        else:
            err_msg = stdout
            errs.append(err_msg)

    if errs:
        return False, errs
    else:
        return True, pids


def kill_all_task(task_id):
    task_queryset = SnapshotTaskModel.objects.filter(id=task_id).first()
    if task_queryset:
        script_path = os.path.join(scripts_path, 'kill_all_snapshot_task.sh')
        cmd = '/bin/bash %s' % script_path
        status, stdout = subprocess.getstatusoutput(cmd)
        logger.info(cmd)
    else:
        status, stdout = 255, 'task_id不存在'
    logger.info('%s: %s' % (status, stdout))

    return status, stdout


def check_dump_process(task_id):
    script_path = os.path.join(scripts_path, 'check_dump.sh')
    cmd = '/bin/bash {script_path} {task_id} {mysql_user} {mysql_pass} {mysql_addr} {mysql_port}'.format(
        script_path=script_path,
        task_id=task_id,
        mysql_user=global_func.get_conf('mysql', 'user'),
        mysql_pass=global_func.get_conf('mysql', 'password'),
        mysql_addr=global_func.get_conf('mysql', 'host'),
        mysql_port=global_func.get_conf('mysql', 'port'),
    )
    status, stdout = subprocess.getstatusoutput(cmd)
    logger.info('begin check dump...')
    logger.info(cmd)
    logger.info('%s: %s' % (status, stdout))
    return True


def get_luban_machines_ip_info(moids):
    '''
    从luban数据库获取机器ip信息
    :param moids: 机器moid列表
    :return:
    '''

    ip_info = {}
    if moids:
        try:
            with connections['luban'].cursor() as cursor:
                sql = '''
                SELECT mi.machine_moid,ii.ip FROM machine_info mi 
                LEFT JOIN ip_info ii ON mi.id=ii.machine_id 
                WHERE ii.flag=1 AND mi.machine_moid IN %s; 
                '''
                params = [moids]
                cursor.execute(sql, params)
                fetchall = cursor.fetchall()

            ip_info = {fetch[0]: fetch[1] for fetch in fetchall}
        except Exception as e:
            err = str(e)
            logger.error(err)

    return ip_info


def get_luban_machines_info(moids):
    '''
    从luban数据库获取机器信息
    :param moids: 机器moid列表
    :return:
    '''

    machines_info = {}
    if moids:
        try:
            with connections['luban'].cursor() as cursor:
                sql = '''
                SELECT mi.machine_moid,ii.ip,mi.machine_name,mi.machine_type,mi.machine_room_moid,mi.machine_room_name
                FROM machine_info mi 
                LEFT JOIN ip_info ii ON mi.id=ii.machine_id 
                WHERE ii.flag=1 AND mi.machine_moid IN %s; 
                '''
                params = [moids]
                cursor.execute(sql, params)
                fetchall = cursor.fetchall()

            machines_info = {fetch[0]: {
                'ip': fetch[1],
                'machine_name': fetch[2],
                'machine_type': fetch[3],
                'machine_room_moid': fetch[4],
                'machine_room_name': fetch[5],
            } for fetch in fetchall}
        except Exception as e:
            err = str(e)
            logger.error(err)

    return machines_info


def get_luban_machines_network_card_info(moids):
    network_card_info = {}
    try:
        with connections['luban'].cursor() as cursor:
            sql = '''
            SELECT mi.machine_moid,mi.machine_name,nci.name FROM machine_info mi 
            LEFT JOIN network_card_info nci on mi.id=nci.machine_id 
            WHERE mi.machine_moid in %s; 
            '''
            params = [moids]
            cursor.execute(sql, params)
            fetchall = cursor.fetchall()
            logger.debug(fetchall)

        for fetch in fetchall:
            if network_card_info.get(fetch[0]):
                network_card_info[fetch[0]]['cards'].append(fetch[2])
            else:
                network_card_info[fetch[0]] = {'cards': [fetch[2]], 'machine_moid': fetch[0], 'machine_name': fetch[1]}
    except Exception as e:
        err = str(e)
        logger.error(err)

    return network_card_info


def get_mt_info(moids):
    '''
    从movision数据库查询终端信息
    :param moids: 终端moid列表
    :return:
    '''
    mt_info = {}
    if moids:
        try:
            with connections['movision'].cursor() as cursor:
                sql = '''
                SELECT ui.moid,up.name,ui.account,ui.e164,ui.email FROM user_info ui 
                LEFT JOIN user_profile up on ui.moid=up.moid 
                WHERE ui.moid in %s;
                '''
                params = [moids]
                cursor.execute(sql, params)
                fetchall = cursor.fetchall()

            mt_info = {fetch[0]: {
                'name': fetch[1],
                'account': fetch[2],
                'e164': fetch[3],
                'email': fetch[4],
            } for fetch in fetchall}
        except Exception as e:
            err = str(e)
            logger.error(err)

    return mt_info


def get_jdb_ip():
    '''
    获取jdb的扫描ip
    :return:
    '''
    jdb_ip = '127.0.0.1'
    try:
        with connections['luban'].cursor() as cursor:
            sql = '''
            SELECT mi.machine_moid,ii.ip FROM machine_info mi 
            LEFT JOIN ip_info ii ON mi.id=ii.machine_id 
            WHERE ii.flag=1 AND mi.machine_type LIKE '%%jdb%%'; 
            '''
            params = []
            cursor.execute(sql, params)
            fetchone = cursor.fetchone()

        jdb_ip = fetchone[1]
    except Exception as e:
        err = str(e)
        logger.error(err)

    return jdb_ip


class TerminalCaptureRabbitmqClient(my_rabbitmq.RMQClient):
    _START_TIME = time.time()
    _REDIS_KEY = 'terminal_capture_%s' % int(_START_TIME)

    def start_terminal_capture_consuming(self, exchange_name='nms.collector.ex', queue_name='ops.nms_packet.q',
                                         routing_key='collector.nms.#'):
        my_redis_client.delete(self._REDIS_KEY)
        item_type = 2
        items = CustomCaptureItemsModel.objects.filter(item_type=item_type)
        item_moids = [item.moid for item in items]
        try:
            queue = self.declare_queue(queue_name=queue_name, exclusive=False, auto_delete=True)
        except Exception as e:
            logger.error(str(e))
        try:
            self.bind_queue(exchange=exchange_name, queue=queue_name, routing_key=routing_key)
        except Exception as e:
            logger.error(str(e))
        self.set_qos()
        for method_frame, properties, body in self.channel.consume(queue_name):
            self.channel.basic_ack(method_frame.delivery_tag)
            body = json.loads(body.decode('utf-8'))
            eventid = body.get('eventid')
            devid = body.get('devid')
            useful_eventid = [
                'EV_PACKETCAPTURE_START_ACK',
                'EV_PACKETCAPTURE_STOP_ACK',
                'EV_PACKETCAPTURE_UPLOAD_PROGRESS_NTF',
            ]
            if not item_moids:
                # 如果全部完成，退出mq消息收取
                break
            now = time.time()
            if now - self._START_TIME > 15 * 60:
                # 如果超过15分钟仍未完成，则认为任务失败，退出mq消息收取
                break
            if eventid in useful_eventid and devid in item_moids:
                logger.debug('properties: %s body: %s' % (properties, body))
                if eventid == 'EV_PACKETCAPTURE_START_ACK':
                    # 开始抓包回复
                    if body.get('reasoncode'):
                        # 开始抓包失败
                        CustomCaptureItemsModel.objects.filter(
                            Q(item_type=item_type) & Q(is_complete=0) & Q(moid=devid)).update(is_complete=2)
                        if item_moids.count(devid):
                            item_moids.remove(devid)
                    else:
                        # 开始抓包成功
                        pass
                elif eventid == 'EV_PACKETCAPTURE_STOP_ACK':
                    if body.get('reasoncode'):
                        # 结束抓包失败
                        CustomCaptureItemsModel.objects.filter(
                            Q(item_type=item_type) & Q(is_complete=0) & Q(moid=devid)).update(is_complete=2)
                        if item_moids.count(devid):
                            item_moids.remove(devid)
                    else:
                        # 结束抓包成功
                        pass
                else:
                    if body.get('progress', -1) < 0:
                        # 上传抓包文件失败
                        CustomCaptureItemsModel.objects.filter(
                            Q(item_type=item_type) & Q(is_complete=0) & Q(moid=devid)).update(is_complete=2)
                        if item_moids.count(devid):
                            item_moids.remove(devid)
                    elif body.get('progress', -1) == 100:
                        # 上传抓包文件成功
                        # url = 'http://10.67.18.11:8083/mnt/files/kdfs/2019-10-12_17-18-34_capfile.tar.gz'
                        url = body.get('url')
                        if url:
                            my_redis_client.hset(self._REDIS_KEY, devid, url)
                        if devid in item_moids:
                            item_moids.remove(devid)
                    else:
                        # 上传抓包文件中
                        pass


class TaskResult(Process):
    def __init__(self, request, task_id, task_type='quick_capture'):
        super().__init__()
        self.request = request
        self.task_id = task_id
        self.task_type = task_type
        self.file_server_ip = get_jdb_ip()
        # self.file_server_ip = '10.67.18.11'
        try:
            self.core_mq = TerminalCaptureRabbitmqClient(
                hosts=global_func.get_conf('rabbitmq_core', 'host').split(','),
                port=global_func.get_conf('rabbitmq_core', 'port'),
                username=global_func.get_conf('rabbitmq_core', 'username'),
                password=global_func.get_conf('rabbitmq_core', 'password')
            )
            logger.debug(self.core_mq.channel)
        except Exception as e:
            err = str(e)
            logger.error(err)
            self.core_mq = None

    def run(self):
        self.func()()

    def func(self):
        # 关闭 uwsgi 连接的文件描述符， 解决 子进程运行过程中 前端 继续get请求阻塞问题
        import uwsgi
        fd = uwsgi.connection_fd()
        uwsgi.close(fd)
        connections.close_all()
        if hasattr(self, self.task_type):
            return getattr(self, self.task_type)
        # if self.task_type == 'quick_capture':
        #     return self.get_quick_capture_result
        else:
            return self.none_func

    def none_func(self):
        pass

    def quick_capture(self):
        logger.info('start %s...' % sys._getframe().f_code.co_name)
        queryset = QuickCaptureTaskModel.objects.filter(pk=self.task_id).first()
        if queryset:
            conf_e164 = queryset.conf_e164
            mt_e164 = queryset.mt_e164
            script_path = os.path.join(scripts_path, 'quick_capture.sh')
            redis_platform_addr = global_func.get_conf('redis_platform', 'host')
            # redis_platform_addr = '10.67.18.203'
            redis_platform_port = global_func.get_conf('redis_platform', 'port')
            # redis_platform_port = '6379'
            redis_platform_password = global_func.get_conf('redis_platform', 'password')
            ssh_port = ANSIBLE_PORT

            cmd = '/bin/bash {script_path} {conf_e164} {mt_e164} ' \
                  '{redis_platform_addr} {redis_platform_port} {redis_platform_password} {ssh_port}'.format(
                script_path=script_path,
                conf_e164=conf_e164,
                mt_e164=mt_e164,
                redis_platform_addr=redis_platform_addr,
                redis_platform_port=redis_platform_port,
                redis_platform_password=redis_platform_password,
                ssh_port=ssh_port,
            )
            logger.debug(cmd)
            status, stdout = subprocess.getstatusoutput(cmd)

            if status == 0:
                logger.debug(stdout)
                if '.tar.gz' and '__ops__' in stdout:
                    queryset.filename = stdout.split('__ops__')[-1]
                    queryset.is_complete = '1'
                    queryset.save()
            else:
                queryset.is_complete = status
                queryset.save()
                logger.debug(stdout)
                logger.debug(status)
        logger.info('stop %s...' % sys._getframe().f_code.co_name)

    @staticmethod
    def get_tcpdump_cmd(ip, timeout=30, card='', ports='', protocol=''):
        '''
        获取tcpdump命令
        :param timeout: 命令超时时间 ，默认30s
        :param card: 抓包网卡，默认全部
        :param ports: 端口字符串，多个以‘，’分开
        :param protocol: 抓包协议 ｛tcp|udp｝，默认不指定
        :return: tcpdump命令
        '''
        filename = os.path.join(MEDIA_ROOT, 'custom_capture', 'ops_%s.pcap' % ip)
        cmd = 'mkdir -p $(dirname %s);' % filename
        if timeout:
            cmd += 'timeout {0} tcpdump -s 0 -w {1}'.format(timeout, filename)
        else:
            cmd += 'tcpdump -s 0 -w {0}'.format(filename)
        if card:
            cmd += ' -i {0} '.format(card)
        else:
            cmd += ' -i any '
        if ports:
            if protocol:
                cmd += '{0} port '.format(protocol) + ' or {0} port '.format(protocol).join(ports.split(','))
            else:
                cmd += 'port ' + ' or port '.join(ports.split(','))
        else:
            if protocol:
                cmd += protocol
        return cmd

    def start_server_custom_capture(self):
        '''
        开始服务器抓包
        :return:
        '''
        logger.info('start %s...' % sys._getframe().f_code.co_name)
        item_type = 1
        tasks = []
        try:
            try:
                task_queryset = CustomCaptureItemsModel.objects.filter(item_type=item_type)

                moids = {
                    task.moid: {
                        'card': task.card,
                        'ports': task.ports,
                        'protocol': task.protocol,
                        'timeout': task.task.timeout,
                    } for task in task_queryset
                }
            except Exception as e:
                err = str(e)
                logger.error(err)
                moids = {}

            # moids = ["5c4eebf0-ac23-11e8-b3e1-a4bf01306d06", "c1b69852-ac24-11e8-88d9-a4bf01306d06"]

            if not moids:
                logger.info('没有需要抓包的服务器')
                CustomCaptureItemsModel.objects.filter(item_type=item_type).update(is_complete=2)
                return
            ip_info = get_luban_machines_ip_info(list(moids.keys()))
            ip_list = ip_info.values()
            logger.debug(ip_list)
            ip2moid = {}
            hosts = my_ansible.AnsibleSameInfoHosts(ip_list)
            ansible_host_list = hosts.get_ansible_host_list()
            ansible_task = my_ansible.AnsibleTask(ansible_host_list)

            shell_content = ''
            for moid, ip in ip_info.items():
                ip2moid[ip] = moid
                tcpdump_params_info = moids.get(moid, {})
                cmd = self.get_tcpdump_cmd(
                    ip=ip,
                    timeout=tcpdump_params_info.get('timeout'),
                    card=tcpdump_params_info.get('card'),
                    protocol=tcpdump_params_info.get('protocol'),
                    ports=tcpdump_params_info.get('ports')
                )
                shell_content += 'if [[ $(hostname -I) =~ {0} ]];then '.format(ip) + cmd + '; fi\n'
            tmp_sh = os.path.join(os.path.abspath(MEDIA_ROOT), 'custom_capture', 'tmp_tcpdump.sh')
            with open(tmp_sh, 'w', encoding='utf-8') as f:
                f.write(shell_content)

            tcpdump_playbook_path = os.path.join(BASE_DIR, 'diagnose', 'scripts', 'tcpdump_on_all_hosts.yaml')
            playbooks = [tcpdump_playbook_path]
            result = ansible_task.exec_playbook(playbooks)

            # result = ansible_task.exec_tasks(tasks)
            unreachable_hosts_moid = []
            for host in result.host_unreachable:
                ip = host.get('ip')
                moid = ip2moid.get(ip)
                unreachable_hosts_moid.append(moid)
            logger.debug('ok: %s' % json.dumps(result.host_ok))
            logger.debug('failed: %s' % json.dumps(result.host_failed))
            logger.debug('unreachable: %s' % json.dumps(result.host_unreachable))
            try:
                self.get_all_server_capture_files(ip_list)
            except Exception as e:
                err = str(e)
                logger.error(err)

            CustomCaptureItemsModel.objects.filter(item_type=item_type).update(is_complete=1)
            CustomCaptureItemsModel.objects.filter(Q(moid__in=unreachable_hosts_moid) & Q(item_type=item_type)).update(
                is_complete=2)
        except Exception as e:
            err = str(e)
            logger.error(err)
        logger.info('stop %s...' % sys._getframe().f_code.co_name)

    def stop_server_custom_capture(self):
        '''
        结束服务器抓包
        :return:
        '''
        logger.info('start %s...' % sys._getframe().f_code.co_name)
        item_type = 1
        tasks = []
        try:
            try:
                task_queryset = CustomCaptureItemsModel.objects.filter(item_type=item_type)
                moids = {
                    task.moid: {
                        'card': task.card,
                        'ports': task.ports,
                        'protocol': task.protocol,
                        'timeout': task.task.timeout,
                    } for task in task_queryset
                }
            except Exception as e:
                err = str(e)
                logger.error(err)
                moids = {}

            # moids = ["5c4eebf0-ac23-11e8-b3e1-a4bf01306d06", "c1b69852-ac24-11e8-88d9-a4bf01306d06"]
            ip_info = get_luban_machines_ip_info(list(moids.keys()))
            ip_list = ip_info.values()
            logger.debug(ip_list)
            hosts = my_ansible.AnsibleSameInfoHosts(ip_list)
            ansible_host_list = hosts.get_ansible_host_list()
            ansible_task = my_ansible.AnsibleTask(ansible_host_list)

            cmd = "ps -ef | grep 'tcpdump -s 0 -w /opt/data/ops/media/custom_capture/ops' | grep -v 'grep' | " \
                  "awk '{print $2}'| xargs kill -9 &>/dev/null"
            tasks.append(ansible_task.SHELL(cmd))
            logger.debug(tasks)

            result = ansible_task.exec_tasks(tasks)
            logger.debug('ok: %s' % json.dumps(result.host_ok))
            logger.debug('failed: %s' % json.dumps(result.host_failed))
            logger.debug('unreachable: %s' % json.dumps(result.host_unreachable))
        except Exception as e:
            err = str(e)
            logger.error(err)
        logger.info('stop %s...' % sys._getframe().f_code.co_name)

    def get_all_server_capture_files(self, ip_list):
        '''
        获取所有服务器网络包到本地
        :return:
        '''
        logger.info('start %s...' % sys._getframe().f_code.co_name)
        fetch_capture_playbook_path = os.path.join(BASE_DIR, 'diagnose', 'scripts', 'fetch_capture_playbook.yaml')
        playbooks = [fetch_capture_playbook_path]
        logger.info(ip_list)
        hosts = my_ansible.AnsibleSameInfoHosts(ip_list)
        ansible_host_list = hosts.get_ansible_host_list()
        ansible_task = my_ansible.AnsibleTask(ansible_host_list)
        server_custom_capture_path = os.path.join(MEDIA_ROOT, 'custom_capture', 'server')
        shutil.rmtree(server_custom_capture_path, ignore_errors=True)
        os.makedirs(server_custom_capture_path, exist_ok=True)

        result = ansible_task.exec_playbook(playbooks)

        logger.debug('ok: %s' % json.dumps(result.host_ok))
        logger.debug('failed: %s' % json.dumps(result.host_failed))
        logger.debug('unreachable: %s' % json.dumps(result.host_unreachable))

        logger.info('stop %s...' % sys._getframe().f_code.co_name)

    def start_terminal_custom_capture(self):
        '''
        开始终端抓包
        :return:
        '''
        logger.info('start %s...' % sys._getframe().f_code.co_name)
        item_type = 2
        items = CustomCaptureItemsModel.objects.filter(item_type=item_type)
        if not self.core_mq:
            logger.info('core rabbitmq is not connected')
            return
        file_server_ip = self.file_server_ip
        file_server_port = 8083
        file_server_upload_dir = '/mnt/files/kdfs/'
        netcard = 'any'
        try:
            for item in items:
                payload = {
                    "eventid": "EV_PACKETCAPTURE_START_REQ",  # 开始抓包
                    "devid": item.moid,  # 终端moid
                    "devtype": item.dev_type,  # 终端类型
                    "file_server_ip": file_server_ip,  # 文件服务器地址
                    "file_server_port": file_server_port,  # 文件服务器端口
                    "file_server_upload_dir": file_server_upload_dir,  # 文件服务器路径 （不生效）
                    "netcard": netcard,  # 终端抓包的网口
                    "isterminal": 1  # 终端标识
                }
                payload = json.dumps(payload)
                # 获取collector_moid
                dsl = copy.deepcopy(es_ql.mttype_online_offline)
                dsl['dsl']['query']['bool']['must'].append({'match_phrase': {'source.devid': item.moid}})
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
                    collector_moid = jsonpath.jsonpath(mt_response, '$..collector_moid')
                    # collector_moid = ['c1b69852-ac24-11e8-88d9-a4bf01306d06']
                    logger.debug(collector_moid)
                    if collector_moid:
                        collector_moid = collector_moid[0]
                        routing_key = 'nms.webserver.k:%s' % collector_moid
                        logger.debug(routing_key)
                        ret = self.core_mq.pub_msg(
                            msg=payload,
                            exchange='nms.webserver.ex',
                            routing_key=routing_key,
                        )
                        logger.info('pub_msg ret:"%s" msg:"%s" routing_key:"%s"' % (ret, payload, routing_key))
                    else:
                        logger.warning('moid: %s collectorid not found' % item.moid)
                else:
                    logger.warning('moid: %s collectorid not found' % item.moid)
            timeout = CustomCaptureTaskModel.objects.all().first().timeout
            timeout = int(timeout) if timeout else 60
            logger.debug('begin terminal custom capture timeout: %s' % timeout)
            time.sleep(timeout)
            logger.debug('end terminal custom capture timeout: %s' % timeout)

            self.stop_terminal_custom_capture()
        except Exception as e:
            err = str(e)
            logger.error(err)

        # CustomCaptureItemsModel.objects.filter(item_type=2).update(is_complete=1)
        logger.info('stop %s...' % sys._getframe().f_code.co_name)

    def stop_terminal_custom_capture(self):
        '''
        结束终端抓包
        :return:
        '''
        logger.info('start %s...' % sys._getframe().f_code.co_name)
        item_type = 2
        if not self.core_mq:
            logger.info('core rabbitmq is not connected')
            return
        if not CustomCaptureItemsModel.objects.filter(Q(item_type=item_type) & Q(is_complete=0)).exists():
            logger.info('all terminal capture tasks have been completed')
            return
        items = CustomCaptureItemsModel.objects.filter(item_type=item_type)
        file_server_ip = self.file_server_ip
        file_server_port = 8083
        file_server_upload_dir = '/mnt/files/kdfs/'
        netcard = 'any'
        try:
            for item in items:
                payload = {
                    "eventid": "EV_PACKETCAPTURE_STOP_REQ",  # 停止抓包
                    "devid": item.moid,  # 终端moid
                    "devtype": item.dev_type,  # 终端类型
                    "file_server_ip": file_server_ip,  # 文件服务器地址
                    "file_server_port": file_server_port,  # 文件服务器端口
                    "file_server_upload_dir": file_server_upload_dir,  # 文件服务器路径 （不生效）
                    "netcard": netcard,  # 终端抓包的网口
                    "isterminal": 1
                }
                payload = json.dumps(payload)
                # 获取collector_moid
                dsl = copy.deepcopy(es_ql.mttype_online_offline)
                dsl['dsl']['query']['bool']['must'].append({'match_phrase': {'source.devid': item.moid}})
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
                    collector_moid = jsonpath.jsonpath(mt_response, '$..collector_moid')
                    # collector_moid = ['c1b69852-ac24-11e8-88d9-a4bf01306d06']
                    if collector_moid:
                        collector_moid = collector_moid[0]
                        routing_key = 'nms.webserver.k:%s' % collector_moid
                        ret = self.core_mq.pub_msg(
                            msg=payload,
                            exchange='nms.webserver.ex',
                            routing_key=routing_key,
                        )
                        logger.info('pub_msg ret:"%s" msg:"%s" routing_key:"%s"' % (ret, payload, routing_key))
                    else:
                        logger.warning('moid: %s collectorid not found' % item.moid)
                else:
                    logger.warning('moid: %s collectorid not found' % item.moid)
        except Exception as e:
            err = str(e)
            logger.error(err)

        logger.info('stop %s...' % sys._getframe().f_code.co_name)

    def check_terminal_capture_status(self):
        '''
        查看终端抓包状态，如完成，则写数据库、获取终端包到本地
        :return:
        '''
        logger.info('start %s...' % sys._getframe().f_code.co_name)
        item_type = 2
        if not self.core_mq:
            logger.info('core rabbitmq is not connected')
            return
        try:
            redis_key = self.core_mq._REDIS_KEY
            self.core_mq.start_terminal_capture_consuming()
        except Exception as e:
            err = str(e)
            logger.error(err)
        else:
            terminals_info = my_redis_client.hgetall(redis_key)
            self.get_all_terminal_capture_files(terminals_info)
            my_redis_client.delete(redis_key)
        logger.info('update terminal items status')
        CustomCaptureItemsModel.objects.filter(Q(item_type=item_type) & Q(is_complete=0)).update(is_complete=1)
        logger.info('stop %s...' % sys._getframe().f_code.co_name)

    def get_all_terminal_capture_files(self, terminals_info):
        '''
        获取所有终端网络包到本地
        :return:
        '''
        logger.info('start %s...' % sys._getframe().f_code.co_name)
        item_type = 2
        protocol = 'http'
        file_server_ip = self.file_server_ip
        file_server_port = 8083
        items = CustomCaptureItemsModel.objects.filter(Q(item_type=item_type) & ~Q(is_complete=2))
        item_moids = [item.moid for item in items]
        mt_info = get_mt_info(item_moids)
        for item_moid in item_moids:
            url = '%s://%s:%s/api/inner/kdfs/v1' % (protocol, file_server_ip, file_server_port)
            path = terminals_info.get(item_moid.encode())
            if path and isinstance(path, bytes):
                path = path.decode().split('/')[-1]
                params = {'path': path, 'type': 'download', 'home': 'platformLog'}
                terminal_capture_path = os.path.join(MEDIA_ROOT, 'custom_capture', 'terminal')
                mt_name = mt_info.get(item_moid, {}).get('name', '')
                ret = requests.get(url, params)
                if ret.status_code == 200:
                    if not os.path.exists(terminal_capture_path):
                        os.makedirs(terminal_capture_path, exist_ok=True)
                    with open(os.path.join(terminal_capture_path, mt_name + '_' + path), 'wb')as f:
                        f.write(ret.content)
                    logger.info('终端%s的抓包文件%s下载完成' % (item_moid, path))
                else:
                    logger.error(ret.text)
                    logger.error('终端%s的抓包文件%s下载失败' % (item_moid, path))
        logger.info('stop %s...' % sys._getframe().f_code.co_name)

    def compress_capture_files(self):
        '''
        压缩本地网络包文件
        :return:
        '''
        logger.info('start %s...' % sys._getframe().f_code.co_name)
        task = CustomCaptureTaskModel.objects.all().first()
        while True:
            if all([item.is_complete for item in task.customcaptureitemsmodel_set.all()]):
                # 开始压缩文件
                logger.info('begin compress...')
                tar_file_name = 'custom_capture_%s.tar.gz' % int(time.time() * 1000)
                custom_capture_path = os.path.join(MEDIA_ROOT, 'custom_capture')
                cmd = 'cd %s;mkdir -p server terminal;tar -zcf %s server terminal' % (
                    custom_capture_path, tar_file_name)
                status, stdout = subprocess.getstatusoutput(cmd)
                logger.info('status: %s, stdout: %s, cmd: [%s]' % (status, stdout, cmd))
                CustomCaptureTaskModel.objects.all().update(filename=tar_file_name)
                logger.info('end compress...')
                break
            logger.debug(
                'check again %s' % {item.moid: item.is_complete for item in task.customcaptureitemsmodel_set.all()})
            time.sleep(1)
        logger.info('stop %s...' % sys._getframe().f_code.co_name)


class CheckAppsProcess(Process):
    def __init__(self, request, task_id, task_type='check_all'):
        super().__init__()
        self.request = request
        self.task_id = task_id
        self.task_type = task_type
        self.all_check_type = ['web', 'midware', 'platform', 'other']
        self.conf_options = ["aps", "css", "cmu", "rms", "dss-master", "cmdataproxy", "media-master", "pas", "mysql",
                             "redis", "ejabberd", "glusterfs", "zookeeper", "upu", "upucore", "modb", "modbcore",
                             "rabbitmq", "web", "machine", "dss-worker"]
        self.check_apps_path = os.path.join(BASE_DIR, 'diagnose', 'scripts', 'check_apps')
        self.scripts_path = os.path.join(self.check_apps_path, 'scripts')
        self.data_path = os.path.join(MEDIA_ROOT, 'check_apps')
        self.log_path = os.path.join(self.data_path, 'log')
        self.conf_file = os.path.join(self.data_path, 'conf', 'ip_info.ini')
        if self.request.method == 'POST':
            self._init_conf()
            self._set_conf_apps()

    def run(self):
        self.func()()

    def func(self):
        # 关闭 uwsgi 连接的文件描述符， 解决 子进程运行过程中 前端 继续get请求阻塞问题
        import uwsgi
        fd = uwsgi.connection_fd()
        uwsgi.close(fd)
        connections.close_all()
        if hasattr(self, self.task_type):
            return getattr(self, self.task_type)
        else:
            return self.none_func

    def none_func(self):
        pass

    def _get_config(self):
        config = ConfigParser()
        config.read(self.conf_file)
        return config

    def _init_conf(self):
        if not os.path.exists(self.conf_file):
            os.makedirs(os.path.dirname(self.conf_file), exist_ok=True)
        with open(self.conf_file, 'w', encoding='utf-8') as f:
            config = self._get_config()
            config.add_section('info')
            config.write(f)

    def _get_conf_apps(self):
        '''
        从luban数据库获取业务地址
        :return:
        '''
        conf_apps = {}
        sql = '''
        SELECT si.server_type,ii.ip FROM server_info si 
        LEFT JOIN machine_info mi ON si.p_server_moid=mi.machine_moid 
        LEFT JOIN ip_info ii on mi.id=ii.machine_id 
        WHERE ii.flag=1;
        '''
        all_x86_machines_sql = '''
        SELECT ii.ip FROM machine_info mi 
        LEFT JOIN ip_info ii ON mi.id=ii.machine_id 
        WHERE ii.flag=1 
        AND client_version!='';
        '''
        params = []
        try:
            with connections['luban'].cursor() as cursor:
                cursor.execute(sql, params)
                fetchall = cursor.fetchall()
                cursor.execute(all_x86_machines_sql, params)
                all_x86_machines = cursor.fetchall()
        except Exception as e:
            err = str(e)
            logger.error(err)
            return conf_apps
        for server in fetchall:
            server_type = server[0]
            ip = server[1]
            if conf_apps.get(server_type) and ip not in conf_apps[server_type]:
                conf_apps[server_type].append(ip)
            else:
                conf_apps[server_type] = [ip]
        conf_apps['machine'] = [machine[0] for machine in all_x86_machines]

        return conf_apps

    def _set_conf_apps(self):
        '''
        写配置文件
        :return:
        '''
        conf_apps = self._get_conf_apps()
        config = self._get_config()
        section = 'info'
        with open(self.conf_file, 'w', encoding='utf-8') as f:
            for option in self.conf_options:
                if option == 'web':
                    all_web = ["amc", "amcapi", "apicomet", "bmc", "serviceCore", "ssoCore", "apiCore",
                               "cmc", "service", "sso", "api", "api5", "ssuweb", "jms"]
                    web_list = []
                    for web in all_web:
                        web_list.extend(conf_apps.get(web, []))
                    web_list = list(set(web_list))
                    config.set(section, option, ' '.join(web_list))
                else:
                    config.set(section, option, ' '.join(conf_apps.get(option, [])))
            config.write(f)

    @property
    def is_conf_ok(self):
        config = self._get_config()
        section = 'info'
        if config.has_section(section):
            for option in config.options(section):
                if not config.get(section, option) and option not in ('mysql', 'redis'):
                    # 阿里云环境，mysql与redis不入网，不检测
                    logger.error('%s is not found from luban...' % option)
                    return False
            return True
        else:
            logger.error('%s can not create...' % self.conf_file)
            return False

    @property
    def is_running(self):
        cmd = 'ps -ef | grep -e begin_check_.*.sh | grep -v grep | wc -l'
        status, stdout = subprocess.getstatusoutput(cmd)
        if int(stdout) > 0:
            return True
        else:
            return False

    def _set_begin_flag(self, check_type):
        my_redis_client.hset('check_apps', check_type, 'begin')

    def _set_end_flag(self, check_type):
        my_redis_client.hset('check_apps', check_type, 'end')
        my_redis_client.hset('check_apps', 'end_time', int(time.time() * 1000))

    def _set_all_begin_flag(self):
        for check_type in self.all_check_type:
            my_redis_client.hset('check_apps', check_type, 'begin')

    def _set_all_end_flag(self):
        for check_type in self.all_check_type:
            my_redis_client.hset('check_apps', check_type, 'end')

    def _get_flag(self, check_type):
        flag = my_redis_client.hget('check_apps', check_type)
        if flag: flag = flag.decode(encoding='utf-8')
        # logger.debug(flag)
        return flag

    def _get_check_end_time(self):
        end_time = my_redis_client.hget('check_apps', 'end_time')
        if end_time:
            try:
                end_time = int(end_time.decode(encoding='utf-8'))
            except Exception as e:
                logger.error(str(e))
                end_time = int(time.time() * 1000)
        else:
            end_time = ''
        # logger.debug(flag)
        return end_time

    def _get_all_flag(self):
        all_flag = my_redis_client.hgetall('check_apps')
        # logger.debug(all_flag)
        return all_flag

    def _clear_all_result(self):
        for check_type in self.all_check_type:
            result_file = os.path.join(self.data_path, '%s.ini' % check_type)
            with open(result_file, 'w', encoding='utf-8') as f:
                pass

    def check_all(self):
        logger.info('start %s...' % sys._getframe().f_code.co_name)
        # begin_check_all.sh脚本同时调用每个类型的入口脚本
        self._set_all_begin_flag()
        self._clear_all_result()
        script_name = 'begin_check_all.sh'
        script = os.path.join(self.scripts_path, script_name)
        status, stdout = subprocess.getstatusoutput(script)
        logger.info('script: %s, status: %s, stdout: %s' % (script, status, stdout))
        self._set_all_end_flag()

        # self._set_all_begin_flag()
        # self._clear_all_result()
        # self.check_web()
        # self.check_midware()
        # self.check_platform()
        # self.check_other()
        # self._set_all_end_flag()
        logger.info('stop %s...' % sys._getframe().f_code.co_name)

    def check_web(self):
        logger.info('start %s...' % sys._getframe().f_code.co_name)
        script_name = 'begin_check_web.sh'
        self._set_begin_flag('web')
        script = os.path.join(self.scripts_path, script_name)
        status, stdout = subprocess.getstatusoutput(script)
        logger.debug('script: %s, status: %s, stdout: %s' % (script, status, stdout))
        self._set_end_flag('web')
        logger.info('stop %s...' % sys._getframe().f_code.co_name)

    def check_platform(self):
        logger.info('start %s...' % sys._getframe().f_code.co_name)
        script_name = 'begin_check_platform.sh'
        self._set_begin_flag('platform')
        script = os.path.join(self.scripts_path, script_name)
        status, stdout = subprocess.getstatusoutput(script)
        logger.debug('script: %s, status: %s, stdout: %s' % (script, status, stdout))
        self._set_end_flag('platform')
        logger.info('stop %s...' % sys._getframe().f_code.co_name)

    def check_midware(self):
        logger.info('start %s...' % sys._getframe().f_code.co_name)
        script_name = 'begin_check_midware.sh'
        self._set_begin_flag('midware')
        script = os.path.join(self.scripts_path, script_name)
        status, stdout = subprocess.getstatusoutput(script)
        logger.debug('script: %s, status: %s, stdout: %s' % (script, status, stdout))
        self._set_end_flag('midware')
        logger.info('stop %s...' % sys._getframe().f_code.co_name)

    def check_other(self):
        logger.info('start %s...' % sys._getframe().f_code.co_name)
        script_name = 'begin_check_other.sh'
        self._set_begin_flag('other')
        script = os.path.join(self.scripts_path, script_name)
        status, stdout = subprocess.getstatusoutput(script)
        logger.debug('script: %s, status: %s, stdout: %s' % (script, status, stdout))
        self._set_end_flag('other')
        logger.info('stop %s...' % sys._getframe().f_code.co_name)

    def get_log(self, check_type, section):
        log = ''
        log_length = -1
        log_file = os.path.join(self.log_path, check_type, '%s.log' % section)
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                log = f.read(log_length)

        return log

    def get_result(self, check_type):
        logger.info('start %s...' % sys._getframe().f_code.co_name)

        log_length = 800

        result_file = os.path.join(self.data_path, '%s.ini' % check_type)
        # logger.debug(result_file)
        config = self._get_config()
        config.clear()
        config.read(result_file)

        is_complete = self._get_flag(check_type)
        end_time = self._get_check_end_time()
        result = {
            'end_time': end_time,
            'check_type': check_type,
            'is_complete': 0 if is_complete == 'begin' else 1,  # 完成：1，未完成：0
            'status': 0,  # 检测结果 正常：0，不正常：1
            'info': []
        }

        for section in config.sections():
            if config.has_option(section, 'status'):
                status = config.getint(section, 'status')
                info = {section: {'status': status, 'err_info': [], 'check_method': [], 'log': '', 'detail': {}}}
                result['info'].append(info)
                for option in config.options(section):
                    if 'err_info' in option:
                        info[section]['err_info'].append(config.get(section, option).replace('\t', ' '))
                    elif 'check_method' in option:
                        info[section]['check_method'].append(config.get(section, option))
                    elif option != 'status':
                        info[section]['detail'].update({option: config.get(section, option)})
                if status == 1:
                    result['status'] = 1
                    log_file = os.path.join(self.log_path, check_type, '%s.log' % section)
                    # logger.debug(log_file)
                    if os.path.exists(log_file):
                        with open(log_file, 'r', encoding='utf-8') as f:
                            info[section]['log'] = f.read(log_length)

        logger.info('stop %s...' % sys._getframe().f_code.co_name)

        return result

    def get_all_result(self):
        logger.info('start %s...' % sys._getframe().f_code.co_name)
        try:
            results = [self.get_result(check_type) for check_type in self.all_check_type]
        except Exception as e:
            err = str(e)
            logger.error(err)
            results = []
        logger.info('stop %s...' % sys._getframe().f_code.co_name)

        return results


def query_mt_addr(mts_e164):
    '''
    通过终端e164号码查询终端本机的ip地址
    :param mts_e164: 终端号码列表: list
    :return: {mt_e164: {mt_info}}
    '''
    dsl = copy.deepcopy(es_ql.mt_info)
    mt_e164_filter = [{"match_phrase": {"source.e164": mt_e164}} for mt_e164 in mts_e164]
    dsl['dsl']['query']['bool']['should'] = mt_e164_filter
    dsl['dsl']['query']['bool']['minimum_should_match'] = 1
    dsls = [dsl]

    m_body = es_client.get_index_header_m_body(*dsls)
    logger.info(m_body)
    try:
        responses = es_client.msearch(m_body)['responses']
    except Exception as e:
        logger.exception(e)
        raise OpsException(code='10002')
    else:
        mt_info_response = responses[0]

        info_data = {}
        mt_e164_buckets = jsonpath.jsonpath(mt_info_response, '$..mt_e164.buckets')
        mt_e164_buckets = mt_e164_buckets[0] if mt_e164_buckets else []

        for mt_e164_bucket in mt_e164_buckets:
            mt_e164_key = mt_e164_bucket.get('key')
            mt_info = jsonpath.jsonpath(mt_e164_bucket, '$.._source.source')
            mt_info = mt_info[0] if mt_info else {}

            info_data.update({mt_e164_key: mt_info})

        logger.debug(info_data)
        return info_data
