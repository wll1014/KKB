# -*- coding: utf-8 -*-
'''
Created on 2018年12月21日

@author: jay
'''


from ctypes import *
from enum import Enum, unique
import threading
import json
import time
import datetime
import argparse
import re
import queue
import os
import traceback
from common.setting import load_my_logging_cfg, config, CONF_PATH
from common.globalfun import save_json, format_timestamp

@unique
class MacroDefinition(Enum):
    """
    @unique 装饰器检测保证没有重复值
    """
    # Mt Info 结构体宏定义
    MOID_MAX_LEN = 41
    E164_MAX_LEN = 14
    COMMON_MAX_LEN = 17
    DOMAIN_MAX_LEN = 65
    TRANTYPE_MAX_LEN = 33
    DATA_MAX_LEN = 1025
    CONF_NAME_MAX_LEN = 65
    MTTYPE_MAX_LEN = 65


class MtInfoStruct(Structure):
    """
    Construct Mt Struct
    """
    _pack_ = 4
    _fields_ = [('moid', c_char * MacroDefinition.MOID_MAX_LEN.value),
                ('e164', c_char * MacroDefinition.E164_MAX_LEN.value),
                ('prototype', c_char * MacroDefinition.COMMON_MAX_LEN.value),
                ('mttype', c_char * MacroDefinition.MTTYPE_MAX_LEN.value),
                ('mtstate', c_char * MacroDefinition.COMMON_MAX_LEN.value),
                ('mtip', c_char * MacroDefinition.COMMON_MAX_LEN.value),
                ('nuip', c_char * MacroDefinition.COMMON_MAX_LEN.value),
                ('userdomain', c_char * MacroDefinition.DOMAIN_MAX_LEN.value),
                ('deviceid', c_char * MacroDefinition.MOID_MAX_LEN.value),
                ('nuplatformid', c_char * MacroDefinition.MOID_MAX_LEN.value),
                ('transfertype', c_char * MacroDefinition.TRANTYPE_MAX_LEN.value),
                ('callstate', c_char * MacroDefinition.COMMON_MAX_LEN.value),
                ('isprivatenetmt', c_int),
                ('roommoid', c_char * MacroDefinition.MOID_MAX_LEN.value),
                ('data', c_char * MacroDefinition.DATA_MAX_LEN.value),
                ('confid', c_char * MacroDefinition.E164_MAX_LEN.value),
                ('confname', c_char * MacroDefinition.CONF_NAME_MAX_LEN.value),
                ('mtdevicetype', c_char * MacroDefinition.COMMON_MAX_LEN.value)
                ]


class UpucLoopThread(threading.Thread):
    """
    Upu Loop
    """
    def __init__(self, upuclientwrap):
        super(UpucLoopThread, self).__init__()
        self.upuclientwrap = upuclientwrap

    def run(self):
        while True:
            try:
                logger.info("UpucLoopThread accept IP :" + self.upuclientwrap.ip)
                self.upuclientwrap.upuclientlib.upu_client_connect(self.upuclientwrap.upuclient,
                                                                   self.upuclientwrap.ip.encode('utf-8'),
                                                                   int(self.upuclientwrap.port), 3)
                self.upuclientwrap.upuclientlib.upu_client_loop(self.upuclientwrap.upuclient)
                time.sleep(3)

            except Exception as e:
                 logger.error(e)


class RecorderThread(threading.Thread):
    """
    Record data to file
    """

    def __init__(self,upuqueue):
        super(RecorderThread, self).__init__()
        self.upuqueue = upuqueue
        self.sys_logger = load_my_logging_cfg(upuwatcher_log(),upulogfile).getLogger('syslog')

    def run(self):
        while True:
            if not self.upuqueue.empty():
                logger.info("RecorderThread start.........")
                self.handler_callback(self.upuqueue.get())
            else:
                time.sleep(1)


    def handler_callback(self,callback_data):
        if callback_data['callback_type']=="common":
            self.handler_common_callback(callback_data)
        elif callback_data['callback_type']=="pub":
            self.handler_pubcallback(callback_data)

    def handler_common_callback(self,callback_data):
        logger.info("handeler_common_callback data recorder..........")
        # for i in range(0, int(callback_data['count'])):
        #     datadict = {}
        #     datadict["@timestamp"] = callback_data['timestamp']
        #     datadict["optype"] = callback_data['optype']
        #     datadict["opcode"] = callback_data['opcode']
        #     datadict["status"] = callback_data['status']
        #     datadict["taskclientid"] = callback_data['taskclientid']
        #     datadict["e164"] = callback_data["result"][i]["e164"]
        #     datadict["transfertype"] = callback_data["result"][i]["transfertype"]
        #     datadict["isprivatenetmt"] = callback_data["result"][i]["isprivatenetmt"]
        #     datadict["nuaddr"] = callback_data["result"][i]["nuaddr"]
        #     datadict["nuplatformid"] = callback_data["result"][i]["nuplatformid"]
        #     datadict["prototype"] = callback_data["result"][i]["prototype"]
        #     datadict["mttype"] = callback_data["result"][i]["mttype"]
        #     datadict["mtaddr"] = callback_data["result"][i]["mtaddr"]
        #     datadict["userdomain"] = callback_data["result"][i]["userdomain"]
        #     datadict["devid"] = callback_data["result"][i]["devid"]
        #     datadict["callstate"] = callback_data["result"][i]["callstate"]
        #     datadict["roommoid"] = callback_data["result"][i]["roommoid"]
        #     datadict["data"] = callback_data["result"][i]["data"]
            # datadict["confid"] = callback_data["result"][i]["confid"]
        # logger.info(callback_data)
        save_json(callback_data, sys_logger=self.sys_logger)
        logger.info("handeler_common_callback data recorder OVER..........")

    def handler_pubcallback(self, callback_data):
        try:
            logger.info("pubcallback data recorder..........")
            # logger.info(callback_data)
            # datadict = {}
            # datadict["@timestamp"] = callback_data['timestamp']
            # datadict["platform_moid"] = callback_data['platform_moid']
            # datadict["optype"] = callback_data['optype']
            # datadict["opcode"] = callback_data['opcode']
            # datadict["topic"] = callback_data['topic']
            # datadict["taskclientid"] = callback_data['taskclientid']
            # datadict["pubdata"] = []
            # # with open("upu_data.json", "a+", encoding="utf-8") as upufile:
            # for i in range(0, int(callback_data['count'])):
            #     temDict={}
            #     temDict["e164"] = callback_data["result"][i].e164.decode()
            #     temDict["transfertype"] = callback_data["result"][i].transfertype.decode()
            #     temDict["isprivatenetmt"] = callback_data["result"][i].isprivatenetmt
            #     temDict["nuaddr"] = callback_data["result"][i].nuip.decode()
            #     temDict["nuplatformid"] = callback_data["result"][i].nuplatformid.decode()
            #     temDict["prototype"] = callback_data["result"][i].prototype.decode()
            #     temDict["mttype"] = callback_data["result"][i].mttype.decode()
            #     temDict["mtaddr"] = callback_data["result"][i].mtip.decode()
            #     temDict["userdomain"] = callback_data["result"][i].userdomain.decode()
            #     temDict["devid"] = callback_data["result"][i].deviceid.decode()
            #     temDict["callstate"] = callback_data["result"][i].callstate.decode()
            #     temDict["roommoid"] = callback_data["result"][i].roommoid.decode()
            #     temDict["data"] = callback_data["result"][i].data.decode()
            #     # datadict["mtstate"] = callback_data["result"][i].mtstate.decode()
            #     # logger.info(datadict)
            #     datadict["pubdata"].append(temDict)

            save_json(callback_data, sys_logger=self.sys_logger)
            logger.info("pubcallback data recorder..........OVER")
        except Exception as e:
            logger.error(e)
            # upufile.write(json.dumps(pubdatadict) + "\n")

class UpuclientWrap():
    """
    Connect Upu
    """
    _default_timeout = 60

    def __init__(self, hosts, port, appmoid, upuqueue,platform_moid):
        self.hosts=hosts
        self.ip = hosts[0]
        self.port = port
        self.connectflag=0
        self.upuqueue=upuqueue
        self.clientid=appmoid + str(os.getpid())
        self.platform_moid=platform_moid
        # Load Upuclient Library
        try:
            self.upuclientlib = cdll.LoadLibrary('libupu_r.so')

            # Connect
            # clientid = appmoid + str(os.getpid())
            self.upuclient = self.upuclientlib.upu_client_init(self.clientid.encode('utf-8'), 10)
            # 设置连接回调函数
            # CMPFUNC = CFUNCTYPE(None, c_int, c_int, c_int, c_int, c_int, c_int, c_int, POINTER(MtInfoStruct), c_void_p)
            CMPFUNC = CFUNCTYPE(None, c_int, c_int, c_int, c_int, c_int, c_int, c_int, c_char_p, c_void_p)
            self._callback = CMPFUNC(self.upuclient_callback)
            self.upuclientlib.upu_client_set_callback(self.upuclient, self._callback, None)
            # 设置订阅回调函数
            CMPPUBFUNC = CFUNCTYPE(None, c_int, c_int, c_int, c_int, c_int, c_int, POINTER(MtInfoStruct), c_void_p)
            self._pubcallback = CMPPUBFUNC(self.upuclient_pubcallback)
            self.upuclientlib.upu_client_set_pubcallback(self.upuclient,self._pubcallback, None)
            # 保活线程
            self.upuloop = UpucLoopThread(self)
            self.upuloop.start()
            # 数据记录线程
            RecorderThread(self.upuqueue).start()

        except Exception as e:
            logger.error(e)

    """
    flag: 请求标识
    event: 通知事件()
    type: 结果类型(增删查才有结果类型)
    errcode: request是否成功
    count: 符合条件的个数(查询有效)
    total: 所有总段数量(仅在 find_mt_multi_by_usrdomain and find_mt_count_by_usrdomain被使用)
    result: 具体查询的信息(只读)
    arg: 用户设定的参数信息
    """
    def upuclient_callback(self, flag, event, opercode, type, errcode, count, total, result, arg):
        logger.info({'flag': flag, 'event': event, 'opercode': opercode, 'type': type, 'errcode': errcode, 'count': count, 'total': total})
        if event == 1:
            self.connectflag=1
            self.subscribe_topic(1, 10000001)
            self.subscribe_topic(2, 10000002)
            logger.info('Connect to UpuServer Success!')
        elif event == 2:
            IP_index=self.hosts.index(self.ip)
            if(IP_index==len(self.hosts)-1):
                self.ip=self.hosts[0]
            else:
                self.ip = self.hosts[IP_index+1]
            logger.error('Disconnect with UpuServer, Try Connect NextAddr....' + self.ip)
            self.upuclientlib.upu_client_stop_loop(self.upuclient)
            # self.upuclientlib.upu_client_connect(self.upuclient, self.ip.encode('utf-8'), int(self.port), 3)
            # self.upuclientlib.upu_client_loop(self.upuclient)
                # self.upu_client_connect()
            # time.sleep(3)
        elif event == 3:
            logger.info('get_all_mt..............')
            types = (13, 14, 15, 16, 17)
            if opercode in types:
                # timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                timestamp = format_timestamp(time.time())
                # logger.error(result.decode("utf-8"))
                _result=json.loads(result.decode("utf-8"),encoding="utf-8")
                data_callback = {
                    'callback_type':'common',
                    'timestamp': timestamp,
                    "platform_moid":self.platform_moid,
                    "optype": type,
                    "opcode": opercode,
                    'topic': 1,
                    "taskclientid": self.clientid,
                    'count': count,
                    'pubdata': _result, }
                try:
                    self.upuqueue.put_nowait(data_callback)
                except queue.Full:
                    logger.error('UpuQueue is Full ....')
            else:
                logger.error('upuclient_callback --> Unknown Error ....')

    def upuclient_pubcallback(self, flag, errcode, opercode, topic, type,  count, result, arg):
        logger.info({'flag': flag, 'errcode': errcode, 'opercode': opercode, 'topic': topic, 'type': type, 'count': count,'result':result})
        if opercode == 200:
            logger.info('PUB UpuServer Success!')
        elif opercode == 201:
            logger.error('DisPUB with UpuServer, Try Connect again....')
#             self.upuclientlib.upu_client_connect(self.upuclient, self.ip.encode('utf-8'), int(self.port), 3)
        elif opercode == 202:
            if type == 2:
                # timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                timestamp = format_timestamp(time.time())
                data_callback={
                        'callback_type': 'pub',
                        '@timestamp': timestamp,
                        "platform_moid": self.platform_moid,
                        "optype": type,
                        "opcode": opercode,
                        'topic': topic,
                        "taskclientid": self.clientid,
                        'count': count,
                        'pubdata':[],}
                try:
                    logger.info("CLibpubcallback data analysis..........")
                    # with open("upu_data.json", "a+", encoding="utf-8") as upufile:
                    for i in range(0, int(count)):
                        temDict = {}
                        temDict["e164"] = result[i].e164.decode()
                        temDict["transfertype"] = result[i].transfertype.decode()
                        temDict["isprivatenetmt"] = result[i].isprivatenetmt
                        temDict["nuaddr"] = result[i].nuip.decode()
                        temDict["nuplatformid"] = result[i].nuplatformid.decode()
                        temDict["prototype"] = result[i].prototype.decode()
                        temDict["mttype"] = result[i].mttype.decode()
                        temDict["mtaddr"] = result[i].mtip.decode()
                        temDict["userdomain"] = result[i].userdomain.decode()
                        temDict["devid"] = result[i].deviceid.decode()
                        temDict["callstate"] = result[i].callstate.decode()
                        temDict["roommoid"] = result[i].roommoid.decode()
                        temDict["data"] = result[i].data.decode()

                        temDict["confid"] = result[i].confid.decode()
                        temDict["confname"] = result[i].confname.decode()
                        temDict["mtdevicetype"] = result[i].mtdevicetype.decode()

                        # datadict["mtstate"] = callback_data["result"][i].mtstate.decode()
                        # logger.info(datadict)
                        data_callback["pubdata"].append(temDict)
                    logger.info("CLibpubcallback data analysis..........OVER")
                except Exception as e:
                    logger.error(e)

                try:
                    self.upuqueue.put_nowait(data_callback)
                except queue.Full:
                    logger.error('upuclient_pubcallback --> UpuQueue is Full ....')

        else:
            logger.error('Unknown Error ....')

    def get_mt_all_to_watcher(self,nflag):
        logger.info("EXC get_mt_all_to_watcher")
        # userdomain="test"
        mtinfo=MtInfoStruct()
        # mtinfo.userdomain = userdomain.encode('utf-8')
        self.upuclientlib.get_mt_all_to_watcher(self.upuclient, byref(mtinfo), nflag)
#         timer = threading.Timer(time_out, self.on_rpc_timeout, (nflag,))
#         timer.start()
    def subscribe_topic(self,_topic,nflag):
        logger.info("EXC subscribe_topic")
        self.upuclientlib.subscribe_topic(self.upuclient, _topic, nflag)

class upuwatcher_log():
    def __init__(self):
        self.__name__="upuwatcher"


if __name__ == '__main__':


    # upu配置获取
    config.read(os.path.join(CONF_PATH, 'UpuWatcher.ini'))
    #ip = config.get('upuInfo', 'IpAddr')
    port = config.get('upuInfo', 'Port')
    appmoid = config.get('upuInfo', 'appmoid')
    queuesize = int(config.get('upuInfo', 'queuesize'))
    # upudatafile = config.get('upuInfo', 'FilePath')
    upulogfile = config.get('common', 'LogPath')
    parser = argparse.ArgumentParser()
    parser.add_argument('--upu-addr', help='upu地址，支持多个，用英文,隔开，'
                                           '如：python3 upu_watcher.py --upu-addr=172.16.186.208,172.16.186.209',
                        required=True)
    parser.add_argument('--platform-moid', help='域moid，'
                                                '如：python3 upu_watcher.py --platform-moid=mooooooo-oooo-oooo-oooo-defaultplatf',
                        required=True)
    args = parser.parse_args()
    hosts = args.upu_addr.split(',')
    platform_moid = args.platform_moid



    # upu日志模板设置
    logger = load_my_logging_cfg(upuwatcher_log(),upulogfile).getLogger('watcher')
    # logger.setLevel(level=logging.INFO)
    # fh = logging.FileHandler(upulogfile)
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    #                               datefmt="%Y/%m/%d %X")
    # fh.setFormatter(formatter)
    # logger.addHandler(fh)

    # 设置队列大小，默认无限制
    q=queue.Queue(queuesize)

    #初始化upuclient
    upuwatcher=UpuclientWrap(hosts,port,appmoid,q,platform_moid)

    # req_id=0
    # def get_new_reqid(_req_id):
    #     MAX_INT = pow(2, 31) - 1
    #     if _req_id >= MAX_INT:
    #         req_id = 0
    #     _req_id += 1
    #     return _req_id

    try:
        # 判断upu是否连接上
        while True:
            # 连上upu后调用获取全部终端函数
            logger.info(upuwatcher.connectflag)
            if upuwatcher.connectflag:
                upuwatcher.get_mt_all_to_watcher(1)
                # upuwatcher.subscribe_topic(1,10000001)
                # upuwatcher.subscribe_topic(2,10000002)
                break
            else:
                time.sleep(1)
    except:
        logger.info(traceback.format_exc())

