#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@shanchenglong
@time: 2019-1-18
"""

import os
import re
import sys
import json
import time
import logging
from common.setting import config, load_my_logging_cfg
from common.globalfun import save_json, format_timestamp

cur_dir = os.path.dirname(sys.argv[0])
if cur_dir:
    os.chdir(cur_dir)
cur_env_path = os.path.join(os.getcwd(), "lib/site-packages")
sys.path.append(cur_env_path)
from kazoo.client import KazooClient
from kazoo.client import DataWatch


# logger class
class ZkWatcherLogger:
    __slots__ = ['__name__']

    def __init__(self):
        self.__name__ = "ZKWatcher"

    @staticmethod
    def get_logger(path):
        return load_my_logging_cfg(ZkWatcherLogger(), path).getLogger("watcher")


# list of apps that needn't to cheek
exclude_business = ["java", "radar-server", "dms", "glusterfsd", "glusterfs", "zookeeper", "boardmanager"]
cmp_pattern = re.compile("status = (\w+)")

config.read('conf/extra_config.ini')
# creat logger recording the running process
try:
    log_path = config.get("Watcher", "LogPath")
except Exception:
    # 获取不到日志配置就不记录日志
    logging.basicConfig(level=logging.FATAL)
    logger = logging.getLogger("ZKWatcher")
else:
    logger = ZkWatcherLogger.get_logger(log_path)
    logger.setLevel(level=logging.INFO)

# read the main config
try:
    with open('conf/ZKWatcher.ini') as f:
        zk_cfg = json.load(f)
except Exception as err:
    logger.error("Can't find the main config file: conf/ZKWatcher.ini")
    exit(1)


def get_config():
    """
    get options from configuration file, default /conf/DataWatcher.ini
    :return: zookeeper_ip_port/data_path/config.json_path
    """
    try:
        zk_ip = zk_cfg['DeployInfo']['zookeeperInfo']['IpAddr']
        zk_port = zk_cfg['DeployInfo']['zookeeperInfo']['Port']
        domain_moid = zk_cfg['DeployInfo']['NodeInfo']['domain_moid']
    except Exception as err:
        logger.error(err)
        return None

    zk_ip_port = ",".join([ip + ':' + zk_port for ip in zk_ip.split(",")])
    return zk_ip_port, domain_moid


class AssembleZKInfo:
    """
    read all installed businesses from deploy.ini and read all business information from deploy.json,
    then assemble zookeeper path for all businesses
    """
    def __init__(self, cfg_json):
        self.cfg_json = cfg_json
        self.apps_zk_path = {}

    def _get_json_info(self):
        """
        read all apps information from json
        :return:list of app information
        """
        try:
            app_info = self.cfg_json['DeployApp']
            room_info = self.cfg_json['DeployRoom']
        except Exception as err:
            logger.error(err)
            return -1
        else:
            return app_info, room_info

    def _make_zk_path(self):
        """
        assemble zookeeper path
        """
        apps, rooms = self.apps_information

        for app_info in apps:
            domain_moid = app_info.get("Domain_moid")
            machineRoom_moid = app_info.get("MachineRoom_moid")
            group_name = app_info.get("Group_name")
            group_moid = app_info.get("Group_moid")
            key = app_info.get("Key")
            moid = app_info.get("Moid")

            if key in exclude_business:
                # 特殊业务不监控
                continue

            if all([domain_moid, machineRoom_moid, group_name, group_moid, key, moid]):
                key_moid = key + "_" + moid
                group_name_moid = group_name + '_' + group_moid
                zk_path = "/".join(["/service", domain_moid, machineRoom_moid, group_name_moid, key_moid, "status"])
                self.apps_zk_path.setdefault(zk_path, key)
            else:
                logger.warning("make zk_path error: ", app_info)

        for room_info in rooms:
            domain_moid = room_info.get("Domain_moid")
            machineRoom_moid = room_info.get("MachineRoom_moid")
            name = room_info.get("name")

            if all([domain_moid, machineRoom_moid, name]):
                zk_path = "/".join(["/service", domain_moid, machineRoom_moid, "status"])
                self.apps_zk_path.setdefault(zk_path, name)
            else:
                logger.warning("make zk_path error: ", room_info)

    def _get_zk_info(self):
        """
        make zookeeper path
        :return: a dict of zk_path for all installed apps, None if ERR
        """

        self.apps_information = self._get_json_info()
        if self.apps_information == -1:
            return None
        self._make_zk_path()
        if len(self.apps_zk_path) == 0:
            logger.warning("make zk_path abnormal, please check config_json file!")
            return None
        return self.apps_zk_path

    def get_zk_info(self):
        return self._get_zk_info()


class ZKWatcher:
    """
    set ZNode watcher ang handing data changes
    """
    def __init__(self, host_port, data_path="/opt/log/datawatcher/", domain_moid="", timeout=10):
        self._host_port = host_port
        self._timeout = timeout
        self._zk = KazooClient(hosts=self._host_port, timeout=self._timeout, randomize_hosts=True,
                               connection_retry={'max_tries': -1, 'delay': 1, 'backoff': 1})
        self._zk.add_listener(self.connection_listener)
        self._data_path = data_path
        self._zk_paths = {}
        self._name = 'zkwatcher'
        self._domain_moid = domain_moid
        self._logger = load_my_logging_cfg(self.__class__, data_path).getLogger("syslog")

    def start(self, zk_paths):
        self._zk_paths = zk_paths
        assert isinstance(zk_paths, dict), "parameters must be dict"

        while True:
            try:
                self._zk.start()
            except Exception as err:
                logger.error("connect zookeeper server error: %s" % err)
                time.sleep(2)
            else:
                break
        self._watcher(self._zk_paths)

    def _watcher(self, zk_paths):
        for zk_path in zk_paths.keys():
            @self._zk.DataWatch(zk_path)
            def my_dw(data, stat, event):
                if event is None:
                    # 首次添加监听
                    if data is None:
                        # 首次监听,节点未创建
                        logger.warning("Adding watcher, but ZNode isn't exits: %s" % zk_path)
                    elif not data:
                        # 首次监听,节点没数据
                        logger.warning("Adding watcher, but ZNode is empty: %s" % zk_path)
                    else:
                        # 首次监听,节点已创建且数据不为空
                        self._handler(data, stat.mtime, zk_path, "CHANGE")
                else:
                    # 推送消息
                    if data is None:
                        # 删除节点
                        self._handler(b"", int(time.time()*1000), event.path, event.type)
                    else:
                        # 正常情况
                        self._handler(data, stat.mtime, event.path, event.type)

    def stop(self):
        self._zk.stop()
        self._zk.close()

    def _handler(self, data, ctime, path, event_type):
        """
        handing ZNode data changes
        :param data: ZNode data
        :param ctime: timestamp of the ZNode changing
        :type ctime: int
        :param path: path of ZNode
        :param event_type: ZNode data
        :return:
        """
        if event_type == 'DELETED':
            status = "offline"
        else:
            status = re.findall(cmp_pattern, data.decode('utf-8'))
            if status[0] == 'started' and event_type == 'CHANGED':
                status = "online"
            else:
                return None
        beat = dict(name=self._name, platform_moid=self._domain_moid)

        timestamp = format_timestamp(ctime / 1000)
        path_spt = path.split("/")
        if len(path_spt) == 7:
            typ = "app"
            name = path_spt[5].rpartition('_')[0]
            moid = path_spt[5].rpartition('_')[2]
        elif len(path_spt) == 5:
            typ = "machine_room"
            name = self._zk_paths.get(path)
            moid = path_spt[3]
        else:
            # 路径格式错误
            logger.warning("path format error: %s" % path)
            return None

        source = dict(zip(['name', 'moid', 'type', 'status', 'zknode'], [name, moid, typ, status, path]))
        save_json(dict(zip(['@timestamp', 'beat', 'source'], [timestamp, beat, source])), self._logger)

    @staticmethod
    def connection_listener(state):
        """
        监控zk连接状态,记录zk状态变化
        LOST: Register somewhere that the session was lost
        SUSPENDED: Handle being disconnected from Zookeeper
        CONNECTED: Handle being connected/reconnected to Zookeeper
        """
        logger.info("zk connection changes: %s" % state)


def main():
    configuration = get_config()
    if configuration is None:
        logger.error('get configuration from config_file failed')
        raise Exception("get configuration from config_file failed")
    zk_ip_port, domain_moid = configuration

    zk_inf_obj = AssembleZKInfo(zk_cfg)
    biz_inf = zk_inf_obj.get_zk_info()

    if biz_inf is None:
        logger.error('get zookeeper information from json_file failed')
        raise Exception("get zookeeper information from json_file failed")

    zk_watcher = ZKWatcher(zk_ip_port, domain_moid=domain_moid)
    zk_watcher.start(biz_inf)


if __name__ == '__main__':
    main()
    while True:
        time.sleep(3600)
