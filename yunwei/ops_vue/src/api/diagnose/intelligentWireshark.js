import base from '@/api/base'; // 导入接口域名列表
import axios from '@/api/http'; // 导入http中创建的axios实例
const IntelligentWireshark = {
  // 一键抓包
  createAutoTcpdumpTask(params){
    return axios.post(`${base.master}/diagnose/tcpdump/quick_capture/`,params);
  },
  async getAutoTcpdumpTaskInfo(id,params){
    let url = '/diagnose/tcpdump/quick_capture/'
    let data = await axios.get(`${base.master}${url}${id}/`, {params: params})
    return data.data
  },
  // 自定义抓包
  getCustomCaptureTask(params){
    let url = '/diagnose/tcpdump/custom_capture/'
    return axios.get(`${base.master}${url}`, {params: params})
    // return data.data
  },
  getCustomCaptureTaskInfo(id,params){
    let url = '/diagnose/tcpdump/custom_capture/'
    return axios.get(`${base.master}${url}${id}/`, {params: params})
    // return data.data
  },
  getCaptureDevCards(moid,params){
    return axios.get(`${base.master}/diagnose/tcpdump/${moid}/cards/`, {params: params})
    // return data.data
  },
  addCustomCaptureTaskItem(params){
    return axios.post(`${base.master}/diagnose/tcpdump/custom_capture_items/`,params);
  },
  editCustomCaptureTaskItem(id,params){
    return axios.put(`${base.master}/diagnose/tcpdump/custom_capture_items/${id}/`,params);
  },
  deleteCustomCaptureTaskItem(id,params){
    return axios.delete(`${base.master}/diagnose/tcpdump/custom_capture_items/${id}/`,{data:params});
  },
  emptyeCustomCaptureTask(id,params){
    return axios.delete(`${base.master}/diagnose/tcpdump/custom_capture_task/`,{data:params});
  },
  putCustomCaptureTask(id,params){
    return axios.put(`${base.master}/diagnose/tcpdump/custom_capture/${id}/`,params);
  },
  startCustomCaptureTask(params){
    return axios.post(`${base.master}/diagnose/tcpdump/custom_capture_task/`,params);
  },
  endCustomCaptureTask(params){
    return axios.put(`${base.master}/diagnose/tcpdump/custom_capture_task/`,params);
  },

};

export default IntelligentWireshark;
