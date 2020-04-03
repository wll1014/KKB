/**
 * sidebarapi模块接口列表
 */

import base from '@/api/base'; // 导入接口域名列表
import axios from '@/api/http'; // 导入http中创建的axios实例

const hostManageApi = {
  postDeploySync() {  // 一键同步 TODO: 重写此API以优化主机管理页面此api的调用 -- 20200317
    return axios.post(`${base.master}/hosts/deploy_sync/`);
  },
  // TODO : 页面重写完成确认无影响后删除 -- 20200317
  // getHostDomains() {
  //   return axios.get(`${base.master}/hosts/domains/`);
  // },
  // getHostGroups(params) {
  //   return axios.get(`${base.master}/hosts/groups/`, {params: params});
  // },
  // getHostInfoList(params) {
  //   return axios.get(`${base.master}/hosts/`, {params: params});
  // },
  // 页面重写完成确认无影响后删除 end

  changeGroup(id, params) {
    return axios.put(`${base.master}/hosts/groups/${id}/members/`, params);
  },
  getSingleHostInfo(id = null) {
    // console.log(id)
    return axios.get(`${base.master}/hosts/${id}/`);
  },
  searchHost(params) {
    return axios.get(`${base.master}/hosts/`, {params: params});
  },
  exportTopN(moid, topn, params) {
    return axios({
      // url:`${base.master}/hosts/${moid}/${topn}/export/`,
      url: `${base.master}/hosts/${moid}/top${topn}/export/`,
      method: 'get',
      responseType: 'blob',
      params: params,
    });
  },

  async hostDomains(params) { // 主机页面平台域
    let res = await axios.get(`${base.master}/hosts/domains/`, {params: params});
    if (res.data.success) {
      return res.data.data
    }
    return []
  },

  async hostGroups(params) { // 主机页面机房和分组
    let res = await axios.get(`${base.master}/hosts/groups/`, {params: params});
    if (res.data.success) {
      return res.data.data
    }
    return []
  },

  // 分组增删改 start
  addHostGroups(params) {
    return axios.post(`${base.master}/hosts/groups/`, params);
  },
  editHostGroups(id, params) {
    return axios.put(`${base.master}/hosts/groups/${id}/`, params);
  },
  delHostGroups(params) {
    return axios.delete(`${base.master}/hosts/groups/`, {data: params});
  },
  // 分组增删改 end

  // 获取主机列表
  async hostList(params) {
    let res = await axios.get(`${base.master}/hosts/`, {params: params});
    if (res.data.success) {
      return res.data
    }
    return null
  },
}

export default hostManageApi;
