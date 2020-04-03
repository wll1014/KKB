<template>
  <div>
    <div style="height: 580px;width: 100%;position: relative;">
      <!--<div v-if="showChart === 'terminalConfSummary'">
        <div style="font-size: 14px;color: #9ca9b1;position: absolute;top: 10px;left: 10px;z-index: 99;" >终端参会概况</div>
      </div>-->
      <div style="font-size: 14px;color: #9ca9b1;position: absolute;top: 25px;left: 20px;z-index: 99;"
           v-if="showChart !== 'terminalConfSummary'">

        <el-select style="margin-right: 7px;" @change="firstFilterChange" filterable popper-class="theme-dark"
                   v-model="firstOptionSelectedType" placeholder="请选择">
          <el-option
            v-for="item in optionsSummaryType" :key="item.type" :label="item.description" :value="item.type">
          </el-option>
        </el-select>
        <el-select style="margin-right: 7px;" v-if="secondOptionsType.length > 0" @change="secondFilterChange"
                   filterable popper-class="theme-dark" v-model="secondOptionSelectedType" placeholder="请选择">
          <el-option
            v-for="item in secondOptionsType" :key="item.option" :label="item.description" :value="item.option">
          </el-option>
        </el-select>
        <el-button @click="buttonChartChange" :disabled="buttonDisabled">搜索</el-button>

      </div>
      <ChartExtendLargeModel ChartID="IDMeetingInfoTerminalConfSummary"
                             :chartConf="activeChartConf"
                             :chartChange="chartChange"
                             :extraPlugin="extraPlugin"
                             extraPluginClass="chart-extend-plugin--mmits"
      ></ChartExtendLargeModel>
    </div>
  </div>
</template>

<script>
  export default {
    name: "MonitorMeetingInfoTerminalSummary",
    components: {
      // ChartExtendLargeModel,
      // KdTabCommon,
      ChartExtendLargeModel: () => import('@/components/monitor/ChartExtendLargeModel.vue'),
    },
    props: {
      showChart: null,
      apiParams: null,
    },
    watch: {
      showChart(newVal) {
        // console.log(newVal,this.chartConf)
        this.init()
      },
      apiParams: {
        deep: true,
        handler: function (newVal, oldVal) {
          // console.log("ChartExtend-Watch:" + newVal.name)
          this.init()
        }
      },
    },
    data() {
      return {
        // 定时器实例
        timer: null,

        // chart封装组件的传参
        extraPlugin: {
          imgExport: true,
          // dataInterval:{
          //   interval:150,
          //   suffix:'秒'
          // },
        },

        // 会议概况图例选择框
        checkboxLegendSelected: true,
        // 过滤信息
        optionsSummaryType: [],
        firstOptionSelectedType: '',
        firstOptionsType: [],
        secondOptionSelectedType: null,
        secondOptionsType: [],

        buttonDisabled: false,
        // ChartID
        // ChartID: '',
        chartChange: '',
        activeChartConf: {},
        keepAliveParams: null,

        // 此组件支持的chartConf
        chartConfSupport: {
          terminalConfSummary: {
            name: "终端参会概况",
            chartRenderMethod: "terminalConfSummary",  //此处定义图表渲染方式
            dataRenderMethon: "timeline",              //此处定义数据渲染方式
            // dataKey:['data','info'],
            url: ['api', 'getTerminalConfSummary'],  //此处定义数据获取方式
            // url:"cpu",
            urlParams: 'nextReFresh',
            routerPush: '跳转cpu',
            timerInterver: 30,
            action: {},
            options: {
              customerColor: ['#373b3f', '#719cba', '#67e0e3', '#fae373', '#8aab90', '#9fe6b8',
                '#369a48', '#00695c', '#008dcc', '#b39ddb', '#747ffa', '#fac864', '#514aff',
                '#fa7373', '#e062ae', '#c75922', '#c93248', '#ff0000'
              ]
            }
          },
          defaultConf: {
            name: "默认配置",
            chartRenderMethod: "timeline",
            dataRenderMethon: "timeline",
            // dataKey:['data','info'],
            url: ['api', 'getTerminalConfMediaInfo'],
            urlParams: 'nextReFresh',
            staticUrlParams: {
              is: true
            },
            routerPush: '跳转cpu',
            timerInterver: 30,
            options: {
              isArea: true,
              echartsCustom: {
                grid: {
                  left: 113,
                  right: 58,
                  bottom: 100,
                  top: 106,
                  containLabel: false
                },
                legend: {
                  top: 28,
                  right: '10%',
                },
              },
            }
          },
          percent: {
            name: "percent",
            chartRenderMethod: "timeline",
            dataRenderMethon: "timeline",
            // dataKey:['data','info'],
            url: ['api', 'getTerminalConfMediaInfo'],
            urlParams: 'nextReFresh',
            staticUrlParams: {
              is: true
            },
            timerInterver: 30,
            options: {
              isArea: true,
              echartsCustom: {
                grid: {
                  left: 113,
                  right: 58,
                  bottom: 100,
                  top: 106,
                  containLabel: false
                },
                legend: {
                  top: 28,
                  right: '10%',
                },
                yAxis: {
                  name: "%",
                  nameTextStyle: {
                    color: '#9ca9b1',
                    fontSize: 12,
                  }
                },
                tooltip: {
                  formatter: (params,) => {
                    let htmlContent = this.tipFormatter(params, ' %')
                    return htmlContent
                  }
                },
              },
            }
          },
          bandwidth: {
            name: "bandwidth",
            chartRenderMethod: "timeline",
            dataRenderMethon: "timeline",
            // dataKey:['data','info'],
            url: ['api', 'getTerminalConfMediaInfo'],
            urlParams: 'nextReFresh',
            staticUrlParams: {
              is: true
            },
            timerInterver: 30,
            options: {
              isArea: true,
              echartsCustom: {
                grid: {
                  left: 113,
                  right: 58,
                  bottom: 100,
                  top: 106,
                  containLabel: false
                },
                legend: {
                  top: 28,
                  right: '10%',
                },
                yAxis: {
                  name: "kbps",
                  nameTextStyle: {
                    color: '#9ca9b1',
                    fontSize: 12,
                  }
                },
                tooltip: {
                  formatter: (params,) => {
                    let htmlContent = this.tipFormatter(params, ' kbps')
                    return htmlContent
                  }
                },
              },
            }
          },
          bitRate: {
            name: "bandwidth",
            chartRenderMethod: "timeline",
            dataRenderMethon: "timeline",
            // dataKey:['data','info'],
            url: ['api', 'getTerminalConfMediaInfo'],
            urlParams: 'nextReFresh',
            staticUrlParams: {
              is: true
            },
            timerInterver: 30,
            options: {
              isArea: true,
              echartsCustom: {
                grid: {
                  left: 113,
                  right: 58,
                  bottom: 100,
                  top: 106,
                  containLabel: false
                },
                legend: {
                  top: 28,
                  right: '10%',
                },
                yAxis: {
                  name: "kb/s",
                  nameTextStyle: {
                    color: '#9ca9b1',
                    fontSize: 12,
                  }
                },
                tooltip: {
                  formatter: (params,) => {
                    let time = this.$echarts.format.formatTime('yyyy-MM-dd', params[0].value[0])
                      + ' ' + this.$echarts.format.formatTime('hh:mm:ss', params[0].value[0]);
                    let usedFormatter = []
                    let leftHtml = '<div class="lchart-tootip-block__left">'
                    let rightHtml = '<div class="lchart-tootip-block__right">'

                    for (let item of params) {

                      let lstyle = 'style="background: ' + item.color + ';"'
                      let lhtmlContent = '<div class="lchart-tootip-content--block">' +
                        '<div class="lchart-tootip-content-legendicon"' + lstyle + '></div>' +
                        '<div class="lchart-tootip-content-left">' + item.seriesName + '</div>' +
                        '</div>'

                      leftHtml += lhtmlContent
                      let showValue = item.value[1] || item.value[1] === 0 ? item.value[1].toFixed(2) + ' kb/s' : item.value[1]

                      let rhtmlContent = '<div class="lchart-tootip-content--block">' +
                        '<div class="lchart-tootip-content-right">' + ':&nbsp' + showValue + '</div>' +
                        '</div>'
                      rightHtml += rhtmlContent
                    }

                    leftHtml += '</div>'
                    rightHtml += '</div>'

                    usedFormatter = [leftHtml, rightHtml]

                    let header = '<div style="font-size: 16px;margin-bottom: 12px;">' + time + '</div>'
                    let content = [...usedFormatter].join('\n')
                    return header + content;

                  }
                },
              },
            }
          },
          delay: {
            name: "delay",
            chartRenderMethod: "timeline",
            dataRenderMethon: "timeline",
            // dataKey:['data','info'],
            url: ['api', 'getTerminalConfMediaInfo'],
            urlParams: 'nextReFresh',
            staticUrlParams: {
              is: true
            },
            timerInterver: 30,
            options: {
              isArea: true,
              echartsCustom: {
                grid: {
                  left: 113,
                  right: 58,
                  bottom: 100,
                  top: 106,
                  containLabel: false
                },
                legend: {
                  top: 28,
                  right: '10%',
                },
                yAxis: {
                  name: "ms",
                  nameTextStyle: {
                    color: '#9ca9b1',
                    fontSize: 12,
                  }
                },
                tooltip: {
                  formatter: (params,) => {
                    let htmlContent = this.tipFormatter(params, ' ms')
                    return htmlContent
                  }
                },
              },
            }
          },
          frame: {
            name: "frame",
            chartRenderMethod: "timeline",
            dataRenderMethon: "timeline",
            // dataKey:['data','info'],
            url: ['api', 'getTerminalConfMediaInfo'],
            urlParams: 'nextReFresh',
            staticUrlParams: {
              is: true
            },
            timerInterver: 30,
            options: {
              isArea: true,
              echartsCustom: {
                grid: {
                  left: 113,
                  right: 58,
                  bottom: 100,
                  top: 106,
                  containLabel: false
                },
                legend: {
                  top: 28,
                  right: '10%',
                },
                yAxis: {
                  name: "fps",
                  nameTextStyle: {
                    color: '#9ca9b1',
                    fontSize: 12,
                  }
                },
                tooltip: {
                  formatter: (params,) => {
                    let htmlContent = this.tipFormatter(params, ' fps')
                    return htmlContent
                  }
                },
              },
            }
          },
          pixels: {
            name: "pixels",
            chartRenderMethod: "timeline",
            dataRenderMethon: "timeline",
            // dataKey:['data','info'],
            url: ['api', 'getTerminalConfMediaInfo'],
            urlParams: 'nextReFresh',
            staticUrlParams: {
              is: true
            },
            timerInterver: 30,
            options: {
              isArea: true,
              echartsCustom: {
                grid: {
                  left: 113,
                  right: 58,
                  bottom: 100,
                  top: 106,
                  containLabel: false
                },
                legend: {
                  top: 28,
                  right: '10%',
                },
                yAxis: {
                  name: "pixels",
                  nameTextStyle: {
                    color: '#9ca9b1',
                    fontSize: 12,
                  }
                },
                tooltip: {
                  formatter: (params,) => {
                    // console.log(params)
                    let htmlContent = this.tipFormatter(params, ' pixels')
                    return htmlContent
                  }
                },
              },
            }
          },
          byte: {
            name: "byte",
            chartRenderMethod: "timeline",
            dataRenderMethon: "timeline",
            // dataKey:['data','info'],
            url: ['api', 'getTerminalConfMediaInfo'],
            urlParams: 'nextReFresh',
            staticUrlParams: {
              is: true
            },
            timerInterver: 30,
            options: {
              isArea: true,
              echartsCustom: {
                grid: {
                  left: 113,
                  right: 58,
                  bottom: 100,
                  top: 106,
                  containLabel: false
                },
                legend: {
                  top: 28,
                  right: '10%',
                },
                yAxis: {
                  name: "Byte",
                  nameTextStyle: {
                    color: '#9ca9b1',
                    fontSize: 12,
                  }
                },
                tooltip: {
                  formatter: (params,) => {
                    let htmlContent = this.tipFormatter(params, ' Byte')
                    return htmlContent
                  }
                },
              },
            }
          },
        },

        // 1: '丢包率',
        // 3: '卡顿次数',
        // 4: '时延',
        // 5: '抖动',
        // 6: '码率',
        // 7: '帧率',
        // 8: '网络丢帧',
        // 9: '媒体丢帧',
        // 10: '最大帧大小',
        // 11: '关键帧频率',
        // 12: '宽/高',
        // 13: "媒体错误",
        // 14: "帧总数",
        // 15: '网口带宽',
        objOptionsTypeToChartConf: {
          1: {conf: 'percent', label: '丢包率'},
          3: {conf: 'defaultConf', label: '卡顿次数'},
          4: {conf: 'delay', label: '时延'},
          5: {conf: 'defaultConf', label: '抖动'},
          6: {conf: 'bitRate', label: '码率'},
          7: {conf: 'frame', label: '帧率'},
          8: {conf: 'defaultConf', label: '网络丢帧'},
          9: {conf: 'defaultConf', label: '媒体丢帧'},
          10: {conf: 'byte', label: '最大帧大小'},
          11: {conf: 'frame', label: '关键帧频率'},
          12: {conf: 'pixels', label: '宽/高'},
          13: {conf: 'defaultConf', label: '媒体错误'},
          14: {conf: 'defaultConf', label: '帧总数'},
          15: {conf: 'bandwidth', label: '网口带宽'},
          mt: {conf: 'defaultConf', label: '终端'},
          mediaworker: {conf: 'defaultConf', label: '平台媒体'},
          dssworker: {conf: 'defaultConf', label: '转发'},
        },

        tooltipTitle: '',
      };
    },
    methods: {
      // 页面内功能start

      // 过滤项变化
      firstFilterChange(val) {
        this.firstOptionSelectedType = val
        let secondType = this.optionsSummaryType.find(item => item.type === val)
        this.secondOptionsType = [...secondType.data]
        this.secondOptionSelectedType = this.secondOptionsType.length > 0 ? this.secondOptionsType[0].option : null

      },

      buttonChartChange() {
        this.clearTimer();
        this.buttonDisabled = true
        setTimeout(() => {
          this.buttonDisabled = false
        }, 500)
        // console.log(this.secondOptionSelectedType)
        this.tooltipTitle = this.objOptionsTypeToChartConf[this.secondOptionSelectedType] ? this.objOptionsTypeToChartConf[this.firstOptionSelectedType].label + this.objOptionsTypeToChartConf[this.secondOptionSelectedType].label : ''
        let key = this.objOptionsTypeToChartConf[this.secondOptionSelectedType] ? this.objOptionsTypeToChartConf[this.secondOptionSelectedType].conf : 'defaultConf'


        this.activeChartConf = this.chartConfSupport[key]
        this.chartChange = this.firstOptionSelectedType + this.secondOptionSelectedType
        // this.optionSelectedSummaryType=val
        if (this.apiParams) {
          let params = {...this.apiParams}
          if (params.endTime === "now") {
            let timestamp = new Date().setSeconds(0, 0);
            params["endTime"] = timestamp
            this.setTimer(30)
          }
          if (this.activeChartConf.staticUrlParams) {
            let temParams = {
              type: this.firstOptionSelectedType,
              option: this.secondOptionSelectedType,
            }
            this.keepAliveParams = temParams
            params = {...params, ...this.keepAliveParams}
          }
          this.$set(this.activeChartConf, 'urlParams', params)
        }
      },

      // 页面内功能end

      // 定时器函数start
      // 设置定时器
      setTimer(interver = 30, range = 3600000) {
        this.clearTimer();
        this.timer = setInterval(() => {
          // console.log(range)
          let timestamp = new Date().setSeconds(0, 0);
          // console.log(timestamp,timestamp-range)
          let params = {...this.apiParams}
          params["endTime"] = timestamp
          if (this.activeChartConf.staticUrlParams) {
            params = {...params, ...this.keepAliveParams}
          }
          this.$set(this.activeChartConf, 'urlParams', params)
          // this.datePickerTimeRange=[timestamp-range,timestamp]
        }, interver * 1000)
      },
      // 清除定时器
      clearTimer() {
        clearInterval(this.timer);
        this.timer = null;
      },
      // 定时器函数end

      tipFormatter(params, suffix = null) {
        let time = this.$echarts.format.formatTime('yyyy-MM-dd', params[0].value[0])
          + ' ' + this.$echarts.format.formatTime('hh:mm:ss', params[0].value[0]);
        let usedFormatter = []
        let leftHtml = '<div class="lchart-tootip-block__left">'
        let rightHtml = '<div class="lchart-tootip-block__right">'

        for (let item of params) {

          let lstyle = 'style="background: ' + item.color + ';"'
          let lhtmlContent = '<div class="lchart-tootip-content--block">' +
            '<div class="lchart-tootip-content-legendicon"' + lstyle + '></div>' +
            '<div class="lchart-tootip-content-left">' + item.seriesName + '</div>' +
            '</div>'
          // usedFormatter.push(item.seriesName + ': ' + showValue)
          leftHtml += lhtmlContent

          let showValue = Math.ceil(item.value[1]) + suffix
          if (item.value[1] === null || item.value[1] === undefined) {
            showValue = null
          }

          let rhtmlContent = '<div class="lchart-tootip-content--block">' +
            '<div class="lchart-tootip-content-right">' + ':&nbsp' + showValue + '</div>' +
            '</div>'
          rightHtml += rhtmlContent
        }

        leftHtml += '</div>'
        rightHtml += '</div>'

        usedFormatter = [leftHtml, rightHtml]
        // console.log(freeFormatter)
        let header = '<div style="font-size: 16px;margin-bottom: 12px;">' + time + '</div>'
        let content = [...usedFormatter].join('\n')
        return header + content;
      },

      // 组件chart初始化
      async init() {
        // this.setTimer(2)
        // console.log(this.apiParams.endTime)
        if (this.apiParams && this.apiParams.confID && this.apiParams.mtE164) {
          if (this.showChart === 'terminalConfSummary') {
            this.activeChartConf = this.chartConfSupport[this.showChart]
            this.chartChange = this.showChart
            let params = {...this.apiParams}
            if (params.endTime === "now") {
              let timestamp = new Date().setSeconds(0, 0);
              params["endTime"] = timestamp
              this.setTimer(30)
            }
            this.$set(this.activeChartConf, 'urlParams', params)
          } else {
            let mediaInfoType = await this.$api.getChartData.getTerminalConfMediaInfoOptions(this.apiParams)
            this.optionsSummaryType = mediaInfoType
            if (this.optionsSummaryType.length > 0) {
              this.firstFilterChange(this.optionsSummaryType[0].type)
              this.buttonChartChange()
            } else {
              this.$notify({
                title: '暂无数据'
              })
            }
          }
          // console.log(this.activeChartConf)
          // let params={
          //   confID: 6660951,
          //   mtE164: 1212120000000,
          //   startTime:1564588800000,
          //   endTime: 1566144000000,
          //   confType:0,
          // }
        }
      },
    },
    mounted() {
      this.init()
    },
    beforeDestroy() {
      this.clearTimer()
    },
  }
</script>

<style>
  .checkbox-terminal-confsummary {
    position: absolute;
    z-index: 99;
    top: 27px;
    left: 45px;

  }

  .el-checkbox.checkbox-terminal-confsummary .el-checkbox__label {
    font-size: 14px;
  }

  .meetinginfo-tootip-content--block {

  }

  .meetinginfo-tootip-content--block {
    font-size: 14px;
    width: 100%;
    /*padding: 0 8px;*/
    box-sizing: border-box;
    text-align: right;
  }

  .meetinginfo-tootip-content-left {
    /*float: left;*/
    display: inline-block;
    text-align: right;
    /*width: calc(100% - 70px);*/
    /*text-align: left;*/
    /*width: 60%;*/
  }

  .meetinginfo-tootip-content-right {
    /*float: right;*/
    display: inline-block;
    /*width: 40px;*/
    width: 80px;
    /*width: 40%;*/
    text-align: left;
    padding-left: 10px;
  }

  .chart-extend-plugin--mmits {
    top: 25px;
    right: 58px;
    z-index: 99;
  }
</style>
