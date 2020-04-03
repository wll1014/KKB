import base from '@/api/base'; // 导入接口域名列表
import axios from '@/api/http'; // 导入http中创建的axios实例

const script = {
	// 脚本列表
	getscript(params){
		return axios.get(`${base.master}/hosts_oper/scripts/`,{params});
	},
	getscriptOne(params){
		return axios.get(`${base.master}/hosts_oper/scripts/${params.id}/`,{params})
	},
	putscript(params){
		var posts={
			'postscript':params.postscripts
		}
		return axios.put(`${base.master}/hosts_oper/scripts/${params.id}/`,posts);
	},
	deleteScript(param){
		return axios.delete(`${base.master}/hosts_oper/scripts/`,{data:param});
	},
	// 查询所有上传人员
	getadminList(params){
		return axios.get(`${base.master}/hosts_oper/scripts/uploader/`,{params});
	},


  // ywj api start
	//即时任务
	async getRealTimeTasks(params){
    let url = '/hosts_oper/oper_tasks/real_time_tasks/'
    let data = await axios.get(`${base.master}${url}`, {params: params})
    return data.data.data
	},

  async getRealTimeTaskInfo(id,params){
    let url = '/hosts_oper/oper_tasks/real_time_tasks/'
    let data = await axios.get(`${base.master}${url}${id}/`, {params: params})
    return data? data.data.data : null
  },

  async getRealTimeTaskOperators(params){
    let url = '/hosts_oper/oper_tasks/real_time_task_operators/'
    let data = await axios.get(`${base.master}${url}`, {params: params})
    return data.data.data
  },

  createRealTimeTask(params){
    return axios.post(`${base.master}/hosts_oper/oper_tasks/real_time_tasks/`,params);
  },

  async getScriptListForTask(params){
    let data = await axios.get(`${base.master}/hosts_oper/scripts/`,{params});
    return data.data.success ? data.data.data.info : null
  },

  //定时任务
  async getCronTaskOperators(params){
    let url = '/hosts_oper/oper_tasks/cron_task_operators/'
    let data = await axios.get(`${base.master}${url}`, {params: params})
    return data.data.data
  },

  async getCronTaskLastModifyOperators(params){
    let url = '/hosts_oper/oper_tasks/cron_task_last_modify_operators/'
    let data = await axios.get(`${base.master}${url}`, {params: params})
    return data.data.data
  },

  async getCronTasks(params){
    let url = '/hosts_oper/oper_tasks/cron_tasks/'
    let data = await axios.get(`${base.master}${url}`, {params: params})
    return data.data.data
  },

  async getCronTaskInfo(id,params){
    let url = '/hosts_oper/oper_tasks/cron_tasks/'
    let data = await axios.get(`${base.master}${url}${id}/`, {params: params})
    return data ? data.data.data : null
  },
  createCronTask(params){
    return axios.post(`${base.master}/hosts_oper/oper_tasks/cron_tasks/`,params);
  },

  deleteCronTask(id,param){
    return axios.delete(`${base.master}/hosts_oper/oper_tasks/cron_tasks/${id}/`,{data:param});
  },
  putEditCronTask(id,params){
    return axios.put(`${base.master}/hosts_oper/oper_tasks/cron_tasks/${id}/`,params);
  },
  // ywj api end
	
}

export default script
