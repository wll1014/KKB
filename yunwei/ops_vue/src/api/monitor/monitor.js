/**
 * sidebarapi模块接口列表
 */

import base from '@/api/base'; // 导入接口域名列表
import staticAxios from 'axios';
import axios from '@/api/http';
import {Notification} from "element-ui"; // 导入http中创建的axios实例

const monitor = {
  //API ywj
  getCpuData(moid, start_time = null, end_time = null) {
    let params = {
      start_time: start_time,
      end_time: end_time
    }
    return axios.get(`${base.master}/hosts/${moid}/cpu_usage/`, {params: params});
  },
  getCpuCoreData(moid, coreid, start_time = null, end_time = null) {
    let params = {
      start_time: start_time,
      end_time: end_time
    }
    return axios.get(`${base.master}/hosts/${moid}/cpu_usage/${coreid}/`, {params: params});
  },
  getMemData(moid, start_time = null, end_time = null) {
    let params = {
      start_time: start_time,
      end_time: end_time
    }
    return axios.get(`${base.master}/hosts/${moid}/memory_usage/`, {params: params});
  },
  getLoadData(moid, start_time = null, end_time = null) {
    let params = {
      start_time: start_time,
      end_time: end_time
    }
    return axios.get(`${base.master}/hosts/${moid}/load_gauge/`, {params: params});
  },
  getPartitionNode(moid) {
    return axios.get(`${base.master}/hosts/${moid}/disk_usage/`);
  },
  getPartitionNodeData(moid, name) {
    let params = {
      partition: name,
    }
    return axios.get(`${base.master}/hosts/${moid}/disk_usage/`, {params: params});
  },
  getDiskageNode(moid) {
    return axios.get(`${base.master}/hosts/${moid}/diskage/`);
  },
  getDiskageNodeData(moid, name) {
    let params = {
      drive: name,
    };
    return axios.get(`${base.master}/hosts/${moid}/diskage/`, {params: params});
  },
  async handlerGetAllDiskageNodeData(moid) {
    let drivesItem = [];
    await axios.get(`${base.master}/hosts/${moid}/diskage/`).then(res =>
      res.data.data.drives.forEach(item => {
        drivesItem.push(this.getDiskageNodeData(moid, item))
      }));
    let data = await staticAxios.all(drivesItem)
      .then(staticAxios.spread((...resList)=> {
        return resList.map(item=>item.data.data)
      }));
    return data
  },
  getNetworkCards(moid) {
    return axios.get(`${base.master}/hosts/${moid}/network/`);
  },
  getNetworkCardData(moid, cardID, start_time = null, end_time = null) {
    let params = {
      card: cardID,
      start_time: start_time,
      end_time: end_time
    }
    return axios.get(`${base.master}/hosts/${moid}/network/`, {params: params});
  },
  async getProcessTopNCpu(moid, num = 10, params) {
    let res =await axios.get(`${base.master}/hosts/${moid}/top${num}/cpu/`,{params: params});
    let dataCB=[]
    if(res.data && res.data.success){
      let temData=res.data.data.topN
      temData.forEach(item =>{
        let temdict = {
          name:item[0],
          value:(item[1]*100).toFixed(2)+"%",
        }
        dataCB.push(temdict)
      })
    }
    return dataCB
  },
  async getProcessTopNMem(moid, num = 10, params) {
    let res =await axios.get(`${base.master}/hosts/${moid}/top${num}/memory/`,{params: params});
    let dataCB=[]
    if(res.data && res.data.success){
      let temData=res.data.data.topN
      temData.forEach(item =>{
        let temdict = {
          name:item[0],
          value:(item[1]*100).toFixed(2)+"%",
        }

        dataCB.push(temdict)
      })
    }
    return dataCB
  },
  getUptime(moid){
    return axios.get(`${base.master}/hosts/${moid}/uptime/`);
  },

   // 告警通知页面start
  // 订阅告警
  async getAlarmCodes(params){
    let backData = await axios.get(`${base.master}/alarms/codes/`,{params: params});
    return backData.data.data.info
  },
  downloadAlarmEvents(params){
    let url="/alarms/export/"
    // return axios.get(`${base.master}/alarms/export/`,{params: params});
    return axios({
      url:`${base.master}${url}`,
      method:'get',
      responseType: 'blob',
      params: params,
    });
  },
  addSubAlarmCodes(params){
    return axios.post(`${base.master}/alarms/sub_warning/`,params);
  },

  delSubAlarmCodes(params){
    return axios.delete(`${base.master}/alarms/sub_warning/`,{data:params});
  },

  async getServerDevTypes(){
    let backData = await axios.get(`${base.master}/alarms/server_dev_types/`);
    return backData.data.data
  },
  async getAlarmInfoServerUnrepaired(params){
    let backData = await axios.get(`${base.master}/alarms/server_unrepaired/`,{params});
    return backData.data.data
  },
  async getAlarmInfoServerRepaired(params){
    let backData = await axios.get(`${base.master}/alarms/server_repaired/`,{params});
    return backData.data.data
  },
  async getTerminalDevTypes(){
    let backData = await axios.get(`${base.master}/alarms/terminal_dev_types/`);
    return backData.data.data
  },
  async getAlarmInfoTerminalUnrepaired(params){
    let backData = await axios.get(`${base.master}/alarms/terminal_unrepaired/`,{params});
    return backData.data.data
  },
  async getAlarmInfoTerminalRepaired(params){
    let backData = await axios.get(`${base.master}/alarms/terminal_repaired/`,{params});
    return backData.data.data
  },
  // 告警通知人员
  async getAlarmNotificationRules(id,params){
    let backData = ''
    if(id){
      backData = await axios.get(`${base.master}/alarms/rules/${id}/`,{params});
    }else{
      backData = await axios.get(`${base.master}/alarms/rules/`,{params});
    }

    if(backData.data.success===0){
      axios.Notification({
        message: '告警通知规则获取失败',
      })
    }else{
      return backData.data.data
    }
  },
  postAddAlarmNotificationRules(params){
    return axios.post(`${base.master}/alarms/rules/`,params);
  },
  putEditAlarmNotificationRules(id,params){
    return axios.put(`${base.master}/alarms/rules/${id}/`,params);
  },
  delAlarmNotificationRules(params){
    return axios.delete(`${base.master}/alarms/rules/`,{data:params});
  },
  async getSearchUserInfo(params){
    let backData = await axios.get(`${base.master}/overview/user_info/`,{params});
    return backData.data.data.info
  },
  // 告警通知人员页面end

  // 会议快照相关api

  // 会议快照相关api  end
  postCreateSnapshots(params){
    // return axios.get(`${base.master}/diagnose/snapshots/`,{params:params});
    return axios({
      url:`${base.master}/diagnose/snapshots/`,
      method:'post',
      headers: {'Content-Type': 'multipart/form-data'},
      params: params,
    });
  },
  async getSnapshotsStatus(id,params){
    return axios.get(`${base.master}/diagnose/snapshots/${id}/`,{params:params})

  },
  downloadSnapshots(params){
    let url="/diagnose/download/"
    // return axios.get(`${base.master}/alarms/export/`,{params: params});
    return axios({
      url:`${base.master}${url}`,
      method:'get',
      responseType: 'blob',
      params: params,
    });
  },
  // API 杨萍


  //告警修复
	postAlarmFix(params){
		 return axios({
		  url:`${base.master}/alarms/ignore/`,
		  method:'post',
		  headers: {'Content-Type': 'multipart/form-data'},
		  params: params,
		});
		// return axios.post(`${base.master}/alarms/ignore/`,params);
	},
	
  //获取阈值信息
  GetThresholds(params){
    return axios.get(`${base.master}/alarms/thresholds/`)
  },
  putThresholds(params){
		// console.log(params.m)
    var param = params.m
    return axios.put(`${base.master}/alarms/thresholds/${params.id}/`,param)
  },
  //获取组织架构用户域
  getAlarmUserDomain(){
    return axios.get(`${base.master}/overview/user_domain/`)
  },
  getMonitorUserDomainUserInfo(user_domain_moid){
    return axios.get(`${base.master}/${user_domain_moid}/user_info/`)
  },

  //以下为会议信息
  //请求平台域值
  getPlatformDomainsOne(){
    return axios.get(`${base.master}/overview/luban_domains/`)
  },
	async getPlatformDomains(params) {
	  let url="/overview/luban_domains"
	  let temData = await axios.get(`${base.master}${url}/`,{params: params})
	    .then(res => res.data.info)
		// console.log(temData)
	  let keyMap={
	    domain_name:"name",
			domain_moid:"moid",
	  }
	  let data=temData.map((item)=>{
	    let back={}
	    for(let key in item){
	      if(Object.keys(keyMap).indexOf(key)>-1){
	        back[keyMap[key]]=item[key]
	      }else{
	        back[key]=item[key]
	      }
	    }
			// console.log(back)
	    return back
	  })
	  return data
	},
	
  //获取用户域
  async getUserDomains(params){
		let url="/overview/user_domain/"
		let temData = await axios.get(`${base.master}${url}`,{params: params})
			.then(res => res.data.data.info)
		let keyMap={
		  user_domain_name:"name",
		  user_domain_moid:"moid",
		}
		let data=temData.map((item)=>{
		  let back={}
		  for(let key in item){
		    if(Object.keys(keyMap).indexOf(key)>-1){
		      back[keyMap[key]]=item[key]
		    }else{
		      back[key]=item[key]
		    }
		  }
		  back['leaf']=true
		  return back
		})
		return data
  },
	async getUserSearchDomains(params) {
	let url="/overview/user_domain/"
	let temData = await axios.get(`${base.master}${url}`,{params: params})
	  .then(res => res.data.data.info)
		// console.log(temData)
	let domainKeyMap={
	  domain_name:"name",
	  domain_moid:"moid",
	}
	let userKeyMap={
		user_domain_name:"name",
		user_domain_moid:"moid",
	}
	let data=temData.map((item)=>{
	  let back={}
	  for(let key in item){
	    if(Object.keys(domainKeyMap).indexOf(key)>-1){
	      back[domainKeyMap[key]]=item[key]
	    }else if(key==='info'){ //如果是子节点
	      let temData = item['info'].map((item2)=>{
					let back2={}
					for(let key2 in item2){
						if(Object.keys(userKeyMap).indexOf(key2)>1){
							back2[userKeyMap[key2]]=item2[key2]
						}else{
							back2[key2]=item2[key2]
						}
					}
					back['leaf']=true
					return back2
				})
				back['info']=temData
	    }else{
				back[key]=item[key]
			}
	  }
	  return back
	})
	 return data
	},
	
	
	
	
	
  //获取会议信息
  meetingGet(params){
    return axios.get(`${base.master}/confs/`,{params});
  },
  //获取会议终端列表
  meetingDevice(param){
		if (param.conf_id){				//多点
			var conf_id = param.conf_id
		}else if (param.caller_id){				//点对点
			var conf_id = param.caller_id
		}
		if(param.conf_status===1){
      var params = {
        "start_time":param.start_time,
        "end_time":(new Date()).valueOf(),
        "conf_type":param.conf_type,
        "conf_status":param.conf_status,
        "count":12,
        "start":param.start,
        "conf_id":param.conf_id,
				"condition":param.condition,
      }
    }else{
      var params = {
        "start_time":param.start_time,
        "end_time":param.end_time,
        "conf_type":param.conf_type,
        "conf_status":param.conf_status,
        "count":12,
        "start":param.start,
        "conf_id":param.conf_id,
				"condition":param.condition,
      }
    }
    return axios.get(`${base.master}/confs/${conf_id}/mts/`,{params})
  },
  //获取实时会议额外信息
  getExtend(param){
    var params={
      "start_time":param.start_time
    }
    return axios.get(`${base.master}/confs/${param.conf_id}/extend/`,{params})
  },

	//获取会议信息call——id

  meetingInfoLinkCallId(val){
    // console.log(val)
    var params = {
      "start_time":val.start_time,
      "end_time":val.end_time,

    }
		return axios.get(`${base.master}/confs/${val.conf_id}/mts/${val.mt_e164}/call_ids/`,{params})
	},
	//获取会议信息呼叫链路信息
	meetingInfoLinkCallInfo(val){
		var params = {
			'start_time':val.start_time,
			'end_time':val.end_time,
      "call_type":val.call_type
		}
		return axios.get(`${base.master}/confs/${val.conf_id}/mts/${val.mt_e164}/${val.call_id}/primary/`,{params})
	},
  meetingInfoLinkCallIdMethod(val){
    var params = {
      'start_time':val.start_time,
      'end_time':val.end_time,
      "call_type":val.call_type
    }
    return axios.get(`${base.master}/confs/${val.conf_id}/mts/${val.mt_e164}/${val.call_id}/methods/`,{params})
  },
  //会议信息查询呼叫详情
  meetingInfoCallDetail(val){
    var params={
      'start_time':val.start_time,
      'end_time':val.end_time,
      "start":val.start,
      "count":val.count,
      "method":val.methods,
      "call_type":val.call_type
    }
    return axios.get(`${base.master}/confs/${val.conf_id}/mts/${val.mt_e164}/${val.call_id}/all/`,{params})
  },
	//获取终端状态信息表单部分信息
  getTerminalStatusForm(params){
	return axios.get(`${base.master}/confs/${params.conf_e164}/mts/${params.mt_e164}/real_time_status/`)
  },
	//获取码流链路信息
	getTerminalMtsLinkInfo(params){
		var param={
			'time':params.time,
			'type':params.type,
			'conf_status':params.conf_status,
		};
		return axios.get(`${base.master}/confs/${params.conf_id}/mts/${params.mt_e164}/switch/`,{params:param})

	},
	getterminalConfInfo(param){
    var params={
    	"start_time":param.start_time,
    	"end_time":param.end_time,
    	"conf_status":param.conf_status,
      'conf_type':param.conf_type,
			"time_on":param.start_time,
    }
		// console.log('222')
    return axios.get(`${base.master}/confs/${param.conf_id}/mts/${param.mt_e164}/conf_info/`,{params:params})
  },
	getChannel(param){
		var params={
			"start_time":param.start_time,
			"end_time":param.end_time,
			"conf_status":param.conf_status,
		}
		return axios.get(`${base.master}/confs/${param.conf_id}/mts/${param.mt_e164}/channel/`,{params})
	},
	getTopology(param){
		var params={
			"start_time":param.start_time,
			"end_time":param.end_time,
			"conf_status":param.conf_status,
		}
		return axios.get(`${base.master}/confs/${param.conf_id}/mts/${param.mt_e164}/topology/`,{params})
	},
	
	
	
	

  //链路检测
	// 创建链路检测任务
	createConf(params){
		return axios.post(`${base.master}/diagnose/createconf/`,params)
	},
	//查询链路检测任务ID
	getConfLink(){
		return axios.get(`${base.master}/diagnose/createconf/`)
  },
	//查询会议链路检测结果
	meetingLinkResult(params){
		return axios.get(`${base.master}/diagnose/createconf/${params}/`)
	},
	//查询呼叫链路Call_id以及显示的时间选项
	callConfId(params){
		var param = {
			"start_time":params.start_time,
			"end_time":params.end_time,
		}
		return axios.get(`${base.master}/diagnose/createconf/${params.task_id}/call_ids/`,)
	},
	//查询呼叫链路检测结果
	callConfResult(param){
		var params = {
			'start_time':param.start_time,
			'end_time':param.end_time,
      "call_type":param.call_type
		}
		// console.log(param,params)
		return axios.get(`${base.master}/diagnose/createconf/${param.call_id}/primary/`,{params})
	},






  //应用检测
  appCluster(){
    return axios.get(`${base.master}/diagnose/check_apps/`)
  },
  appExport(){
    return axios.get(`${base.master}/diagnose/check_apps/export/`,{
    responseType: 'arraybuffer'
})
  },
  appDetectionBegin(){
    return axios.post(`${base.master}/diagnose/check_apps/`)
  },
  getEveryOneDetectionLog(params){
    // console.log(params)
    return axios.get(`${base.master}/diagnose/check_apps/${params.check_types}/${params.val}/log/`)
  },
	
	//业务监控
	businessMonitor(params){
		return axios.get(`${base.master}/apps/monitor/`,{params})
	}
}

export default monitor;
