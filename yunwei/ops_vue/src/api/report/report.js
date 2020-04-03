import base from '@/api/base'; // 导入接口域名列表
import axios from '@/api/http';

const report = {
  getConcurrentConfsPeakNum (params) {
    return axios.get(`${base.master}/report/daily/${params.date}/${params.type}/`);
  },

}

export default report
