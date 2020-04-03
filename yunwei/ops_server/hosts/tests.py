from django.test import TestCase

# Create your tests here.

from common.my_elastic import es_client
from elasticsearch_dsl import Search, Q, A, MultiSearch
import json


# def dsl(es_client, _query, _filter, _aggs, _size, *args, **kwargs):
#     # s = Search(using=es_client, index='metricbeat-*').filter('range', **{'@timestamp': {'gte': 'now-24h/m', 'lte': 'now/m'}})
#     s = Search(using=es_client, index='metricbeat-*')
#     # s = s.filter('range', **{'@timestamp': {'gte': 'now-24h/m', 'lte': 'now/m'}})
#
#     _filter = [['range', {'@timestamp': {"gte": "now-24h/m", "lte": "now/m"}}]]
#     _query = [['match', {'metricset.name': 'cpu'}],
#               ['match', {'beat.machine_moid': '9ef403ca-0f04-11e9-b9f7-a3f569b0ab2b'}]]
#     _aggs = {
#         'bucket': [['by_time', 'date_histogram', {"field": "@timestamp", "interval": "360000ms", "time_zone": "+08:00",
#                                                   "format": "yyyy-MM-dd HH:mm:ss", "min_doc_count": 0}]],
#         'metric': [['total_pct', 'avg', {'field': 'system.cpu.total.pct'}],
#                    ['idle_pct', 'avg', {'field': 'system.cpu.idle.pct'}]]
#     }
#     _size = 0
#     for f in _filter:
#         s = s.filter(f[0], **f[1])
#     for q in _query:
#         s = s.query(q[0], **q[1])
#
#     for b in _aggs['bucket']:
#         s.aggs.bucket(b[0], b[1], **b[2])
#     for m in _aggs['metric']:
#         s.aggs.metric(m[0], m[1], **m[2])
#     s = s[0:_size]
#     response = s.execute()
#     # print(json.dumps(s.to_dict()))
#     return response
#
#
# # r = dsl(es_client, 1,2,3,4)
#
# # print(dir(r), r.hits.hits, r.aggregations.idle_pct.value)
# # body = {
# #     "_source": [
# #         "@timestamp",
# #         "system.filesystem.total",
# #         "system.filesystem.free",
# #         "system.filesystem.device_name"
# #     ],
# #     "query": {
# #         "bool": {
# #             "must": [{
# #                 "match": {
# #                     "metricset.name": "filesystem"
# #                 }
# #             },
# #             {
# #             	"match":{
# #             		"beat.machine_moid":"9ef403ca-0f04-11e9-b9f7-a3f569b0ab2b"
# #             	}
# #             }
# #             ],
# #             "filter": {
# #                 "range": {
# #                     "@timestamp": {
# #                         "gte": "now-1m/m"
# #                     }
# #                 }
# #             }
# #         }
# #     }
# # }
# #
#
#
# #
# # # s = Search(using=es_client, index="metricbeat-*") \
# # #     .filter("match", category="search") \
# # #     .query("match", title="python")   \
# # #     .exclude("match", description="beta")
# # #
# # # s.aggs.bucket('per_tag', 'terms', field='tags') \
# # #     .metric('max_lines', 'max', field='lines')
# #
# s = Search(using=es_client, index='metricbeat-*') \
#     .filter('range', **{'@timestamp': {"gte": "now-24h/m", "lte": "now/m"}}) \
#     .query('match', **{'metricset.name': 'cpu'}) \
#     .query('match', **{'beat.machine_moid': '9ef403ca-0f04-11e9-b9f7-a3f569b0ab2b'}) \
#
# s.aggs.bucket('by_time', 'date_histogram', **{
#     "field": "@timestamp",
#     "interval": "360000ms",
#     "time_zone": "+08:00",
#     "format": "yyyy-MM-dd HH:mm:ss",
#     "min_doc_count": 0
# }).metric('total_pct', 'avg', field='system.cpu.total.pct') \
#     .metric('idle_pct', 'avg', field='system.cpu.idle.pct')
# s = s[0:0]
# print(json.dumps(s.to_dict()))
#
# response = s.execute()
# print(response)
# #
# #
#
# s2 = Search(using=es_client, index='metricbeat-*')
# s2 = s2.filter('range', **{'@timestamp': {"gte": "now-24h/m", "lte": "now/m"}})
# s2 = s2.query('match', **{'metricset.name': 'cpu'})
# s2 = s2.query('match', **{'beat.machine_moid': '9ef403ca-0f04-11e9-b9f7-a3f569b0ab2b'})
#
# s2.aggs.bucket('by_time', 'date_histogram', **{
#     "field": "@timestamp",
#     "interval": "360000ms",
#     "time_zone": "+08:00",
#     "format": "yyyy-MM-dd HH:mm:ss",
#     "min_doc_count": 0
# })
#
# s2.aggs['by_time'].metric('total_pct', 'avg', field='system.cpu.total.pct')
# s2.aggs['by_time'].metric('idle_pct', 'avg', field='system.cpu.idle.pct')
# s2 = s2[0:0]
# print('s2', json.dumps(s2.to_dict()))
#
# # s_uptime = Search(using=es_client, index='metricbeat-*') \
# #     .source(["system","@timestamp"]) \
# #     .filter('range', **{'@timestamp':{"gte": "now-5m/m"}}) \
# #     .query('match', **{'metricset.name': 'uptime'}) \
# #     .query('match', **{'beat.machine_moid': '9ef403ca-0f04-11e9-b9f7-a3f569b0ab2b'})
# #
# # s_uptime.sort()
# # s_uptime = s_uptime[0]
# # response_uptime = s_uptime.execute()
# #
# # data = dict()
# # for ret in response_uptime:
# #     data['uptime'] = ret.system.uptime.duration.ms
# #     # print(ret.system.uptime.duration.ms)
# #     data['machine_moid'] = '9ef403ca-0f04-11e9-b9f7-a3f569b0ab2b'
# # print(data)
# #
# #     # ret = es_client.search(index='metricbeat-*', doc_type='doc', body=body, filter_path=['hits.hits._source.*', 'hits.total']) # filter_path=['hits.hits._source.*', 'hits.total']
# # # import json
# # # print(json.dumps(ret))
# # data = dict()
# # l = []
# # data['total'] = []
# # data['idle'] = []
# # for ret in response.aggregations.by_time.buckets:
# #     data['total'].append([ret.key, ret.total_pct.value])
# #     data['idle'].append([ret.key, ret.idle_pct.value])
# # print(ret.key, ret.idle_pct.value, ret.total_pct.value)
# # for i in ret:
# #     print('i: ',i)
# # print(l)
# import json
# # print(json.dumps(data))
#
# # from common.my_elastic import es_client
#
# # l = []
# # for field in es_client.fields_dic.get('load'):
# #     l.append([field.replace('.','_'), 'avg', {'field': field}])
#
#
# # x = [[field.replace('.','_'), 'avg',{'field': field}, field for field in es_client.fields_dic.get(metricset_name)]]
# # print(l)
#
#
# # class Request:
# #     def __init__(self):
# #         self.data = {}
# # request = Request()
# # metricset_name = 'load'
# # machine_moid = '9ef403ca-0f04-11e9-b9f7-a3f569b0ab2b'
# # start_time, end_time, interval = es_client.get_time_info(request)
# # _query = [['match', {'metricset.name': metricset_name}], ['match', {'beat.machine_moid': machine_moid}]]
# # _filter = [['range', {'@timestamp': {"gte": start_time, "lte": end_time}}]]
# # metric = []
# # for field in es_client.fields_dic.get(metricset_name):
# #     metric.append([field.replace('.', '_'), 'avg', {'field': field}])
# #
# # _aggs = {
# #     'bucket':[['by_time', 'date_histogram', {
# #         "field": "@timestamp", "interval": str(interval)+'ms',
# #         "time_zone": "+08:00", "format": "yyyy-MM-dd HH:mm:ss", "min_doc_count": 0
# #     }]],
# #     'metric':metric,
# # }
# #
# # x = es_client.get_es_data(request, es_client, _query, _filter, _aggs, _size=0)
# #
# # print(x)
#
# b = [
#     {'bucket': ['by_time', 'date_histogram',
#                  {'field': '@timestamp', 'interval': '360000ms', 'time_zone': '+08:00', 'format': 'yyyy-MM-dd HH:mm:ss',
#                   'min_doc_count': 0}],
#      'metric': [['system_network_in_bytessystem_network_out_bytes', 'avg',
#                                                     {'field': 'system.network.in.bytessystem.network.out.bytes'}]]}
# ]
#
# x = {
#    "size": 0,
#    "query": {
#       "bool": {
#       "must": [
#         { "match": { "metricset.name":"network" }},
#         {"match": { "system.network.name": "lo"}}
#         ],
#       "filter": {
#           "range": {
#               "@timestamp": {
#                   "gte": "now-9h"}
#                   }
#               }
#         }
#
#    },
#   "aggs": {
#       "time": {
#          "date_histogram": {
#             "field": "@timestamp",
#             "interval": "10m",
#             "format": "yyyy-MM-dd HH:mm:ss",
#             "time_zone": "+08:00",
#             "min_doc_count" : 0
#          },
#          "aggs": {
#             "in_bytes": {
#                "max": {
#                   "field": "system.network.in.bytes" }
#                },
#                  "bytes_deriv": {
#                    "derivative": {
#                      "buckets_path": "in_bytes",
#                      "unit": "10m"
#                    }
#                  }
#             }
#          }
#       }
# }
#
#
#
# # from elasticsearch_dsl import MultiSearch, Search
#
# s3 = Search(using=es_client, index='metricbeat-*')
# s3 = s3.filter('range', **{'@timestamp': {"gte": 'now-20m/m', "lte": 'now/m'}})
# s3 = s3.query('match',**{ "metricset.name":"network" })
# s3 = s3.query('match',**{ "system.network.name": "lo"})
#
# s3.aggs.bucket('by_time', 'date_histogram', **{
#                         "field": "@timestamp", "interval": '360000ms',
#                         "time_zone": "+08:00", "format": "yyyy-MM-dd HH:mm:ss", "min_doc_count": 0
#                     })
# s3.aggs['by_time'].metric('in_bytes', 'max', **{"field": "system.network.in.bytes"})
# s3.aggs['by_time'].pipeline('bytes_deriv',"derivative",**{"buckets_path": "in_bytes",
#                      "unit": "360000ms"})
# print('s3',json.dumps(s3.to_dict()))





s1 = Search()
s1 = s1.query('match', **{'metricset.name': 'cpu'})

s1 = s1[0:1]


s2 = Search()
s2 = s2.query('match', **{'metricset.name': 'core'})
s2 = s2[0:1]


s3 = Search()
q = Q('match', **{'metricset.name': 'memory',}) & ~Q('match', **{ 'beat.machine_moid':'3973d1e0-3576-11e9-9304-001e67e37d47',}) & ~Q('match', **{'beat.machine_moud':'50981888-6652-11e9-8da9-001e67e37d47'})
# s3 = s3.query('match', **{'metricset.name': 'memory',})
# s3 = s3.query('match', **{ 'beat.machine_moid':'3973d1e0-3576-11e9-9304-001e67e37d47',})
s3 = s3.query(q)
s3 = s3[0:1]

m = MultiSearch(using=es_client)

m = m.add(s1)
m = m.add(s2)
m = m.add(s3)

# print(m.to_dict)

print(json.dumps(m.to_dict()))

responses = m.execute()

for response in responses:
    # print(dir(response))
    # print(response.search.query)

    for hit in response:
        print(dir(hit))
        print(hit.beat.machine_moid)
        print(hit.meta)
        # print(hit)
