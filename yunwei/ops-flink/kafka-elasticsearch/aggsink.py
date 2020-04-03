import threading
from kafka import KafkaConsumer
from elasticsearch import Elasticsearch
import datetime
from config import *

def sink_to_elasticsearch(es_server,timeout_param,kafka_topic,kafka_bootstrap,encoding_type,index_head,system,domain_moid,doctype):
	
	es = Elasticsearch([es_server], timeout=timeout_param)

	consumer = KafkaConsumer(kafka_topic,bootstrap_servers=[kafka_bootstrap])
	for msg in consumer:
		bs=msg.value
		bs_str= str(bs, encoding = encoding_type)
		index_name=index_head+'-'+system+'-'+domain_moid+'-'+datetime.datetime.now().strftime('%Y.%m-%V')
		print(index_name)
		re = es.index(index=index_name, doc_type=doctype, body=bs_str)


def main():
	for app in agg:
		system_name=agg[app]
		print(system_name)
		param=dict()
		es_server=elasticsearch_server
		timeout_param=timeout_parameter
		kafka_topic=system_name
		kafka_bootstrap=bootstrap_server
		index_head=platform
		t1 = threading.Thread(target=sink_to_elasticsearch, args=(es_server,timeout_param,kafka_topic,kafka_bootstrap,encoding_type,index_head,system_name,domain_moid,doctype,))
		t1.start()

if __name__=='__main__':
	main()
