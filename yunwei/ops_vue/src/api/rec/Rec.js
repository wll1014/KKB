import base from '@/api/base'; // 导入接口域名列表
import axios from '@/api/http'; // 导入http中创建的axios实例

const rec = {
		//维护记录端口
	records(params){
		return axios.get(`${base.master}/maintenance/`,{params});
	},
	recordsGet(params){
		return axios.get(`${base.master}/maintenance/${params.record_id}/`);
	},
	recordsPost(params){
		return axios.post(`${base.master}/maintenance/`,params);
	},
	recordsPut(params){
		return axios.put(`${base.master}/maintenance/${params.record_id}/`,params);
	},
	recordsDelete(param){	
		return axios.delete(`${base.master}/maintenance/`,{data:param});
	},
  platformget(){
    return axios.get(`${base.master}/overview/luban_domains/`);
  },
};

export default rec;
