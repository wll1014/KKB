/**
 * sidebarapi模块接口列表
 */

import base from './base'; // 导入接口域名列表
import axios from '@/api/http'; // 导入http中创建的axios实例

const sidebarapi = {
    // 登录信息
    islogin(){
      return axios.get(`${base.master}/islogin/`);
    },
    // 注销
    logout(){
      return axios.post(`${base.master}/logout/`);
    },
    // 侧边栏列表
    sidebarList () {        
        return axios.get(`${base.master}/sidebar/`);
           // return axios.get(`${base.test}/api/v1/sidebar/`);
    },
}

export default sidebarapi;
