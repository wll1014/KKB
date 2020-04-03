<template>
  <div class="view-stats-app-request">
    <!--主页面-->
    <div v-if="showPage">
      <div style="margin-left: 10px;">
        <SelectPlatformDomain @change="changeFilter($event,'selectPlatformDomain')"
                              @loadSelectedOption="loadSelectedOption($event,'selectPlatformDomain')"
                              :filterDomainType=1
                              :hasOptionAll=true
                              showSelectMachineRoom></SelectPlatformDomain>
        <SelectTimeRange ref="appRequestSelectTimeRange" style="margin-left: 7px;"
                         @loadSelectedOption="loadSelectedOption($event,'selectTimeRange')"
                         @change="changeFilter($event,'selectTimeRange')"></SelectTimeRange>

        <el-button style="vertical-align: 1px;" @click="refreshPage" :disabled="refreshButtonDisabled">搜索</el-button>
      </div>
      <div class="area-request-header">
        <div>
          <div class="left">
            <div>
              <i class="ops-icons-bg icon-web-request-pv"></i>
            </div>
          </div>
          <div class="right">
            <div>请求总次数（PV）：</div>
            <div>{{requestOutline.pv}}</div>
          </div>
        </div>
        <div>
          <div class="left">
            <div>
              <i class="ops-icons-bg icon-web-request-uv"></i>
            </div>
          </div>
          <div class="right">
            <div>IP访问数（UV）：</div>
            <div>{{requestOutline.uv}}</div>
          </div>
        </div>
        <div>
          <div class="left">
            <div>
              <i class="ops-icons-bg icon-web-request-avgtime"></i>
            </div>
          </div>
          <div class="right">
            <div>接口平均响应时长：</div>
            <div>{{requestOutline.avg_request_time }} ms</div>
          </div>
        </div>
      </div>

      <div class="area-request-content">
        <div v-for="(key,index) in contentList" :key="key+index">
          <span class="title">{{contentConf[key].name}}</span>

          <button type="button" class="ops-button-text button-more"
                  @click="buttonMore(contentConf[key])"
                  v-if="contentConf[key].childPage">
            <span style="font-size: 12px;">更多</span>
          </button>

          <div v-if="contentConf[key] && contentConf[key].renderType === 'chart'" class="content-chart">
            <ChartExtendLargeModel :ChartID="'ID'+ key + index"
                                   :chartConf="chartConfSupport[key]"></ChartExtendLargeModel>
          </div>

          <div v-if="contentConf[key] && contentConf[key].renderType === 'table'"
               class="content-table">
            <TableNest :tableConf="tableConfSupport[key].tableConf"
                       :data="tableConfSupport[key].data"
                       v-loading="tableConfSupport[key].loading"
                       element-loading-text="正在加载，请稍后..."
                       element-loading-background="rgba(0, 0, 0, 0.5)"></TableNest>
          </div>

          <div v-if="contentConf[key] && contentConf[key].renderType === 'webEngine'"
               class="content-table"
               v-loading="contentConf[key].loading"
               element-loading-text="正在加载，请稍后..."
               element-loading-background="rgba(0, 0, 0, 0.5)">
            <ChartExtendLargeModel :ChartID="'ID'+ key + index"
                                   :chartConf="contentConf[key].chartConf"
                                   style="width: 20%;display: inline-block;"></ChartExtendLargeModel>
            <TableNest :tableConf="contentConf[key].tableConf"
                       :data="contentConf[key].data"
                       style="width: 79%;display: inline-block;vertical-align: top;"></TableNest>
          </div>
        </div>
      </div>
    </div>

    <!--子页面-->
    <div v-else>
      <component :is="childPageComponent"
                 @back="back"
                 :tab="childPageProp.tab"
                 :defaultSelected="childPageProp.defaultSelected"></component>
    </div>
  </div>
</template>

<script>
  export default {
    components: {
      TableNest: () => import('@/components/common/TableNest.vue'),
      SelectPlatformDomain: () => import('@/components/common/SelectPlatformDomain.vue'),
      SelectTimeRange: () => import('@/components/common/SelectTimeRange.vue'),
      ChartExtendLargeModel: () => import('@/components/monitor/ChartExtendLargeModel.vue'),
      StatsAppRequestDetail: () => import('@/view/monitor/StatsAppRequestDetail.vue'),
    },
    name: "StatsAppReuqest",
    data() {
      return {
        showPage: true,  // 是否显示首页
        childPageComponent: 'StatsAppRequestDetail',
        childPageProp: {},
        filterComponentLoad: {
          selectPlatformDomain: false,
          selectTimeRange: false
        },
        filterParams: {},

        refreshButtonDisabled: false,

        requestOutline: {},
        contentList: ['requestsTraffic', 'requestsPV', 'requestsIP',
          'requestsSlowResponses', 'requestURL', 'webEngine',
          'httpCode', 'errRequest', 'requestMethod'],

        contentConf: {
          requestsTraffic: {
            name: "请求流量统计",
            renderType: 'chart',
            renderMethod: 'chartCommon',
            childPage: {
              component: 'StatsAppRequestDetail',
              tab: 'requestsDetail',
            },
          },
          requestsPV: {
            name: "访问量统计",
            renderType: 'chart',
            renderMethod: 'chartCommon',
            childPage: {
              component: 'StatsAppRequestDetail',
              tab: 'requestsDetail',
            },
          },
          requestsIP: {
            name: "请求IP统计",
            renderType: 'chart',
            renderMethod: 'chartCommon',
            childPage: {
              component: 'StatsAppRequestDetail',
              tab: 'requestsIP',
            },
          },
          requestsSlowResponses: {
            name: "慢响应>1s的统计",
            renderType: 'table',
            renderMethod: 'table',
            childPage: {
              component: 'StatsAppRequestDetail',
              tab: 'requestsSlowResponses',
              defaultSelected: {
                optionSelectedSlowResponses: 1,
              },
            },
          },
          requestURL: {
            name: "请求URL统计",
            renderType: 'table',
            renderMethod: 'table',
            childPage: {
              component: 'StatsAppRequestDetail',
              tab: 'requestURL',
            },
          },
          webEngine: {
            name: "客户端统计",
            renderType: "webEngine",
            renderMethod: 'webEngine',
            childPage: {
              component: 'StatsAppRequestDetail',
              tab: 'webEngine',
            },
            chartConf: {
              name: "客户端统计",
              chartRenderMethod: "appRequest",
              dataRenderMethon: "appRequestWebEngine",
              chartKey: 'stats_enterprise_info',
              // dataKey:['data','info'],
              url: ['common', '/statistics/requests/clients_pct/'],
              urlParams: 'nextReFresh',
              // url:"cpu",
              routerPush: '跳转cpu',
              timerInterver: 300,
              options: {
                // customerColor: ['#2c8dc5', '#e45959'],
                echartsCustom: {
                  legend: {
                    orient: 'vertical',
                    itemWidth: 10,
                    itemHeight: 5,
                    icon: 'roundRect',
                    itemGap: 16,
                    left: 'center',
                    // left:100,
                    textStyle: {
                      color: '#9ca9b1',
                      padding: [1, 0, 0, 5]
                    },
                    top: '60%',
                  }
                },
                minAngle: 10,
                center: ['50%', '30%'],
                radius: '60%',
                labelLine: {
                  show: false,
                },
                label: {
                  show: false,
                },
              }
            },
            tableUrl: ['common', '/statistics/requests/clients/'],
            tableStaticUrlParams: {
              start: 0,
              count: 10,
            },
            tableConf: [
              {prop: "index", title: "序号", width: "60"},
              {prop: "url", title: "客户端信息"},
              {prop: "data", title: "数量", width: "100"},
            ],
            data: []
          },
          httpCode: {
            name: "HTTP状态码统计",
            renderType: 'chart',
            renderMethod: 'chartCommon',
            childPage: {
              component: 'StatsAppRequestDetail',
              tab: 'requestsDetail',
            },
          },
          errRequest: {
            name: "异常统计",
            renderType: 'table',
            renderMethod: 'table',
            childPage: {
              component: 'StatsAppRequestDetail',
              tab: 'errRequest',
            },
          },
          requestMethod: {
            name: "请求方法统计",
            renderType: 'chart',
            renderMethod: 'chartCommon',
          }
        },
        chartConfSupport: {
          requestsTraffic: {
            name: "请求流量统计",
            chartRenderMethod: "timeline",
            dataRenderMethon: "timeline",
            url: ['api', 'getAppRequestTraffic'],
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
                  name: "Mbps",
                  nameTextStyle: {
                    color: '#9ca9b1',
                    fontSize: 12,
                  }
                },
                tooltip: {
                  trigger: 'axis',
                  padding: [18, 14],

                  backgroundColor: '#141414',
                  borderColor: '#383b3c',
                  borderWidth: 1,
                  textStyle: {
                    color: '#9ca9b1',
                  },
                  formatter: (params,) => {
                    // console.log(params)
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

                      let showValue = null
                      if (item.value[1] !== null && item.value[1] !== undefined) showValue = item.value[1].toFixed(2) + " Mbps"
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
                },
              },
            }
          },
          requestsPV: {
            name: "访问量统计",
            chartRenderMethod: "timeline",
            dataRenderMethon: "timeline",
            url: ['common', '/statistics/requests/pv/'],
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
          httpCode: {
            name: "HTTP状态码统计",
            chartRenderMethod: "timeline",
            dataRenderMethon: "timeline",
            url: ['common', '/statistics/requests/status_code/'],
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
          requestsIP: {
            name: "请求IP统计",
            chartRenderMethod: "barYaxis",
            dataRenderMethon: "barYaxis",
            url: ['api', 'getAppRequestIP'],
            timerInterver: 60,
            urlParams: 'nextReFresh',
            loading: true,
            staticUrlParams: {
              count: 10,
            },
            options: {
              yAxisLabelLength: 16,
              grid: {
                left: 93,
                right: 40,
                bottom: 35,
                top: 50,
                containLabel: false
              },
            },
          },
          requestMethod: {
            name: "请求方法统计",
            chartRenderMethod: "barXaxis",
            dataRenderMethon: "barXaxis",
            url: ['common', '/statistics/requests/methods/'],
            urlParams: 'nextReFresh',
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
              },
            },
          },
        },
        tableConfSupport: {
          requestsSlowResponses: {
            name: "慢响应>1s的统计",
            url: ['common', '/statistics/requests/slow_responses/'],
            staticUrlParams: {
              start: 0,
              count: 10,
              slow_time_threshold: 1,
            },
            tableConf: [
              {prop: "index", title: "序号", width: "60"},
              {prop: "url", title: "请求URL"},
              {prop: "data", title: "数量", width: "100"},
            ],
            data: []
          },
          requestURL: {
            name: "请求URL统计",
            url: ['common', '/statistics/requests/urls/'],
            staticUrlParams: {
              start: 0,
              count: 10,
            },
            tableConf: [
              {prop: "index", title: "序号", width: "60"},
              {prop: "url", title: "请求URL"},
              {prop: "data", title: "数量", width: "100"},
            ],
            data: [],
          },
          errRequest: {
            name: "异常统计",
            url: ['common', '/statistics/requests/errors/'],
            staticUrlParams: {
              start: 0,
              count: 10,
            },
            tableConf: [
              {prop: "index", title: "序号", width: "60"},
              {prop: "url", title: "请求URL"},
              {prop: "data", title: "数量", width: "100"},
            ],
            data: [],
          },
        },
      };
    },
    methods: {
      buttonMore(conf) {
        let defaultSelected = {
          selectedMoidPlatform: this.filterParams.domainMoid,
          selectedMoidMachineRoom: this.filterParams.roomMoid,
          timeRange: this.filterParams.dateRange
        }
        this.childPageComponent = conf.childPage.component
        this.$set(this.childPageProp, 'tab', conf.childPage.tab)
        this.$set(this.childPageProp, 'defaultSelected', defaultSelected)
        this.showPage = false
      },
      back(v) {
        if (v) this.showPage = true
        this.childPageProp = {}
      },
      refreshPage() {
        this.refreshButtonDisabled = true
        this.renderInit()
        setTimeout(() => this.refreshButtonDisabled = false, 1000)
      },
      // 过滤项改变触发的函数
      changeFilter(val, k) {
        this.setFilterParams(val, k)
        let loadingFlag = Object.values(this.filterComponentLoad).includes(false)
        if (k === 'selectTimeRange' && !val.dateRange) loadingFlag = true //当选择时间为空时不做渲染
        if (!loadingFlag) {
          this.renderInit()
        }
      },
      // 用于处理所有过滤条件初始化完成后，做第一次带参请求
      loadSelectedOption(val, k) {
        this.setFilterParams(val, k)
        this.$set(this.filterComponentLoad, k, true)
        let loadingFlag = Object.values(this.filterComponentLoad).includes(false)
        if (!loadingFlag) {
          this.renderInit()
        }
      },
      setFilterParams(val, k) {
        if (k === 'selectPlatformDomain') {
          let domainMoid = val.domainMoid === 'all' ? '' : val.domainMoid
          let roomMoid = val.roomMoid === 'all' ? '' : val.roomMoid
          this.$set(this.filterParams, 'domainMoid', domainMoid)
          this.$set(this.filterParams, 'roomMoid', roomMoid)
        } else if (k === 'selectTimeRange') {
          this.$set(this.filterParams, 'timeSelect', val.select)
          this.$set(this.filterParams, 'dateRange', val.dateRange)
        }
      },

      // 渲染函数,负责将当前展示项用不同的方法渲染
      renderInit() {
        let renderChartTypeMethod = {
          'chartCommon': this.renderChartCommon, //常规chart渲染
          'table': this.renderTable, //常规table渲染
          'webEngine': this.renderWebEngine, //客户端统计图表渲染
        };
        let gloablConf = {} //用于配置默认或全局的参数

        this.judgeTimeRange() //判断是否有时间，没有则给默认值

        this.getDataRequestOutline(this.filterParams) //顶部统计数据

        this.contentList.forEach(confKey => {
          let method = this.contentConf[confKey].renderMethod
          if (method) renderChartTypeMethod[method](gloablConf, confKey, this.filterParams)
        })
      },
      // 不同渲染方法函数
      renderChartCommon(gConf, confKey, filterParams) {
        let timestamp = (new Date()).getTime();
        let params = this.chartConfSupport[confKey].staticUrlParams

        let gloablParams = {
          start_time: filterParams.dateRange[0],
          end_time: filterParams.dateRange[1],
          platform_moid: filterParams.domainMoid,
          room_moid: filterParams.roomMoid,
        }
        params = {...params, ...gloablParams}
        this.$set(this.chartConfSupport[confKey], 'loading', true)
        this.$set(this.chartConfSupport[confKey], 'urlParams', params)
      },

      async renderTable(gConf, confKey, filterParams) {
        this.$set(this.tableConfSupport[confKey], 'loading', true)
        let params = this.tableConfSupport[confKey].staticUrlParams

        let gloablParams = {
          start_time: filterParams.dateRange[0],
          end_time: filterParams.dateRange[1],
          platform_moid: filterParams.domainMoid,
          room_moid: filterParams.roomMoid
        }
        params = {...params, ...gloablParams}
        // this.$set(this.chartConfSupport[confKey], 'urlParams', params)
        let method = this.tableConfSupport[confKey].url[0]
        let tableDataTrans = {
          'common': this.tableDataTransCommon, //常规table数据获取
        };
        let data = await tableDataTrans[method](this.tableConfSupport[confKey], params)
        this.$set(this.tableConfSupport[confKey], 'loading', false)
      },

      async renderWebEngine(gConf, confKey, filterParams) {
        this.$set(this.contentConf[confKey], 'loading', true)
        let chartParams = this.contentConf[confKey].chartConf.staticUrlParams

        let gParams = {
          start_time: filterParams.dateRange[0],
          end_time: filterParams.dateRange[1],
          platform_moid: filterParams.domainMoid,
          room_moid: filterParams.roomMoid,
        }
        chartParams = {...chartParams, ...gParams}
        this.$set(this.contentConf[confKey].chartConf, 'urlParams', chartParams) //左侧chart变化

        let tableParams = this.contentConf[confKey].tableStaticUrlParams
        tableParams = {...tableParams, ...gParams}
        let res = await this.$api.getChartData.getAppRequestWebEngine(tableParams)
        let tableData = res.info ? res.info : []
        // if (tableData && tableData.length) {
        let tempList = []
        tableData.forEach((item, indexItem) => {
          let tempDict = {}
          tempDict.index = indexItem + 1 //设置序号
          item.forEach((i, indexI) => {
            let key = this.contentConf[confKey].tableConf[indexI + 1].prop //为每列做数据转换，[indexI+1]目的是为了错开第一个index位
            tempDict[key] = item[indexI]
          })
          tempList.push(tempDict)
        })
        this.$set(this.contentConf[confKey], 'loading', false)
        this.$set(this.contentConf[confKey], 'data', tempList)
        // }
      },
      // 渲染函数,负责将当前展示项用不同的方法渲染 end

      // table数据获取 start
      async tableDataTransCommon(conf, params) {
        let res = await this.$api.appReuqestData.requestTopData(conf.url[1], params)
        let data = res.info
        let tableData = []
        if (data.length) {
          data.forEach((item, indexItem) => {
            let tempDict = {}
            tempDict.index = indexItem + 1 //设置序号
            conf.tableConf.forEach((i, indexI) => {
              let key = i.prop //为每列做数据转换，
              if (key === 'index') {
                return
              } else {
                tempDict[key] = item[indexI - 1]
              }
            })
            tableData.push(tempDict)
          })
        }
        this.$set(conf, 'data', tableData)
      },
      // table数据获取 end

      async getDataRequestOutline(filterParams) {
        let gloablParams = {
          start_time: filterParams.dateRange[0],
          end_time: filterParams.dateRange[1],
          platform_moid: filterParams.domainMoid,
          room_moid: filterParams.roomMoid
        }
        let res = await this.$api.appReuqestData.requestOutline(gloablParams)
        let data = res.info || []
        data.forEach((item) => {
          let val = item.name === 'avg_request_time' ? item.data * 1000 : item.data
          this.$set(this.requestOutline, item.name, val)
        })
      },

      // 其他函数
      // 用于判断当前时间选择器是否为空，若为空则赋予默认值
      judgeTimeRange() {
        if (!this.filterParams.dateRange) {
          let timestamp = (new Date()).getTime();
          let defaultTimeRange = [timestamp - 3600000, timestamp]
          this.$set(this.filterParams, 'dateRange', defaultTimeRange)
          this.$refs.appRequestSelectTimeRange.defaultReset()
        }
      },

    },
    mounted() {
    },
  }
</script>

<style>
  .view-stats-app-request {
    padding: 20px 20px 20px 20px;
  }

  .area-request-header {
    display: flex;
    height: 200px;
    background: #232629;
    margin: 10px;
  }

  .area-request-header > div {
    flex: 1;
    box-sizing: border-box;
    padding: 40px;
    font-size: 0px;
    width: 100%;
  }

  .area-request-header > div > div {
    display: inline-block;
    box-sizing: border-box;
    vertical-align: top;
    height: 100%;
    font-size: 12px;
  }

  .area-request-header > div > div:nth-child(1) {
    width: 40%;
  }

  .area-request-header > div > div:nth-child(2) {
    width: 60%;
    border-right: #5f656a 1px solid;
  }

  .area-request-header .left > div:nth-child(1) {
    padding-top: 14px;
    padding-left: 60px;
  }

  .area-request-header .right > div:nth-child(1) {
    width: 100%;
    padding-top: 30px;
    height: 30px;
  }

  .area-request-header .right > div:nth-child(2) {
    width: 100%;
    font-size: 16px;
    color: #299dff;
  }

  .area-request-header > div:last-child div {
    border-right: none;
  }

  .area-request-content {
    display: flex;
    flex-wrap: wrap;
  }

  .area-request-content > div {
    flex: 1;
    flex-basis: 50%;
    max-width: 50%;
    position: relative;
    box-sizing: border-box;
    padding: 10px;
    height: 350px;
  }

  .area-request-content > div > div {
    height: 100%;
    width: 100%;
    position: relative;
  }

  .area-request-content .title {
    position: absolute;
    top: 20px;
    left: 20px;
    z-index: 9;
  }

  .area-request-content .content-table,
  .area-request-content .content-chart {
    background-color: #232629;
    padding: 40px 20px 20px 20px;
    box-sizing: border-box;
  }

  .area-request-content .button-more {
    position: absolute;
    top: 20px;
    right: 30px;
    z-index: 9;
  }

  .area-request-content .content-table .components-table-nest {
    min-height: 200px;
  }
</style>
