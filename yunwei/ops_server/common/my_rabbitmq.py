#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

import pika
import os
import json
import logging
from common.global_func import get_conf

logger = logging.getLogger('ops.' + __name__)


class RMQClient:
    def __init__(self, hosts, port=5672, username='dev', password='dev'):
        self.hosts = hosts
        self.port = port
        self.username = username
        self.password = password
        self._validate()
        self.user_pwd = pika.PlainCredentials(self.username, self.password)
        self.parameters = [pika.ConnectionParameters(
            host=host, port=self.port, credentials=self.user_pwd) for host in self.hosts]
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()

    def _validate(self):
        if not isinstance(self.hosts, list):
            raise Exception('hosts 参数错误')

    def declare_queue(self, queue_name, exclusive=False, auto_delete=True):
        queue = self.channel.queue_declare(queue=queue_name,
                                           exclusive=exclusive,
                                           auto_delete=auto_delete)
        return queue

    def bind_queue(self, exchange, queue, routing_key):
        self.channel.queue_bind(exchange=exchange, queue=queue, routing_key=routing_key)

    def pub_msg(self, msg, exchange, routing_key):
        if self.channel.is_open:
            self.channel.basic_publish(exchange=exchange, routing_key=routing_key, body=msg)
            return True
        else:
            return False

    def set_qos(self):
        self.channel.basic_qos(prefetch_count=0)

    def callback(cls, ch, method, properties, body):
        logger.debug(" [x] Received %r " % body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def consume(self, queue_name, callback=None, auto_ack=True):
        if callback == None:
            self.channel.basic_consume(self.callback,
                                       queue=queue_name, auto_ack=auto_ack)
        else:
            self.channel.basic_consume(callback,
                                       queue=queue_name, auto_ack=auto_ack)
        self.channel.start_consuming()

    def close(self):
        self.channel.close()
        self.connection.close()
