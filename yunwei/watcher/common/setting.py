#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

import os
import configparser
import logging.config

# 路径定义
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONF_PATH = os.path.join(BASE_PATH, 'conf')

# 配置文件
config = configparser.ConfigParser()


def load_my_logging_cfg(App, log_path):
    """
    定义日志格式
    :param App: Watcher类
    :param log_path: 日志文件路径
    :return: logging
    """
    # 日志格式
    standard_format = '[%(asctime)s][%(levelname)s][%(filename)s:%(lineno)d][%(threadName)s][%(message)s]'
    syslog_format = App.__name__.lower() + ':%(message)s'

    LOGGING_DIC = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': standard_format
            },
            'syslog': {
                'format': syslog_format
            }
        },
        'filters': {},
        'handlers': {
            # 打印到文件的日志
            'default': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件
                'formatter': 'standard',
                'filename': os.path.join(log_path, 'DataWatcher.log'),  # 日志文件
                'encoding': 'utf-8',  # 日志文件的编码
            },
            'syslog': {
                'level': 'DEBUG',
                'class': 'logging.handlers.SysLogHandler',
                # 'address': ('10.68.5.101', 514),
                'address': ('127.0.0.1', 514),
                # 'address': ('172.16.186.208', 514),
                # 'facility': SysLogHandler.LOG_LOCAL3,
                # 'facility': 'local3',
                'formatter': 'syslog',
            }
        },
        'loggers': {
            # logging.getLogger(__name__)拿到的logger配置
            'watcher': {
                'handlers': ['default'],  # 这里把上面定义的handler加上，即log数据既写入文件
                'level': 'DEBUG',
                'propagate': True,  # 向上（更高level的logger）传递
            },
            'syslog': {
                'handlers': ['syslog'],
                'level': 'DEBUG',
                'propagate': True
            }
        },
    }

    if not os.path.isdir(log_path):
        os.makedirs(log_path)
    # 将日志文件替换为模块本身的日志路径
    LOGGING_DIC['handlers']['default'].update(
        {'filename': os.path.join(os.path.abspath(log_path), '%s.log' % App.__name__.lower())})
    logging.config.dictConfig(LOGGING_DIC)
    return logging

