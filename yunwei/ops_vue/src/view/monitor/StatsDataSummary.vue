<template>
  <div class="theme-dark">
    <!--图区-->
    <div style="width: 100%;position: relative;box-sizing: border-box;padding: 10px 10px 10px 17px"
         v-if="showArea==='main'">
      <div style="padding: 0 10px;">
        <KdTabCommon style="display: inline-block;" :tab-list="tabList" :active-tab="activeTab" class-name="tab-alarm"
                     @tab-change="tabChange"></KdTabCommon>
        <div style="display: inline-block;float: right;line-height: 24px;" v-if="!pageEditStatu">
          <el-button @click="pageEdit('edit')">编辑图表</el-button>
        </div>


        <div style="display: inline-block;float: right;line-height: 24px;" v-if="pageEditStatu">
          <el-dropdown placement="bottom-start" trigger="click" @command="addChart">
            <el-button style="padding: 6px 18px 6px 18px;">添加</el-button>
            <el-dropdown-menu slot="dropdown" class="theme-dark" style="width: 240px;">
              <el-dropdown-item v-for="item in Object.keys(chartConfSupport)" :command="[item,chartConfSupport[item]]"
                                :key="item">{{chartConfSupport[item].name}}
              </el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>
          <el-button style="margin-left: 10px;" @click="pageEdit('save')">保存</el-button>
          <el-button @click="pageEdit('cancel')">取消</el-button>
        </div>
      </div>
      <!--<div style="position: relative;">-->
      <!---->
      <!--</div>-->
      <div style="width: 100%;margin-top: 20px;font-size: 0;box-sizing:border-box;">
        <div class="area-block--dragchart" style=""
             v-for="(item,index) in chartList"
             :draggable="pageEditStatu"
             @dragstart="handleDragStart($event, item)"
             @dragover.prevent
             @drop="handleDrop($event, item)"
             :key="item.name+index">
          <!--标题区-->
          <div style="position: absolute;top:8px;left: 20px;z-index: 9;">
            <div style="font-size: 14px;color:#9ca9b1;">{{chartConfSupport[item.name].name}}</div>
          </div>
          <!--更多按钮区域-->
          <div style="position: absolute;top:8px;right: 20px;z-index: 1000">
            <button type="button" class="ops-button-text" @click="buttonMore(item.name)"
                    v-if="!pageEditStatu && childPageConf[item.name]">
              <span style="font-size: 12px;">更多</span>
            </button>
            <i style="font-size: 14px;cursor: pointer;" class="el-icon-delete" @click="delChart(item)"
               v-if="pageEditStatu"></i>
          </div>
          <ChartExtendLargeModel :ChartID="'ID'+ item.name + index" :chartConf="chartConfSupport[item.name]"
                                 :chartChange="item.name"></ChartExtendLargeModel>
        </div>

      </div>
    </div>
    <!--子页面区-->
    <div style="width: 100%;" v-if="showArea==='children'">
      <StatsDataSummaryChildPage :chartConf="activeChildChartConf" :pageConf="activeChildPageConf"
                                 @back="backMainPage"></StatsDataSummaryChildPage>
    </div>
    <div style="width: 100%;" v-if="showArea==='detail'">
      <StatsDataSummaryDetail @back="backMainPage"
                              :name="activeChildPageConf.key"></StatsDataSummaryDetail>
    </div>
  </div>
</template>

<script>
  export default {
    name: "StatsDataSummary",
    components: {
      KdTabCommon: () => import('@/components/common/KdTabCommon.vue'),
      ChartExtendLargeModel: () => import('@/components/monitor/ChartExtendLargeModel.vue'),
      StatsDataSummaryChildPage: () => import('@/view/monitor/StatsDataSummaryChildPage.vue'),
      StatsDataSummaryDetail: () => import('@/view/monitor/StatsDataSummaryDetail.vue'),
    },
    data() {
      return {
        // 定时器实例
        timer: null,
        // 传递子页面当前的chartConf
        activeChildPageConf: '',
        activeChildChartConf: '',
        // tab信息
        activeTab: 'StatsDataSummary',
        tabList: [
          ['StatsDataSummary', '数据概览'],
        ],
        // 显示的区域
        showArea: 'main',

        pageEditStatu: false,

        chartList: [],

        // start 此组件支持的chartConf
        chartConfSupport: {
          enterprise_conf_stats_number: {
            name: "当日企业会议数",
            chartRenderMethod: "barYaxis",
            dataRenderMethon: "barYaxis",
            chartKey: 'enterprise_conf_stats_number',
            // dataKey:['data','info'],
            url: ['common', '/statistics/company_conf/'],
            timerInterver: 30,
            startTime: 'today',
            urlParams: 'nextReFresh',
            loading: true,
            staticUrlParams: {
              count: 10,
            },
            // url:"cpu",
            routerPush: '跳转cpu',
            options: {
              grid: {
                left: 93,
                right: 40,
                bottom: 35,
                top: 50,
                containLabel: false
              },
            },
          },
          stats_enterprise_info: {
            name: "企业信息统计",
            chartRenderMethod: "pie",
            dataRenderMethon: "pie",
            chartKey: 'stats_enterprise_info',
            // dataKey:['data','info'],
            url: ['common', '/statistics/company_info/'],
            urlParams: 'nextReFresh',
            loading: true,
            routerPush: '跳转cpu',
            timerInterver: 30,
            options: {
              customerColor: ['#2c8dc5', '#e45959'],
              selectedMode: ['停用企业'],
              minAngle: 10,
              center: ['50%', '55%'],
              label: {

                formatter: function (params) {
                  return "{label|" + params.name + "}" + "{value|：" + params.value + "个}\n" +
                    "{label|占比}" + "{value|：" + params.percent + "%}"
                },
                // formatter:'{b}：{c} 个\n\n占比： {d} %',
                rich: {
                  label: {
                    fontSize: 12,
                    height: 16,
                    width: 54,
                    color: '#9ca9b1',
                    align: 'left',
                    padding: [0, 0, 0, 10]
                  },
                  value: {
                    fontSize: 12,
                    height: 16,
                    align: 'left',
                    color: '#9ca9b1',
                  },
                }
              },
            }
          },
          stats_terminal_info: {
            name: "账号信息统计",
            chartRenderMethod: "pie",
            dataRenderMethon: "pie",
            chartKey: 'stats_terminal_info',
            // dataKey:['data','info'],
            url: ['common', '/statistics/terminal_info/'],
            urlParams: 'nextReFresh',
            loading: true,
            routerPush: '跳转cpu',
            timerInterver: 30,
            options: {
              customerColor: ['#2c8dc5', '#e45959'],
              selectedMode: ['停用帐号'],
              minAngle: 10,
              center: ['50%', '55%'],
              label: {
                color: '#9ca9b1',
                formatter: function (params) {
                  return "{label|" + params.name + "}" + "{value|：" + params.value + "个}\n" +
                    "{label|占比}" + "{value|：" + params.percent + "%}"
                },
                rich: {
                  label: {
                    fontSize: 12,
                    height: 16,
                    width: 54,
                    color: '#9ca9b1',
                    align: 'left',
                    padding: [0, 0, 0, 10]

                  },
                  value: {
                    fontSize: 12,
                    height: 16,
                    align: 'left',
                    color: '#9ca9b1',
                  },
                }
              },
            }
          },
          conf_created_time: {
            name: "当日创建会议时长 (单位：个数)",
            chartRenderMethod: "barXaxis",
            dataRenderMethon: "barXaxis",
            // dataKey:['data','info'],
            chartKey: 'conf_created_time',
            url: ['common', '/statistics/create_conf_time/'],
            loading: true,
            startTime: 'today',
            urlParams: 'nextReFresh',
            routerPush: '跳转cpu',
            timerInterver: 30,
            options: {
              echartsCustom: {
                grid: {
                  left: 93,
                  right: 40,
                  bottom: 50,
                  top: 50,
                  containLabel: false
                },
                tooltip: {
                  enterable: true,
                  hideDelay: 500,
                  formatter: (params,) => {
                    let title = '<div class="tooltip-title-create-conf-p">' + '<span>' + params.value[0] + '</span>' +
                      '<span>' + ':&nbsp' + params.value[1] + '个' + '</span>' + '</div>'
                    let detail = params.value[2]
                    let htmlContent = []
                    let ct = '<div class="tooltip-content-create-conf-p" >' +
                      '<span>' + '会议号' + '</span>' +
                      '<span>' + '会议名' + '</span>' +
                      '</div>'
                    if (detail.length > 0) {
                      htmlContent.push(ct)
                      detail.forEach((item) => {
                        let temHtml = '<div class="tooltip-content-create-conf-p" >' +
                          '<span>' + item.confE164 + '</span>' +
                          '<span>' + item.confname + '</span>' +
                          '</div>'
                        htmlContent.push(temHtml)
                      })
                    }
                    let content = htmlContent.join('\n')
                    return '<div class="tooltip-block-create-conf-p">' + title + content + '</div>'
                  },
                },
              }
            },
          },
          conf_continue_time: {
            name: "当日会议时长 (单位：个数)",
            chartRenderMethod: "barXaxis",
            dataRenderMethon: "barXaxis",
            seriseDataReverse: true, //数据是否翻转
            // dataKey:['data','info'],
            chartKey: 'conf_continue_time',
            url: ['common', '/conf_time/'],
            startTime: 'today',
            urlParams: 'nextReFresh',
            loading: true,
            timerInterver: 30,
            options: {
              grid: {
                left: 93,
                right: 40,
                bottom: 50,
                top: 50,
                containLabel: false
              }
            }
          },
          stats_created_conf: {
            name: "创会数量统计",
            chartRenderMethod: "scatter",
            dataRenderMethon: "scatter",
            // dataKey:['data','info'],
            url: ['common', '/statistics/create_conf_type/'],
            // url:"cpu",
            urlParams: 'nextReFresh',
            chartKey: 'stats_created_conf',
            loading: true,
            timerInterver: 30,
            options: {
              echartsCustom: {
                grid: {
                  left: 93,
                  right: 40,
                  bottom: 50,
                  top: 50,
                  containLabel: false
                },
                legend: {
                  top: 8,
                },
                yAxis: {
                  max: function (v) {
                    let l = v.max.toString().length
                    if (l) {
                      let x = ('1' + new Array(l).join('0'))
                      return v.max + parseInt(x)
                    }
                  },
                },
              },
            },
          },
          stats_terminal_call: {
            name: "终端呼叫数量",
            chartRenderMethod: "timeline",
            dataRenderMethon: "timeline",
            // dataKey:['data','info'],
            chartKey: 'stats_terminal_call',

            url: ['common', '/statistics/calling_terminals/'],
            urlParams: 'nextReFresh',
            loading: true,
            timerInterver: 30,
            options: {
              isArea: true,
              echartsCustom: {
                grid: {
                  left: 93,
                  right: 40,
                  bottom: 50,
                  top: 50,
                  containLabel: false
                },
                legend: {
                  top: 8,
                },
              },
            }
          },
          utilization_live_broadcasts: {
            name: "直播资源使用率",
            chartRenderMethod: "timeline",
            dataRenderMethon: "timeline",
            chartKey: 'utilization_live_broadcasts',
            url: ['api', 'getStatisticsVrsResources'],
            urlParams: 'nextReFresh',
            loading: true,
            timerInterver: 30,
            options: {
              isArea: true,
              // color:['#d8a77e','#cb7579']
              echartsCustom: {
                grid: {
                  left: 93,
                  right: 40,
                  bottom: 50,
                  top: 50,
                  containLabel: false
                },
                legend: {
                  top: 8,
                },
                yAxis: {
                  max: function (v) {
                    let l = (v.max.toString().length > 3 ? v.max.toString().length - 3 : v.max.toString().length)
                    if (l) {
                      let x = ('1' + new Array(l).join('0'))
                      return Math.ceil(v.max) + parseInt(x)
                    }
                  }
                },
                tooltip: {
                  formatter: (params,) => {
                    // console.log(params)
                    let time = this.$echarts.format.formatTime('yyyy-MM-dd', params[0].value[0])
                      + ' ' + this.$echarts.format.formatTime('hh:mm:ss', params[0].value[0]);
                    let usedFormatter = []
                    let leftHtml = '<div class="lchart-tootip-block__left">'
                    let rightHtml = '<div class="lchart-tootip-block__right">'
                    for (let item of params) {
                      let lstyle = 'style="background: ' + item.color + ';"'
                      let leftHtmlContent = '<div class="lchart-tootip-content--block">' +
                        '<div class="lchart-tootip-content-legendicon"' + lstyle + '></div>' +
                        '<div class="lchart-tootip-content-left">' + item.seriesName + '使用率' + '</div>' +
                        '</div>' +
                        '<div class="lchart-tootip-content--block">' +
                        '<div class="lchart-tootip-content-legendicon"' + lstyle + '></div>' +
                        '<div class="lchart-tootip-content-left">' + item.seriesName + '已用' + '</div>' +
                        '</div>' +
                        '<div class="lchart-tootip-content--block">' +
                        '<div class="lchart-tootip-content-legendicon"' + lstyle + '></div>' +
                        '<div class="lchart-tootip-content-left">' + item.seriesName + '总数' + '</div>' +
                        '</div>'

                      // usedFormatter.push(item.seriesName + ': ' + showValue)
                      leftHtml += leftHtmlContent

                      let showValue = null
                      if (item.value[1] !== null && item.value[1] !== undefined) showValue = item.value[1].toFixed(2) + " %"
                      let rightHtmlContent = '<div class="chart-tootip-content--block">' +
                        '<div class="lchart-tootip-content-right">' + ':&nbsp' + showValue + '</div>' +
                        '</div>' +
                        '<div class="lchart-tootip-content--block">' +
                        '<div class="lchart-tootip-content-right">' + ':&nbsp' + item.value[2][1] + '</div>' +
                        '</div>' +
                        '<div class="lchart-tootip-content--block">' +
                        '<div class="lchart-tootip-content-right">' + ':&nbsp' + item.value[2][0] + '</div>' +
                        '</div>'
                      // usedFormatter.push(item.seriesName + ': ' + showValue)
                      rightHtml += rightHtmlContent
                    }
                    leftHtml += '</div>'
                    rightHtml += '</div>'
                    usedFormatter = [leftHtml, rightHtml]
                    let header = '<div style="font-size: 12px;margin-bottom: 8px;">' + time + '</div>'
                    let content = [...usedFormatter].join('\n')
                    return header + content;
                  }
                },
              },
            }
          },
          resource_reservation: {
            name: "预约资源",
            chartRenderMethod: "timeline",
            dataRenderMethon: "timeline",
            // dataKey:['data','info'],
            chartKey: 'resource_reservation',

            url: ['common', '/statistics/appointment/'],
            urlParams: 'nextReFresh',
            loading: true,
            timerInterver: 30,
            options: {
              isArea: true,
              echartsCustom: {
                grid: {
                  left: 93,
                  right: 40,
                  bottom: 50,
                  top: 50,
                  containLabel: false
                },
                legend: {
                  top: 8,
                },
                yAxis: {
                  max: function (v) {
                    let l = v.max.toString().length
                    if (l) {
                      let x = ('1' + new Array(l).join('0'))
                      return v.max + parseInt(x)
                    }
                  }
                },
              },
            }
          },
          stats_living_terminal: {
            name: "观看直播人数",
            chartRenderMethod: "timeline",
            dataRenderMethon: "timeline",
            // dataKey:['data','info'],
            chartKey: 'stats_living_terminal',
            url: ['common', '/statistics/vrs/'],
            urlParams: 'nextReFresh',
            loading: true,
            timerInterver: 30,
            options: {
              isArea: true,
              echartsCustom: {
                grid: {
                  left: 93,
                  right: 40,
                  bottom: 50,
                  top: 50,
                  containLabel: false
                },
                legend: {
                  top: 8,
                },
                yAxis: {
                  max: function (v) {
                    let l = v.max.toString().length
                    if (l) {
                      let x = ('1' + new Array(l).join('0'))
                      return v.max + parseInt(x)
                    }
                  },
                },
              },
            }
          },
          equipment_usage: {
            name: "当天设备使用率统计",
            chartRenderMethod: "statsDataSummary",
            dataRenderMethon: "equipmentUsage",
            chartKey: 'equipment_usage',
            url: ['api', 'getEquipmentUsage'],
            startTime: 'today',
            urlParams: 'nextReFresh',
            loading: true,
            timerInterver: 30,
            options: {
              echartsCustom: {
                legend: {
                  top: 8,
                },
              },
            }
          },
          equipment_online: {
            name: "当天设备运行时长（分钟）",
            chartRenderMethod: "barXaxis",
            dataRenderMethon: "barYaxisMoreCategory",
            url: ['api', 'getEquipmentOnline'],
            urlParams: 'nextReFresh',
            loading: true,
            startTime: 'today',
            options: {
              XAxisData: ['服务器设备统计', '终端设备统计'],
              seriesLabel: {
                show: true,
                position: 'top',
              },
              echartsCustom: {
                grid: {
                  left: 93,
                  right: 40,
                  bottom: 50,
                  top: 50,
                  containLabel: false
                },
                legend: {
                  itemWidth: 10,
                  itemHeight: 5,
                  width: '70%',
                  icon: 'roundRect',
                  itemGap: 22,
                  top: 8,
                  right: 53,
                  textStyle: {
                    color: '#9ca9b1',
                    padding: [1, 0, 0, 5]
                  },
                },
              },
            },
          },
          terminalMeetingTime: {
            name: "当日终端参会时长统计(单位：分钟)",
            chartRenderMethod: "barYaxis",
            dataRenderMethon: "barYaxis",
            chartKey: 'enterprise_conf_stats_number',
            // dataKey:['data','info'],
            url: ['api', 'getTerminalMeetingTime'],
            timerInterver: 30,
            startTime: 'today',
            urlParams: 'nextReFresh',
            loading: true,
            staticUrlParams: {
              start: 0,
              count: 10,
            },
            // url:"cpu",
            routerPush: '跳转cpu',
            options: {
              grid: {
                left: 93,
                right: 40,
                bottom: 35,
                top: 50,
                containLabel: false
              },
            },
          },
          terminalMeetingFreq: {
            name: "当日终端参会统计(单位：次数)",
            chartRenderMethod: "barYaxis",
            dataRenderMethon: "barYaxis",
            chartKey: 'enterprise_conf_stats_number',
            // dataKey:['data','info'],
            url: ['api', 'getTerminalMeetingFreq'],
            timerInterver: 30,
            startTime: 'today',
            urlParams: 'nextReFresh',
            loading: true,
            staticUrlParams: {
              start: 0,
              count: 10,
            },
            routerPush: '跳转cpu',
            options: {
              grid: {
                left: 93,
                right: 40,
                bottom: 35,
                top: 50,
                containLabel: false
              },
            },
          },
        },
        // end 此组件支持的chartConf

        // 需要传递子页面的配置
        childPageConf: {
          enterprise_conf_stats_number: {
            name: "企业会议数统计",
            areaDetailShow: 'table',
            dataRender: 'table',
            dataUrl: 'getTableDataCompanyConf',
            exportUrl: 'downloadCompanyConfExport',
            tableTitle: [
              {prop: "description", label: "企业名称", width: "300"},
              {prop: "data", label: "会议数量",}
            ],
            inputSearch: true,  //用于判断是否显示输入搜索框
            timeRange: 'today'
          },
          stats_enterprise_info: {
            name: "企业信息统计",
            areaDetailShow: 'chartCommon',
            dataRender: 'chartCommon',
            dataUrl: 'conf_created_time',
            inputSearch: false,
            noDateFilter: true,
          },
          stats_terminal_info: {
            name: "账号信息统计",
            areaDetailShow: 'chartCommon',
            dataRender: 'chartCommon',
            dataUrl: 'conf_created_time',
            inputSearch: false,
            noDateFilter: true,
          },
          conf_created_time: {
            name: "创建会议时长统计",
            areaDetailShow: 'chartCommon',
            dataRender: 'chartCommon',
            dataUrl: 'conf_created_time',
            timeRange: 'today',
            inputSearch: false,
          },
          conf_continue_time: {
            name: "会议时长统计",
            areaDetailShow: 'chartCommon',
            dataRender: 'chartCommon',
            dataUrl: 'conf_created_time',
            timeRange: 'today',
            inputSearch: false,
          },
          stats_created_conf: {
            name: "创会数量统计",
            areaDetailShow: 'table',
            dataRender: 'table',
            dataUrl: 'getTableDataCreateConfTime',
            exportUrl: 'downloadCreateConfTypeExport',
            inputSearch: true,
            tableTitle: [
              {prop: "name", label: "企业名称", width: "300"},
              {prop: "terminal_data", label: "终端创会数量",},
              {prop: "data", label: "会控创会数量",}
            ]
          },
          stats_terminal_call: {
            name: "终端呼叫数量",
            areaDetailShow: 'chartCommon',
            dataRender: 'chartCommon',
            dataUrl: 'conf_created_time',
            inputSearch: false,
          },
          stats_living_terminal: {
            name: "观看直播人数",
            areaDetailShow: 'chartCommon',
            dataRender: 'chartCommon',
            dataUrl: 'conf_created_time',
            inputSearch: false,
          },
          utilization_live_broadcasts: {
            name: "直播资源使用率",
            areaDetailShow: 'chartCommon',
            dataRender: 'chartCommon',
            dataUrl: 'conf_created_time',
            inputSearch: false,
          },
          resource_reservation: {
            name: "预约资源",
            areaDetailShow: 'chartCommon',
            dataRender: 'chartCommon',
            dataUrl: 'conf_created_time',
            inputSearch: false,
            startTimeFilter: true,
            noDateFilter: true,
          },
          terminalMeetingFreq: {
            name: "预约资源",
            components: 'detail',
            key: 'mtInConfCount'
          },
        },
        // 需要传递子页面的配置end
      };
    },
    methods: {
      // tab变化
      tabChange(val) {
        // console.log(val)
        this.activeTab = val
        this.chartChange = val
      },
      backMainPage(val) {
        if (val) {
          this.showArea = 'main'
          // this.init()
        }
      },
      // 页面内按钮功能函数
      pageEdit(val) {
        if (val === 'edit') {
          this.pageEditStatu = !this.pageEditStatu
          this.clearTimer()
        } else if (val === 'save') {
          // this.clearTimer()
          // console.log(this.chartList)
          let newChartList = this.chartList.map((item, index) => {
            let temConf = {}
            if (item) {
              temConf["name"] = item.name
              temConf["description"] = item.description
              temConf["width"] = item.width
              temConf["height"] = item.height
              temConf["y"] = item.y
              temConf["x"] = index
            }
            return temConf
          })
          // newChartList.forEach((item)=>{console.log(item.x)})
          this.$api.getChartData.delPageLayout({ids: "all"})
            .then((res) => {
              let params = newChartList
              this.$api.getChartData.changePageLayout(params)
                .then(res => {
                  this.init()
                }).catch(err => {
                console.log(err)
              })
            }).catch(err => {
            console.log(err)
          })
          this.pageEditStatu = !this.pageEditStatu
        } else if (val === 'cancel') {
          this.pageEditStatu = !this.pageEditStatu
          this.init()
          this.setTimer()
        }

      },
      buttonMore(item) {
        this.activeChildChartConf = this.chartConfSupport[item]
        this.activeChildPageConf = this.childPageConf[item]
        if (this.activeChildPageConf.components === 'detail') {
          this.showArea = "detail"
        } else {
          this.showArea = "children"
        }
      },
      addChart(command) {
        // console.log(command)
        let layoutConf = {
          name: command[0],
          width: 0,
          height: 0,
          y: 0,
          description: command[1].name,
          x: this.chartList.length
        }
        if (this.chartList.find(i => i.description === layoutConf.description)) {
          this.$message({
            message: '表已存在，请勿重复添加',
          })
        } else {
          this.chartList.push(layoutConf)
        }
      },
      delChart(item) {
        const newItems = [...this.chartList]
        // console.log(newItems)
        const index = newItems.indexOf(item)
        newItems.splice(index, 1)
        this.chartList = newItems
      },

      // 页面内按钮功能函数end

      // 拖拽功能函数start
      handleDragStart(e, item) {
        // this.dragging = item;
        // console.log("DragStart--->"+item.x)
        e.dataTransfer.setData("dragging", item.x);
      },
      handleDrop(e, item) {
        let draggingItem = e.dataTransfer.getData("dragging")
        draggingItem = parseInt(draggingItem)
        // e.dataTransfer.clearData()
        if (item.x === draggingItem) {
          return false
        }
        const newItems = [...this.chartList]
        // console.log(draggingItem.x)
        const src = newItems.findIndex((item) => item.x === draggingItem)
        const dst = newItems.indexOf(item)
        // console.log(src,dst)
        newItems.splice(dst, 0, ...newItems.splice(src, 1))
        this.chartList = newItems
      },
      // 拖拽功能函数end

      // 定时器函数start
      // 设置定时器
      setTimer(interver = 60, range = 86400000) {
        this.clearTimer();
        this.timer = setInterval(() => {
          this.renderChart(range)
          // this.datePickerTimeRange=[timestamp-range,timestamp]
        }, interver * 1000)
      },
      // 清除定时器
      clearTimer() {
        clearInterval(this.timer);
        this.timer = null;
      },
      // 定时器函数end

      // 功能函数start
      compare(property) {
        return function (a, b) {
          //value1 - value2升序
          //value2 - value1降序
          var value1 = a[property];
          var value2 = b[property];
          return value1 - value2;//升序
        }
      },
      // 功能函数end
      renderChart(range) {
        // console.log(range)
        let timestamp = (new Date()).getTime();
        let today = new Date().setHours(0, 0, 0, 0)
        // console.log(timestamp,timestamp-range)
        for (let item of this.chartList) {
          if (this.chartConfSupport[item.name]) {  //如果是页面内支持的conf
            let params = this.chartConfSupport[item.name].staticUrlParams
            let timeParams = {
              start_time: timestamp - range,
              end_time: timestamp,
            }

            if (this.chartConfSupport[item.name].startTime) {
              timeParams.start_time = eval(this.chartConfSupport[item.name].startTime)
            }

            params = {...params, ...timeParams}
            this.$set(this.chartConfSupport[item.name], 'urlParams', params)
          }
        }
      },

      async getPageLayout() {
        let dataPageLayout = await this.$api.getChartData.getPageLayout()
        dataPageLayout.info.sort(this.compare('x'))
        this.chartList = []
        this.chartList = [...dataPageLayout.info]
        this.renderChart(3600000)
      },
      init() {
        // 调整当前route，变化侧边栏高亮
        let activeRouteList = ['/ops/monitor/stats_data_summary', '/ops/monitor']
        this.$store.dispatch('activeRouteChange', activeRouteList)

        this.getPageLayout()
      },
    },
    mounted() {
      // window.addEventListener("mouseup",this.divMoveMouseup())
      this.init()
      this.setTimer(60, 3600000)
    },
    beforeDestroy() {
      this.clearTimer()
    },
  }
</script>

<style>
  .area-block--dragchart {
    width: calc(33.3% - 20px);
    height: 250px;
    display: inline-block;
    margin: 10px;
    position: relative;
  }

  .tooltip-block-create-conf-p {
    overflow-y: auto;
    overflow-x: hidden;
    max-height: 200px;
  }

  .tooltip-title-create-conf-p span {
    /*width: 40px;*/
    display: inline-block;
    padding: 4px 5px;
    font-size: 14px;
  }

  .tooltip-content-create-conf-p {
    border-bottom: #272c2e 1px solid;

  }

  .tooltip-content-create-conf-p span {
    display: inline-block;
    word-wrap: break-word;
    word-break: break-all;
    white-space: pre-wrap;
    box-sizing: border-box;
    padding: 2px 5px;
    vertical-align: middle;
    font-size: 12px;
  }

  .tooltip-content-create-conf-p span:first-child {
    width: 80px;
  }

  .tooltip-content-create-conf-p span:last-child {
    max-width: 350px;
  }
</style>
