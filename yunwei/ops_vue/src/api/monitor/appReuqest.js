/**
 * 应用统计页面接口列表
 */

import base from '@/api/base'; // 导入接口域名列表
import axios from '@/api/http';

const appReuqestData = {
  async requestOutline(params){
    let res = await axios.get(`${base.master}/statistics/requests/outline/`,{params: params}).catch(e=>e);
    if(res.data && res.data.success){
      // await setTimeout("()=>{return res.data.data}",1000)
      return res.data.data
    }else{
      return null
    }
  },

  async requestTopData(url, params){
    let res = await axios.get(`${base.master}${url}`, {params: params}).catch(e=>e);
    if(res.data && res.data.success){
      // await setTimeout("()=>{return res.data.data}",1000)
      return res.data.data
    }else{
      return null
    }
  },

  async requestDetail(params){
    let res = await axios.get(`${base.master}/statistics/requests/detail/`,{params: params}).catch(e=>e);
    if(res.data && res.data.success){
      return res.data.data
    }else{
      return null
    }
  },

  downloadRequestExport(params){
    let url="/statistics/requests/export/"
    return axios({
      url:`${base.master}${url}`,
      method:'get',
      responseType: 'blob',
      params: params,
    });
  },
}

export default appReuqestData;
