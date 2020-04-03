#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import threading
from daemonize import Daemonize
import logging, logging.handlers
import setproctitle
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'ops.settings'
django.setup()

from terminal_check import terminal_warning_check
from server_check import server_warning_check
from threshold_warning_check import threshold_warning_check
from common.global_func import get_conf

PARENT_NAME = 'ops-warning-timer-process'


def init_logger():
    if sys.platform == 'linux':
        log_file = '%s/warning-timer.log' % get_conf('log', 'path')
    else:
        log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'warning-timer.log')
    if not os.path.exists(os.path.dirname(log_file)):
        os.mkdir(os.path.dirname(log_file))
    formatter = logging.Formatter(
        '%(levelname)-7s %(asctime)-24s %(filename)s %(lineno)4d: %(message)s')

    logger = logging.getLogger('warning-timer')
    logger.setLevel(logging.DEBUG)
    handler = logging.handlers.RotatingFileHandler(
        filename=log_file, encoding='utf-8')
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return handler


def main():
    logger = logging.getLogger("warning-timer")
    setproctitle.setproctitle(PARENT_NAME)
    logger.info('warning-timer run. pid = %s\n' % os.getpid())
    logger.info('-' * 20)

    # 查询间隔，默认60s
    terminal_period = get_conf('warning_timer', 'terminal_period') \
        if get_conf('warning_timer', 'terminal_period') else 60
    server_period = get_conf('warning_timer', 'server_period') \
        if get_conf('warning_timer', 'server_period') else 60
    threshold_period = get_conf('warning_timer', 'threshold_period') \
        if get_conf('warning_timer', 'threshold_period') else 60
    # 重复告警间隔，默认6h
    terminal_alarm_interval = get_conf('warning_timer', 'terminal_alarm_interval') \
        if get_conf('warning_timer', 'terminal_alarm_interval') else 21600
    server_alarm_interval = get_conf('warning_timer', 'server_alarm_interval') \
        if get_conf('warning_timer', 'server_alarm_interval') else 21600
    threshold_alarm_interval = get_conf('warning_timer', 'threshold_alarm_interval') \
        if get_conf('warning_timer', 'threshold_alarm_interval') else 21600
    # 终端告警相关检测线程
    terminal_warning_check_t = threading.Thread(
        target=terminal_warning_check,
        args=(
            terminal_period,
            terminal_alarm_interval
        ),
        daemon=True
    )
    # 服务器告警相关检测线程
    server_warning_check_t = threading.Thread(
        target=server_warning_check,
        args=(
            server_period,
            server_alarm_interval
        ),
        daemon=True
    )
    # 阈值告警相关检测线程
    threshold_warning_check_t = threading.Thread(
        target=threshold_warning_check,
        args=(
            threshold_period,
            threshold_alarm_interval
        ),
        daemon=True
    )

    terminal_warning_check_t.start()
    server_warning_check_t.start()
    threshold_warning_check_t.start()
    terminal_warning_check_t.join()
    server_warning_check_t.join()
    threshold_warning_check_t.join()
    logger.info('*' * 30)


if __name__ == '__main__':
    log_handler = init_logger()
    logger = logging.getLogger("warning-timer")
    logger.info('warning-timer start...')
    keep_fds = [
        log_handler.stream.fileno(),
    ]
    pid_path = os.path.join('/opt/data/ops/', 'warning-timer.pid')
    if not os.path.exists(os.path.dirname(pid_path)):
        os.makedirs(os.path.dirname(pid_path), exist_ok=True)
    daemon = Daemonize(
        app=PARENT_NAME,
        action=main,
        pid=pid_path,
        logger=logger,
        keep_fds=keep_fds
    )
    daemon.start()
