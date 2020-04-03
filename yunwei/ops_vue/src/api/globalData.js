import base from './base'; // 导入接口域名列表
import axios from '@/api/http'; // 导入http中创建的axios实例
import store from '@/store/index'; //导入vuex

const globalData = {
  // 获取所有平台域
  // return : Array
  async allPlatformDomain() {
    let data = store.getters.opsPlatformDomain
    if (data) return data
    let url = "/overview/luban_domains/"
    let res = await axios.get(`${base.master}${url}`)
    res = res.data.info || []
    let keyMap = {
      domain_name: "name",
      domain_moid: "moid",
    }
    data = res.map((item) => {
      let back = {}
      for (let key in item) {
        if (Object.keys(keyMap).indexOf(key) > -1) {
          back[keyMap[key]] = item[key]
        } else {
          back[key] = item[key]
        }
      }
      return back
    })
    store.dispatch('setOpsPlatformDomain', data)
    return data
  },

  // 获取所有用户域
  // return : Array
  async allUserDomain() {
    let data = store.getters.opsUserDomain
    if (data) return data
    let url = "/overview/user_domain/"
    data = await axios.get(`${base.master}${url}`)
    data = data.data.success ? data.data.data.info : []
    store.dispatch('setOpsUserDomain', data)
    return data
  },

  // 常用导出/下载函数
  // 数据导出
  exportFile(url, params) {
    axios({
      url: `${base.master}${url}`,
      method: 'get',
      responseType: 'blob',
      params: params,
    }).then(res => {
      const content = res.data
      const blob = new Blob([content])
      const fileName = res.headers["content-disposition"] ? res.headers['content-disposition'].split("filename=")[1] : 'export.csv'
      if ('download' in document.createElement('a')) { // 非IE下载
        const elink = document.createElement('a')
        elink.download = fileName
        elink.style.display = 'none'
        elink.href = URL.createObjectURL(blob)
        document.body.appendChild(elink)
        elink.click()
        URL.revokeObjectURL(elink.href) // 释放URL 对象
        document.body.removeChild(elink)
      } else { // IE10+下载
        navigator.msSaveBlob(blob, fileName)
      }
    }).catch(err => {
      console.log(err)
    })
  },

}

export default globalData;
