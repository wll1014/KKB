import base from '@/api/base'; // 导入接口域名列表
import axios from '@/api/http'; // 导入http中创建的axios实例

const fileDistribution = {
  async getFileDistributionTasks(params){
    let url = '/hosts_oper/oper_tasks/distribution_tasks/'
    let data = await axios.get(`${base.master}${url}`, {params: params})
    return data.data.data
  },

  async getFileDistributionTaskInfo(id,params){
    let url = '/hosts_oper/oper_tasks/distribution_tasks/'
    let data = await axios.get(`${base.master}${url}${id}/`, {params: params})
    return data ? data.data.data : null
  },

  async getFileDistributionTaskOperators(params){
    let url = '/hosts_oper/oper_tasks/distribution_task_operators/'
    let res = await axios.get(`${base.master}${url}`, {params: params})
    return res.data.data
  },

  createFileDistributionTask(params){
    return axios.post(`${base.master}/hosts_oper/oper_tasks/distribution_tasks/`,params);
  },

  deleteFileDistributionTask(id,params){
    return axios.delete(`${base.master}/hosts_oper/oper_tasks/distribution_tasks/${id}/`,{data:params});
  },

  putFileDistributionTask(id,params){
    return axios.put(`${base.master}/hosts_oper/oper_tasks/distribution_tasks/${id}/`,params);
  },

  deleteFileDistributionFile(id,params){
    return axios.delete(`${base.master}/hosts_oper/oper_tasks/distribution_files/${id}/`,{data:params});
  },
}

export default fileDistribution
