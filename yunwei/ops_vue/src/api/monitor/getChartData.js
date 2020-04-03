/**
 * 获取图表数据接口列表
 */

import base from '@/api/base'; // 导入接口域名列表
import axios from '@/api/http';
import staticAxios from "axios";
// import {Notification} from "element-ui";

const getChartData = {
  async getUrlDataSync(url, params) {
    let data = await axios.get(`${base.master}${url}`, {params: params})
      .then(res =>
        res.data
      );
    let backData = null
    if (data && data.success) {
      // console.log(data.data)
      backData = data.data.info
    } else {
      axios.Notification({
        title: 'Error Code: ' + data.error_code,
        type: "error",
        message: data.msg
      })
    }
    return backData
  },

  async getP2pConfResources(params) {
    let url = '/statistics/p2p_conf_resources/'
    let data = await axios.get(`${base.master}${url}`, {params: params})
    return data.data

  },
  async getPMoreConfResources(params) {
    let url = '/statistics/conf_resources/'
    let data = await axios.get(`${base.master}${url}`, {params: params})
    return data.data
  },

  async getStaticConfResource(params) {

    // console.log(params)
    let drivesItem = [this.getP2pConfResources(params), this.getPMoreConfResources(params)]
    let callbackData = await staticAxios.all(drivesItem)
      .then(staticAxios.spread((...resList) => {
        return resList.map(item => item.success === 1 ? item.data.info : undefined).filter(item => item)
        // console.log(resList)
      }));
    return callbackData.flat(1)
  },

  async getCreateConfTime(params) {
    let url = '/statistics/create_conf_time/'
    let data = await axios.get(`${base.master}${url}`, {params: params})
    // console.log(data.data)
    // console.log(data.data.success,data.data.data.info)
    let res = data.data.success ? data.data.data.info : null
    // console.log(res)
    // let cbData = res.map((item) => {
    //   let tem = {
    //     data:[item.data,item.detail],
    //     description:item.description,
    //   }
    //   return tem
    // })
    return res
  },
  async getLineMediaResources(params) {
    let url = '/statistics/media_resources/'
    let data = await axios.get(`${base.master}${url}`, {params: params})
    let temData = data.data.data.info
    let backData = temData.map(data => {
      let transData = []
      data.data.forEach(item => {
        let l = []
        l[0] = item[0]
        // item[1] ? l[1]=item[2]/item[1]*100 : l[1] = 0
        // l[2]=item[2]
        l[1] = item[2]
        transData.push(l)
      })
      let bd = {
        name: data.description,
        description: data.description,
        data: transData
      }
      return bd
    })
    return backData
  },
  async getSHTransmitResources(params) {
    let url = '/statistics/h_transmit_resources/'
    let data = await axios.get(`${base.master}${url}`, {params: params})
    let temData = data.data.data.info
    let transData = []
    temData[0].data.forEach(item => {
      let l = []
      l[0] = item[0]
      l[1] = item[1] ? item[2] / item[1] * 100 : null
      l[2] = item[2]
      transData.push(l)
    })
    let backData = [{
      name: 'bandwidth',
      description: "转发带宽",
      data: transData
    }]
    return backData
  },
  async getStatisticsVrsResources(params) {   // 数据统计--直播资源使用率
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
  // 终端概况 API
  async getTerminalConfSummary(params) {
    let filter = {
      start_time: params.startTime,
      end_time: params.endTime,
      conf_type: params.confType,
      conf_status: params.confStatus,
      time_on: params.time_on,
      interval: params.interval
    }

    let YAixsData = ['辅视频(上行)', '音频(上行)', '主视频(上行)', '辅视频(下行)', '音频(下行)', '主视频(下行)', '会议活动',]
    let legendDataInit = ['码流/参会状态', '入会离会', '静音开启/关闭', '哑音开启/关闭', '内容共享开启/关闭', '发言人设置/取消', '管理方设置/取消',
      '摄像头异常/恢复', '麦克风异常/恢复', '扬声器异常/恢复', '混音开始/结束', '画面合成开始/结束', '轮询开始/结束',
      '丢包率', '时延', '抖动', '卡顿', '丢帧',
    ]
    let legendData = ['码流/参会状态', '入会离会', '静音开启/关闭', '哑音开启/关闭', '发言人设置/取消', '管理方设置/取消',
      '丢包率', '时延', '卡顿', '丢帧',
    ]

    let objTransLegend = {
      'lose_rate': '丢包率',
      'rtt': '时延',
      'shake': '抖动',
      'rebuffer': '卡顿',
      'medianet_lost': '丢帧',
    }

    let objTransYAixs = {
      'time': '会议活动',
      'actions': '会议活动',

      'recv_video_bitrate': '主视频(下行)',
      "recv_dualvideo_bitrate": '辅视频(下行)',
      "recv_audio_bitrate": '音频(下行)',

      'recv_video_err_info': '主视频(下行)',
      "recv_dualvideo_err_info": '辅视频(下行)',
      "recv_audio_err_info": '音频(下行)',

      'send_video_bitrate': '主视频(上行)',
      "send_dualvideo_bitrate": '辅视频(上行)',
      "send_audio_bitrate": '音频(上行)',

      'send_video_err_info': '主视频(上行)',
      "send_dualvideo_err_info": '辅视频(上行)',
      "send_audio_err_info": '音频(上行)',
    }

    let renderMethod = {
      'time': 'commonRange',
      'actions': 'confAction',

      'recv_video_bitrate': 'commonRange',
      "recv_dualvideo_bitrate": 'commonRange',
      "recv_audio_bitrate": 'commonRange',

      'recv_video_err_info': 'recvAction',
      "recv_dualvideo_err_info": 'recvAction',
      "recv_audio_err_info": 'recvAction',

      'send_video_bitrate': 'commonRange',
      "send_dualvideo_bitrate": 'commonRange',
      "send_audio_bitrate": 'commonRange',

      'send_video_err_info': 'sendAction',
      "send_dualvideo_err_info": 'sendAction',
      "send_audio_err_info": 'sendAction',
    }

    let res = await axios.get(`${base.master}/confs/${params.confID}/mts/${params.mtE164}/conf_info/`, {params: filter})
    let confInfo = res.data.data
    // if(!confInfo) return null

    // 定义各个横条宽度
    let timeRange = parseInt(confInfo.end_time) - parseInt(confInfo.start_time)
    let lWidth = 5000 //长
    let sWidth = 2000 //短
    if (timeRange <= 300000) {
      lWidth = 1000
      sWidth = 500
    }
    // 定义各个横条宽度end

    // 先转成列表格式
    let transData = confInfo.info.flatMap((item, index) => {
      let YAixsIndex = YAixsData.indexOf(objTransYAixs[item.name])
      let method = renderMethod[item.name]
      let itemList = [{
        legendName: null,
        name: item.description,
        value: null,
      }]

      // 判断有无数据
      if (item.data && item.data.length > 0) {
        // 判断如何处理数据
        // 正常范围处理
        if (method === 'commonRange') {
          itemList = item.data.map(i => {
            let tempDict = {}
            tempDict["legendName"] = legendData[0]
            tempDict["name"] = item.description
            tempDict["value"] = [YAixsIndex, i.start_time, i.end_time]
            return tempDict
          })
        }
        // 会议事件处理
        else if (method === 'confAction') {
          itemList = item.data.flatMap(i => {
            let actList = i.actions.map((act, index) => {
              let tempDict = {}
              // // yp__start  修改颜色显示问题
              // if(parseInt(act.code) === 5){
              // 	tempDict["legendName"]=legendData[4]
              // }else if(parseInt(act.code)=== 6){
              // 	tempDict["legendName"]=legendData[5]
              // }else{
              // 	tempDict["legendName"]=legendData[parseInt(act.code)]
              // }
              // yp__end
              // 原本
              tempDict["legendName"] = legendDataInit[parseInt(act.code)]
              // 原本
              tempDict["name"] = item.description
              let start = i.timestamp + (index * lWidth)
              let end = start + lWidth
              let extend = {
                type: 'confAction',
                timestamp: i.timestamp,
                desc: act.desc,
                info: act.info
              }
              tempDict["value"] = [YAixsIndex, start, end, extend]
              return tempDict
            })
            return actList

          })
        }
        // 上行（发送）事件处理 || 下行（接收）事件处理
        else if (method === 'sendAction' || method === 'recvAction') {
          itemList = item.data.flatMap(i => {
            let objErrorKey = {
              'lose_rate': {prefix: '丢包率', suffix: '%', index: 0},
              'rtt': {prefix: '时延', suffix: 'ms', index: 1},
              'shake': {prefix: '抖动', suffix: '次', index: 2},
              'rebuffer': {prefix: '卡顿', suffix: '次', index: 3},
              'medianet_lost': {prefix: '丢帧', suffix: '帧', index: 4},
            }
            let tempList = []
            let extend = {
              type: 'errAction',
              timestamp: i.timestamp,
              info: []
            }
            let tempNum = 0 //记录这是第几条事件
            for (let k in i) {
              let tempDict = {}
              if (objErrorKey[k]) {
                if (i[k] && i[k].length > 0) {
                  let singleAllInfo = []
                  i[k].forEach(eachInfo => {
                    // 对不同的类型做汇总处理
                    if (eachInfo.value && eachInfo.value > 0) {
                      let temEachInfo = {}
                      temEachInfo["desc"] = eachInfo.desc
                      temEachInfo["errType"] = k
                      temEachInfo["errTypeName"] = objErrorKey[k].prefix
                      temEachInfo["value"] = eachInfo.value
                      temEachInfo["title"] = eachInfo.desc + objErrorKey[k].prefix
                      temEachInfo["content"] = eachInfo.value + objErrorKey[k].suffix
                      singleAllInfo.push(temEachInfo)
                    }
                  })
                  if (singleAllInfo.length > 0) {
                    // 如果有数据则画线
                    tempDict["legendName"] = objTransLegend[k]
                    tempDict["name"] = item.description
                    let start = i.timestamp + (tempNum * sWidth)
                    let end = start + sWidth
                    tempDict["value"] = [YAixsIndex, start, end, extend]
                    // let tempInfo = {
                    //   title: objErrorKey[k].prefix,
                    //   content: i[k] + objErrorKey[k].suffix,
                    //   // value:i[k]
                    // }
                    // extend.info.push(tempInfo)
                    extend.info = extend.info.concat(singleAllInfo)
                    tempList.push(tempDict)
                    tempNum += 1 //事件条数加1
                  }
                  ;
                }
              }
            }
            ;
            if (i.bitrate && i.bitrate.length > 0) {  //如果有码率信息，则加入显示
              let bitrateInof = i.bitrate[0].value + "kb/s"
              extend.info.unshift({title: '码率', content: bitrateInof})
            }
            return tempList
          });
        }
        ;
        // 判断如何处理数据 end
      }
      return itemList
    })

    for (let iteml of legendData) {
      let totalTime = {
        name: "会议总时长",
        legendName: iteml,
        value: ['total', parseInt(confInfo.start_time), parseInt(confInfo.end_time)]
      }
      transData.push(totalTime)
    }

    let callbackData = []

    // 再转成绘图所需格式
    legendData.forEach(i => {
      let temDict = {}
      temDict["lName"] = i
      temDict['value'] = transData.filter(item => item.legendName === i)

      callbackData.push(temDict)
    })

    let bd = {
      yAxisData: YAixsData,
      data: callbackData
    }
    return bd
  },
  // 会议事件 API
  async getConfEventSummary(params) {
    let filter = {
      start_time: params.startTime,
      end_time: params.endTime,
    }
    let res = await axios.get(`${base.master}/confs/${params.confID}/actions/`, {params: filter})
    if (!res.data.success) {
      return null
    }
    let confInfo = res.data.data

    let YAixsData = ['会议活动']

    let legendData = confInfo.info.map(i => i.description)

    // 定义各个横条宽度
    let timeRange = parseInt(confInfo.end_time) - parseInt(confInfo.start_time)
    let lWidth = parseInt(timeRange / 600)

    // 定义各个横条宽度end

    // 先转成列表格式
    let transData = confInfo.info.map((event, index) => {
      let YAixsIndex = 0
      let eventObj = {
        legendName: event.description,
        name: event.description,
        value: null,
      }
      let eventValueList = []
      if (event.data && event.data.length) {
        if (event.name === 'create_destroy_conf') {  //如果是开会创会
          let frontValue = event.data[0]
          let start = event.data[0][0]
          let end = parseInt(confInfo.end_time)
          event.data.forEach((eventDetail, dIndex) => {
            if (eventDetail[1] !== frontValue[1]) {
              if (eventDetail[1] === 0) {
                end = eventDetail[0]
                eventValueList.push([YAixsIndex, start, end, eventDetail])
              } else if (eventDetail[1] === 1) {
                start = eventDetail[0]
              }
            }
          })
          if (event.data[event.data.length - 1][1] === 1) eventValueList.push([YAixsIndex, start, parseInt(confInfo.end_time), [parseInt(confInfo.end_time), 2]])
        } else {
          eventValueList = event.data.map((eventDetail, dIndex) => {
            let start = eventDetail[0]
            let end = parseInt(start) + lWidth
            let value = [YAixsIndex, start, end, eventDetail]
            return value
          })
        }
      }
      eventObj.value = eventValueList
      return eventObj
    })
    for (let item of transData) {
      let confTotalTime = ['total', parseInt(confInfo.start_time), parseInt(confInfo.end_time)]
      item.value.push(confTotalTime)
    }

    let bd = {
      yAxisData: YAixsData,
      data: transData
    }

    return bd
  },

  async getTerminalConfMediaInfoOptions(params) {
    let filter = {
      start_time: params.startTime,
      end_time: params.endTime === 'now' ? new Date().getTime() : params.endTime
    }
    let res = await axios.get(`${base.master}/confs/${params.confID}/mts/${params.mtE164}/media_info/options/`, {params: filter})
    return res.data.data.info
  },

  async getTerminalConfMediaInfo(params) {
    let filter = {
      start_time: params.startTime,
      end_time: params.endTime,
      type: params.type,
      option: params.option,
    }
    if ((filter.end_time - filter.start_time) <= 2700000) filter.interval = 30000
    let res = await axios.get(`${base.master}/confs/${params.confID}/mts/${params.mtE164}/media_info/`, {params: filter})
    let confInfo = res.data.data.info

    if (filter.option === 6) {  //
      confInfo = confInfo.map(item => {
        let tempD = {}
        tempD.name = item.name
        tempD.description = item.description
        if (item.data !== null) {
          tempD.data = item.data.map(i => {
            // 原
            // let calcData = i[1] ? i[1]/1024 : i[1],
            // yp__start
            let calcData = i[1]
            // yp__end
            let tempL = [i[0], calcData]
            return tempL
          })
        }

        return tempD
      })
    }
    ;

    return confInfo
  },
  async getTableDataCompanyConf(params) {
    let url = '/statistics/company_conf/'
    let data = await axios.get(`${base.master}${url}`, {params: params})
    return data.data.data
  },
  async getTableDataCreateConfTime(params) {
    let url = '/statistics/create_conf_type_detail/'
    let data = await axios.get(`${base.master}${url}`, {params: params})
    return data.data.data
  },
  async getPageLayout(params) {
    let url = '/statistics/img_position/'
    let data = await axios.get(`${base.master}${url}`, {params: params})
    return data.data.data
  },
  delPageLayout(params) {
    return axios.delete(`${base.master}/statistics/img_position/`, {data: params});
  },
  changePageLayout(params) {
    return axios.post(`${base.master}/statistics/img_position/`, params);
  },

  async getSingleHostCpuData(params) {
    let filter = {
      start_time: params.start_time,
      end_time: params.end_time
    }
    let backData = await axios.get(`${base.master}/hosts/${params.moid}/cpu_usage/`, {params: filter});
    // console.log(backData)
    let data = null
    if (backData.data && backData.data.success) {

      let cpuData = backData.data.data
      let cpuCoreCount = cpuData['system.cpu.cores'][0][1]
      let key = ['system.cpu.user.pct', 'system.cpu.system.pct', 'system.cpu.iowait.pct', 'system.cpu.nice.pct',
        'system.cpu.irq.pct', 'system.cpu.softirq.pct', 'system.cpu.steal.pct']

      let cb = {}
      for (let i of key) {
        let temData = []
        cpuData[i].forEach(item => {
          let t = item[1] * 100 / cpuCoreCount
          temData.push([item[0], t])
        })
        cb[i] = temData
      }
      let cpuInfo = [{
        name: 'user',
        description: "user",
        data: cb['system.cpu.user.pct']
      }, {
        name: 'system',
        description: "system",
        data: cb['system.cpu.system.pct']
      }, {
        name: 'iowait',
        description: "iowait",
        data: cb['system.cpu.iowait.pct']
      }, {
        name: 'nice',
        description: "nice",
        data: cb['system.cpu.nice.pct']
      }, {
        name: 'irq',
        description: "irq",
        data: cb['system.cpu.irq.pct']
      }, {
        name: 'softirq',
        description: "softirq",
        data: cb['system.cpu.softirq.pct']
      }, {
        name: 'steal',
        description: "steal",
        data: cb['system.cpu.steal.pct']
      },]

      data = {
        coreCount: cpuCoreCount,
        info: cpuInfo.reverse()
      }
    }


    return data
  },

  async getCpuCoreData(params) {
    let filter = {
      start_time: params.start_time,
      end_time: params.end_time
    }
    let backData = await axios.get(`${base.master}/hosts/${params.moid}/cpu_usage/${params.coreid}/`, {params: filter});
    let data = null
    if (backData.data && backData.data.success) {

      let cpuData = backData.data.data

      let cpuInfo = [{
        name: 'Used',
        description: "Used",
        data: cpuData['system.core.idle.pct']
      },]
      for (let i of cpuInfo[0].data) {
        if (typeof(i[1]) === "number") {
          i[1] = (1 - i[1]) * 100
        }
      }
      data = cpuInfo
    }

    return data
  },

  async getSingleHostMemData(params) {
    let filter = {
      start_time: params.start_time,
      end_time: params.end_time
    }
    let backData = await axios.get(`${base.master}/hosts/${params.moid}/memory_usage/`, {params: filter});
    let data = []
    if (backData.data && backData.data.success) {
      let memTotal = backData.data.data['system.memory.total'][0][1]
      let tempDate = backData.data.data['system.memory.actual.used.pct']
      for (let item of tempDate) {
        item[1] = typeof(item[1]) === "number" ? (item[1] * 100).toFixed(2) : item[1]
        item[2] = memTotal
      }
      // console.log(tempDate)
      data = [{
        name: 'used',
        description: "使用率",
        data: tempDate
      }]
    }

    return data
  },

  async getSingleHostLoadData(params) {
    let filter = {
      start_time: params.start_time,
      end_time: params.end_time
    }
    let backData = await axios.get(`${base.master}/hosts/${params.moid}/load_gauge/`, {params: filter});
    let data = null
    if (backData.data && backData.data.success) {
      data = [{
        name: '一分钟',
        description: "一分钟",
        data: backData.data.data['system.load.1']
      }, {
        name: '五分钟',
        description: "五分钟",
        data: backData.data.data['system.load.5']
      }, {
        name: '十五分钟',
        description: "十五分钟",
        data: backData.data.data['system.load.15']
      },]
    }
    return data
  },


  async getNetworkCards(moid) {
    let backData = await axios.get(`${base.master}/hosts/${moid}/network/`);
    let data = null
    if (backData.data && backData.data.success) {
      data = backData.data.data
    }
    return data
  },

  async getSingleHostNetworkCardData(params) {
    let filter = {
      card: params.card,
      start_time: params.start_time,
      end_time: params.end_time
    }
    let backData = await axios.get(`${base.master}/hosts/${params.moid}/network/`, {params: filter});
    let data = null
    if (backData.data && backData.data.success) {
      let networkIN = backData.data.data['system.network.in.bytes']
      let networkOUT = backData.data.data['system.network.out.bytes']

      //单位：Mbps
      for (let item of networkIN) {
        if (typeof(item[1]) === "number") {
          item[1] = (item[1] / 1048576)
        }
      }
      for (let item of networkOUT) {
        if (typeof(item[1]) === "number") {
          // item[1]=-(item[1]/1048576)
          item[1] = (item[1] / 1048576)
        }
      }

      data = [{
        name: '网口进口带宽',
        description: "网口进口带宽",
        data: networkIN
      }, {
        name: '网口出口带宽',
        description: "网口出口带宽",
        data: networkOUT
      }]
    }
    return data
  },

  async getDiskageNode(moid) {
    let backData = await axios.get(`${base.master}/hosts/${moid}/diskage/`);
    let data = null
    if (backData.data && backData.data.success) {
      data = backData.data.data
    }
    return data
  },
  async getDiskageNodeData(params) {
    let filter = {
      drive: params.drive,
    }
    let backData = await axios.get(`${base.master}/hosts/${params.moid}/diskage/`, {params: filter});
    let data = null
    if (backData.data && backData.data.success) {
      data = {
        name: '磁盘寿命',
        description: "已使用",
        data: backData.data.data['system.diskage.count'] * 100
      }
    }
    return data
  },

  async getPartitionNode(moid) {
    let backData = await axios.get(`${base.master}/hosts/${moid}/disk_usage/`);
    let data = null
    if (backData.data && backData.data.success) {
      data = backData.data.data
    }
    return data
  },
  async getPartitionNodeData(params) {
    let filter = {
      partition: params.partition,
    }
    let backData = await axios.get(`${base.master}/hosts/${params.moid}/disk_usage/`, {params: filter});
    let data = null
    if (backData.data && backData.data.success) {

      data = {
        name: '磁盘使用率',
        description: "已使用",
        data: backData.data.data['used.pct'] * 100
      }
    }
    return data
  },
  downloadCompanyConfExport(params) {
    let url = "/statistics/company_conf_export/"
    // return axios.get(`${base.master}/alarms/export/`,{params: params});
    return axios({
      url: `${base.master}${url}`,
      method: 'get',
      responseType: 'blob',
      params: params,
    });
  },
  downloadCreateConfTypeExport(params) {
    let url = "/statistics/create_conf_type_export/"
    // return axios.get(`${base.master}/alarms/export/`,{params: params});
    return axios({
      url: `${base.master}${url}`,
      method: 'get',
      responseType: 'blob',
      params: params,
    });
  },

  // 数据统计相关API start
  // 表格类

  // 数据类表格的数据
  async getArrayTypeTableData(url, params) {
    let res = await axios.get(`${base.master}${url}`, {params: params}).catch(e => e);
    let data = []
    if (res.data && res.data.success) {
      res.data.data.info = res.data.data.info.map((item) => {
        let tempDict = {}
        item.forEach((v, index) => {
          let k = 'column' + index
          tempDict[k] = v
        })
        return tempDict
      })
      data = res.data.data
    }
    return data
  },
  // 图表类
  // 当天设备使用率统计
  async getEquipmentUsage(params) {
    let res = await axios.get(`${base.master}/statistics/equipment_usage/`, {params: params});
    if (res.data && res.data.success) {
      return res.data.data.info
    }
    return null
  },
  // 当天设备运行时长
  async getEquipmentOnline(params) {
    let res = await axios.get(`${base.master}/statistics/equipment_online/`, {params: params});
    if (res.data && res.data.success) {
      let devData = res.data.data.info[0].data
      let mtData = res.data.data.info[1].data
      let cbData = [{
        name: 'time_total',
        description: '总时间',
        data: [(devData[0] || 0), (mtData[0] || 0)]
      }, {
        name: 'time_avg',
        description: '平均时间',
        data: [(devData[1] || 0), (mtData[1] || 0)]
      }]
      return cbData
    }
    return null
  },
  // 终端参会时长
  async getTerminalMeetingTime(params) {
    let res = await axios.get(`${base.master}/statistics/terminal_meeting_time/`, {params: params});
    if (res.data.success) {
      let data = res.data.data.info.map(item => {
        return {
          name: item[0],
          description: item[0],
          data: item[1]
        }
      })
      return data
    }
    return null
  },
  // 终端参会次数
  async getTerminalMeetingFreq(params) {
    let res = await axios.get(`${base.master}/statistics/terminal_meeting_freq/`, {params: params});
    if (res.data.success) {
      let data = res.data.data.info.map(item => {
        return {
          name: item[0],
          description: item[0],
          data: item[1]
        }
      })
      return data
    }
    return null
  },
  // 数据统计相关API end

  // 日报相关的图表数据API start
  async getReporterDayCommon(params) {
    let res = await axios.get(`${base.master}/report/daily/${params.date}/${params.type}/`);
    if (res.data.success) {
      return res.data.data
    }
  },
  async getReporterDayTransmitResource(params) {
    let res = await axios.get(`${base.master}/report/daily/${params.date}/${params.type}/`);
    if (res.data.success) {
      if (res.data.data.report_data.length > 0) {
        let newData = res.data.data.report_data.map(item => [item[0], item[1] * 100])
        let date = [{
          name: "转发资源",
          description: "转发资源",
          data: newData
        }]
        return date
      }
      // return res.data.data.report_data.length > 0 ? res.data.data.report_data : null
    }
    return null
  },
  async getReporterDayConfQuality(params) {
    let res = await axios.get(`${base.master}/report/daily/${params.date}/${params.type}/`).catch(e => e);
    if (res.data && res.data.success) {
      let resData = res.data.data.report_data
      resData.forEach(i => {
        i['data'] = i.count
      })
      return res.data.data
    } else {
      return null
    }
  },

  // 日报相关的图表数据API end

  // 访问统计相关的图表数据API start
  async getAppRequestIP(params) {
    let res = await axios.get(`${base.master}/statistics/requests/ip/`, {params: params});
    if (res.data.success) {
      let data = res.data.data.info.map(item => {
        return {
          name: item[0],
          description: item[0],
          data: item[1]
        }
      })
      return data
    }
  },
  async getAppRequestTraffic(params) {
    let res = await axios.get(`${base.master}/statistics/requests/traffic/`, {params: params});
    let temData = res.data.data.info
    let transData = []
    temData[0].data.forEach(item => {
      let l = []
      l[0] = item[0]
      l[1] = item[1] / 1024 / 1024
      transData.push(l)
    })
    let backData = [{
      name: 'RequestTraffic',
      description: "请求流量统计",
      data: transData
    }]
    return backData
  },
  async getAppRequestWebEngine(params) {
    let res = await axios.get(`${base.master}/statistics/requests/clients/`, {params: params});
    if (res.data.success) {
      return res.data.data
    }
    return null
  },
  // 访问统计相关的图表数据API start

  // 终端诊断相关Api start
  async getMtConfTime(params) {
    // let res = await axios.get(`${base.master}/report/daily/${params.date}/${params.type}/`);
    // if(res.data.success){
    // }
    // return null
    // console.log(params.date[1])
    let data = [{
      name: 'time_online',
      description: '在线时长',
      data: params.date[0].data
    }, {
      name: 'time_onconf',
      description: '会议时长',
      data: params.date[1].data
    }]
    return data
  },
  // 终端诊断相关Api start
}

export default getChartData;
