#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from daemonize import Daemonize
import logging
import logging.handlers
import setproctitle
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'ops.settings'
django.setup()

from common.global_func import get_conf
from exec_custom_scripts import main as exec_main

PARENT_NAME = 'ops-custom-scripts-process'

logger = logging.getLogger('custom-scripts')


def init_logger():
    log_file_name = 'custom-scripts.log'
    if sys.platform == 'linux':
        log_file = '%s/%s' % (get_conf('log', 'path'), log_file_name)
    else:
        log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), log_file_name)
    if not os.path.exists(os.path.dirname(log_file)):
        os.mkdir(os.path.dirname(log_file))
    formatter = logging.Formatter(
        '%(levelname)-7s %(asctime)-24s %(filename)s %(lineno)4d: %(message)s')

    logger = logging.getLogger('custom-scripts')
    logger.setLevel(logging.DEBUG)
    handler = logging.handlers.RotatingFileHandler(
        filename=log_file, encoding='utf-8')
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return handler


def main():
    setproctitle.setproctitle(PARENT_NAME)
    logger.info('custom-scripts-timer run. pid = %s\n' % os.getpid())
    logger.info('-' * 20)

    exec_main()


if __name__ == '__main__':
    log_handler = init_logger()
    logger = logging.getLogger("custom-scripts")
    keep_fds = [
        log_handler.stream.fileno(),
    ]
    pid_path = os.path.join('/opt/data/ops/', 'custom-scripts-timer.pid')
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
