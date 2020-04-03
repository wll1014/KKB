<template>
  <div class="theme-dark" style="position: relative;padding-top: 20px;padding-left: 27px;padding-right: 20px;">
    <div>
      <KdTabCommon :tab-list="tabList" :active-tab="activeTab" class-name="tab-alarm"
                   @tab-change="tabChange"></KdTabCommon>
    </div>
    <!--筛选区-->
    <div class="area-stats-rc-filter" style="background-color: #232629;padding-top: 20px;padding-left: 20px;">
      <div :class="activeTab!=='ResourceConference'?'conf-filter--oneline conf-filter--layout':'conf-filter--twoline'">
        <div class="conf-filter--layout">
          <el-select style="margin-right: 7px;width: 240px;" @change="filterChangeDomainPlatform" filterable
                     :popper-append-to-body="false" popper-class="theme-dark" v-model="optionSelectedDomainPlatform"
                     placeholder="请选择">
            <el-option
              v-for="item in optionsDomainPlatform" :key="item.moid" :label="item.name" :value="item.moid">
            </el-option>
          </el-select>
        </div>
        <div class="conf-filter--layout">
          <el-select style="margin-right: 7px;width: 240px;" @change="filterChangeMachineRoom" filterable
                     :popper-append-to-body="false" popper-class="theme-dark" v-model="optionSelectedMachineRoom"
                     placeholder="请选择">
            <el-option
              v-for="item in optionsMachineRoom" :key="item.moid" :label="item.name" :value="item.moid">
            </el-option>
          </el-select>
        </div>
        <div class="conf-filter--layout" style="display: inline-block;margin-right: 7px;">
          <el-select style="width: 120px;" @change="selectDataChange" popper-class="theme-dark"
                     v-model="timeRnageSelectedOptions" placeholder="请选择平台域">
            <el-option
              v-for="item in timeRnageList" :key="item[0]" :label="item[0]" :value="item[1]">
            </el-option>
          </el-select>
        </div>

        <div class="conf-filter--layout" style="margin-right: 7px;vertical-align: top;">
          <el-date-picker
            v-model="datePickerTimeRange"
            type="datetimerange"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            popper-class="theme-dark"
            value-format="timestamp"
            format="yyyy-MM-dd HH:mm"
            @focus="recoderDatePicker(datePickerTimeRange)"
            @blur="judgeDatePickerChange(datePickerTimeRange)"
            style="width: 322px;vertical-align: bottom;"
            range-separator=""
            class="clear-close-icon"
            prefix-icon="ops-icons-bg icon-calendar"
            :clearable=false
          >
          </el-date-picker>
        </div>
        <div class="conf-filter--layout" style="">
          <el-button @click="searchMonitor">搜索</el-button>
        </div>
      </div>
    </div>
    <!--筛选区 end-->
    <div v-if="activeTab==='ResourceConference'" style="background-color: #1e2224;">
      <div style="height: 242px;width: 100%;background-color: #232629">
        <ChartStatsConferenceInfo ChartID="IDChartStatsConferenceInfo"
                                  :chartList="['conf_resources']"></ChartStatsConferenceInfo>
      </div>
      <!--<hr style="border:1px dashed #4e4e4e;" width="90%" >-->
      <div class="resource-conference-block"
           style="margin-top: 20px;padding-top: 60px;">
        <div style="height: 100%;width: 100%;">
          <ChartExtendLargeModel ChartID="IDStatsResourceConference"
                                 :chartChange="chartChange"
                                 :chartConf="activeChartConf"
                                 :extraPlugin="extraPlugin"
                                 extraPluginClass="chart-extend-plugin--common"></ChartExtendLargeModel>
        </div>
      </div>
    </div>
    <div v-if="activeTab==='OnGoingConference'">
      <div class="resource-conference-block">
        <ChartExtendLargeModel key="IDOnGoingConference" ChartID="IDOnGoingConference" :chartChange="chartChange"
                               :chartConf="activeChartConf" :extraPlugin="extraPlugin"
                               extraPluginClass="chart-extend-plugin--resconf"></ChartExtendLargeModel>
      </div>
    </div>
    <div v-if="activeTab==='AmountTerminal'">
      <div class="resource-conference-block">
        <ChartExtendLargeModel key="IDAmountTerminal" ChartID="IDAmountTerminal" :chartChange="chartChange"
                               :chartConf="activeChartConf" :extraPlugin="extraPlugin"
                               extraPluginClass="chart-extend-plugin--resconf"></ChartExtendLargeModel>
      </div>
    </div>
    <div v-if="activeTab==='ForwardingResources'">
      <div class="resource-conference-block">
        <ChartExtendLargeModel key="IDForwardingResources" ChartID="IDForwardingResources" :chartChange="chartChange"
                               :chartConf="activeChartConf" :extraPlugin="extraPlugin"
                               extraPluginClass="chart-extend-plugin--resconf"></ChartExtendLargeModel>
      </div>
    </div>
    <!--  <div v-if="activeTab==='mtInfo'">
          <MonitorMeetingInfoTerminalSummary :apiParams="mtParams" showChart="networkUtilizationIn"></MonitorMeetingInfoTerminalSummary>
      </div>-->
  </div>
</template>

<script>
  // import ChartExtendLargeModel from '@/components/monitor/ChartExtendLargeModel.vue'
  // import KdTabCommon from '@/components/common/KdTabCommon.vue'
  export default {
    name: "StatsResourceConference",
    components: {
      // ChartExtendLargeModel,
      // KdTabCommon,
      ChartStatsConferenceInfo: () => import('@/components/monitor/ChartStatsConferenceInfo.vue'),
      KdTabCommon: () => import('@/components/common/KdTabCommon.vue'),
      ChartExtendLargeModel: () => import('@/components/monitor/ChartExtendLargeModel.vue'),
      MonitorMeetingInfoTerminalSummary: () => import('@/components/monitor/MonitorMeetingInfoTerminalSummary.vue'),
    },
    data() {
      return {
        // 定时器实例
        timer: null,
        // tab信息
        activeTab: 'ResourceConference',
        tabList: [
          ['ResourceConference', '会议资源'],
          ['OnGoingConference', '会议数量'],
          ['AmountTerminal', '终端数量'],
          ['ForwardingResources', '转发资源'],
        ],

        // 过滤信息
        optionSelectedDomainPlatform: '',
        optionsDomainPlatform: [],
        optionSelectedMachineRoom: '',
        optionsMachineRoom: [],

        defaultDomainPlatform: '',//默认显示的第一个平台域

        // 时间相关
        theTimeRange: 3600000,
        datePickerTimeRange: '',
        timeRnageSelectedOptions: '最近 一小时',
        timeRnageList: [["自定义", "customer"],
          ["最近 一小时", 3600000],
          ["最近 一天", 86400000],
          ["最近 七天", 86400000 * 7],
          ["最近 十五天", 86400000 * 15],
          ["最近 一个月", 86400000 * 30],
          ["最近 半年", 86400000 * 180],
        ],

        // 记录上一次时间的选择
        frontDatePickerTimeRange: null,

        // 公用过滤信息
        filterParams: {},

        // ChartID
        // ChartID: '',
        chartChange: '',
        activeChartConf: {},

        // chart封装组件的传参
        extraPlugin: {
          imgExport: true,
        },

        // 此组件支持的chartConf
        chartConfSupport: {
          // mtInfo:{
          //   name: "测试",
          //   timerInterver: 60,
          // },
          ResourceConference: {
            name: "会议资源统计信息",
            chartRenderMethod: "timeline",
            dataRenderMethon: "timeline",
            // dataKey:['data','info'],
            url: ['api', 'getLineMediaResources'],
            urlParams: 'nextReFresh',
            loading: true,
            routerPush: '跳转cpu',
            timerInterver: 30,
            options: {
              isArea: true,
              echartsCustom: {
                grid: {
                  bottom: 45,
                  top: 60,
                },
                yAxis: {
                  name: "个数",
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
                        '<div class="lchart-tootip-content-left">' + item.seriesName + "已占用" + '</div>' +
                        '</div>'
                      // usedFormatter.push(item.seriesName + ': ' + showValue)
                      leftHtml += lhtmlContent

                      let showValue = null
                      if (item.value[1] !== null && item.value[1] !== undefined) showValue = item.value[1].toFixed(0)
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
                  }
                },
              },
            }
          },
          OnGoingConference: {
            name: "会议数量",
            chartRenderMethod: "timeline",
            dataRenderMethon: "timeline",
            // dataKey:['data','info'],
            // url: ['common','/statistics/conf_num/'],
            url: ['common', '/statistics/curr_confs/'],
            urlParams: 'nextReFresh',
            loading: true,
            routerPush: '跳转cpu',
            timerInterver: 30,
            options: {
              isArea: true,
              echartsCustom: {
                grid: {
                  bottom: 45
                },
                yAxis: {
                  name: "个数",
                  nameTextStyle: {
                    color: '#9ca9b1',
                    fontSize: 12,
                  }
                },
              },
            }
          },
          AmountTerminal: {
            name: "终端数量",
            chartRenderMethod: "timeline",
            dataRenderMethon: "timeline",
            // dataKey:['data','info'],
            url: ['common', '/statistics/terminal_resources/'],
            urlParams: 'nextReFresh',
            loading: true,
            timerInterver: 30,
            options: {
              isArea: true,
              echartsCustom: {
                grid: {
                  bottom: 45
                },
                yAxis: {
                  name: "个数",
                  nameTextStyle: {
                    color: '#9ca9b1',
                    fontSize: 12,
                  }
                },
              },
            }
          },
          ForwardingResources: {
            name: "转发资源",
            chartRenderMethod: "timeline",
            dataRenderMethon: "timeline",
            // dataKey:['data','info'],
            url: ['api', 'getSHTransmitResources'],
            urlParams: 'nextReFresh',
            loading: true,
            timerInterver: 30,
            options: {
              isArea: true,
              echartsCustom: {
                grid: {
                  bottom: 45
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
                    let time = this.$echarts.format.formatTime('yyyy-MM-dd', params[0].value[0])
                      + ' ' + this.$echarts.format.formatTime('hh:mm:ss', params[0].value[0]);
                    let usedFormatter = []

                    let leftHtml = '<div class="lchart-tootip-block__left">'
                    let rightHtml = '<div class="lchart-tootip-block__right">'

                    for (let item of params) {

                      let lstyle = 'style="background: ' + item.color + ';"'
                      let lhtmlContent = '<div class="lchart-tootip-content--block">' +
                        '<div class="lchart-tootip-content-legendicon"' + lstyle + '></div>' +
                        '<div class="lchart-tootip-content-left">' + '使用率' + '</div>' +
                        '</div>' +
                        '<div class="lchart-tootip-content--block">' +
                        '<div class="lchart-tootip-content-legendicon"' + lstyle + '></div>' +
                        '<div class="lchart-tootip-content-left">' + '已用带宽' + '</div>' +
                        '</div>'
                      // usedFormatter.push(item.seriesName + ': ' + showValue)
                      leftHtml += lhtmlContent

                      let showValue = null
                      let avaliable = null
                      if (item.value[1] !== null && item.value[1] !== undefined) {
                        showValue = item.value[1].toFixed(2) + " %"
                        avaliable = (item.value[2] / 1024).toFixed(2) + "Mbps"
                      }
                      let rhtmlContent = '<div class="lchart-tootip-content--block">' +
                        '<div class="lchart-tootip-content-right">' + ':&nbsp' + showValue + '</div>' +
                        '</div>' +
                        '<div class="lchart-tootip-content--block">' +
                        '<div class="lchart-tootip-content-right">' + ':&nbsp' + avaliable + '</div>' +
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
                  }
                },
              },
            }
          },
        }
      };
    },
    methods: {
      // 页面内功能start
      // tab变化
      tabChange(val) {
        // console.log(val)
        this.clearTimer()
        this.activeTab = val
        this.chartChange = val
        this.activeChartConf = {...this.chartConfSupport[val]}
        this.theTimeRange = 3600000
        this.timeRnageSelectedOptions = '最近 一小时'
        this.selectDataChange(this.theTimeRange);
        // this.getAllPlatformDomainInfo()
        this.optionSelectedDomainPlatform = this.defaultDomainPlatform,
          this.filterChangeDomainPlatform(this.optionSelectedDomainPlatform, true)
        this.setTimer(this.activeChartConf.timerInterver, this.theTimeRange)
      },
      // 过滤项变化
      async filterChangeDomainPlatform(val, reFresh = false) {
        this.optionSelectedMachineRoom = '',
          this.optionsMachineRoom = []
        if (val) {
          await this.getMachineRoomInfo(val)
          if (reFresh) {
            this.$nextTick(function () {
              this.getChartData()
            });
          }
        }
      },
      filterChangeMachineRoom(val) {

      },
      // 自定义时间段选择器函数
      selectDataChange(val) {
        // console.log(val)
        this.theTimeRange = val
        if (val === "customer") {
          // this.clearTimer();
          this.datePickerTimeRange = '';
        } else {
          let timestamp = (new Date()).getTime();
          // console.log(timestamp,timestamp-val)
          this.datePickerTimeRange = [timestamp - val, timestamp]
        }
        // this.getData(timestamp-3600000,timestamp)
      },
      // 搜索按钮
      searchMonitor() {
        let urlParams = {
          platform_moid: this.optionSelectedDomainPlatform === 'all' ? null : this.optionSelectedDomainPlatform,
          room_moid: this.optionSelectedMachineRoom === 'all' ? null : this.optionSelectedMachineRoom,
          start_time: this.datePickerTimeRange ? this.datePickerTimeRange[0] : null,
          end_time: this.datePickerTimeRange ? this.datePickerTimeRange[1] : null,
        }
        // console.log(urlParams)
        let newFilterParams = {
          platform_moid: this.optionSelectedDomainPlatform === 'all' ? null : this.optionSelectedDomainPlatform,
          room_moid: this.optionSelectedMachineRoom === 'all' ? null : this.optionSelectedMachineRoom,
        }
        this.filterParams = {...newFilterParams}
        this.$set(this.activeChartConf, 'loading', true)  // 图表加载页面
        if (this.theTimeRange === "customer") {
          this.clearTimer();
          this.$set(this.activeChartConf, 'urlParams', urlParams)
          // this.dataChange(this.datePickerTimeRange)
        } else {
          // this.dataChange(this.datePickerTimeRange)
          this.$set(this.activeChartConf, 'urlParams', urlParams)
          this.setTimer(this.activeChartConf.timerInterver, this.theTimeRange)
        }
      },
      // 选中时间组件时判断时间是否有改变，若改变下拉框改为“自定义”
      recoderDatePicker(val) {
        this.frontDatePickerTimeRange = val
      },
      judgeDatePickerChange(val) {
        if (this.frontDatePickerTimeRange !== this.datePickerTimeRange) {
          this.timeRnageSelectedOptions = "自定义"
          this.theTimeRange = "customer"
        }
      },
      // 页面内功能end


      // 定时器函数start
      // 设置定时器
      setTimer(interver = 60, range = 3600000) {
        this.clearTimer();
        this.timer = setInterval(() => {
          // console.log(range)
          let timestamp = (new Date()).getTime();

          let params = {
            start_time: timestamp - range,
            end_time: timestamp,
          }
          let urlParams = {...this.filterParams, ...params}
          this.$set(this.activeChartConf, 'urlParams', urlParams)
          // this.datePickerTimeRange=[timestamp-range,timestamp]
        }, interver * 1000)
      },
      // 清除定时器
      clearTimer() {
        clearInterval(this.timer);
        this.timer = null;
      },
      // 定时器函数end

      // api start
      async getAllPlatformDomainInfo() {
        let platformDomainInfo = await this.$api.globalData.allPlatformDomain()

        this.optionsDomainPlatform = []
        // this.optionSelectedDomainPlatform= 'all'

        let filterDomain = platformDomainInfo.filter(item => item.domain_type === 1) //过滤出平台域
        this.optionsDomainPlatform = this.optionsDomainPlatform.concat(filterDomain)
        this.defaultDomainPlatform = filterDomain[0].moid
        this.$nextTick(function () {
          this.optionSelectedDomainPlatform = filterDomain[0].moid
        });
        await this.getMachineRoomInfo(filterDomain[0].moid)
        this.$nextTick(function () {
          this.getChartData()
        });
      },
      async getMachineRoomInfo(id) {
        // this.optionSelectedMachineRoom= 'all',
        this.optionsMachineRoom = []
        let machineRoomInfo = await this.$api.homePage.getMachineRoomInfo(id)
        this.optionsMachineRoom = machineRoomInfo
        this.$nextTick(function () {
          this.optionSelectedMachineRoom = machineRoomInfo[0] ? machineRoomInfo[0].moid : ''
        });

      },

      async getChartData() {
        let urlParams = {
          platform_moid: this.optionSelectedDomainPlatform === 'all' ? null : this.optionSelectedDomainPlatform,
          room_moid: this.optionSelectedMachineRoom === 'all' ? null : this.optionSelectedMachineRoom,
          start_time: this.datePickerTimeRange ? this.datePickerTimeRange[0] : null,
          end_time: this.datePickerTimeRange ? this.datePickerTimeRange[1] : null,
        }
        // console.log(urlParams)
        let newFilterParams = {
          platform_moid: this.optionSelectedDomainPlatform === 'all' ? null : this.optionSelectedDomainPlatform,
          room_moid: this.optionSelectedMachineRoom === 'all' ? null : this.optionSelectedMachineRoom,
        }
        this.filterParams = {...newFilterParams}
        this.$set(this.activeChartConf, 'urlParams', urlParams)
      },
      // api end
      // 组件chart初始化
      init() {
        // this.setTimer(10)
        // 调整当前route，变化侧边栏高亮
        let activeRouteList = ['/ops/monitor/stats_resource_conf', '/ops/monitor']
        this.$store.dispatch('activeRouteChange', activeRouteList)
        // 调整当前route，变化侧边栏高亮 end
        if (Object.keys(this.$route.query).length !== 0) {
          this.activeTab = this.$route.query.tab
        }

        this.activeChartConf = {...this.chartConfSupport[this.activeTab]}
        this.chartChange = this.activeTab

        this.selectDataChange(this.theTimeRange);
        this.getAllPlatformDomainInfo()
        this.setTimer(this.activeChartConf.timerInterver, this.theTimeRange)

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
  .tab-alarm {
    margin-bottom: 20px;
  }

  .chart-extend-plugin--common {
    top: -26px;
    right: 20px;
  }

  .chart-extend-plugin--resconf {
    top: -26px;
    right: 20px;
  }

  .conf-filter--oneline {
    display: inline-block;
  }

  .conf-filter--twoline {
    /*display: inline-block;*/
    position: absolute;
    top: 364px;
    z-index: 99;
  }

  .conf-filter--layout {
    height: 28px;
    line-height: 28px;
    display: inline-block;
    padding-left: 5px;
  }

  .resource-conference-block {
    height: 450px;
    width: 100%;
    padding-top: 10px;
    background-color: #232629;
  }
</style>
