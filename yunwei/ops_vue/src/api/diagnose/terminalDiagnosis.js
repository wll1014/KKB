import base from '@/api/base'; // 导入接口域名列表
import axios from '@/api/http'; // 导入http中创建的axios实例

const terminalDiagnosis = {
//获取terminal Info
  getTerminalAccountInfo(params){
    return axios.get(`${base.master}/diagnose/accounts/`,{params})
  },
  getTerminalDeviceInfo(params){
		return axios.get(`${base.master}/diagnose/accounts/${params.e164}/`);
	},
  getTerminalBaseInfo(params){
    return axios.get(`${base.master}/diagnose/accounts/${params.e164}/terminals/`);
  },
  getTerminalConnectInfo(params){
    return axios.get(`${base.master}/diagnose/accounts/${params.e164}/terminals/${params.terminal}/connect/`);
  },
  getTerminalStatusInfo(params){
    return axios.get(`${base.master}/diagnose/accounts/${params.e164}/terminals/${params.terminal}/status/`);
  },
  getTerminalStatistic(params){
    return axios.get(`${base.master}/diagnose/accounts/${params.e164}/terminals/${params.terminal}/statistic/`);
  },
  getTerminalPeripheralInfo(params){
    return axios.get(`${base.master}/diagnose/accounts/${params.e164}/terminals/${params.terminal}/peripheral/`);
  },
  getTerminalCrucialInfo(params){
    return axios.get(`${base.master}/diagnose/accounts/${params.e164}/terminals/${params.terminal}/crucial/`);
  },
  getTerminalCallInfo(param){
    var params = {
      start:param.start,
      count:param.count,
    }
    return axios.get(`${base.master}/diagnose/accounts/${param.e164}/terminals/${param.terminal}/call/`,{params});
  }
};

export default terminalDiagnosis;
