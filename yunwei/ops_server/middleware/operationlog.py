"""
记录操作日志
只处理 增删改
"""
import re
import json
import logging
from django.db import transaction, connection
from oplog.views import OperationLogSerializers

logger = logging.getLogger('ops.' + __name__)

faq = {'classes/': 'FAQ问题分类', 'classes/\d+/': 'FAQ问题分类', "": 'FAQ问答记录', "\d+/": 'FAQ问答记录'}
maintenance = {"": '维护记录', "\d+/": '维护记录'}
hosts_oper = {"scripts/": '脚本', "scripts/\d+/": '脚本', "oper_tasks/distribution_files/": "文件分发",
              "oper_tasks/distribution_tasks/": "文件分发任务", "oper_tasks/distribution_tasks/\d+/": "文件分发任务",
              "oper_tasks/cron_tasks/": "定时任务", "oper_tasks/real_time_tasks/": "即时任务"}
diagnose = {"createconf/": '链路检测', 'tcpdump/custom_capture_task/': '自定义抓包', "snapshots/": "会议/终端快照",
            'tcpdump/custom_capture/\w*': '自定义抓包任务', 'tcpdump/custom_capture_items/\w*': '自定义抓包任务子项',
            'check_apps/': '应用检测', 'tcpdump/quick_capture/': '一键抓包'}
alarms = {'rules/': '告警规则', 'rules/\d+/': '告警规则', 'thresholds/\d+/': '告警阈值', 'export/': '告警导出',
          'ignore/': '主动告警忽略','sub_warning/':'订阅告警'}
hosts = {'deploy_sync/': '同步luban数据', 'groups': '主机分组'}
issuetracking = {'issues/': '问题追踪', "issues/\d+/": '问题追踪', }
versions = {"platform/": "平台版本", "terminal/": "终端版本", "os/": "系统版本", "platform/\d+/": "平台版本文件", "terminal/\d+/": "终端版本文件", "os/\d+/": "系统版本文件"}


# 特殊处理的URL


class OperationLog:
    _Handle_Methods = ['PUT', 'DELETE', 'POST']
    _Operations = {'LOGIN': 1, 'LOGOUT': 2, 'POST': 3, 'DELETE': 4, 'PUT': 5, 'UPLOAD': 6}
    Handle_Models = ['faq', 'maintenance', 'hosts_oper', 'diagnose', 'alarms', 'hosts', 'issuetracking', 'logout', 'versions']

    def get_operations(self, request_method, request_model, request_url):
        """
        判断操作类型
        :return: int
        """
        # 特殊处理
        if request_model == 'hosts_oper' and request_method == 'POST' and request_url == "":
            # 上传脚本
            return self._Operations.get('UPLOAD')
        elif request_model == 'versions' and request_method == 'POST':
            return self._Operations.get('UPLOAD')
        logger.info(request_url)
        if request_model == 'logout':
            return self._Operations.get('LOGOUT')
        return self._Operations.get(request_method)

    def get_describe(self, request_method, request_model, request_url):
        """
        获取 操作描述
        :return: str
        """
        if request_model == 'logout':
            return "用户注销登录"
        try:
            model_patterns = eval(request_model)  # 将模块名转换为对应字典
        except Exception as err:
            logger.error(err)
            return ""

        for key in model_patterns.keys():
            if re.match(key, request_url):
                return model_patterns.get(key)
        return ""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        rq_type = None  # 请求类型 默认为None
        method = request.method

        if method in self._Handle_Methods:
            if len(request.FILES) != 0:
                # 上传文件
                rq_type = 'file'
            else:
                rq_encode = request.encoding if request.encoding else 'utf-8'
                content = request.body.decode(rq_encode)

        response = self.get_response(request)

        if method not in self._Handle_Methods:
            return response

        spt_path = request.path.split(sep='/', maxsplit=5)
        model_name = spt_path[4].lower()  # 模块名
        if model_name not in self.Handle_Models:
            return response
        if len(spt_path) >= 5:
            useful_url = spt_path[5]  # 路径
        else:
            useful_url = ''
        op_type = self.get_operations(method, model_name, useful_url)  # 操作类型
        desc = self.get_describe(method, model_name, useful_url)  # 操作描述
        username = request.META.get('ssoAuth').get('account')  # 获取用户名
        ip = request.META.get('HTTP_X_REAL_IP', request.META.get('REMOTE_ADDR', ''))  # 获取ip
        rs_charset = response.charset
        if rs_charset:
            if response.status_code == 204:
                # 默认delete请求的成功返回码，无response.content
                rs_content = {'success': 1}
            else:
                try:
                    rs_content = json.loads(response.content.decode(rs_charset))
                except Exception as e:
                    err = str(e)
                    logger.error(err)
                    rs_content = {}
        else:
            try:
                rs_content = json.loads(response.content.decode())
            except Exception as e:
                err = str(e)
                logger.error(err)
                rs_content = {}
        rs_stat = rs_content.get('success', 1)  # 获取执行状态

        if rq_type == 'file' and rs_stat == 1:
            # 请求类型为file且执行成功  从response中获取文件名
            content = rs_content.get('filename', '')
        elif rs_stat == 0:
            # 执行失败 获取失败原因
            content = rs_content.get('msg', '')
        else:
            content = rs_content.get('data', '')
        logger.info(content)
        try:
            content = json.dumps(content)
        except:
            pass
        if not desc:
            # 记录无描述的操作，便于补充
            logger.warning('no desc %s: %s' % (request.method, request.path))
        if not content:
            # 记录无详情的操作，便于补充
            logger.warning('no content %s: %s --> %s' % (request.method, request.path, rs_content))
        connection.close()
        operation_data = OperationLogSerializers(
            data=dict(username=username, opertype=op_type, operdesc=desc, detail=content, operrest=rs_stat, ip=ip))
        if operation_data.is_valid():  # 校验数据
            try:
                with transaction.atomic():
                    operation_data.save()
                    logger.debug(operation_data.data)
            except Exception as err:
                logger.error(err)
            else:
                pass
        else:
            logger.error(operation_data.errors)

        return response
