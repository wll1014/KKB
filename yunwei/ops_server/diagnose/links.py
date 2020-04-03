#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
链路检测

H323 协议：
根据主被叫和info中 setup 查询 guid

根据guid,proto=h225 查询数据，根据src，port 确定 模块数画图
详细信息根据guid查询数据返回
"""

from abc import ABCMeta, abstractmethod

import http.cookiejar
import json
import jsonpath
import logging
import multiprocessing
import time
from urllib import request
from urllib.parse import urlencode
from django.db import connections

from diagnose.models import LinkCheckerModel
from common.global_func import get_conf
from common.es_client import es_client
from common.timeFormatConverter import utcstr2localstr
from common.platform_errorcode import PLATFORM_ERROR
from common.my_elastic import ESIndex
from common.my_exception import OpsException
from common.conf_params_enum import MtProtocol

logger = logging.getLogger('ops.' + __name__)


class CallLinkCallIDAbstract(metaclass=ABCMeta):
    """
    获取呼叫ID
    """

    @abstractmethod
    def get_call_id(self, *args, **kwargs):
        pass


class CallLinkCallIDMethodsAbstract(metaclass=ABCMeta):
    """
    获取单个呼叫ID的呼叫类型
    """

    @abstractmethod
    def get_call_id_methods(self, *args, **kwargs):
        pass


class CallLinkInformationAbstract(metaclass=ABCMeta):
    """
    获取呼叫链路节点及节点信息
    """

    @abstractmethod
    def get_call_link_info(self, *args, **kwargs):
        pass


class CallLinkAllMsgAbstract(metaclass=ABCMeta):
    """
    获取所有呼叫信息
    """

    @abstractmethod
    def get_all_call_msg(self, *args, **kwargs):
        pass


class SimulateCreateConf:
    """
    create a conf with the given params
    a user account and password is needed
    the conf_name is random
    """
    _conf_name_length = 23
    _account_token_url = "http://{}/api/v1/system/token"
    _login_url = "http://{}/api/v1/system/login"
    _create_meeting_url = "http://{}/api/v1/mc/confs"
    _delete_meeting_url = "http://{}/api/v1/mc/confs/{}"

    oauth_consumer_key = "TrueLink"
    oauth_consumer_secret = "12345678"

    def __init__(self, mt_moid, user, password, login_host, task_id):
        logger.info("init link_checker:{}".format(task_id))
        logger.info("moid:{}".format(mt_moid))
        logger.info("user:{}".format(user))
        logger.info("host:{}".format(login_host))
        try:
            self.task_id = task_id
            self.task_obj = LinkCheckerModel.objects.get(task_id=task_id)
            self.mt_moid = mt_moid
            self.user_account = user
            self.host = login_host
            self.user_password = password
            self.conf_name = self.generate_conf_name()
            self.account_token_url = self._account_token_url.format(login_host)
            self.login_url = self._login_url.format(login_host)
            self.create_meeting_url = self._create_meeting_url.format(login_host)
            self.create_time = None
            self.opener = None
        except Exception as err:
            logger.error(err)
            end_time = int(time.time() * 1000)
            conf_status = "init failed"
            conf_error = "任务初始化失败"
            is_complete = 1
            data = dict(conf_error=conf_error, conf_status=conf_status, end_time=end_time, is_complete=is_complete)
            self.save_data(**data)
            raise ValueError("链路检查任务初始化失败")

    def generate_conf_name(self):
        """
        :return: str
        """
        return "test_{}_createmeeting".format(self.task_id)

    def process_platform_err_response(self, platform_response, addition_msg=None):
        """
        :type platform_response: dict
        :type addition_msg: str
        :return:
        """
        plat_error_code = platform_response.get("error_code")
        if plat_error_code is None:
            msg = str(platform_response)
        else:
            msg = PLATFORM_ERROR.get(str(plat_error_code), str(platform_response))
        if addition_msg is None:
            return False, msg
        else:
            return False, addition_msg + msg

    def get_account_token(self):
        """
        get account token
        :return: tuple : (True/False, token/err)
        """
        post_data = urlencode({"oauth_consumer_key": self.oauth_consumer_key,
                               "oauth_consumer_secret": self.oauth_consumer_secret}).encode('utf-8')
        header = {"Content-Type": "application/x-www-form-urlencoded"}

        req_account_token = request.Request(self.account_token_url, post_data, header)

        try:
            account_token_response = request.urlopen(req_account_token, timeout=3).read().decode('utf-8')
        except Exception as err:
            logger.error(err)
            return False, "获取Token出错:" + str(err.args)
        else:
            account_token_response = json.loads(account_token_response)

        is_success = account_token_response.get("success")
        if is_success == 1:
            return True, account_token_response.get("account_token")
        else:
            return self.process_platform_err_response(account_token_response, addition_msg="获取Token失败:")

    def login(self, account_token):
        # 获取保存cookies
        post_data_cookie = urlencode({"password": self.user_password,
                                      "username": self.user_account,
                                      "account_token": account_token}).encode('utf-8')

        # cookie = http.cookiejar.MozillaCookieJar(cookie_filename)
        cookie = http.cookiejar.CookieJar()
        self.opener = request.build_opener(request.HTTPCookieProcessor(cookie))
        try:
            login_response = self.opener.open(self.login_url, post_data_cookie, timeout=3).read().decode('utf-8')
        except Exception as err:
            logger.error(err)
            return False, "用户登陆出错:" + str(err.args)

        is_success = json.loads(login_response).get("success")
        if is_success != 1:
            # 登陆失败
            return self.process_platform_err_response(login_response, addition_msg="用户登陆失败:")
        else:
            return True,

    def get_meeting_tem_params(self):
        meeting_tem_params = {
            "name": self.conf_name,
            "conf_type": 0,
            "create_type": 1,
            "duration": 2,
            "bitrate": 720,
            "closed_conf": 0,
            "safe_conf": 0,
            "encrypted_type": 0,
            "encrypted_auth": 0,
            "call_times": 4,
            "call_mode": 2,
            "call_interval": 13,
            "password": "",
            "mute": 0,
            "silence": 0,
            "video_quality": 0,
            "dual_mode": 1,
            "voice_activity_detection": 0,
            "vacinterval": 0,
            "cascade_mode": 1,
            "cascade_upload": 1,
            "cascade_return": 0,
            "cascade_return_para": 0,
            "public_conf": 0,
            "vmp_enable": 0,
            "mix_enable": 1,
            "poll_enable": 0,
            "invited_mt_num": 1,
            "max_join_mt": 8,
            "creator": {
                "account": self.mt_moid,
                "account_type": 1
            },
            "chairman": {
                "account": self.mt_moid,
                "account_type": 1
            },
            "video_formats": [
                {
                    "format": 5,
                    "resolution": 12,
                    "frame": 30,
                    "bitrate": 1024
                },
                {
                    "format": 0,
                    "resolution": 0,
                    "frame": 0,
                    "bitrate": 0
                },
                {
                    "format": 0,
                    "resolution": 0,
                    "frame": 0,
                    "bitrate": 0
                },
                {
                    "format": 0,
                    "resolution": 0,
                    "frame": 0,
                    "bitrate": 0
                }
            ],
            "one_reforming": 0,
            "auto_end": 1,
            "preoccpuy_resource": 1,
            "mute_filter": 0,
            "fec_mode": 0,
            "doubleflow": 0
        }
        meeting_mt_tem_params = {
            "keep_calling_members": [
                {
                    "account": "{}".format(self.task_obj.mt_id),
                    "account_type": 5
                }
            ],
            "invite_members": [
                {

                    "account": "{}".format(self.task_obj.mt_id),
                    "account_type": 5,
                    "protocol": 1
                }
            ]
        }
        if self.task_obj.link_type == 1:
            # conf_type link
            return json.dumps(meeting_tem_params)
        else:
            # call_type link
            meeting_tem_params.update(meeting_mt_tem_params)
            return json.dumps(meeting_tem_params)

    def _create_conf(self, account_token):
        """
        # 创会
        :param account_token: str
        :return: tuple true/false, conf_id/err
        """
        meeting_tem_params = self.get_meeting_tem_params()
        post_data_create_meeting = urlencode({
            "account_token": account_token,
            "params": meeting_tem_params}).encode('utf-8')

        try:
            create_response = self.opener.open(self.create_meeting_url, post_data_create_meeting,
                                               timeout=100).read().decode('utf-8')
        except Exception as err:
            logger.error(str(err))
            return False, str(err.args)
        else:
            # check create response
            create_response = json.loads(create_response)
            is_create_success = create_response.get("success")
            if is_create_success != 1:
                # create failed
                return self.process_platform_err_response(create_response, addition_msg="API创会失败:")
            else:
                # create success
                conf_id = create_response.get('conf_id')
                return True, conf_id

    def _delete_conf(self, conf_id, account_token):
        """
        delete conf
        :param conf_id:
        :return:
        """
        delete_meeting_url = self._delete_meeting_url.format(self.host, conf_id)
        post_data_delete_meeting = urlencode({
            "_method": "DELETE",
            "account_token": account_token}).encode('utf-8')
        try:
            delete_meeting_response = self.opener.open(delete_meeting_url, post_data_delete_meeting,
                                                       timeout=100).read().decode('utf-8')
        except Exception as err:
            logger.error("结会失败: %s" % conf_id)
            logger.error(str(err))
            return False
            # other operation ????????????????????
        else:
            is_delete_success = json.loads(delete_meeting_response).get("success")
            if is_delete_success != 1:
                logger.error("结会失败: %s" % conf_id + str(delete_meeting_response))
                return False
            else:
                return True

    def save_data(self, **data):
        try:
            connections.close_all()
            LinkCheckerModel.objects.filter(task_id=self.task_id).update(**data)
        except Exception as err:
            logger.error(str(err))

    def create_conf(self):
        """
        create a testing conf with the CMC API, if success, delete the conf, otherwise return the conf_name.
        :return: None
        """
        logger.info("begin createconf")
        # 关闭 uwsgi 连接的文件描述符， 解决 子进程运行过程中 前端 继续get请求阻塞问题
        import uwsgi
        fd = uwsgi.connection_fd()
        uwsgi.close(fd)

        self.create_time = int(time.time() * 1000)
        data = dict(conf_status='creating', start_time=self.create_time, conf_name=self.conf_name)
        self.save_data(**data)

        logger.info("begin access account_token")
        token_stat, account_token = self.get_account_token()
        if not token_stat:
            # get account_token failed
            logger.info("access account_token failed")
            end_time = int(time.time() * 1000)
            conf_status = "failed"
            conf_error = account_token
            is_complete = 1
            data = dict(end_time=end_time, conf_status=conf_status, conf_error=conf_error, is_complete=is_complete)
            self.save_data(**data)
            exit()
        logger.info("access account_token success")

        logger.info("begin login")
        login_stat = self.login(account_token)
        if not login_stat[0]:
            # login failed
            logger.info("login failed")
            end_time = int(time.time() * 1000)
            conf_status = "failed"
            conf_error = login_stat[1]
            is_complete = 1
            data = dict(end_time=end_time, conf_status=conf_status, conf_error=conf_error, is_complete=is_complete)
            self.save_data(**data)
            exit()
        logger.info("login success")

        logger.info("begin create conf")
        create_stat, conf = self._create_conf(account_token)
        if not create_stat:
            logger.info("create conf failed")
            # create failed
            conf_status = "failed"
            conf_error = conf
            data = dict(conf_status=conf_status, conf_error=conf_error)
            self.save_data(**data)

            if self.task_obj.link_type == 2:
                logger.info("begin sleeping...")
                time.sleep(60)

            end_time = int(time.time() * 1000)
            is_complete = 1
            data = dict(end_time=end_time, is_complete=is_complete)
            self.save_data(**data)
            logger.info("task complete, bye...")
            exit()
        else:
            logger.info("create conf success")
            conf_status = "created"
            conf_id = conf
            data = dict(conf_status=conf_status, conf_id=conf_id)
            self.save_data(**data)

            if self.task_obj.link_type == 2:
                logger.info("begin sleeping...")
                time.sleep(60)

            end_time = int(time.time() * 1000)
            is_complete = 1
            data = dict(end_time=end_time, is_complete=is_complete)
            self.save_data(**data)

            logger.info("begin stop conf")
            del_stat = self._delete_conf(conf, account_token)
            if not del_stat:
                logger.error('stop conf failed: %s' % conf)
            else:
                logger.info('stop conf success: %s' % conf)

            logger.info("task complete, bye...")
            exit()


class CreateConf(multiprocessing.Process):
    """
    create a thread to check the given task
    a django_db orm instance and the task password is needed
    """

    def __init__(self, user, password, task_id):
        super().__init__()
        self.password = password
        self.task_id = task_id
        self.user = user

    def get_host(self):
        """
        获取创会请求主机IP
        :return:
        """
        return get_conf('elasticsearch', 'hosts')

    def get_mt_id(self):
        """
        通过输入的账号查询 终端的moid
        匹配 acount/email/e164/mobile 四个字段
        :return: moid or None
        """
        with connections['movision'].cursor() as cursor:
            sql = "SELECT md.moid FROM ( SELECT moid, CONCAT_WS( '#', account, email, e164, mobile, '#' ) AS filter FROM user_info WHERE binded='0' ) AS md WHERE md.filter LIKE '%{}#%'".format(
                self.user)
            cursor.execute(sql)
            sql_result = cursor.fetchall()
        moid = [x[0] for x in sql_result]
        moid = moid[0] if len(moid) != 0 else None
        assert moid is not None, "用户不存在"
        return moid

    def run(self):
        try:
            connections.close_all()
            host = self.get_host()
            mt_moid = self.get_mt_id()
            create = SimulateCreateConf(mt_moid, self.user, self.password, host, self.task_id)
            create.create_conf()
        except AssertionError as err:
            logger.error(str(err))

            end_time = int(time.time() * 1000)
            conf_status = "prepare failed"
            conf_error = str(err.args)
            is_complete = 1
            need_del = 1
            data = dict(conf_error=conf_error, conf_status=conf_status, end_time=end_time, is_complete=is_complete,
                        need_del=need_del)
            LinkCheckerModel.objects.filter(task_id=self.task_id).update(**data)
        except Exception as err:
            logger.error(str(err))

            end_time = int(time.time() * 1000)
            conf_status = "other failed"
            conf_error = "未知错误:{}".format(str(err.args))
            is_complete = 1
            need_del = 1
            data = dict(conf_error=conf_error, conf_status=conf_status, end_time=end_time, is_complete=is_complete,
                        need_del=need_del)
            LinkCheckerModel.objects.filter(task_id=self.task_id).update(**data)


class ConfLinkChecker:
    """
    handle conf link
    """
    mq_messages = ['CM_MAU_CREATECONF_REQ', 'MAU_CM_CREATECONF_NACK', 'MAU_CM_CREATECONF_ACK', 'CSS_RMS_APPLYRES_REQ',
                   'RMS_CSS_APPLYRES_ACK', 'RMS_CSS_APPLYRES_NACK', 'MAU_MCU_CREATECONF_REQ', 'MCU_MAU_CREATECONF_ACK',
                   'MCU_MAU_CREATECONF_NACK']

    mq_msg_desc = {
        "CM_MAU_CREATECONF_REQ": '创会请求',
        "MAU_CM_CREATECONF_NACK": "创会失败",
        "MAU_CM_CREATECONF_ACK": "创会成功",
        "CSS_RMS_APPLYRES_REQ": "分配资源",
        "RMS_CSS_APPLYRES_ACK": "分配资源成功",
        "RMS_CSS_APPLYRES_NACK": "分配资源失败",
        "MAU_MCU_CREATECONF_REQ": "分配Mcu",
        "MCU_MAU_CREATECONF_ACK": "分配Mcu成功",
        "MCU_MAU_CREATECONF_NACK": "分配Mcu失败"
    }

    mq_msg_point_des = {'CM': 'CMC', 'MAU': 'CSS', 'CSS': 'CSS', 'RMS': 'RMS', 'MCU': 'CMU'}

    points = ["CMC", "CSS", "RMS", "CMU"]

    def __init__(self, conf, conf_tp, start_time, end_time):
        """
        :param conf: str conf_id/conf_name
        :param conf_tp: str  'id'/'name'
        :param start_time:
        :param end_time:
        """
        if conf_tp == 'id':
            self.conf_id = conf
            self.conf_name = None
        elif conf_tp == 'name':
            self.conf_id = None
            self.conf_name = conf
        else:
            raise ValueError('params err: conf_tp')
        self.start_time = start_time
        self.end_time = end_time

    def query_conf_id(self):
        """
        query conf_id with the conf_name from RMQ message CM_MAU_CREATECONF_REQ
        :return: tuple true/false,conf_id/err
        """
        dsl = {"size": 1, "_source": "source.confE164", "query": {"bool": {
            "must": [{"match": {"source.type": "CM_MAU_CREATECONF_REQ"}}, {"match": {"source.confname": "kf1的会议"}}],
            "filter": {"range": {"@timestamp": {"gte": 1568194881425, "lte": 1568195001425}}}}},
               "sort": [{"@timestamp": {"order": "asc"}}]}

        must_block = dsl['query']['bool']['must']
        for item in must_block[::-1]:
            if 'source.confname' in item['match']:
                must_block.remove(item)
                break

        must_block.append({"match": {"source.confname": "{}".format(self.conf_name)}})
        dsl['query']['bool']['must'] = must_block
        # query time in two minutes
        dsl['query']['bool']['filter']['range']['@timestamp'] = {"gte": self.start_time, "lte": self.end_time}

        es = es_client()
        index = "mqwatcher-*"
        try:
            results = es.search(index=index, dsl=dsl)
        except Exception as err:
            logger.error(err)
            return False, "查询会议号码出错:" + str(err.args)
        else:
            conf_id = jsonpath.jsonpath(results, '$..source.confE164')
            if conf_id is False:
                return True, None
            else:
                return True, conf_id[0]

    def query_mq_msgs(self):
        """
        query mq messages from es with conf_id
        :return:
        """
        if self.conf_id is None:
            raise ValueError("conf_id is None")
        dsl = {"query": {"bool": {"must": [{"match": {"source.confE164": "6660109"}}, {"match": {
            "source.type": "CM_MAU_CREATECONF_REQ MAU_CM_CREATECONF_NACK MAU_CM_CREATECONF_ACK CSS_RMS_APPLYRES_REQ RMS_CSS_APPLYRES_ACK RMS_CSS_APPLYRES_NACK MAU_MCU_CREATECONF_REQ MCU_MAU_CREATECONF_ACK MCU_MAU_CREATECONF_NACK"}}],
                                  "filter": {"range": {"@timestamp": {"gte": 1568772604316, "lte": 1568772605169}}}}},
               "collapse": {"field": "source.type.keyword"}, "sort": [{"@timestamp": {"order": "asc"}}], "from": 0}

        must_block = dsl['query']['bool']['must']
        for item in must_block[::-1]:
            if 'source.confE164' in item['match']:
                must_block.remove(item)
                continue
            if 'source.type' in item['match']:
                must_block.remove(item)
                continue

        must_block.append({"match": {"source.confE164": "{}".format(self.conf_id)}})
        must_block.append({"match": {"source.type": "{}".format(" ".join(self.mq_messages))}})

        dsl['query']['bool']['must'] = must_block
        # query time in two minutes
        dsl['query']['bool']['filter']['range']['@timestamp'] = {"gte": self.start_time, "lte": self.end_time}

        es = es_client()
        index = "mqwatcher-*"
        try:
            results = es.search(index=index, dsl=dsl)
        except Exception as err:
            logger.error(err)
            return False, "查询MQ消息出错:" + str(err.args)
        else:
            results = results['hits']['hits']
            if len(results) == 0:
                return True, []
            return True, results

    def filter_extra_info(self, msg, data):
        """
        :param msg:
        :param data:
        :return:
        """
        if msg == 'CM_MAU_CREATECONF_REQ':
            confname = jsonpath.jsonpath(data, '$..confname')
            confE164 = jsonpath.jsonpath(data, '$..confE164')
            moid = jsonpath.jsonpath(data, '$..moid')
            duration = jsonpath.jsonpath(data, '$..duration')
            createbymt = jsonpath.jsonpath(data, '$..createbymt')
            creatormoid = jsonpath.jsonpath(data, '$..creatormoid')
            isportconf = jsonpath.jsonpath(data, '$..isportconf')
            meetingID = jsonpath.jsonpath(data, '$..meetingID')
            creatorname = jsonpath.jsonpath(data, '$..creatorname')
            field = [confname, confE164, moid, duration, createbymt, creatormoid, isportconf, meetingID, creatorname]
            values = [x[0] if x is not False else "" for x in field]
            keys = ['confname', 'confE164', 'moid', 'duration', 'createbymt', 'creatormoid', 'isportconf', 'meetingID',
                    'creatorname']
        elif msg in ['RMS_CSS_APPLYRES_ACK', 'MAU_MCU_CREATECONF_REQ']:
            media_master = jsonpath.jsonpath(data, '$..media_master')
            pasroommoid = jsonpath.jsonpath(data, '$..pasroommoid')
            confroommoid = jsonpath.jsonpath(data, '$..confroommoid')
            dss_master = jsonpath.jsonpath(data, '$..dss_master')
            cmu = jsonpath.jsonpath(data, '$..cmu')
            field = [media_master, pasroommoid, confroommoid, dss_master, cmu]
            values = [x[0] if x is not False else "" for x in field]
            keys = ['media_master', 'pasroommoid', 'confroommoid', 'dss_master', 'cmu']
        elif msg == 'MCU_MAU_CREATECONF_ACK':
            pid = jsonpath.jsonpath(data, '$..pid')
            ip = jsonpath.jsonpath(data, '$..ip')
            cmumoid = jsonpath.jsonpath(data, '$..cmumoid')
            starttime = jsonpath.jsonpath(data, '$..starttime')
            endtime = jsonpath.jsonpath(data, '$..endtime')
            confE164 = jsonpath.jsonpath(data, '$..confE164')
            confid = jsonpath.jsonpath(data, '$..confid')
            field = [pid, ip, cmumoid, starttime, endtime, confE164, confid]
            values = [x[0] if x is not False else "" for x in field]
            keys = ['pid', 'ip', 'cmumoid', 'starttime', 'endtime', 'confE164', 'confid']
        else:
            source = jsonpath.jsonpath(data, '$..source')
            field = [source]
            values = [x[0] if x is not False else "" for x in field]
            keys = ['source']

        info = dict(zip(keys, values))
        return info

    def checker(self):
        messages = self.query_mq_msgs()
        if not messages[0]:
            return messages
        else:
            messages = messages[1]

        info = []
        if len(messages) == 0:
            return True, [self.points, info]

        for message in messages:
            msg = jsonpath.jsonpath(message, '$..source.type')[0]
            t = jsonpath.jsonpath(message, '$..sort[0]')[0]

            msg_spt = msg.split('_')
            src = self.mq_msg_point_des.get(msg_spt[0])
            dst = self.mq_msg_point_des.get(msg_spt[1])
            stat = 0 if msg_spt[-1] == 'NACK' else 1
            desc = self.mq_msg_desc.get(msg)

            param_pri_keys = ["src", "dst", "status", "description", 'time', 'type']
            inf = dict(zip(param_pri_keys, [src, dst, stat, desc, t, msg]))

            #  other information
            data = self.filter_extra_info(msg, message)
            inf['data'] = data
            info.append(inf)
        return True, [self.points, info]

    def check(self):
        if self.conf_id is None:
            query_id = self.query_conf_id()
            if not query_id[0]:
                return self.points, []
            elif query_id[1] is None:
                return self.points, []
            else:
                self.conf_id = query_id[1]

        check_info = self.checker()
        if not check_info[0]:
            return self.points, []
        else:
            return check_info[1]


class SipCallLinkCallID(CallLinkCallIDAbstract):
    """
    query sip call_id
    """

    def __init__(self, mt_id, start_time, end_time, conf_id=""):
        self.start_time = start_time
        self.end_time = end_time
        self.mt_id = mt_id
        self.conf_id = conf_id

    def make_call_id_dsl(self):
        dsl = {"size": 0, "query": {"bool": {"filter": [{"terms": {"sip.method": ["INVITE", "ACK", "BYE"]}},
                                                        {"wildcard": {"sip.to": "<sip:%s@*" % self.mt_id}}]}}, "aggs": {
            "call_id": {"terms": {"field": "sip.headers.call-id", "size": 10000, "order": {"min_time": "desc"}},
                        "aggs": {"min_time": {"min": {"field": "@timestamp"}}}}}}

        if self.conf_id:
            pattern_conf = {"wildcard": {"sip.from": "*<sip:%s@*" % self.conf_id}}
            dsl['query']['bool']['filter'].append(pattern_conf)

        #  time
        time_ = {"range": {"@timestamp": {"gte": self.start_time, "lte": self.end_time}}},
        dsl['query']['bool']['filter'].append(time_)
        return dsl

    def get_call_id(self):
        """
        :return: list
        """
        dsl = self.make_call_id_dsl()
        index = ESIndex.SIPProtoIndex.value
        es = es_client()

        try:
            results = es.search(index=index, dsl=dsl)
        except Exception as err:
            logger.error(err.args)
            raise OpsException(code="10002")
        else:
            info = []
            if results['hits']['total'] == 0:
                return info
            for sig_id_info in results['aggregations']['call_id']['buckets']:
                call_id = jsonpath.jsonpath(sig_id_info, '$.key')
                call_min_time = jsonpath.jsonpath(sig_id_info, '$.min_time.value_as_string')

                if call_id is False or call_min_time is False:
                    continue
                else:
                    call_min_time = utcstr2localstr(call_min_time[0])
                    call_id = call_id[0]
                    info.append(dict(zip(['timestamp', 'id', "call_type"], [call_min_time, call_id, "sip"])))
            return info


class SipCallLinkCallIDMethods(CallLinkCallIDMethodsAbstract):
    """
    query sip call methods
    """

    def __init__(self, call_id, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time
        self.call_id = call_id

    def make_call_id_dsl(self):
        dsl = {"size": 0, "query": {"bool": {"filter": [
            {"range": {"@timestamp": {"gte": self.start_time, "lte": self.end_time}}},
            {"term": {"sip.call-id": self.call_id}}]}},
               "aggs": {"methods": {"terms": {"field": "sip.method", "size": 10000}}}}
        return dsl

    def get_call_id_methods(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return: list
        """
        dsl = self.make_call_id_dsl()
        index = ESIndex.SIPProtoIndex.value
        es = es_client()

        try:
            results = es.search(index=index, dsl=dsl)
        except Exception as err:
            logger.error(err.args)
            raise OpsException(code="10002")
        else:
            methods = jsonpath.jsonpath(results, '$.aggregations.methods..key')
            methods = methods if methods is not False else []
            return methods


class SipCallLinkInformation(CallLinkInformationAbstract):
    """
    call link detail information for sip
    """

    def __init__(self, call_id, start_time, end_time):
        self.call_id = call_id
        self.start_time = start_time
        self.end_time = end_time

    def query_modules(self):
        """
        :return: list
        """
        dsl = {"size": 0,
               "query": {"bool": {"must": [], "filter": {"range": {"@timestamp": {"gte": 10, "lte": "now"}}}}},
               "aggs": {"src": {"terms": {"field": "sip.src", "size": 10000}}}}

        pattern = {"match": {"sip.headers.call-id": self.call_id}}
        dsl['query']['bool']['must'].append(pattern)
        dsl['query']['bool']['filter']['range']["@timestamp"] = {"gte": self.start_time, "lte": self.end_time}

        index = ESIndex.SIPProtoIndex.value
        es = es_client()

        try:
            results = es.search(index=index, dsl=dsl)
        except Exception as err:
            logger.error(err.args)
            raise OpsException(code="10002")
        else:
            models = jsonpath.jsonpath(results, '$.aggregations..key')
            if models is False:
                return []
            else:
                models.sort(key=lambda x: int(x.split(":")[1]))

                # res = []
                for result in models[:]:
                    ip, port = result.split(':')
                    if port == '5090':
                        # agent
                        models.remove(result)
                        models.insert(0, result)
                        continue
                    elif port == "5060":
                        # proxy
                        models.remove(result)
                        models.insert(1, result)
                        continue
                    else:
                        # mt
                        models.remove(result)
                        models.append(result)
                        continue

                if models[0].split(':')[1] == "5090":
                    agent_ip = models[0].split(':')[0]
                    for tmp in models[1:-1]:
                        if tmp.split(':')[0] == agent_ip and tmp.split(':')[1] == '5060':
                            models.remove(tmp)
                            models.insert(1, tmp)
                            break
                    return models
                else:
                    # 没有agent
                    return models

    def make_sip_dsl(self):
        dsl = {"size": 10000,
               "_source": ["sip.method", "sip.raw", "sip.status-code", "sip.status-phrase", "sip.src", "sip.dst"],
               "query": {"bool": {"must": [], "should": [{"wildcard": {"sip.headers.cseq": {"value": "* INVITE"}}},
                                                         {"wildcard": {"sip.headers.cseq": {"value": "* ACK"}}},
                                                         {"wildcard": {"sip.headers.cseq": {"value": "* BYE"}}}],
                                  "minimum_should_match": 1,
                                  "filter": {"range": {"@timestamp": {"gte": 10, "lte": "now"}}}}},
               "sort": [{"@timestamp": {"order": "asc"}}]}

        pattern = {"match": {"sip.headers.call-id": self.call_id}}
        dsl['query']['bool']['must'].append(pattern)
        dsl['query']['bool']['filter']['range']["@timestamp"] = {"gte": self.start_time, "lte": self.end_time}
        return dsl

    def query_sip_info(self):
        dsl_ = self.make_sip_dsl()
        index = ESIndex.SIPProtoIndex.value
        es = es_client()

        try:
            results = es.search(index=index, dsl=dsl_)
        except Exception as err:
            logger.error(err.args)
            raise OpsException(code="10002")
        else:
            return results['hits']['hits']

    def get_call_link_info(self):
        """
        :return: list
        """
        modules = self.query_modules()

        if len(modules) == 0:
            return [[], []]

        # points_dict = {}
        # points_name = []

        # cur_porxy_num = 0
        # for module in modules:
        #     port = module.split(':')[1]
        #     if port == '5090':
        #         point_name = 'SipAgent({})'.format(module)
        #     elif port == '5060':
        #         point_name = 'SipPorxy({})'.format(module)
        #         # if porxy_num > 1:
        #         #     cur_porxy_num += 1
        #         #     point_name = 'SipPorxy_%s' % cur_porxy_num
        #         # else:
        #         #     point_name = 'SipPorxy'
        #     else:
        #         point_name = 'MT({})'.format(module)
        #
        #     points_name.append(point_name)
        #     points_dict[module] = point_name

        sip_info = self.query_sip_info()

        final_info = []
        for info in sip_info:  # type: dict
            keys = ['src', 'dst', 'status', 'description', 'time', 'raw']

            t = info['sort'][0]
            source = info['_source']

            sip_src = source.get('sip.src')
            sip_dst = source.get('sip.dst')
            sip_raw = source.get('sip.raw')

            sip_method = source.get('sip.method')
            sip_status_code = source.get('sip.status-code')
            sip_status_phrase = source.get('sip.status-phrase')

            src = sip_src
            dst = sip_dst
            if sip_method is not None:
                status = 1
                description = sip_method
            else:
                # 呼叫链路状态全部为正常
                status = 1
                # if sip_status_code == 200:
                #     status = 1
                # else:
                #     status = 0
                description = str(sip_status_code) + " " + str(sip_status_phrase)

            # convert sip.raw to dict from str
            sip_raw = sip_raw.split('\r\n')
            sip_raw = [x for x in sip_raw if x]

            cur_point_info = dict(zip(keys, [src, dst, status, description, t, sip_raw]))
            final_info.append(cur_point_info)
        return [modules, final_info]


class SipCallLinkAllMsg(CallLinkAllMsgAbstract):
    """
    call link all sip_info for single call_id
    """

    def __init__(self, call_id, start_time, end_time, start, count, method=None):
        self.start = start
        self.count = count
        self.call_id = call_id
        self.start_time = start_time
        self.end_time = end_time
        self.call_method = method

    def make_sip_dsl(self):
        dsl = {"from": 1, "size": 2, "_source": ["sip.headers.cseq", "sip.raw", "sip.src", "sip.dst"],
               "query": {"bool": {"must": [], "filter": {"range": {"@timestamp": {"gte": 10, "lte": "now"}}}}},
               "sort": [{"@timestamp": {"order": "asc"}}]}

        pattern = {"match": {"sip.headers.call-id": self.call_id}}
        if self.call_method:
            method = {"wildcard": {"sip.headers.cseq": {"value": "* {}".format(self.call_method)}}}
            dsl['query']['bool']['must'].append(method)
        dsl['query']['bool']['must'].append(pattern)
        dsl['query']['bool']['filter']['range']["@timestamp"] = {"gte": self.start_time, "lte": self.end_time}
        dsl['from'] = self.start
        dsl['size'] = self.count
        return dsl

    def get_all_call_msg(self):
        dsl = self.make_sip_dsl()
        index = ESIndex.SIPProtoIndex.value
        es = es_client()

        try:
            results = es.search(index=index, dsl=dsl)
        except Exception as err:
            logger.error(err.args)
            raise OpsException(code="10002")
        else:
            total = results['hits']['total']
            results = results['hits']['hits']

        keys = ['src', 'dst', 'cseq', 'time', 'raw']
        final_info = []
        for result in results:
            try:
                t = result['sort'][0]
                source = result['_source']

                sip_src = source.get('sip.src')
                sip_dst = source.get('sip.dst')
                sip_cseq = source['sip.headers']['cseq'][0]
                sip_raw = source.get('sip.raw')
            except Exception as err:
                logger.error(err.args)
                continue
            cur_info = dict(zip(keys, [sip_src, sip_dst, sip_cseq, t, sip_raw]))
            final_info.append(cur_info)

        return [total, final_info]


class H323CallLinkCallID(CallLinkCallIDAbstract):
    """
    query h323 guid
    """

    def __init__(self, mt_id, start_time, end_time, conf_id=""):
        self.start_time = start_time
        self.end_time = end_time
        self.mt_id = mt_id
        self.conf_id = conf_id

    def make_call_id_dsl(self):
        dsl_ = {"size": 0, "query": {"bool": {"filter": [{"term": {"dialledDigits.dst.keyword": self.mt_id}},
                                                         {"term": {"info.keyword": "CS: setup "}}]}},
                "aggs": {"guid": {"terms": {"field": "guid.keyword", "size": 10000},
                                  "aggs": {"min_time": {"min": {"field": "@timestamp"}}}}}}

        if self.conf_id:
            pattern_conf = {"term": {"dialledDigits.src.keyword": self.conf_id}}
            dsl_['query']['bool']['filter'].append(pattern_conf)

        # time
        time_ = {"range": {"@timestamp": {"gte": self.start_time, "lte": self.end_time}}}
        dsl_['query']['bool']['filter'].append(time_)
        return dsl_

    def get_call_id(self, *args, **kwargs):
        """
        :return: list
        """
        dsl = self.make_call_id_dsl()
        index = ESIndex.H323ProtoIndex.value
        es = es_client()

        try:
            results = es.search(index=index, dsl=dsl)
        except Exception as err:
            logger.error(err.args)
            raise OpsException(code="10002")
        else:
            info = []
            if results['hits']['total'] == 0:
                return info
            for sig_id_info in results['aggregations']['guid']['buckets']:
                guid = jsonpath.jsonpath(sig_id_info, '$.key')
                call_min_time = jsonpath.jsonpath(sig_id_info, '$.min_time.value_as_string')

                if guid is False or call_min_time is False:
                    continue
                else:
                    call_min_time = utcstr2localstr(call_min_time[0])
                    guid = guid[0]
                    info.append(dict(zip(['timestamp', 'id', "call_type"], [call_min_time, guid, "h323"])))
            return info


class H323CallLinkCallIDMethods(CallLinkCallIDMethodsAbstract):
    """
    query h323 call methods for guid

    H323协议暂不支持筛选 呼叫类型
    """

    def __init__(self, guid, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time
        self.guid = guid

    def get_call_id_methods(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return: list
        """
        pass


class H323CallLinkInformation(CallLinkInformationAbstract):
    """
    call link detail information for h323
    """

    def __init__(self, guid, start_time, end_time):
        self.guid = guid
        self.start_time = start_time
        self.end_time = end_time

    def query_modules(self):
        """
        :return: list
        """
        dsl_ = {"size": 0, "query": {"bool": {
            "filter": [{"term": {"guid.keyword": self.guid}},
                       {"term": {"proto.keyword": "H.225.0"}},
                       {"range": {"@timestamp": {"gte": self.start_time, "lte": self.end_time}}}]}},
                "aggs": {"models": {
                    "terms": {"script": "doc['src.ip.keyword'].value + ':' + doc['src.port.keyword'].value",
                              "size": 10000}}}}

        index = ESIndex.H323ProtoIndex.value
        es = es_client()

        try:
            results = es.search(index=index, dsl=dsl_)
        except Exception as err:
            logger.error(err.args)
            raise OpsException(code="10002")
        else:
            models = jsonpath.jsonpath(results, '$.aggregations..key')
            if models is False:
                return []
            else:
                return models

    def make_h323_dsl(self):
        dsl = {"size": 10000,
               "_source": ["src", "dst", "info", "source"],
               "query": {"bool": {
                   "filter": [{"term": {"guid.keyword": self.guid}},
                              {"term": {"proto.keyword": "H.225.0"}},
                              {"range": {"timestamp": {"gte": self.start_time, "lte": self.end_time}}}]}},
               "sort": [{"timestamp": {"order": "asc"}}]}
        return dsl

    def query_h323_info(self):
        dsl = self.make_h323_dsl()
        index = ESIndex.H323ProtoIndex.value
        es = es_client()

        try:
            results = es.search(index=index, dsl=dsl)
        except Exception as err:
            logger.error(err.args)
            raise OpsException(code="10002")
        else:
            return results['hits']['hits']

    def get_call_link_info(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return: list
        """
        modules = self.query_modules()
        if len(modules) == 0:
            return [[], []]

        h323_info = self.query_h323_info()

        final_info = []
        for info in h323_info:  # type: dict
            keys = ['src', 'dst', 'status', 'description', 'time', 'raw']

            status = 1
            t = info['sort'][0]
            source = info['_source']

            src = source["src"]["ip"] + ":" + source["src"]["port"]
            dst = source["dst"]["ip"] + ":" + source["dst"]["port"]

            description = source.get("info")
            raw = source.get('source')

            cur_point_info = dict(zip(keys, [src, dst, status, description, t, raw]))
            final_info.append(cur_point_info)
        return [modules, final_info]


class H323CallLinkAllMsg(CallLinkAllMsgAbstract):
    """
    call link all h323_info for single guid
    """

    def __init__(self, guid, start_time, end_time, start, count, method=None):
        self.start = start
        self.count = count
        self.guid = guid
        self.start_time = start_time
        self.end_time = end_time
        # self.call_method = method

    def make_h323_dsl(self):
        dsl = {"from": self.start,
               "size": self.count,
               "_source": ["src", "dst", "info", "source"],
               "query": {"bool": {
                   "filter": [{"term": {"guid.keyword": self.guid}},
                              {"range": {"timestamp": {"gte": self.start_time, "lte": self.end_time}}}]}},
               "sort": [{"timestamp": {"order": "asc"}}]}
        return dsl

    def get_all_call_msg(self):
        """
        :return: list
        """
        dsl = self.make_h323_dsl()
        index = ESIndex.H323ProtoIndex.value
        es = es_client()

        try:
            results = es.search(index=index, dsl=dsl)
        except Exception as err:
            logger.error(err.args)
            raise OpsException(code="10002")
        else:
            total = results['hits']['total']
            results = results['hits']['hits']

        keys = ['src', 'dst', 'cseq', 'time', 'raw']
        final_info = []
        for result in results:
            try:
                t = result['sort'][0]
                source = result['_source']

                src = source["src"]["ip"] + ":" + source["src"]["port"]
                dst = source["dst"]["ip"] + ":" + source["dst"]["port"]
                cseq = source["info"]
                raw = source.get("source")
            except Exception as err:
                logger.error(err.args)
                continue
            cur_info = dict(zip(keys, [src, dst, cseq, t, raw]))
            final_info.append(cur_info)

        return [total, final_info]


class CallLinkFunctionsAdapter:

    @staticmethod
    def get_call_id(mt_id, start_time, end_time, conf_id="", *args, **kwargs):
        """
        查询呼叫 ID
        sip为call_id
        h323为guid
        :return: list
        """
        sip_call_id = SipCallLinkCallID(mt_id, start_time, end_time, conf_id).get_call_id()
        h323_call_id = H323CallLinkCallID(mt_id, start_time, end_time, conf_id).get_call_id()
        sip_call_id.extend(h323_call_id)
        return sip_call_id

    @staticmethod
    def get_call_id_methods(call_type, call_id, start_time, end_time, *args, **kwargs):
        """
        查询呼叫id的呼叫 类型

        还h323协议暂时不查询呼叫类型

        :param end_time:
        :param start_time:
        :param call_id: 呼叫ID
        :param call_type: 呼叫协议类型  sip/h323
        :return: list
        """
        if call_type == MtProtocol.H323.name.lower():
            return []
        elif call_type == MtProtocol.SIP.name.lower():
            call_methods = SipCallLinkCallIDMethods(call_id, start_time, end_time).get_call_id_methods()
        else:
            raise OpsException(code="30002")
        return call_methods

    @staticmethod
    def get_call_link_info(call_type, call_id, start_time, end_time, *args, **kwargs):
        """
        查询呼叫链路 用于画图
        :param end_time:
        :param start_time:
        :param call_id: 呼叫ID
        :param call_type: 呼叫协议类型  sip/h323
        :param args:
        :param kwargs:
        :return: list
        """
        if call_type == MtProtocol.SIP.name.lower():
            primary_info = SipCallLinkInformation(call_id, start_time, end_time).get_call_link_info()
        elif call_type == MtProtocol.H323.name.lower():
            primary_info = H323CallLinkInformation(call_id, start_time, end_time).get_call_link_info()
        else:
            raise OpsException(code="30002")
        return primary_info

    @staticmethod
    def get_all_call_msg(call_type, call_id, start_time, end_time, start=0, count=20, method=None, *args, **kwargs):
        """
        查询呼叫链路所有消息
        :param call_id: 呼叫ID
        :param start_time:
        :param end_time:
        :param start:
        :param count:
        :param method:
        :param call_type: 呼叫协议类型  sip/h323
        :param args:
        :param kwargs:
        :return: list
        """
        if call_type == MtProtocol.SIP.name.lower():
            all_msgs = SipCallLinkAllMsg(call_id, start_time, end_time, start, count, method).get_all_call_msg()
        elif call_type == MtProtocol.H323.name.lower():
            all_msgs = H323CallLinkAllMsg(call_id, start_time, end_time, start, count, method).get_all_call_msg()
        else:
            raise OpsException(code="30002")
        return all_msgs
