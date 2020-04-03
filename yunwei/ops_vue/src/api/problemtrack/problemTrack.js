import base from '@/api/base'; // 导入接口域名列表
import axios from '@/api/http'; // 导入http中创建的axios实例

const problemTrack = {
  postData(params){
    return axios.post(`${base.master}/issuetracking/issues/`,params);
  },
  getdata(params){
    return axios.get(`${base.master}/issuetracking/issues/`,{params});
  },
  putData(params){
    return axios.put(`${base.master}/issuetracking/issues/${params.id}/`,params);
  },
  deleteProblem(param){
    return axios.delete(`${base.master}/issuetracking/issues/`,{data:param});
  },
  exportProblem(params){
    return axios.get(`${base.master}/issuetracking/export/`,{params});
  }
}

export default problemTrack
