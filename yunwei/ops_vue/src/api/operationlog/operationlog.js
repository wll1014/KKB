import base from '@/api/base'; // 导入接口域名列表
import axios from '@/api/http'; // 导入http中创建的axios实例

const operationlog = {
	getAction(params){
		return axios.get(`${base.master}/oplog/`,{params});
	},
  downloadOperationLog(params){
    return axios.get(`${base.master}/oplog/export/`,{params});
  }
	
}

export default operationlog
