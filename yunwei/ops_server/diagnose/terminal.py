#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
终端诊断
"""

import os
import ipaddress
import logging
import json
import datetime

from copy import deepcopy

from jsonpath import jsonpath

from ops.settings import BASE_DIR
from django.db import connections
from common.my_exception import OpsException
from common.my_elastic import es_client, ESIndex
from common.conf_params_enum import MtProtocol, MtProtocolType, MtStatus, MtType
from common.my_redis import redis_client

logger = logging.getLogger('ops.' + __name__)

# 是否支持终端多登
_MULTI_LOGIN = False


class AccountsTerminalSearch:
    """
    根据终端 e164/终端名称/终端ip搜索 终端
    返回终端满足条件的终端账号信息
    """

    def __init__(self, keyword):
        self.keyword = keyword

    @staticmethod
    def is_ipv4(addr):
        # return False if the *addr* passed isn't a v4 address else return True
        try:
            return isinstance(ipaddress.IPv4Address(addr), ipaddress.IPv4Address)
        except Exception:
            return False

    @staticmethod
    def get_mt_e164_through_ip(ip):
        """
        get e164 from ES by ip
        :return:str or None
        """
        dsl_ = {
            "size": 1,
            "_source": [
                "source.status",
                "source.e164",
                "source.mtaddr"
            ],
            "query": {
                "bool": {
                    "filter": [
                        {
                            "term": {
                                "source.mtaddr": ip
                            }
                        }
                    ]
                }
            },
            "sort": [
                {
                    "@timestamp": {
                        "order": "desc"
                    }
                }
            ]
        }
        index = ESIndex.UpuWatcherIndex.value

        try:
            results = es_client.search(index=index, body=dsl_)
        except Exception as err:
            logger.error(err.args)
            raise OpsException(code='10002')

        dev_status = jsonpath(results, '$..status')
        if dev_status is not False and dev_status[0] == 'online':
            dev_e164 = jsonpath(results, '$..e164')
            if dev_e164 is not False:
                return dev_e164[0]
        return None

    @staticmethod
    def get_terminal_user_info(terminal):
        """
        get moid/e164/account/user_domain_moid/user_domain_name/dev_name from mysql by terminal_name or terminal_e164
        :param terminal: E164 or dev_name
        :return: list
        """
        sql = """
        SELECT
            ui.moid,
            ui.e164,
            ui.account,
            ui.user_domain_moid,
            ud.user_domain_name,
            up.`name` 
        FROM
            user_info ui
            LEFT JOIN user_profile up ON ui.moid = up.moid
            LEFT JOIN user_domain ud ON ui.user_domain_moid = ud.user_domain_moid 
        WHERE
            ui.binded = 0 
            AND ui.`enable` = 1 
            AND ui.isdeleted = 0 
            AND ( ui.e164 = %s OR up.`name` = %s )
        """
        with connections['movision'].cursor() as cursor:
            params = [terminal, terminal]
            cursor.execute(sql, params)
            terminal_info = cursor.fetchall()

        terminal_info = [list(info) for info in terminal_info]
        return terminal_info

    @staticmethod
    def get_upu_register_online_info(e164_s):
        """
        get dev_status   online/offline
        :param e164_s: list [e164, e164, ...]
        :return: list of int     1：online; 0：offline
        """
        if len(e164_s) == 0:
            return []

        dsl_ = {
            "size": 0,
            "query": {
                "bool": {
                    "filter": [
                        {
                            "term": {
                                "source.e164": ""
                            }
                        }
                    ]
                }
            },
            "aggs": {
                "devtype": {
                    "terms": {
                        "field": "source.mttype.keyword",
                        "size": 10000
                    },
                    "aggs": {
                        "top1": {
                            "top_hits": {
                                "size": 1,
                                "_source": {
                                    "includes": [
                                        "source.status",
                                        "source.e164",
                                        "source.mtaddr"
                                    ]
                                },
                                "sort": [
                                    {
                                        "@timestamp": {
                                            "order": "desc"
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }
        m_dsl = ''
        index = ESIndex.UpuWatcherIndex.value
        for e164 in e164_s:
            dsl_['query']['bool']['filter'][0]['term'] = {"source.e164": "%s" % e164}
            m_dsl += '%s\n%s\n' % (json.dumps({'index': index}), json.dumps(dsl_))

        try:
            results = es_client.msearch(body=m_dsl)
        except Exception as err:
            logger.error(err.args)
            raise OpsException('10002')

        status = []
        for result in results['responses']:
            dev_status = jsonpath(result, '$..source.status')
            if dev_status is not False and 'online' in dev_status:
                # any client online return online
                status.append(1)
            else:
                status.append(0)
        return status

    def search(self):
        """
        :return: list
        """
        if self.is_ipv4(self.keyword):
            # ip
            keyword = self.get_mt_e164_through_ip(self.keyword)
            if keyword is None:
                return []
        else:
            keyword = self.keyword

        # moid/e164/account/user_domain_moid/user_domain_name/dev_name
        device_info = self.get_terminal_user_info(keyword)
        dev_numbers = [info[1] for info in device_info]
        dev_status = self.get_upu_register_online_info(dev_numbers)
        [x.append(y) for x, y in zip(device_info, dev_status)]
        keys = ['moid', 'e164', 'account', 'user_domain_moid', 'user_domain_name', 'name', 'status']
        results = [dict(zip(keys, info)) for info in device_info]
        return results


class AccountTerminalInfo:
    """
    根据终端164号 查询账号信息
    包括 账号基本信息、权限、可登录设备
    """

    def __init__(self, e164):
        self.e164 = e164

    @staticmethod
    def get_terminal_account_info(e164):
        """
        get moid/e164/account/user_domain_moid/user_domain_name/dev_name/enable_device from mysql by terminal_e164
        :param e164: terminal_e164
        :return: tuple   (basic_info:dict, enable_device:list)
        """
        basic_info_keys = ['moid', 'e164', 'account', 'user_domain_moid', 'user_domain_name', 'name']
        sql = """
                SELECT
                    ui.moid,
                    ui.e164,
                    ui.account,
                    ui.user_domain_moid,
                    ud.user_domain_name,
                    up.`name`,
                    up.restrict_used_on
                FROM
                    user_info ui
                    LEFT JOIN user_profile up ON ui.moid = up.moid
                    LEFT JOIN user_domain ud ON ui.user_domain_moid = ud.user_domain_moid 
                WHERE
                    ui.e164 = %s 
                    AND ui.binded = 0 
                    AND ui.`enable` = 1 
                    AND ui.isdeleted = 0
                """
        with connections['movision'].cursor() as cursor:
            params = [e164]
            cursor.execute(sql, params)
            terminal_info = cursor.fetchone()
        if len(terminal_info) == 0:
            return {}, []

        basic_info = list(terminal_info[:-1])
        basic_info = dict(zip(basic_info_keys, basic_info))
        enable_device = terminal_info[-1].split(';')
        return basic_info, enable_device

    @staticmethod
    def get_terminal_privilege(moid):
        """
        get privilege info from mysql by terminal_moid
        :param moid: dev_moid
        :return: tuple (role_info, privilege_info)
        """
        keys = ('name', 'desc', 'status')

        sql = """
        SELECT
            upl.privilege_key,
            upl.privilege_name,
            upd.privilege 
        FROM
            user_privilege_list upl
            LEFT JOIN ( SELECT privilege_key, 1 AS privilege FROM user_privilege_data WHERE moid = %s ) upd ON upl.privilege_key = upd.privilege_key
        """
        with connections['movision'].cursor() as cursor:
            params = [moid]
            cursor.execute(sql, params)
            all_privilege_info = cursor.fetchall()

        all_privilege_info = [(key, name, stat) if stat == 1 else (key, name, 0) for key, name, stat in
                              all_privilege_info]

        # role
        role_info = [dict(zip(keys, info)) for info in all_privilege_info if info[1].endswith("管理员")]
        # privilege
        privilege_info = [dict(zip(keys, info)) for info in all_privilege_info if not info[1].endswith("管理员")]

        return role_info, privilege_info

    def get_account_info(self):
        """
        :return: dict
        """
        info_keys = ["timestamp", 'account', 'privilege', 'role', 'enable_device']

        timestamp = int(datetime.datetime.now().timestamp() * 1000)
        # account info
        # moid/e164/account/user_domain_moid/user_domain_name/dev_name/enable_device
        base_info, enable_device = self.get_terminal_account_info(self.e164)
        if len(base_info) == 0:
            # no matched case
            return dict(zip(info_keys, [{}, [], [], []]))

        moid = base_info.get('moid')
        # role/privilege
        role, privilege = self.get_terminal_privilege(moid)

        info = dict(zip(info_keys, [timestamp, base_info, privilege, role, enable_device]))
        return info


class AccountTerminals:
    """
    根据终端e164号查找 设备
    账号多设备登陆
    """

    def __init__(self, e164):
        self.e164 = e164
        self.moid = self.get_terminal_moid(self.e164)

    @staticmethod
    def get_upu_register_info(e164):
        """
        从UPUwatcher 获取终端注册信息  区分多终端登陆
        include  mttype/devid/prototype/*call_protocol*/status/mtaddr/roommoid/userdomain/nuaddr/nuplatformid
                 型号/moid/注册协议/协议类型/在线状态/ip/机房moid/用户域moid/pas_ip/平台域moid

        :return: list of tuple, the first list is timestamps, the second is infos
        infos ex:
            [{
                "type": "TrueLink",
                "moid": "13bf2ec4-4743-11ea-8b67-a4bf01306d06",
                "register_protocol": "H323"
                "call_protocol": 1,
                "status": 1,
                "ip": "192.168.1.100",
                "machineroom_moid": "8d5e9e9f-4bbc-49f9-bd90-287e3c2195d4",
                "userdomain_moid": "729qq1rywt88fzuccqvbccj5",
                "pas_ip": "112.4.82.120",
                "platform_moid": "mooooooo-oooo-oooo-oooo-defaultplatf"
            }]
        """
        result_keys = ["type", "moid", "register_protocol", "call_protocol", "status", "ip", "machineroom_moid",
                       "userdomain_moid", "pas_ip", "platform_moid"]
        dsl_ = {
            "size": 0,
            "_source": "source",
            "query": {
                "bool": {
                    "filter": [
                        {
                            "term": {
                                "source.e164": e164
                            }
                        }
                    ]
                }
            },
            "aggs": {
                "type": {
                    "terms": {
                        "field": "source.mttype.keyword",
                        "size": 10000
                    },
                    "aggs": {
                        "top1": {
                            "top_hits": {
                                "size": 1,
                                "sort": [
                                    {
                                        "@timestamp": {
                                            "order": "desc"
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }
        index = ESIndex.UpuWatcherIndex.value

        try:
            result = es_client.search(index=index, body=dsl_)
        except Exception as err:
            logger.error(err.args)
            raise OpsException('10002')

        total = jsonpath(result, "$.hits.total")
        if total and total[0] == 0:
            return [], []

        res = []
        timestamps = []  # 搜索文档的时间戳
        for upu_info in result["aggregations"]["type"]["buckets"]:
            type_ = jsonpath(upu_info, '$..mttype')
            moid = jsonpath(upu_info, '$..devid')
            ip = jsonpath(upu_info, '$..mtaddr')
            machineroom_moid = jsonpath(upu_info, '$..roommoid')
            userdomain_moid = jsonpath(upu_info, '$..userdomain')
            pas_ip = jsonpath(upu_info, '$..nuaddr')
            platform_moid = jsonpath(upu_info, '$..nuplatformid')

            prototype = jsonpath(upu_info, '$..prototype')  # type: list
            if prototype:
                if prototype[0].startswith("H323"):
                    register_protocol = [MtProtocol.H323.name]
                    if prototype[0].endswith('s'):
                        call_protocol = [MtProtocolType.Standard.value]
                    elif prototype[0].endswith('n'):
                        call_protocol = [MtProtocolType.NonStandard.value]
                    else:
                        call_protocol = False
                elif prototype[0].startswith("Sip"):
                    register_protocol = [MtProtocol.SIP.name]
                    # sip 协议只有标准协议
                    call_protocol = [MtProtocolType.Standard.value]
                else:
                    register_protocol = False
                    call_protocol = False
            else:
                register_protocol = False
                call_protocol = False

            status = jsonpath(upu_info, '$..status')
            if status and status[0] == "online":
                status = [MtStatus.Online.value]
            else:
                status = [MtStatus.Offline.value]

            res.append([type_, moid, register_protocol, call_protocol, status, ip, machineroom_moid,
                        userdomain_moid, pas_ip, platform_moid])

            timestamp = jsonpath(upu_info, "$..sort[0]")[0]
            timestamps.append(timestamp)

        res = [[x[0] if x is not False else "" for x in info] for info in res]
        data = [dict(zip(result_keys, info)) for info in res]

        return timestamps, data

    @staticmethod
    def get_nms_register_info(moid):
        """
        从网管 获取终端注册信息  区分多终端登陆
        include  devtype/devname/devver/SN/aps_addr/ip
                 型号/名称/版本号/SN/aps_ip/ip

        :return: list of tuple, the first list is timestamps, the second is infos
        infos ex:
            [{
                "type": "TrueLink",
                "name": "王伟",
                "version": "V6.0.0.4.0.20200318"
                "SN": "KDC003997",
                "aps_ip": "127.0.0.1",
                "ip": "192.168.1.100"
            }]
        """

        nms_keys = ["type", "name", "version", "SN", "aps_ip", "ip"]
        # if dev_type is None:
        #     return {}.fromkeys(nms_keys, "")
        #
        # dev_type = dev_type.strip('/').strip('_')
        # dev_tp = []
        # for spt in dev_type.split('/'):
        #     dev_tp.extend(spt.split('_'))
        # dev_type = " ".join(dev_tp)

        dsl_ = {
            "size": 0,
            "query": {
                "bool": {
                    "filter": [
                        {
                            "term": {
                                "source.eventid.keyword": "EV_MT_INFO"
                            }
                        },
                        {
                            "term": {
                                "source.devid.keyword": moid
                            }
                        }
                    ]
                }
            },
            "aggs": {
                "type": {
                    "terms": {
                        "field": "source.devtype.keyword",
                        "size": 10000
                    },
                    "aggs": {
                        "top1": {
                            "top_hits": {
                                "size": 1,
                                "sort": [
                                    {
                                        "@timestamp": {
                                            "order": "desc"
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }
        index = ESIndex.NMSMTIndex.value

        try:
            result = es_client.search(index=index, body=dsl_)
        except Exception as err:
            logger.error(err.args)
            raise OpsException('10002')

        total = jsonpath(result, "$.hits.total")
        if total and total[0] == 0:
            return [], []

        res = []
        timestamps = []
        for nms_info in result["aggregations"]["type"]["buckets"]:
            type_ = jsonpath(nms_info, '$...source.devtype')
            name = jsonpath(nms_info, '$..source.mt_info.devname')
            version = jsonpath(nms_info, '$..source.mt_info.devver')
            SN = jsonpath(nms_info, '$..source.mt_info.SN')
            aps_ip = jsonpath(nms_info, '$..source.mt_info.aps_addr.ip')
            ip = jsonpath(nms_info, '$..source.mt_info.netinfo.ip')

            res.append([type_, name, version, SN, aps_ip, ip])

            timestamp = jsonpath(nms_info, "$..sort[0]")[0]
            timestamps.append(timestamp)

        res = [[x[0] if x is not False else "" for x in info] for info in res]
        data = [dict(zip(nms_keys, info)) for info in res]
        return timestamps, data

    @staticmethod
    def get_pas_register_info(e164):
        """
        从 callmanager 日志获取终端注册信息  区分多终端登陆
        include  devicetype/serverip/protocol/*call_protocol*/mtaddr/mtisdmz/mtish460/mtisnat/mtisportreuse/mtisprivatenetmt/
                    mtistp/mtloginaps/mtnataddr/mtproductId/mtroommoid/mttransporttype/mtdevid/moid/*ret*/
                 终端类型/注册服务器地址（pas_ip）/注册协议/协议类型/ip_port/dmz状态/h460状态/nat状态/端口复用/privatenet状态/网呈终端/
                 loginaps/Nat地址_port/productId（终端型号）/机房moid/传输类型/versionId/moid/注册结果/

        :return: list of tuple, the first list is timestamps, the second is infos
        infos ex:
            [{
              "dev_type": 1,
              "pas_ip": "10.67.18.220",
              "register_protocol": "H323",
              "call_protocol": 1,
              "ip": "10.67.17.134.1719",
              "dmz": "1",
              "h460": "0",
              "nat_status": "0",
              "portreuse": "0",
              "privatenet": "1",
              "stp": "0",
              "aps_login": "0",
              "last_nat_ip": "10.67.17.113.1759"
              "product_id": "Kdvpcmt",
              "machineroom_moid": "16e6ac4f-6600-431e-a4c6-e80d5c6ab136",
              "transport_type": "UnKnow",
              "dev_id": "",
              "moid": "ba8990ad-e6df-4e58-b96c-33aca1149c5f",
              "register_status": 1
            }]
        """
        result_keys = ["dev_type", "pas_ip", "register_protocol", "call_protocol", "ip", "dmz", "h460", "nat_status",
                       "portreuse", "privatenet", "stp", "aps_login", "last_nat_ip", "product_id", "machineroom_moid",
                       "transport_type", "dev_id", "moid", "register_status"]
        dsl_ = {
            "size": 0,
            "query": {
                "bool": {
                    "filter": [
                        {
                            "term": {
                                "beat.name": "callmanager"
                            }
                        },
                        {
                            "term": {
                                "source.src.mt164": e164
                            }
                        }
                    ]
                }
            },
            "aggs": {
                "type": {
                    "terms": {
                        "field": "source.src.mtproductId.keyword",
                        "size": 10000
                    },
                    "aggs": {
                        "top1": {
                            "top_hits": {
                                "size": 1,
                                "_source": {
                                    "includes": "source"
                                },
                                "sort": [
                                    {
                                        "@timestamp": {
                                            "order": "desc"
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }
        index = ESIndex.APPLogIndex.value

        try:
            result = es_client.search(index=index, body=dsl_)
        except Exception as err:
            logger.error(err.args)
            raise OpsException('10002')

        total = jsonpath(result, "$.hits.total")
        if total and total[0] == 0:
            return [], []

        res = []
        timestamps = []

        def get_value(key):
            """
            :param key:
            :type key: str
            :return: str
            """
            nonlocal pas_info
            try:
                jsonpath(pas_info, "$..source")[0].get(key, False)
            except Exception:
                return ""

        for pas_info in result["aggregations"]["type"]["buckets"]:
            dev_type = get_value("devicetype")
            if dev_type is not False:
                if dev_type[0] == "SOFT":
                    dev_type = [MtType.Soft.value]
                elif dev_type[0] == "HARD":
                    dev_type = [MtType.Hard.value]
                else:
                    dev_type = [MtType.OtherProduct.value]
            else:
                dev_type = [MtType.Unknown.value]
            pas_ip = get_value("serverip")

            protocol = get_value("protocol")  # type: str
            if protocol:
                if protocol.startswith("H323"):
                    register_protocol = MtProtocol.H323.name
                    if protocol.endswith('s'):
                        call_protocol = MtProtocolType.Standard.value
                    elif protocol.endswith('n'):
                        call_protocol = MtProtocolType.NonStandard.value
                    else:
                        call_protocol = ""
                elif protocol.startswith("Sip"):
                    register_protocol = MtProtocol.SIP.name
                    # sip 协议只有标准协议
                    call_protocol = MtProtocolType.Standard.value
                else:
                    register_protocol = ""
                    call_protocol = ""
            else:
                register_protocol = ""
                call_protocol = ""

            ip = get_value("src.mtaddr")
            dmz = get_value("src.mtisdmz")
            h460 = get_value("src.mtish460")
            nat_status = get_value("src.mtisnat")
            portreuse = get_value("src.mtisportreuse")
            privatenet = get_value("src.mtisprivatenetmt")
            stp = get_value("src.mtistp")
            aps_login = get_value("src.mtloginaps")
            last_nat_ip = get_value("src.mtnataddr")
            product_id = get_value("src.mtproductId")
            machineroom_moid = get_value("src.mtroommoid")
            transport_type = get_value("src.mttransporttype")
            dev_id = get_value("devid")
            moid = get_value("src.mtmoid")

            ret = get_value("ret")
            if ret == "success":
                register_status = 1
            else:
                register_status = 0

            res.append([dev_type, pas_ip, register_protocol, call_protocol, ip, dmz, h460, nat_status, portreuse,
                        privatenet, stp, aps_login, last_nat_ip, product_id, machineroom_moid, transport_type,
                        dev_id, moid, register_status])

            timestamp = jsonpath(pas_info, "$..sort[0]")[0]
            timestamps.append(timestamp)

        res = [[x if x is not False else "" for x in info] for info in res]
        data = [dict(zip(result_keys, info)) for info in res]
        return timestamps, data

    @staticmethod
    def get_terminal_moid(e164):
        """
        :return: str or None
        """
        basic_info, _ = AccountTerminalInfo.get_terminal_account_info(e164)
        return basic_info.get("moid")

    @staticmethod
    def filter_data(timestamps, data, flag=None):
        """
        过滤信息
        目前不考虑多登陆 仅返回最近一次登陆信息
        :param flag: str  "upu"/"nms"/"pas"
        :param timestamps: list
        :param data: list
        :return: list of dict
        """
        if flag is not None:
            # 根据flag 转换终端类型  统一终端类型
            # 业务暂不支持 暂不实现
            # 向pas数据中添加 'type' 终端类型字段
            if flag == "pas":
                #  向pas数据中添加 'type' 终端类型字段    目前暂定product_id字段  后续优化
                [x.setdefault("type", x.get("product_id", "")) for x in data]

        if _MULTI_LOGIN:
            # 支持多登
            # 统一终端类型
            return data
        else:
            # 目前不考虑多登陆 仅返回最近一次登陆信息
            try:
                last_time = timestamps.index(max(timestamps))
                return [data[last_time]]
            except Exception:
                return [{}]

    def _merge_data(self, upu_infos, nms_infos, pas_infos):
        """
        合并数据
        :param data: list
        :return: list
        """
        template = {
            "type": "",
            "dev_type": "",
            "version": "",
            "name": "",
            "SN": "",
            "register_status": "",
            "ip": "",
            "pas_ip": "",
            "register_protocol": "",
            "call_protocol": "",
            "nat_status": "",
            "dmz": "",
            "proxy_status": "",
            "proxy_ip": "",
            "h323_port": ""
        }
        infos = []

        if _MULTI_LOGIN:
            # 按照终端类型合并数据
            # 以pas为准

            for info_pas in pas_infos:
                dev_type = info_pas.get("type")
                info_upu = [x if x.get("type") == dev_type else {} for x in upu_infos][0]
                info_nms = [x if x.get("type") == dev_type else {} for x in nms_infos][0]

                tem = deepcopy(template)
                tem.update(info_nms)
                tem.update(info_upu)
                tem.update(info_pas)

                infos.append(tem)
        else:
            # 单登
            upu_info = upu_infos[0]
            nms_info = nms_infos[0]
            pas_info = pas_infos[0]

            tem = deepcopy(template)
            tem.update(nms_info)
            tem.update(upu_info)
            tem.update(pas_info)

            infos.append(tem)

        # 处理 终端类型中的 '/' 替换成 '_'
        for info in infos:
            dev_type = info.get("type")
            info["type"] = dev_type.replace("/", "_")

        return infos

    def get_dev_register_info(self):
        """
        get device register information from nms upu and pas
        :return:  dict
        """
        timestamps_upu, upu_infos = self.get_upu_register_info(self.e164)
        timestamps_nms, nms_infos = self.get_nms_register_info(self.moid)
        timestamps_pas, pas_infos = self.get_pas_register_info(self.e164)

        upu_info = self.filter_data(timestamps_upu, upu_infos)
        nms_info = self.filter_data(timestamps_nms, nms_infos)
        pas_info = self.filter_data(timestamps_pas, pas_infos)

        info = self._merge_data(upu_info, nms_info, pas_info)
        return info

    def get_terminals(self):
        return self.get_dev_register_info()


class TerminalConnect:
    """
    根据终端e164号和终端类型 获取终端连接信息
    """

    def __init__(self, e164, dev_type):
        self.e164 = e164
        self.dev_type = dev_type
        self.moid = AccountTerminals.get_terminal_moid(self.e164)

    def get_should_connect(self):
        """
        :return: list
        """
        dsl_ = {
            "size": 1,
            "query": {
                "bool": {
                    "filter": [
                        {
                            "term": {
                                "source.devid.keyword": self.moid
                            }
                        },
                        {
                            "term": {
                                "source.eventid.keyword": "EV_SHOULD_CONNSRV_MSG"
                            }
                        }
                    ]
                }
            },
            "sort": [
                {
                    "@timestamp": {
                        "order": "desc"
                    }
                }
            ]
        }

        if _MULTI_LOGIN:
            dsl_["query"]["bool"]["filter"].append({"term": {"source.devtype.keyword": self.dev_type}})

        index = ESIndex.NMSMTIndex.value
        try:
            result = es_client.search(index=index, body=dsl_)
        except Exception as err:
            logger.error(err.args)
            raise OpsException('10002')

        total = jsonpath(result, "$.hits.total")
        if total and total[0] == 0:
            return []

        conn = jsonpath(result, "$..conn_srv_type_info")
        conn = conn[0] if conn is not False else []
        conn = list(set(conn))
        return conn

    def get_real_connect(self):
        """
        :return: list
        ex:
        [
            {
                "type": "APS",
                "data": {
                    "ip": "127.0.0.1"
                }
            }
        ]
        """
        dsl_ = {
            "size": 1,
            "query": {
                "bool": {
                    "filter": [
                        {
                            "term": {
                                "source.devid.keyword": self.moid
                            }
                        },
                        {
                            "term": {
                                "source.eventid.keyword": "EV_CONNSRV_CONN_MSG"
                            }
                        }
                    ]
                }
            },
            "sort": [
                {
                    "@timestamp": {
                        "order": "desc"
                    }
                }
            ]
        }

        if _MULTI_LOGIN:
            dsl_["query"]["bool"]["filter"].append({"term": {"source.devtype.keyword": self.dev_type}})

        index = ESIndex.NMSMTIndex.value
        try:
            result = es_client.search(index=index, body=dsl_)
        except Exception as err:
            logger.error(err.args)
            raise OpsException('10002')

        total = jsonpath(result, "$.hits.total")
        if total and total[0] == 0:
            return []

        conn = jsonpath(result, "$..conn_srv_state_info")
        conn = conn[0] if conn is not False else []
        conn = [{"type": x.get("type"), "data": {"ip": x.get("ip")}} for x in conn]
        return conn

    def get_connect(self):
        """
        :return: dict
        """

        should_conn = self.get_should_connect()
        real_connect = self.get_real_connect()

        # PAS 节点添加信息
        for info in real_connect:
            type_ = info.get("type")
            if type_ == "PAS":
                pas_all_info = AccountTerminals.get_pas_register_info(self.e164)
                pas_all_info = AccountTerminals.filter_data(*pas_all_info)

                if _MULTI_LOGIN:
                    for pas_info in pas_all_info:
                        if pas_info.get("type") == self.dev_type:
                            info["data"].update(pas_info)
                            break
                    break
                else:
                    # 目前不考虑多登录  仅返回最新数据
                    info["data"].update(pas_all_info[0])
                    break

        return {"should_connect": should_conn, "connect": real_connect}


class TerminalCallRecords:
    """
    根据终端e164和终端类型查询 终端呼叫记录
    查询 mpcadp 的日志
    """

    def __init__(self, e164, dev_type, start=0, count=20):
        self.e164 = e164
        self.dev_type = dev_type
        self.start = start
        self.count = count

    def _get_call_records(self):
        """
        :return: tuple
        """
        dsl_ = {
            "size": self.count,
            "from": self.start,
            "_source": ["source.Mcu.errcode", "source.reason"],
            "query": {
                "bool": {
                    "filter": [
                        {
                            "term": {
                                "beat.name": "mpcadp"
                            }
                        },
                        {
                            "term": {
                                "source.callee.ee.keyword": self.e164
                            }
                        }
                    ]
                }
            },
            "sort": [
                {
                    "@timestamp": {
                        "order": "desc"
                    }
                }
            ]
        }

        if _MULTI_LOGIN:
            # 过滤终端类型  业务没支持 暂不实现
            # dsl_["query"]["bool"]["filter"].append({"term": {}})
            pass

        index = ESIndex.APPLogIndex.value
        try:
            result = es_client.search(index=index, body=dsl_)
        except Exception as err:
            logger.error(err.args)
            raise OpsException('10002')

        total = result["hits"]["total"]
        call_info = []
        result_keys = ["time", "result", "err_msg"]
        if total == 0:
            return total, call_info

        for info in result["hits"]["hits"]:
            time_ = info["sort"][0]
            err_msg = jsonpath(info, "$..reason")
            if err_msg:
                call_info.append(dict(zip(result_keys, [time_, 0, err_msg[0]])))
            else:
                call_info.append(dict(zip(result_keys, [time_, 1, ""])))
        return total, call_info

    def get_call_records(self):
        """
        :return: tuple  total/info
        """
        return self._get_call_records()


class TerminalCrucialProcesses:
    """
    根据终端164号和终端类型查询终端关键进程
    业务无数据 暂不实现
    """

    def __init__(self, e164, dev_type):
        self.e164 = e164
        self.dev_type = dev_type

    def _get_crucial_process(self):
        result_keys = ["process", "runtime", "restart", "data"]

        process = ""
        runtime = 0
        restart = 0
        data = [{"time": "", "reason": ""}]

        return [dict(zip(result_keys, [process, runtime, restart, data]))]

    def get_crucial_processes(self):
        return self._get_crucial_process()


class TerminalPeripheral:
    """
    根据终端164号和终端类型查询终端外设信息
    业务无数据 暂不实现
    """

    def __init__(self, e164, dev_type):
        self.e164 = e164
        self.dev_type = dev_type

    def _peripheral(self):
        result_keys = ["name", "type", "status", "id", "soft_version", "hard_version"]

        name = ""
        type_ = 1
        status = 0
        id_ = ""
        soft_version = ""
        hard_version = ""

        return [dict(zip(result_keys, [name, type_, status, id_, soft_version, hard_version]))]

    def get_peripheral(self):
        return self._peripheral()


class TerminalStatistic:
    """
    根据终端164号和终端类型查询终端统计信息
    """

    def __init__(self, e164, dev_type):
        self.e164 = e164
        self.dev_type = dev_type

    @staticmethod
    def time_splitter(timestamp, time_range, start=None):
        """
        :param start: start index
        :type timestamp: timestamp
        :type time_range: list
        :return: int or None
        """
        if start is not None:
            iterator = range(start, len(time_range))
        else:
            iterator = range(len(time_range))
        for index in iterator:
            if time_range[index] >= timestamp:
                return index
        return None

    @staticmethod
    def calculate(t, v, in_flag, out_flag):
        """
        :type t: list
        :type v: list
        :type in_flag: str
        :type out_flag: str
        :param index: int
        :return: int
        """
        status = False
        total_time = 0
        for count, flag in enumerate(v):
            if flag == in_flag and status is False:
                status = True
                start_time = t[count]
            elif flag == out_flag and status is True:
                status = False
                total_time += t[count] - start_time
        return total_time

    def get_terminal_online_time(self):
        """
        :return: dict
        """
        dsl_online = {
            "size": 10000,
            "_source": "source.status",
            "query": {
                "bool": {
                    "filter": [
                        {
                            "term": {
                                "source.e164.keyword": self.e164
                            }
                        },
                        {
                            "range": {
                                "@timestamp": {
                                    "gte": "now-1y",
                                    "lte": "now"
                                }
                            }
                        }
                    ]
                }
            },
            "sort": [
                {
                    "@timestamp": {
                        "order": "asc"
                    }
                }
            ]
        }

        if _MULTI_LOGIN:
            # 过滤终端类型  业务没支持 暂不实现
            dsl_online["query"]["bool"]["filter"].append({"term": {"source.mttype.keyword": self.dev_type}})

        index_online = ESIndex.UpuWatcherIndex.value
        keys = ["name", "desc", "last_year", "last_month", "last_week"]
        total_time = ["online_time", "在线时长"]

        try:
            result = es_client.search(body=dsl_online, index=index_online)
        except Exception as err:
            logger.error(err.args)
            raise OpsException('10002')

        time_list = jsonpath(result, "$..sort[0]")
        status_list = jsonpath(result, "$..status")

        if time_list is False or status_list is False:
            logger.info('terminal %s has no online/offline data' % self.e164)
            total_time.extend([0, 0, 0])
            return dict(zip(keys, total_time))

        now = datetime.datetime.now()
        last_week = int((now - datetime.timedelta(days=7)).timestamp() * 1000)
        last_month = int((now - datetime.timedelta(days=30)).timestamp() * 1000)
        last_year = int((now - datetime.timedelta(days=365)).timestamp() * 1000)

        find = None
        for target_time in [last_year, last_month, last_week]:
            find = self.time_splitter(target_time, time_list, start=find)

            tmp_time_list = time_list[find:]
            tmp_status_list = status_list[find:]

            total_t = self.calculate(tmp_time_list, tmp_status_list, 'online', 'offline')
            total_time.append(total_t // 1000)  # seconds
        return dict(zip(keys, total_time))

    def get_terminal_meeting_time(self):
        """
        :return: dict
        """
        dsl_meeting = {
            "size": 10000,
            "_source": "source.eventid",
            "query": {
                "bool": {
                    "filter": [
                        {
                            "terms": {
                                "source.eventid.keyword": [
                                    "EV_MCU_MT_ADD",
                                    "EV_MCU_MT_DEL"
                                ]
                            }
                        },
                        {
                            "term": {
                                "source.mtinfo.mtaccount.keyword": self.e164
                            }
                        },
                        {
                            "range": {
                                "@timestamp": {
                                    "gte": "now-1y",
                                    "lte": "now"
                                }
                            }
                        }
                    ]
                }
            },
            "sort": [
                {
                    "@timestamp": {
                        "order": "asc"
                    }
                }
            ]
        }

        if _MULTI_LOGIN:
            # 过滤终端类型  业务没支持 暂不实现
            # dsl_meeting["query"]["bool"]["filter"].append({"term": {"source.mttype.keyword": self.dev_type}})
            pass

        index_meeting = ESIndex.NMSCmuIndex.value
        total_time = ["meeting_time", "会议时长"]
        keys = ["name", "desc", "last_year", "last_month", "last_week"]

        try:
            result = es_client.search(body=dsl_meeting, index=index_meeting)
        except Exception as err:
            logger.error(err.args)
            raise OpsException('10002')

        time_list = jsonpath(result, "$..sort[0]")
        status_list = jsonpath(result, "$..eventid")

        if time_list is False or status_list is False:
            logger.info('terminal %s has no meeting add/del data' % self.e164)
            total_time.extend([0, 0, 0])
            return dict(zip(keys, total_time))

        now = datetime.datetime.now()
        last_week = int((now - datetime.timedelta(days=7)).timestamp() * 1000)
        last_month = int((now - datetime.timedelta(days=30)).timestamp() * 1000)
        last_year = int((now - datetime.timedelta(days=365)).timestamp() * 1000)

        find = None
        for target_time in [last_year, last_month, last_week]:
            find = self.time_splitter(target_time, time_list, start=find)

            if find is None:
                total_t = 0
            else:
                tmp_time_list = time_list[find:]
                tmp_status_list = status_list[find:]
                total_t = self.calculate(tmp_time_list, tmp_status_list, 'EV_MCU_MT_ADD', 'EV_MCU_MT_DEL')
            total_time.append(total_t // 1000)  # seconds
        return dict(zip(keys, total_time))

    def get_statistic(self):
        """
        get dev meeting time and online time
        :param e164: str
        :return: list
        """
        meet_time = self.get_terminal_meeting_time()
        online_time = self.get_terminal_online_time()
        return [meet_time, online_time]


class TerminalStatus:
    """
    根据终端164号和终端类型查询终端状态信息
    """

    def __init__(self, e164, dev_type):
        self.e164 = e164
        self.dev_type = dev_type
        self.moid = AccountTerminals.get_terminal_moid(self.e164)

    def is_online(self):
        """
        终端是否在线
        :return: int
        """
        upu_all_info = AccountTerminals.get_upu_register_info(self.e164)
        upu_all_info = AccountTerminals.filter_data(*upu_all_info)

        if len(upu_all_info) == 0:
            return MtStatus.Offline.value

        if _MULTI_LOGIN:
            for info in upu_all_info:
                type_ = info.get("type")
                #  判断终端类型是都相同  此处需要后续优化
                if type_ == self.dev_type:
                    return info.get("status")
            return MtStatus.Offline.value
        else:
            return upu_all_info[0].get("status")

    def is_alarm(self):
        """
        获取终端告警状态
        :return: int  1: warning  0:safe
        """
        sql = """
        SELECT
            COUNT( 1 ) 
        FROM
            terminal_warning_unrepaired 
        WHERE
            device_moid = %s
        """
        with connections['default'].cursor() as cursor:
            params = [self.moid]
            cursor.execute(sql, params)
            warning_info = cursor.fetchone()

        is_warn = 1 if warning_info[0] > 0 else 0
        return is_warn

    def is_meeting(self):
        """
        是否在会
        :return: tuple
        for example  :  (0, "") or (1, "1111111")
        int  1: meeting  0:no
        """
        script_path = os.path.join(BASE_DIR, 'lua', 'find_conf_by_e164.lua')
        with open(script_path, 'r') as f:
            script_content = f.read()

        try:
            multiply = redis_client.register_script(script_content)
            conf_id = multiply(args=[self.e164])
        except Exception as err:
            logger.error(err.args)
            return 0, ""

        conf_id = conf_id.decode('utf8')
        meeting = 1 if conf_id else 0
        return meeting, conf_id

    def _get_common_status(self):
        """
        查询终端 在线状态/告警状态/会议状态/会议号
        :return: dict
        """
        status_keys = ["online", "alarm", "meeting", "confid"]

        is_online = self.is_online()
        if is_online:
            is_meeting, conf_id = self.is_meeting()
        else:
            is_meeting, conf_id = 0, ""

        is_alarm = self.is_alarm()
        return dict(zip(status_keys, [is_online, is_alarm, is_meeting, conf_id]))

    def _get_other_status(self):
        """
        # 获取其它状态
        # 业务暂不支持  暂不实现
        :return: dict
        """

        other_status = ["os_time", "cpu_userate", "mem_total", "mem_use", "osd"]

        data = dict.fromkeys(other_status, "")
        return data

    def get_status(self):
        common_status = self._get_common_status()
        other_status = self._get_other_status()
        common_status.update(other_status)
        return common_status
