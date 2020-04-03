#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

import pika
import logging
from common.global_func import get_conf


class RMQClient:
    def __init__(self):
        self.channel = self.get_rmq_client()

    @property
    def logger(self):
        return logging.getLogger("warning-timer")

    def get_rmq_client(self):
        logger = self.logger
        hosts = get_conf('rabbitmq_core', 'host').split(',')
        port = get_conf('rabbitmq_core', 'port')
        username = get_conf('rabbitmq_core', 'username')
        password = get_conf('rabbitmq_core', 'password')

        user_pwd = pika.PlainCredentials(username, password)
        parameters = [pika.ConnectionParameters(host=host, port=port, credentials=user_pwd) for host in hosts]
        connection = pika.BlockingConnection(parameters)
        try:
            if connection.is_open:
                channel = connection.channel()
                return channel
            else:
                return None
        except Exception as e:
            logger.exception(e)
            return None

    def pub_msg(self, msg, exchange='wps.notify.ex', routing_key=''):
        logger = self.logger
        if self.channel:
            try:
                logger.debug(self.channel)
                self.channel.basic_publish(
                    exchange=exchange,
                    routing_key=routing_key,
                    body=msg
                )
                return True
            except Exception as e:
                logger.exception(e)
                return False
        else:
            self.channel = self.get_rmq_client()
            return False
