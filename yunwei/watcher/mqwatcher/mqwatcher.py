#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

import sys
import os
import time
import argparse
import re
import json
import threading
from queue import Queue

import setproctitle
import pika
from kafka.errors import KafkaError, NoBrokersAvailable

from common.setting import load_my_logging_cfg, config, CONF_PATH
from common.globalfun import save_json, format_timestamp
from common.kafka_client import Producer


class MQWatcher(object):
    def __init__(self, hosts=('127.0.0.1',), port=5672, username='dev', password='dev', vhost='/',
                 platform_moid='', process_name='mqwatcher', log_path=None,
                 json_queues=(), json_exchanges=(), pb_queues=(), pb_exchanges=(),
                 kafka_hosts=('127.0.0.1',), kafka_port=9092):
        self.hosts = hosts
        self.port = port
        self.username = username
        self.password = password
        self.vhost = vhost
        self.platform_moid = platform_moid
        self.logger = load_my_logging_cfg(self.__class__, log_path).getLogger('watcher')
        self.sys_logger = load_my_logging_cfg(self.__class__, log_path).getLogger('syslog')
        self.json_queues = json_queues
        self.json_exchanges = json_exchanges
        self.pb_queues = pb_queues
        self.pb_exchanges = pb_exchanges
        self.queue = Queue()
        self.process_name = process_name

        self.kafka_hosts = kafka_hosts
        self.kafka_port = kafka_port
        try:
            self.kafka_producer = Producer(['%s:%s' % (kafka_host, self.kafka_port) for kafka_host in self.kafka_hosts])
        except NoBrokersAvailable:
            self.kafka_producer = None
        except KafkaError as e:
            self.logger.exception(e)
            raise e

        # 设置进程名称
        setproctitle.setproctitle(
            sys.argv[0] + ' --mq-addr=%s' % ','.join(hosts) +
            ' --platform-moid=%s' % platform_moid +
            ' --kafka-addr=%s' % ','.join(kafka_hosts) +
            ' --kafka-port=%s' % kafka_port
        )

    @property
    def producer(self):
        if self.kafka_producer:
            return self.kafka_producer
        else:
            try:
                producer = Producer(['%s:%s' % (kafka_host, self.kafka_port) for kafka_host in self.kafka_hosts])
            except KafkaError:
                return None
            else:
                self.kafka_producer = producer
                return producer

    @property
    def connection(self):
        user_pwd = pika.PlainCredentials(self.username, self.password)
        parameters = [pika.ConnectionParameters(host=host, port=self.port, credentials=user_pwd) for host in self.hosts]
        connection = pika.BlockingConnection(parameters)
        return connection

    @property
    def channel(self):
        try:
            if self.connection.is_open:
                channel = self.connection.channel()
                return channel
            else:
                return None
        except Exception as e:
            self.logger.error(str(e))
            return None

    def consumer(self, exchange_name='amq.rabbitmq.trace', queue_name='ops.trace.q', routing_key='deliver.#'):
        # channel = self.get_channel()
        channel = self.channel
        if channel:
            try:
                channel.queue_declare(queue=queue_name, exclusive=False, auto_delete=True)
            except Exception as e:
                self.logger.error(str(e))
            try:
                channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)
            except Exception as e:
                self.logger.error(str(e))
                # 如果无对应exchange，10s后退出线程
                time.sleep(10)
                exit(1)
            channel.basic_qos(prefetch_count=0)
            try:
                for method_frame, properties, body in channel.consume(queue_name):
                    timestamp = format_timestamp(time.time())
                    channel.basic_ack(method_frame.delivery_tag)
                    self.queue.put([method_frame, properties, body, timestamp])
            except Exception as e:
                self.logger.error(str(e))

    def save_trace(self):
        content = {
            '@timestamp': '',
            'beat': {
                'platform_moid': self.platform_moid,
                'name': self.process_name,
                'exchange': '',
                'headers': {}
            },
            'source': ''
        }
        json_exchange_name = [json_exchange[0] for json_exchange in self.json_exchanges]
        pb_exchange_name = [pb_exchange[0] for pb_exchange in self.pb_exchanges]
        json_save_flag = 0
        pb_save_flag = 0

        while True:
            if not self.queue.empty():
                for i in range(self.queue.qsize()):
                    # 队列中拿到的为长度为4的列表，分别赋值给4个变量
                    method_frame, properties, body, timestamp = self.queue.get()
                    # 正则匹配exchange和queue名称
                    pattern = r'deliver\.(.*?\.q):?.*'
                    dssclient_pattern = r'deliver\.(.*)'
                    q_name = re.findall(pattern=pattern, string=method_frame.routing_key)
                    dssclient_q_name = re.findall(pattern=dssclient_pattern, string=method_frame.routing_key)
                    content['@timestamp'] = timestamp
                    content['beat']['exchange'] = method_frame.exchange
                    content['beat']['headers'] = properties.headers

                    # exchange：exchange名字和headers['exchange_name']匹配，且routing_keys包含在headers['routing_keys']中的
                    # queue：headers['exchange_name']为空，且method_frame.routing_keys和queue名字匹配的
                    if properties.headers.get('exchange_name') in json_exchange_name:
                        # exchange名字和headers['exchange_name']匹配
                        now_routing_key = \
                            self.json_exchanges[json_exchange_name.index(properties.headers.get('exchange_name'))][1]
                        # routing_keys中包含*
                        if '*' in now_routing_key:
                            now_routing_key = now_routing_key.split('*')[0]
                            if any((now_routing_key in routing_key) for
                                   routing_key in properties.headers.get('routing_keys')):
                                json_save_flag = 1
                            else:
                                self.logger.debug('drop msg headers: %s' % properties.headers)
                        # routing_keys中不包含*，则为字符串完全匹配
                        elif now_routing_key:
                            if now_routing_key in properties.headers['routing_keys']:
                                json_save_flag = 2
                            else:
                                self.logger.debug('drop msg headers: %s' % properties.headers)
                        # routing_keys为空字符串，则此exchange的消息全部保存
                        else:
                            json_save_flag = 3
                    elif (not properties.headers.get('exchange_name')) and q_name and q_name[0] in self.json_queues:
                        # headers['exchange_name']为空，且method_frame.routing_keys和queue名字匹配的
                        json_save_flag = 4
                    elif (method_frame.exchange == 'alternate.exchange'):
                        # 无法路由的消息（json格式）
                        json_save_flag = 5
                    elif properties.headers.get('exchange_name') in pb_exchange_name:
                        # pb类型消息的exchange匹配
                        now_routing_key = \
                            self.pb_exchanges[pb_exchange_name.index(properties.headers.get('exchange_name'))][1]
                        if '*' in now_routing_key:
                            now_routing_key = now_routing_key.split('*')[0]
                            if any((now_routing_key in routing_key) for
                                   routing_key in properties.headers.get('routing_keys')):
                                pb_save_flag = 1
                            else:
                                self.logger.debug('drop msg headers: %s' % properties.headers)
                        # routing_keys中不包含*，则为字符串完全匹配
                        elif now_routing_key:
                            if now_routing_key in properties.headers['routing_keys']:
                                pb_save_flag = 2
                            else:
                                self.logger.debug('drop msg headers: %s' % properties.headers)
                        # routing_keys为空字符串，则此exchange的消息全部保存
                        else:
                            pb_save_flag = 3

                    elif (not properties.headers.get('exchange_name')) and dssclient_q_name:
                        # 轮询pb_queue列表，使用正则匹配当前queue名称，匹配成功则为需要保存的消息
                        for pb_queue in self.pb_queues:
                            if re.search(pb_queue, dssclient_q_name[0]):
                                # pb类型消息的queue匹配
                                pb_save_flag = 4
                                break

                    else:
                        # 丢弃的数据
                        json_save_flag, pb_save_flag = 0, 0
                        self.logger.debug(
                            'drop msg headers: %s, method_frame: %s' % (properties.headers, method_frame.routing_key))

                    if json_save_flag:
                        # content['flag'] = json_save_flag
                        json_save_flag = 0
                        try:
                            content['source'] = json.loads(body.decode(encoding='utf-8'))
                            save_json(content)
                        except Exception as e:
                            self.logger.error(str(e))

                    if pb_save_flag:
                        pb_save_flag = 0
                        try:
                            if self.producer and self.producer.is_connected:
                                self.producer.send(
                                    'ods.dsspb',
                                    body,
                                    headers=[
                                        ('headers', json.dumps(properties.headers).encode('utf-8')),
                                        ('exchange', method_frame.exchange.encode('utf-8')),
                                        ('platform_moid', self.platform_moid.encode('utf-8')),
                                    ]
                                )
                            else:
                                self.logger.warning(
                                    'kafka [%s] is not connected, some data will be discarded...' %
                                    ['%s:%s' % (kafka_host, self.kafka_port) for kafka_host in self.kafka_hosts]
                                )
                            # content['source'] = str(base64.b64encode(body), encoding='utf-8')
                            # save_json(content, sys_logger=self.sys_logger)
                        except Exception as e:
                            self.logger.exception(e)
            else:
                # self.logger.info('queue is empty...wait')
                time.sleep(0.001)


def main():
    conf_path = os.path.join(CONF_PATH, 'mqwatcher.json')
    with open(conf_path, 'r')as f:
        config = json.load(f)
    if sys.platform == 'linux':
        parser = argparse.ArgumentParser()
        parser.add_argument('--mq-addr',
                            help='rabbitmq地址，支持多个，用英文,隔开，'
                                 '如：python3 mqwatcher.py --mq-addr=172.16.186.208,172.16.186.209',
                            required=True)
        parser.add_argument('--platform-moid',
                            help='域moid，'
                                 '如：python3 mqwatcher.py --platform-moid=mooooooo-oooo-oooo-oooo-defaultplatf',
                            required=True)
        parser.add_argument('--kafka-addr',
                            help='kafka地址，支持多个，用英文,隔开，'
                                 '如：python3 mqwatcher.py --kafka-addr=127.0.0.1',
                            required=False)
        parser.add_argument('--kafka-port',
                            help='kafka端口，'
                                 '如：python3 mqwatcher.py --kafka-port=9092',
                            required=False)
        args = parser.parse_args()

        hosts = args.mq_addr.split(',')
        platform_moid = args.platform_moid
        # kafka相关参数解析
        if args.kafka_addr:
            kafka_hosts = args.kafka_addr.split(',')
        else:
            kafka_hosts = ['127.0.0.1']
        if args.kafka_port:
            kafka_port = args.kafka_port
        else:
            kafka_port = 9202
        if not os.path.exists(conf_path):
            # 配置文件路径不存在即报错
            parser.print_help()
            print('\ncannot access %s: No such file or directory' % conf_path)
            exit(1)

        log_path = config.get('watcher').get('log_path')
        log_level = config.get('watcher').get('log_level', 'DEBUG')
    else:
        log_path = './log/'
        log_level = 'DEBUG'
        platform_moid = config.get('node_info').get('platform_domain_moid')
        hosts = config.get('mq_info').get('mq_ip_addr')
        kafka_hosts = ['127.0.0.1']
        kafka_port = 9202

    port = config.get('mq_info').get('mq_port')
    username = config.get('mq_info').get('user_name')
    password = config.get('mq_info').get('user_pwd')
    vhost = config.get('mq_info').get('vhost')
    process_name = 'mqwatcher'
    json_queues = config.get('json').get('queue')
    json_exchanges = config.get('json').get('exchange')
    pb_queues = config.get('pb').get('queue')
    pb_exchanges = config.get('pb').get('exchange')
    extra_consumers = config.get('watcher').get('extra_consumers')
    thread_name_l = [
        't_consumer',
        't_save_trace',
    ]

    watcher = MQWatcher(hosts=hosts, port=port, username=username, password=password, vhost=vhost,
                        platform_moid=platform_moid, process_name=process_name, log_path=log_path,
                        json_queues=json_queues, json_exchanges=json_exchanges,
                        pb_queues=pb_queues, pb_exchanges=pb_exchanges, kafka_hosts=kafka_hosts, kafka_port=kafka_port)
    pid = os.getpid()
    logger = watcher.logger
    logger.setLevel(log_level)
    logger.info('MQWatcher started with pid:%s, config file is %s' % (pid, conf_path))

    try:
        # 消费者线程，向queue中投递消息
        t_consumer = threading.Thread(target=watcher.consumer, name='t_consumer')
        t_consumer.start()
        # 无法路由消息消费者线程，向queue中投递消息
        for extra_consumer in extra_consumers:
            thread_name_l.append('t_%s' % extra_consumer)
            extra_t = threading.Thread(
                target=watcher.consumer,
                name='t_%s' % extra_consumer,
                args=(
                    extra_consumers.get(extra_consumer).get('exchange'),
                    extra_consumers.get(extra_consumer).get('queue'),
                    extra_consumers.get(extra_consumer).get('routing_key')
                )
            )
            extra_t.start()

        # 存储线程，向syslog写日志
        t_save_trace = threading.Thread(target=watcher.save_trace, name='t_save_trace')
        t_save_trace.start()
        while True:
            for thread_name in thread_name_l:
                # 如果线程未存活，重建线程
                if thread_name not in str(threading.enumerate()):
                    if thread_name == 't_consumer':
                        logger.info('restart t_consumer thread')
                        t_consumer = threading.Thread(target=watcher.consumer, name='t_consumer')
                        t_consumer.start()
                    elif thread_name == 't_save_trace':
                        logger.info('restart save_trace thread')
                        t_save_trace = threading.Thread(target=watcher.save_trace, name='t_save_trace')
                        t_save_trace.start()
                    else:
                        extra_t = threading.Thread(
                            target=watcher.consumer,
                            name=thread_name,
                            args=(
                                extra_consumers.get(thread_name.lstrip('t_')).get('exchange'),
                                extra_consumers.get(thread_name.lstrip('t_')).get('queue'),
                                extra_consumers.get(thread_name.lstrip('t_')).get('routing_key'),
                            )
                        )
                        extra_t.start()

            time.sleep(3)
            logger.info('check threads alive...')

    except Exception as e:
        logger.error(str(e))


if __name__ == '__main__':
    main()
