import base from '@/api/base'; // 导入接口域名列表
import axios from '@/api/http'; // 导入http中创建的axios实例
const intelligentCapture = {
    //一键抓包
    oneClickCapture(params){
      return axios.post(`${base.master}/packet/oneclick/`,params)
    },
    //自定义抓包
    selfBeginCapture(params){
      return axios.post(`${base.master}/packet/tcpdump/`,params)
    },
    //判断是否结束抓包
    endCapture(params){
    },
    //查询网口
    getOneIpNetPort(params){
      return 	axios.get(`${base.master}/`,{params})
    },
    //下载抓包文件
    downCaptureFiles(params){

    },
    //清空抓包文件
    clearFiles(){

    },
  };

export default intelligentCapture;
