/**
 * sidebarapi模块接口列表
 */

import base from '@/api/base'; // 导入接口域名列表
import axios from '@/api/http';
import staticAxios from "axios"; // 导入http中创建的axios实例

const homePage = {
  async getJsonFileSync(name) {
    let data = await axios.get(`../../../ops/static/json/${name}.json`)
      .then(res => res.data)
    return data
  },
  getMapJson(path) {
    return axios.get(`${path}`);
  },
  // 获取base.master下的api数据
  async getUrlDataSync(url, params, product = false) {
    let data = await axios.get(`${base.master}${url}`, {params: params})
      .then(res => res.data.data.info).catch(e => {
        return false
      })
    return data
  },

  // 获取其他服务器下的api数据
  async getFullUrlDataSync(url, params) {
    let data = await axios.get(`${url}`, {params: params})
      .then(res => res.data)
    return data
  },

  async getStatisticsVrsResources(params) {
    let url = "/statistics/vrs_resources/"
    let data = await axios.get(`${base.master}${url}`, {params: params})
      .then(res => {
        if (res.data) {
          let data = res.data.data.info
          let newData = data.map(item => {
            let tempD = {}
            tempD['description'] = item.description
            tempD['name'] = item.name
            // 对返回data做处理
            tempD['data'] = item.data.map(i => {
              let tempL = []
              tempL[0] = i[0]
              tempL[1] = i[1] ? Number((i[2] * 100 / i[1]).toFixed(2)) : i[1]
              tempL[2] = [i[1], i[2]]
              // console.log(tempL)
              return tempL
            });

            return tempD
          });
          return newData
        }
        ;
      })

    return data
  },
  async getStatisticsConfNumber(params) {
    let url = "/overview/confs/"
    let data = await axios.get(`${base.master}${url}`, {params: params})
      .then(res => res.data.data.info)

    return data
  },
  async getAlarmInfoServerPct(params) {
    let url = "/alarms/server_warning_pct/"
    let data = await axios.get(`${base.master}${url}`, {params: params})
      .then(res => res.data.data)

    return data
  },
  async getAlarmInfoTerminalPct(params) {
    let url = "/alarms/terminal_warning_pct/"
    let data = await axios.get(`${base.master}${url}`, {params: params})
      .then(res => res.data.data)

    return data
  },

  async getProvinceInfo(params) {
    let url = "/overview/provinces/"
    let data = await axios.get(`${base.master}${url}`, {params: params})
    // let data = await axios.get(`${url}`,{params: params})
      .then(res => res.data.data)
    // console.log(data)
    return data
  },
  async getCityInfo(params) {
    let url = "/overview/cities/"
    let data = await axios.get(`${base.master}${url}`, {params: params})
      .then(res => res.data.data)
    return data
  },
  async postMapBaseConfig(params) {
    let url = "/overview/gis_config/"
    return axios.post(`${base.master}${url}`, params);
  },
  async putMapBaseConfig(id, params) {
    let url = "/overview/gis_config/"
    return axios.put(`${base.master}${url}${id}/`, params);
  },
  async getMapBaseConfig(params) {
    let url = "/overview/gis_config/"
    let data = await axios.get(`${base.master}${url}`, {params: params})
      .then(res => res.data.data)
    return data
  },
  async getMapRoomInfo(params) {
    let url = "/machine_rooms/"
    let dataFront = await axios.get(`${base.master}${url}`, {params: params})
      .then(res => res.data.data.info)
    let data = dataFront.filter(item => item.coordinate.length === 2)

    // // 测试数据start
    // let data = [
    //   {
    //     "id": 1,
    //     "coordinate": [
    //       '120.902291','31.979878'
    //     ],
    //     "status": 0,
    //     "moid": "08ba5358-d51c-11e9-871e-000c2916f792",
    //     "name": "核心域默认机房",
    //     "coordinate_str": "116.401394,39.914271"
    //   },
    //   {
    //     "id": 3,
    //     "coordinate": [
    //       "116.401394",
    //       "39.914271"
    //     ],
    //     "status": 0,
    //     "moid": "mooooooo-oooo-oooo-oooo-defaultmachi",
    //     "name": "默认机房",
    //     "coordinate_str": "116.401394,39.914271"
    //   }
    // ]
    // // 测试数据end
    return data
  },
  async getMapPeripheralInfo(params) {
    let url = "/peripherals/"
    let dataFront = await axios.get(`${base.master}${url}`, {params: params})
      .then(res => res.data.data.info)
    let data = dataFront.filter(item => item.coordinate.length === 2)

    return data
  },
  async getMapTerminalsInfo(params) {
    let url = "/terminals/"
    let dataFront = await axios.get(`${base.master}${url}`, {params: params})
      .then(res => res.data.data.info)

    let data = dataFront.filter(item => item.coordinate.length === 2)
    return data
  },
  async getMapLinksInfo(params) {
    let url = "/gis/links/"
    let dataFront = await axios.get(`${base.master}${url}`, {params: params})
      .then(res => res.data && res.data.success ? res.data.data.info : null)
      .catch(err => {
        return null
      })
    return dataFront
  },

  async getMapLinkDetail(e164) {
    return axios.get(`${base.master}/gis/links/${e164}/`)
  },

  async getAllPlatformDomainInfo(params) {
    let url = "/overview/luban_domains/"
    let temData = await axios.get(`${base.master}${url}`, {params: params})
      .then(res => res.data.info)
    let keyMap = {
      domain_name: "name",
      domain_moid: "moid",
    }
    let data = temData.map((item) => {
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
    return data
  },
  async getMachineRoomInfo(id, params) {
    let url = "/overview"
    let temData = await axios.get(`${base.master}${url}/${id}/machine_room_info/`, {params: params})
      .then(res => res.data.data.info)
    let keyMap = {
      machine_room_name: "name",
      machine_room_moid: "moid",
    }
    let data = temData.map((item) => {
      let back = {}
      for (let key in item) {
        if (Object.keys(keyMap).indexOf(key) > -1) {
          back[keyMap[key]] = item[key]
        } else {
          back[key] = item[key]
        }
      }
      back['leaf'] = true
      return back
    })
    return data
  },
  async getMachineRoomInfoBySearch(params) {
    let url = "/overview/machine_room_info/"
    let temData = await axios.get(`${base.master}${url}`, {params: params})
      .then(res => res.data.data.info)
    let domainKeyMap = {
      domain_name: "name",
      domain_moid: "moid",
    }
    let userKeyMap = {
      machine_room_name: "name",
      machine_room_moid: "moid"
    }
    let data = temData.map((item) => {
      let back = {}
      for (let key in item) {
        if (Object.keys(domainKeyMap).indexOf(key) > -1) {
          back[domainKeyMap[key]] = item[key]
        } else if (key === "info") {  //如果是子节点
          let temData = item["info"].map((item2) => {
            let back2 = {}
            for (let key2 in item2) {
              if (Object.keys(userKeyMap).indexOf(key2) > -1) {
                back2[userKeyMap[key2]] = item2[key2]
              } else {
                back2[key2] = item2[key2]
              }
            }
            back2['leaf'] = true
            return back2
          })
          back["info"] = temData
        } else {
          back[key] = item[key]
        }
      }
      return back
    })
    return data
  },
  async getAllUserDomainInfo(params) {
    let url = "/overview/user_domain/"
    let temData = await axios.get(`${base.master}${url}`, {params: params})
      .then(res => res.data.data.info)
    let keyMap = {
      user_domain_name: "name",
      user_domain_moid: "moid",
    }
    let data = temData.map((item) => {
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
    return data
  },
  async getUserDomainUserInfo(id, params) {
    let url = "/overview"
    let temData = await axios.get(`${base.master}${url}/${id}/user_info/`, {params: params})
      .then(res => res.data.data.info)
    let keyMap = {
      name: "name",
    }
    let data = temData.map((item) => {
      let back = {}
      for (let key in item) {
        if (Object.keys(keyMap).indexOf(key) > -1) {
          back[keyMap[key]] = item[key]
        } else {
          back[key] = item[key]
        }
      }
      back['leaf'] = true
      return back
    })
    return data
  },

  async getUserInfoBySearch(params) {
    let url = "/overview/user_info/"
    let temData = await axios.get(`${base.master}${url}`, {params: params})
      .then(res => res.data.data.info)
    let domainKeyMap = {
      user_domain_name: "name",
      user_domain_moid: "moid",
    }
    let userKeyMap = {
      name: "name",
    }
    let data = temData.map((item) => {
      let back = {}
      for (let key in item) {
        if (Object.keys(domainKeyMap).indexOf(key) > -1) {
          back[domainKeyMap[key]] = item[key]
        } else if (key === "info") {  //如果是子节点
          let temData = item["info"].map((item2) => {
            let back2 = {}
            for (let key2 in item2) {
              if (Object.keys(userKeyMap).indexOf(key2) > -1) {
                back2[userKeyMap[key2]] = item2[key2]
              } else {
                back2[key2] = item2[key2]
              }
            }
            back2['leaf'] = true
            return back2
          })
          back["info"] = temData
        } else {
          back[key] = item[key]
        }
      }
      return back
    })
    return data
  },

  async getPeripheralMachineRoomInfo(params) {
    let url = "/overview/over_peripheral_rooms/"
    let temData = await axios.get(`${base.master}${url}`, {params: params})
      .then(res => res.data.data.info)
    let keyMap = {
      machine_room_name: "name",
      machine_room_moid: "moid",
    }
    let data = temData.map((item) => {
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
    return data
  },

  async getPeripheralInfo(id, params) {
    let url = "/overview"
    let temData = await axios.get(`${base.master}${url}/${id}/luban_peripheral_info/`, {params: params})
      .then(res => res.data.data.info)
    let keyMap = {
      per_sub_type: "name",
      per_moid: "moid",
    }
    let data = temData.map((item) => {
      let back = {}
      for (let key in item) {
        if (Object.keys(keyMap).indexOf(key) > -1) {
          back[keyMap[key]] = item[key]
        } else {
          back[key] = item[key]
        }
      }
      back['leaf'] = true
      return back
    })
    return data
  },

  async getPeripheralInfoBySearch(params) {
    let url = "/overview/luban_peripheral_info/"
    let temData = await axios.get(`${base.master}${url}`, {params: params})
      .then(res => res.data.data.info)
    let domainKeyMap = {
      machine_room_name: "name",
      machine_room_moid: "moid",
    }
    let userKeyMap = {
      per_sub_type: "name",
      per_moid: "moid"
    }
    let data = temData.map((item) => {
      let back = {}
      for (let key in item) {
        if (Object.keys(domainKeyMap).indexOf(key) > -1) {
          back[domainKeyMap[key]] = item[key]
        } else if (key === "info") {  //如果是子节点
          let temData = item["info"].map((item2) => {
            let back2 = {}
            for (let key2 in item2) {
              if (Object.keys(userKeyMap).indexOf(key2) > -1) {
                back2[userKeyMap[key2]] = item2[key2]
              } else {
                back2[key2] = item2[key2]
              }
            }
            back2['leaf'] = true
            return back2
          })
          back["info"] = temData
        } else {
          back[key] = item[key]
        }
      }
      return back
    })
    return data
  },

  async getAllMachineRoomInfo(params) {
    let url = "/overview/over_machine_rooms/"
    let temData = await axios.get(`${base.master}${url}`, {params: params})
      .then(res => res.data.data.info)
    let keyMap = {
      machine_room_name: "name",
      machine_room_moid: "moid",
    }
    let data = temData.map((item) => {
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
    return data
  },
  async getDeviceInfoFromMachineRoom(id, params) {
    let url = "/overview"
    // console.log(params)
    let temData = await axios.get(`${base.master}${url}/${id}/luban_machine_info/`, {params: params})
      .then(res => res.data.data.info)
    let keyMap = {
      machine_name: "name",
      machine_moid: "moid",
    }
    let data = temData.map((item) => {
      let back = {}
      for (let key in item) {
        if (Object.keys(keyMap).indexOf(key) > -1) {
          back[keyMap[key]] = item[key]
        } else {
          back[key] = item[key]
        }
      }
      back['leaf'] = true
      return back
    })
    return data
  },
  async getDeviceInfoBySearch(params) {
    let url = "/overview/luban_machine_info/"
    let temData = await axios.get(`${base.master}${url}`, {params: params})
      .then(res => res.data.data.info)
    let domainKeyMap = {
      machine_room_name: "name",
      machine_room_moid: "moid",
    }
    let userKeyMap = {
      machine_name: "name",
      machine_moid: "moid",
    }
    let data = temData.map((item) => {
      let back = {}
      for (let key in item) {
        if (Object.keys(domainKeyMap).indexOf(key) > -1) {
          back[domainKeyMap[key]] = item[key]
        } else if (key === "info") {  //如果是子节点
          let temData = item["info"].map((item2) => {
            let back2 = {}
            for (let key2 in item2) {
              if (Object.keys(userKeyMap).indexOf(key2) > -1) {
                back2[userKeyMap[key2]] = item2[key2]
              } else {
                back2[key2] = item2[key2]
              }
            }
            back2['leaf'] = true
            return back2
          })
          back["info"] = temData
        } else {
          back[key] = item[key]
        }
      }
      return back
    })
    return data
  },

  async getGeoRoomInfo(params) {
    let url = "/machine_rooms/"
    let data = await axios.get(`${base.master}${url}`, {params: params})
      .then(res => res.data.data)
    data.info.forEach((item) => {
      if (!item.coordinate_str) {
        item.coordinate_str = "待编辑"
      }
    })
    return data
  },
  async postGeoRoomInfo(params) {
    let url = "/machine_rooms/"
    return axios.post(`${base.master}${url}`, params);
  },
  async putGeoRoomInfo(id, params) {
    let url = "/machine_rooms/"
    return axios.put(`${base.master}${url}${id}/`, params);
  },
  async delGeoRoomInfo(params) {
    let url = "/machine_rooms/"
    return axios.delete(`${base.master}${url}`, {data: params});
  },
  async getGeoPeripheralInfo(params) {
    let url = "/peripherals/"
    let data = await axios.get(`${base.master}${url}`, {params: params})
      .then(res => res.data.data)
    data.info.forEach((item) => {
      if (!item.coordinate_str) {
        item.coordinate_str = "待编辑"
      }
    })
    return data
  },
  async postGeoPeripheralInfo(params) {
    let url = "/peripherals/"
    return axios.post(`${base.master}${url}`, params);
  },
  async putGeoPeripheralInfo(id, params) {
    let url = "/peripherals/"
    return axios.put(`${base.master}${url}${id}/`, params);
  },
  async delGeoPeripheralInfo(params) {
    let url = "/peripherals/"
    return axios.delete(`${base.master}${url}`, {data: params});
  },
  async getGeoTerminalsInfo(params) {
    let url = "/terminals/"
    let data = await axios.get(`${base.master}${url}`, {params: params})
      .then(res => res.data.data)
    data.info.forEach((item) => {
      // console.log(item.moid)
      if (!item.coordinate_str) {
        item.coordinate_str = "待编辑"
      }
    })
    return data
  },
  async postGeoTerminalsInfo(params) {
    let url = "/terminals/"
    return axios.post(`${base.master}${url}`, params);
  },
  async putGeoTerminalsInfo(id, params) {
    let url = "/terminals/"
    return axios.put(`${base.master}${url}${id}/`, params);
  },
  async delGeoTerminalsInfo(params) {
    let url = "/terminals/"
    return axios.delete(`${base.master}${url}`, {data: params});
  },
}

export default homePage;
