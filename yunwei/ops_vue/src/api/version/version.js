import base from '@/api/base'; // 导入接口域名列表
import axios from '@/api/http'; // 导入http中创建的axios实例

const version = {
  //平台版本api
  getVersionUrl(){            //获取上传路径
    return axios.post(`${base.master}/versions/platform/`);
  },
  editVersion(param){                //编辑版本信息
    var params = {
      "postscript":param.postscripts,
      "describe":param.describes,
      "version":param.versions
    }
    return axios.put(`${base.master}/versions/platform/${param.id}/`,params);
  },
  versionDelete(param){
    return axios.delete(`${base.master}/versions/platform/`,{data:param});
  },
  downUrl(params){
    return axios.get(`${base.master}/versions/platform/${params}/`);
  },
  upClose(){                  //上传关闭
    return axios.put(`${base.master}/versions/platform/`);
  },
  getData(params){
    return axios.get(`${base.master}/versions/platform/`,{params});
  },


  // 终端版本
  getMtVersionUrl(){            //获取上传路径
    return axios.post(`${base.master}/versions/terminal/`);
  },
  editMtVersion(param){                //编辑版本信息
    var params = {
      "postscript":param.postscripts,
      "describe":param.describes,
      "version":param.versions
    }
    return axios.put(`${base.master}/versions/terminal/${param.id}/`,params);
  },
  versionMtDelete(param){
    return axios.delete(`${base.master}/versions/terminal/`,{data:param});
  },
  downMtUrl(params){
    return axios.get(`${base.master}/versions/terminal/${params}/`);
  },
  upMtClose(){                  //上传关闭
    return axios.put(`${base.master}/versions/terminal/`);
  },
  getMtData(params){
    return axios.get(`${base.master}/versions/terminal/`,{params});
  },


  // 系统版本
  getOpVersionUrl(){            //获取上传路径
    return axios.post(`${base.master}/versions/os/`);
  },
  editOpVersion(param){                //编辑版本信息
    var params = {
      "postscript":param.postscripts,
      "describe":param.describes,
      "version":param.versions
    }
    return axios.put(`${base.master}/versions/os/${param.id}/`,params);
  },
  versionOpDelete(param){
    return axios.delete(`${base.master}/versions/os/`,{data:param});
  },
  downOpUrl(params){
    return axios.get(`${base.master}/versions/os/${params}/`);
  },
  upOpClose(){                  //上传关闭
    return axios.put(`${base.master}/versions/os/`);
  },
  getOpData(params){
    return axios.get(`${base.master}/versions/os/`,{params});
  },
}

export default version
