#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

import logging
from collections import Iterable

from kafka import KafkaProducer
from kafka.errors import KafkaError

logger = logging.getLogger('watcher')


class Producer:
    def __init__(self, bootstrap_servers):
        """

        :param bootstrap_servers: kafka集群地址列表或地址字符串
        """
        self.bootstrap_servers = bootstrap_servers if \
            (not isinstance(bootstrap_servers, str) and
             isinstance(bootstrap_servers, Iterable)) \
            else [bootstrap_servers]
        self.producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers)

    def send(self, topic, value=None, key=None, headers=None, partition=None, timestamp_ms=None):
        try:
            self.producer.send(
                topic=topic,
                value=value,
                key=key,
                headers=headers,
                partition=partition,
                timestamp_ms=timestamp_ms
            )
        except KafkaError as e:
            logger.exception(e)
        except Exception as e:
            logger.exception(e)

    @property
    def is_connected(self):
        return self.producer.bootstrap_connected()


if __name__ == '__main__':
    producer = Producer('10.67.16.101:9092')
