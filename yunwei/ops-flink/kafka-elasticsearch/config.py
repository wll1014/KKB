
elasticsearch_server='10.67.18.100:9310'

timeout_parameter=30

bootstrap_server='10.67.18.100:9092'

encoding_type='utf-8'

platform='platform'
domain_moid='mooooooo-oooo-oooo-oooo-defaultplatf'

doctype='_doc'


system={
	'nms':{
		'machine':{'topic':'dwd.nms.machine'},
		'mt':{'topic':'dwd.nms.mt'},
		'amc':{},
		'amcapi':{},
		'api':{},
		'apicore':{},
		'aps':{},
		'bmc':{},
		'cds':{},
		'cmc':{},
		'cmdataproxy':{},
		'cmu':{},
		'css':{},
		'dcs':{},
		'dms':{},
		'dssmaster':{},
		'dssworker':{},
		'ejabberd':{},
		'glusterfs':{},
		'glusterfsd':{},
		'graphite':{},
		'hduapiagent':{},
		'hdupool':{},
		'mediamaster':{},
		'mediaworker':{},
		'modb':{},
		'mysql':{},
		'nds':{},
		'nms_bridge26':{},
		'nms_bridge48':{},
		'nms_collector':{},
		'nms_starter':{},
		'nms_webserver':{},
		'pas':{'topic':'dwd.nms.pas'},
		'portal':{},
		'portalcore':{},
		'prsworker':{},
		'rabbitmq':{},
		'redis':{},
		'redis_nms':{},
		'restapi':{},
		'rms':{},
		'service':{},
		'servicecore':{},
		'sm':{},
		'sso':{},
		'ssocore':{},
		'sus':{},
		'susmgr':{},
		'tomcat':{},
		'upu':{},
		'upucore':{},
		'vrs':{},
		'zookeeper':{}
	},
	'beat':{
		'h323':{'topic':'dwd.h323'}
	},
	'dsspb':{
		'dsspb':{'topic':'dwd.dsspb'}
	}
}

agg={
	'pas-P2P-meeting':'ads.nms.pas-p2p-meeting',
	'h323':'ads.h323',
	'mediaswitch':'dwd.dssswitch'
}

