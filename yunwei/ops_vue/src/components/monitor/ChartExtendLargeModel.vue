<template>
  <div class="component-chart-extend"
       v-loading="chartLoading"
       element-loading-text="正在加载，请稍后..."
       element-loading-background="rgba(0, 0, 0, 0.5)">
    <!--由于此插件需要相对chart固定位置，所以防止第二层div-->
    <div v-if="extraPlugin.dataRoom" :class="['plugin-dataroom',extraPlugin.dataRoom.className]">
      <el-tooltip :content="extraPlugin.dataRoom.leftTooltip" placement="top">
        <div
          :class="['ops-icons-bg icon-arrow-left__timeaxis dataroom__left',{'disabled':extraPlugin.dataRoom.leftButtonDisabled}]"
          @click="pluginEvents('dataRoomLeft')"></div>
      </el-tooltip>
      <el-tooltip :content="extraPlugin.dataRoom.rightTooltip" placement="top">
        <div
          :class="['ops-icons-bg icon-arrow-right__timeaxis dataroom__right',{'disabled':extraPlugin.dataRoom.rightButtonDisabled}]"
          @click="pluginEvents('dataRoomRight')"></div>
      </el-tooltip>
    </div>
    <!--插件相关文档-->
    <div :class="[extraPluginClass,'area-chart-extend-extra']" style="">
      <div v-if="extraPlugin.imgExport" class="plugin-imgexport">
        <el-tooltip content="保存图片" placement="top">
          <el-button icon="ops-icons-bg icon-imgexport" @click="downloadImg" circle></el-button>
        </el-tooltip>
      </div>
      <div v-if="extraPlugin.dataInterval" class="plugin-datainterval">
        <el-tooltip content="放大" placement="top">
          <el-button icon="ops-icons-bg icon-circle-plus" class="datainterval__plus" @click="pluginEvents('plus')"
                     circle></el-button>
        </el-tooltip>
        <span class="datainterval__input">{{extraPlugin.dataInterval.interval}}</span>
        <span class="datainterval__suffix">{{extraPlugin.dataInterval.suffix}}</span>
        <el-tooltip content="缩小" placement="top">
          <el-button icon="ops-icons-bg icon-circle-minus" class="datainterval__minus" @click="pluginEvents('minus')"
                     circle></el-button>
        </el-tooltip>
      </div>
    </div>
    <!--插件相关文档 end-->

    <ChartBase :chartID="ChartID" :ref="ChartID"></ChartBase>

    <!--无数据时展示页面-->
    <div class="chart--dialog" v-if="showDialog">
      <slot name="emptyData">
        <span style="position: absolute;top:45%;">暂无数据</span>
      </slot>
    </div>
    <!--无数据时展示页面 end-->
  </div>
</template>

<script>
  import ChartBase from "@/components/home/ChartBase.vue"
  import extendReporterDay from "./MixinChartExtendRepoterDay.js"
  import extendAppRequest from "./MixinChartExtendAppRequest.js"
  import extendStatsDataSummary from "./MixinChartExtendStatsDataSummary.js"

  export default {
    name: "ChartExtendLargeModel",
    components: {
      // ChartBase: () => import('@/components/home/ChartBase.vue'),
      ChartBase,
    },
    props: {
      // echart实例化ID
      ChartID: String,
      // chartconf
      chartConf: Object,
      // 当多个chart ID相同，但需要变换表的样式，可改变此值
      chartChange: String,
      //当请求的url带变化的参数时使用此参数
      // urlParams:null,
      // 额外组件 :目前支持：imgExport:图片导出
      extraPlugin: {
        type: Object,
        default: function () {
          return {
            imgExport: false,
            dataInterval: false,
            dataRoom: false,
          }
        }
      },
      extraPluginClass: String,
    },
    mixins: [extendReporterDay, extendAppRequest, extendStatsDataSummary],
    computed: {
      paramsChange() {
        return this.chartConf.urlParams
      },
      actionChange() {
        return this.chartConf.action
      },
    },
    watch: {
      // chartConf:{
      //   deep:true,
      //   handler:function(newVal,oldVal){
      //     // console.log("ChartExtend-Watch:" + newVal.name)
      //     // this.$refs[this.ChartID].init();
      //   }
      // },
      chartChange(newVal) {
        // console.log(newVal,this.chartConf)
        this.renderChartInit(this.chartConf)
      },
      paramsChange: {
        deep: true,
        handler: function (newVal, oldVal) {
          if (!this.chartRenderStatu) {
            // console.log("ChartExtend-Watch:" + newVal)
            this.renderChartInit(this.chartConf, false)
          }
        }
      },
      actionChange: {
        deep: true,
        handler: function (newVal, oldVal) {
          // console.log("actionChange-Watch:" + newVal.legend.value)
          this.chartAction(newVal)
        }
      },
    },
    data() {
      return {
        // 是否显示无数据蒙版
        showDialog: false,
        // 判断chart渲染状态，防止监听状态重复导致表格重复渲染
        chartRenderStatu: false,
        // loading 界面
        chartLoading: false,
        // echarts实例
        chartBaseInstance: '',
        // echarts颜色库
        colorCustomer: ['#5eb9ef', '#63cd81', '#fb265d', '#f1ac17', '#d66ef8', '#1d4ff4', '#db6b08'],
        colorCustomerRGBA: ['rgba(94,185,239,0.1)', 'rgba(99,205,129,0.1)', 'rgba(251,38,93,0.1)',
          'rgba(241,172,23,0.1)', 'rgba(214,110,248,0.1)', 'rgba(29,79,244,0.1)', 'rgba(219,107,8,0.1)'],
        // echarts背景色
        echartsBackgroudColor: '#232629',
      }
    },
    methods: {
      // chart初始化
      async renderChartInit(chartConf, isNewChart = true) {
        this.chartRenderStatu = true
        let defaultConf = {
          echartsBackgroudColor: this.echartsBackgroudColor,
          colorCustomer: this.colorCustomer,
          colorCustomerRGBA: this.colorCustomerRGBA,
          // urlParams:this.urlParams,
        }
        // 根据chartConf.chartRenderMethod判断chart渲染方法
        let renderChartTypeMethod = {
          'timeline': this.renderChartTypeTimeline, //横轴时间线chart
          'terminalConfSummary': this.renderChartTypeTerminalConfSummary, //终端参会概况chart
          'confEvent': this.renderChartTypeConfEvent, //会议事件概况chart
          'barYaxis': this.renderChartTypeBaseBar, //Y轴类目轴柱状图chart-->基础柱状图chart
          'barXaxis': this.renderChartTypeBaseBar, //X轴类目轴柱状图chart-->基础柱状图chart
          'pie': this.renderChartTypeBasePie, //基础饼图chart
          'scatter': this.renderChartTypeBaseScatter, //基础散点图chart
          // 日报相关渲染方法 通过mixins: [extendReporterDay] 混入
          'reportDay': this.renderChartDayReportInit, //日报图表
          // 日报相关渲染方法 end
          // web请求统计渲染方法 通过mixins: [extendAppRequest] 混入
          'appRequest': this.renderChartAppRequestInit, //日报图表
          // web请求统计渲染方法 end
          // 数据统计页面请求统计渲染方法 通过mixins: [extendStatsDataSummary] 混入
          'statsDataSummary': this.renderChartStatsDataSummary, //日报图表
          // 数据统计页面请求统计渲染方法 end
        };
        let renderChartDataMethod = {
          'timeline': this.renderChartDataMethodTimeline, //横轴时间线渲染数据方法
          'barYaxis': this.renderChartDataMethodBarYaxis, //Y轴类目轴柱状图渲染数据方法
          'barXaxis': this.renderChartDataMethodBarXaxis, //X轴类目轴柱状图渲染数据方法
          'barYaxisMoreCategory': this.renderChartDataMethodBarYaxisMoreCategory,//Y轴多类目轴柱状图渲染数据方法
          'confContinueTime': this.renderChartDataMethodBarConfContinueTime, //会议时长柱状图渲染数据方法
          'pie': this.renderChartDataMethodPie, //基础饼图渲染数据方法
          'ringHalf': this.renderChartDataMethodRingHalf, //只有一个数据的环形图数据渲染方法
          'scatter': this.renderChartDataMethodScatter, //基础散点图渲染数据方法
        };

        if (chartConf.options && chartConf.options.customerColor) {
          defaultConf.colorCustomer = chartConf.options.customerColor.concat(this.colorCustomer)
        }

        if (chartConf.chartRenderMethod) {
          await renderChartTypeMethod[chartConf.chartRenderMethod](defaultConf, chartConf, renderChartDataMethod, isNewChart)
          this.chartRenderStatu = false
          this.pluginEvents("over")
        }
      },

      // api数据获取函数
      async getApiData(defaultConf, chartConf) {
        // 每次请求会清除loading flag
        // 若需每次请求都loading 可配置prop：apiLoad:true;  TODO:此功能和prop暂不支持（后续补充） -- 20200326
        if (chartConf.loading) {
          this.chartLoading = true;
          delete chartConf.loading
        }
        let getData = ''
        let urlParams = chartConf.urlParams
        // console.log(colorLibrary)
        if (urlParams === 'nextReFresh') {
          return null
        }
        if (chartConf.url[0] === 'common') {
          getData = await this.$api.getChartData.getUrlDataSync(chartConf.url[1], urlParams)
        } else if (chartConf.url[0] === 'api') {
          getData = await this.$api.getChartData[chartConf.url[1]](urlParams)
        } else {
          getData = await this.$api[chartConf.url[0]][chartConf.url[1]](urlParams)
        }

        if (getData) {  // 根据返回有无判断是否显示遮罩层
          this.showDialog = false
          if (chartConf.dataKey) {
            chartConf.dataKey.forEach((item) => {
              getData = getData[item]
            })
          }
        } else {
          this.showDialog = true
        }

        this.chartLoading = false
        let isExistence = this.chartBaseInstance.getDom().attributes
        if (isExistence._echarts_instance_ && isExistence._echarts_instance_.value) {
          this.$emit('chart-data', getData);  // 通知父组件获取到的数据
          return getData
        } else {
          return false
        }

      },
      // api数据获取函数 end

      // chart渲染start：横轴时间线chart
      async renderChartTypeTimeline(defaultConf, chartConf, renderChartDataMethod, isNewChart) {
        // 时间线类图形配置
        let chartBaseOptionLine = {
          backgroundColor: defaultConf.echartsBackgroudColor,
          color: defaultConf.colorCustomer,
          grid: {
            left: 93,
            right: 40,
            bottom: 50,
            top: 50,
            containLabel: false
          },
          legend: {
            // data:[],
            itemWidth: 10,
            itemHeight: 5,
            width: '70%',
            icon: 'roundRect',
            itemGap: 22,
            right: 53,
            // left:100,
            textStyle: {
              color: '#9ca9b1',
              padding: [1, 0, 0, 5]
            },
            top: 20,
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
                if (item.value[1] !== null && item.value[1] !== undefined) showValue = Math.ceil(item.value[1])
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
          xAxis: {
            type: 'time',
            splitNumber: 10,
            // maxInterval: 3600 * 1000,
            axisLine: {
              lineStyle: {
                color: '#5f656a'
              },
            },
            axisTick: {
              show: false,
            },
            splitLine: {
              lineStyle: {
                color: ['#5f656a'],
                type: 'dotted'
              },
            },
            axisLabel: {
              fontSize: 10,
              color: '#9ca9b1',
              margin: 10,
              // interval:20,
              formatter: (value, index) => {
                // console.log(params)
                let time = this.$echarts.format.formatTime('hh:mm', value);
                return time
              },
              rotate: 90,
            },
          },
          yAxis: {
            // name:'使用率%',
            nameTextStyle: {
              fontSize: 12,
            },
            axisLabel: {
              fontSize: 10,
              color: '#9ca9b1',
              margin: 10,
            },
            axisLine: {
              lineStyle: {
                color: '#5f656a'
              },
            },
            axisTick: {
              show: false,
            },
            splitLine: {
              lineStyle: {
                color: ['#5f656a'],
                type: 'dotted'
              },
            },
          },
          series: []
        };
        // 时间线类图形配置end

        // 用于后续增加的整体样式调整 options
        let optionsAppend = {}
        // 颜色库初始化
        let colorLibrary = defaultConf.colorCustomer
        // 判断是否是新的一张表，若是，则重新渲染整张表，否，则只渲染数据
        if (isNewChart) {
          this.chartBaseInstance.setOption(chartBaseOptionLine, true)

          // 判断是否需要配置grid start
          if (chartConf.options.grid) {
            optionsAppend["grid"] = chartConf.options.grid
            // optionsAppend["grid"]["containLabel"]=true
          }
          // 判断是否需要配置grid end

          // 判断是否需要配置legend start
          if (chartConf.options.legend) {
            optionsAppend["legend"] = chartConf.options.legend
          }
          // 判断是否需要配置legend end

          // 判断是否需要Title start
          if (chartConf.options.title) {
            optionsAppend["title"] = chartConf.options.title
          }
          // 判断是否需要Title end

          // 判断是否需要tooltip start
          if (chartConf.options.tooltip) {
            optionsAppend["tooltip"] = chartConf.options.tooltip
          }
          // 判断是否需要tooltip end

          // 对于自定义项目的修改
          if (chartConf.options && chartConf.options.echartsCustom) {
            for (let key in chartConf.options.echartsCustom) {
              key ? optionsAppend[key] = chartConf.options.echartsCustom[key] : ''
            }
          }


          // 判断数据的tootip格式
          if (chartConf.options.dataFormat) {
            if (chartConf.options.dataFormat[0] === "percent") {  //百分比显示规则
              optionsAppend['tooltip'] = {
                // tooltip: {
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

                    let showValue = null
                    if (item.value[1] !== null && item.value[1] !== undefined) showValue = Math.round(item.value[1] * 100) / 100 + "%"
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
              }
              optionsAppend["yAxis"] = {
                ...optionsAppend["yAxis"],
                axisLabel: {
                  formatter: '{value}%'
                }
              }
            }
            ;
          }
          ;
          // 判断数据的tootip格式end
        }
        // end判断是否是新的一张表，若是，则重新渲染整张表，否，则只渲染数据
        this.chartBaseInstance.setOption(optionsAppend)
        // 数据处理部分
        // 根据chartConf.dataRenderMethon判断data渲染方式
        // console.log(chartConf.dataRenderMethon)
        renderChartDataMethod[chartConf.dataRenderMethon](defaultConf, chartConf, isNewChart)
        // 数据处理部分end
      },
      // chart渲染end：横轴时间线chart

      // 数据渲染start：横轴时间线渲染数据方法
      async renderChartDataMethodTimeline(defaultConf, chartConf, isNewChart) {
        // console.log(chartConf.name)
        let getData = await this.getApiData(defaultConf, chartConf)
        if (!getData) {
          return false
        }
        let colorLibrary = this.chartBaseInstance.getOption().color

        // 线的基础配置
        let confTimeLine = {
          symbolSize: 1,
          // symbol: 'none',
          type: "line",
          showSymbol: false,
          symbol: 'circle',
          symbolSize: 6,
          smooth: true,
          smoothMonotone: 'x',
          sampling: 'max',
          lineStyle: {
            width: 2,
          },
        };

        let seriseData = getData.map((item, index) => {
          let seriseDataConf = {...confTimeLine}

          // 图例名称和数据系列标识
          seriseDataConf["name"] = item.description

          // 判读数据是否需要叠加
          if (chartConf.options.stack) {
            let vStack = chartConf.options.stack.filter(i => i.name === item.description)
            if (vStack.length > 0) {
              seriseDataConf["stack"] = vStack[0].data
            }
          }

          // 判断曲线区域是否需要填充颜色start
          if (chartConf.options.isArea) {
            let linearColor = new this.$echarts.graphic.LinearGradient(
              0, 0, 0, 1,
              [
                {offset: 0, color: defaultConf.colorCustomerRGBA[index]},
                // {offset: 0, color: 'rgba(99,205,129,0.1)'},
                {offset: 1, color: 'rgba(0,0,0,0)'}
                // {offset: 1, color: 'rgba(63,177,227,0)'}
              ])

            seriseDataConf["areaStyle"] = {
              // type: 'linear',
              color: linearColor,
              // opacity:0.1,
            }

            // 判断数据是否有数据
            // if(item.data.length===0){
            // console.log(chartConf)
            // }
          }
          ;
          // 判断曲线区域是否需要填充颜色end

          // 线条加阴影
          // seriseDataConf['lineStyle']={
          //   shadowColor: colorLibrary[index],
          //   shadowBlur: 1,
          //   width: 1,
          // }

          // 对有数据处理的数据做处理后返回
          let dataFront = item.data
          if (chartConf.dataCalculation) {
            let temData = item.data.map((data) => {
              let dataCalculation = eval(chartConf.dataCalculation)
              // console.log(temdata)
              return dataCalculation
            });
            dataFront = temData
          }
          seriseDataConf["data"] = dataFront
          return seriseDataConf
        })
        // 对有数据处理的数据做处理后返回end

        this.chartBaseInstance.setOption({
          series: seriseData
        })

      },
      // 数据渲染end：横轴时间线渲染数据方法

      // chart渲染start：终端参会概况chart
      async renderChartTypeTerminalConfSummary(defaultConf, chartConf, renderChartDataMethod, isNewChart) {
        // 会议信息终端参会chart options
        let chartOpitonsTerminalConfSummary = {
          backgroundColor: defaultConf.echartsBackgroudColor,
          grid: {
            left: 113,
            right: 58,
            bottom: 80,
            top: 140,
            containLabel: false
          },
          legend: {},
          tooltip: {
            trigger: 'item',
            padding: [18, 14],
            backgroundColor: '#141414',
            borderColor: '#383b3c',
            borderWidth: 1,
            textStyle: {
              color: '#9ca9b1',
            },

            formatter: (params,) => {
              // console.log(params)
              if (!params.value[3]) {
                let startTime = this.$echarts.format.formatTime('yyyy-MM-dd', params.value[1])
                  + ' ' + this.$echarts.format.formatTime('hh:mm:ss', params.value[1]);
                let endTime = this.$echarts.format.formatTime('yyyy-MM-dd', params.value[2])
                  + ' ' + this.$echarts.format.formatTime('hh:mm:ss', params.value[2]);

                let usedFormatter = []

                let htmlContent = '<div style="text-align: left;">' +
                  '<div style="display: inline-block;">' + "开始时间" + '</div>' +
                  '<div style="display: inline-block;">' + '&nbsp:&nbsp' + startTime +
                  '</div></div>' +
                  '<div style="text-align: left;">' +
                  '<div style="display: inline-block;">' + "结束时间" + '</div>' +
                  '<div style="display: inline-block;">' + '&nbsp:&nbsp' + endTime +
                  '</div></div>'

                let extend = null

                // usedFormatter.push(item.seriesName + ': ' + showValue)
                usedFormatter.push(htmlContent)
                // console.log(freeFormatter)
                let header = '<div style="font-size: 16px;margin-bottom: 12px;">' + params.name + '</div>'
                let content = htmlContent

                return header + content + (extend ? extend : '');
              } else {
                if (params.value[3].type === 'confAction') {
                  let startTime = this.$echarts.format.formatTime('yyyy-MM-dd', params.value[3].timestamp)
                    + ' ' + this.$echarts.format.formatTime('hh:mm:ss', params.value[3].timestamp);
                  let s = params.value[3].desc + "时间：" + startTime

                  let usedFormatter = []

                  // console.log(params.value[3].info)
                  if (params.value[3].info) {
                    for (let i of params.value[3].info) {
                      let htmlContent = '<div style="text-align: left;">' +
                        '<div style="display: inline-block;">' + i.title + '</div>' +
                        '<div style="display: inline-block;">' + '&nbsp:&nbsp' + i.content +
                        '</div></div>'
                      usedFormatter.push(htmlContent)
                    }
                  }

                  // console.log(freeFormatter)
                  let header = '<div style="font-size: 16px;margin-bottom: 12px;">' + s + '</div>'
                  let content = usedFormatter.join('')

                  return header + content;
                }
                else if (params.value[3].type === 'errAction') {
                  let startTime = this.$echarts.format.formatTime('yyyy-MM-dd', params.value[3].timestamp)
                    + ' ' + this.$echarts.format.formatTime('hh:mm:ss', params.value[3].timestamp);
                  let s = "时间：" + startTime
                  let usedFormatter = []
                  let leftHtml = '<div class="lchart-tootip-block__left">'
                  let rightHtml = '<div class="lchart-tootip-block__right">'

                  if (params.value[3].info) {
                    for (let i of params.value[3].info) {
                      let lhtmlContent = '<div class="lchart-tootip-content--block" style="text-align: right;">' +
                        '<div class="lchart-tootip-content-left">' + i.title + '</div>' +
                        '</div>'
                      leftHtml += lhtmlContent

                      let rhtmlContent = '<div class="lchart-tootip-content--block">' +
                        '<div class="lchart-tootip-content-right">' + ':&nbsp' + i.content + '</div>' +
                        '</div>'
                      rightHtml += rhtmlContent
                    }
                  }

                  leftHtml += '</div>'
                  rightHtml += '</div>'

                  usedFormatter = [leftHtml, rightHtml]
                  // console.log(freeFormatter)
                  let header = '<div style="font-size: 16px;margin-bottom: 12px;">' + s + '</div>'
                  let content = [...usedFormatter].join('\n')
                  return header + content;
                }
              }
              ;
            },
          },
          xAxis: {
            type: 'time',
            splitNumber: 10,
            // maxInterval: 3600 * 1000,
            axisLine: {
              lineStyle: {
                color: '#5f656a'
              },
            },
            splitLine: {
              show: false,
              lineStyle: {
                color: ['#5f656a'],
                type: 'dotted'
              },
            },
            axisLabel: {
              fontSize: 12,
              margin: 10,
              color: '#9ca9b1',
              // interval:20,
              formatter: (value, index) => {
                let day = this.$echarts.format.formatTime('MM-dd', value);
                let time = this.$echarts.format.formatTime('hh:mm:ss', value);
                return '{time|' + time + '}{day|\n' + day + '}';
              },
              rich: {
                day: {
                  color: "#9ca9b1",
                  fontSize: 12,
                  height: 16,
                  padding: [0, 2],
                },
                time: {
                  color: "#9ca9b1",
                  fontSize: 12,
                  height: 16,
                  padding: [0, 2],
                },
              },
              // formatter:  (value,index) => {
              //   // console.log(params)
              //   let time =this.$echarts.format.formatTime('hh:mm', value);
              //   return time
              // },
              // rotate:90,
            },
            axisTick: {
              show: false,
              color: '#5f656a',
            },
          },
          yAxis: {
            type: 'category',
            data: [],
            // name:'使用率%',
            nameTextStyle: {
              fontSize: 12,
            },
            axisLabel: {
              fontSize: 10,
              color: '#9ca9b1',
              margin: 10,
            },
            axisLine: {
              lineStyle: {
                color: '#5f656a'
              },
            },
            splitLine: {
              show: true,
              lineStyle: {
                color: ['#5f656a'],
                type: 'dotted'
              },
            },
            axisTick: {
              show: false,
              color: '#5f656a',
            },
          },
          series: []
        }

        // 用于后续增加的整体样式调整 options
        let optionsAppend = {}
        // 颜色库初始化
        let colorLibrary = defaultConf.colorCustomer

        // start判断是否是新的一张表，若是，则重新渲染整张表，否，则只渲染数据
        if (isNewChart) {
          this.chartBaseInstance.setOption(chartOpitonsTerminalConfSummary, true)
        }
        // end判断是否是新的一张表，若是，则重新渲染整张表，否，则只渲染数据
        let getData = await this.getApiData(defaultConf, chartConf)
        if (!getData) {
          return false
        }

        // Y轴项目列表
        // let YItem=getData.filter(item => item.name !== "会议总时长").map(item=>item.name)
        // YItem = [...new Set(YItem)]
        let YItem = getData.yAxisData

        // legend排列
        let XOffectList = ['15%', '25%', '35%', '45%', '55%', '65%',]
        let YOffectList = [25]
        for (let i = 0; i < getData.data.length; i++) {
          if (i % 6 === 0 && i !== 0) {
            YOffectList.push(parseInt(YOffectList.slice(-1)) + 25)
          }
        }
        // console.log(getData)
        // console.log(XOffectList,YOffectList)
        let newLegend = getData.data.map((litem, index) => {
          let XOffect = Math.floor(index % 6)
          let YOffect = Math.floor(index / 6)
          // console.log(XOffect,YOffect)
          let temLegend = {
            itemWidth: 10,
            itemHeight: 5,
            // width:'20%',
            icon: 'roundRect',
            textStyle: {
              color: '#b5b5b6',
              fontSize: 14,
              padding: [1, 0, 0, 5]
            },
            left: XOffectList[XOffect],
            top: YOffectList[YOffect],
            data: [litem.lName]
          }
          return temLegend
        })

        // legend排列 end

        let baseConf = {
          type: 'custom',
          renderItem: (params, api) => {
            var categoryIndex = api.value(0);
            var start = api.coord([api.value(1), categoryIndex]);
            var end = api.coord([api.value(2), categoryIndex]);
            var height = api.size([0, 1])[1];
            var rectShape = this.$echarts.graphic.clipRectByRect({
              x: start[0],
              y: start[1] - height / 4,
              width: end[0] - start[0],
              height: height / 2
            }, {
              x: params.coordSys.x,
              y: params.coordSys.y,
              width: params.coordSys.width,
              height: params.coordSys.height
            })
            return rectShape && {
              type: 'rect',
              shape: rectShape,
              style: api.style()
            };
          },
          encode: {
            x: [1, 2],
            y: 0
          },
          data: []
        }
        let seriseDataConfData = getData.data.map((item, index) => {
          let dataConf = {...baseConf}
          let dataColor = colorLibrary[index]
          dataConf["name"] = item.lName
          dataConf["itemStyle"] = {
            color: dataColor,
            // opacity:0.5,
          }
          dataConf['z'] = index + 20
          dataConf["data"] = item.value.map(i => {
            let tem = {
              name: i.name,
              value: i.value,
            }
            return tem
          })
          // dataConf["value"]=item.value
          return dataConf
        })

        this.chartBaseInstance.setOption({
          yAxis: {
            data: YItem,
          },
          legend: newLegend,
          series: seriseDataConfData
        })
      },
      // chart渲染end：终端参会概况chart

      // chart渲染start：会议事件chart
      async renderChartTypeConfEvent(defaultConf, chartConf, renderChartDataMethod, isNewChart) {
        // 会议信息终端参会chart options
        let chartOpitonsTerminalConfSummary = {
          backgroundColor: defaultConf.echartsBackgroudColor,
          grid: {
            left: 113,
            right: 58,
            bottom: 80,
            top: 140,
            containLabel: false
          },
          legend: {},
          tooltip: {
            trigger: 'item',
            padding: [18, 14],
            backgroundColor: '#141414',
            borderColor: '#383b3c',
            borderWidth: 1,
            textStyle: {
              color: '#9ca9b1',
            },

            formatter: (params,) => {
              if (params.seriesName === '开会/结会') {
                let startTime = this.$echarts.format.formatTime('yyyy-MM-dd', params.value[1])
                  + ' ' + this.$echarts.format.formatTime('hh:mm:ss', params.value[1]);
                let endTime = this.$echarts.format.formatTime('yyyy-MM-dd', params.value[2])
                  + ' ' + this.$echarts.format.formatTime('hh:mm:ss', params.value[2]);

                if (params.value[3][1] === 2) endTime = '正在召开'  // 如果最后时间是当前（实时会议）
                let usedFormatter = []

                let htmlContent = '<div style="text-align: left;">' +
                  '<div style="display: inline-block;">' + "开会时间" + '</div>' +
                  '<div style="display: inline-block;">' + '&nbsp:&nbsp' + startTime +
                  '</div></div>' +
                  '<div style="text-align: left;">' +
                  '<div style="display: inline-block;">' + "结会时间" + '</div>' +
                  '<div style="display: inline-block;">' + '&nbsp:&nbsp' + endTime +
                  '</div></div>'

                usedFormatter.push(htmlContent)
                let content = htmlContent

                return content
              } else {  //前缀五个字的处理方法
                let name = params.seriesName.slice(5)
                let operationList = [params.seriesName.slice(3, 5), params.seriesName.slice(0, 2)]
                let startTime = this.$echarts.format.formatTime('yyyy-MM-dd', params.value[1])
                  + ' ' + this.$echarts.format.formatTime('hh:mm:ss', params.value[1]);
                let htmlContent = '<div style="text-align: left;">' +
                  '<div style="display: inline-block;">' + name + operationList[params.value[3][1]] + '</div>' +
                  '<div style="display: inline-block;">' + '&nbsp:&nbsp' + startTime +
                  '</div></div>'
                let content = htmlContent
                return content
              }
            },
          },
          xAxis: {
            type: 'time',
            splitNumber: 10,
            // maxInterval: 3600 * 1000,
            axisLine: {
              lineStyle: {
                color: '#5f656a'
              },
            },
            splitLine: {
              show: false,
              lineStyle: {
                color: ['#5f656a'],
                type: 'dotted'
              },
            },
            axisLabel: {
              fontSize: 12,
              margin: 10,
              color: '#9ca9b1',
              // interval:20,
              formatter: (value, index) => {
                let day = this.$echarts.format.formatTime('MM-dd', value);
                let time = this.$echarts.format.formatTime('hh:mm:ss', value);
                return '{time|' + time + '}{day|\n' + day + '}';
              },
              rich: {
                day: {
                  color: "#9ca9b1",
                  fontSize: 12,
                  height: 16,
                  padding: [0, 2],
                },
                time: {
                  color: "#9ca9b1",
                  fontSize: 12,
                  height: 16,
                  padding: [0, 2],
                },
              },
              // formatter:  (value,index) => {
              //   // console.log(params)
              //   let time =this.$echarts.format.formatTime('hh:mm', value);
              //   return time
              // },
              // rotate:90,
            },
            axisTick: {
              show: false,
              color: '#5f656a',
            },
          },
          yAxis: {
            type: 'category',
            data: [],
            // name:'使用率%',
            nameTextStyle: {
              fontSize: 12,
            },
            axisLabel: {
              fontSize: 10,
              color: '#9ca9b1',
              margin: 10,
            },
            axisLine: {
              lineStyle: {
                color: '#5f656a'
              },
            },
            splitLine: {
              show: true,
              lineStyle: {
                color: ['#5f656a'],
                type: 'dotted'
              },
            },
            axisTick: {
              show: false,
              color: '#5f656a',
            },
          },
          series: []
        }

        // 用于后续增加的整体样式调整 options
        let optionsAppend = {}
        // 颜色库初始化
        let colorLibrary = defaultConf.colorCustomer

        // start判断是否是新的一张表，若是，则重新渲染整张表，否，则只渲染数据
        if (isNewChart) {
          this.chartBaseInstance.setOption(chartOpitonsTerminalConfSummary, true)
        }
        // end判断是否是新的一张表，若是，则重新渲染整张表，否，则只渲染数据
        let getData = await this.getApiData(defaultConf, chartConf)
        if (!getData) {
          return false
        }
        // Y轴项目列表
        // let YItem=getData.filter(item => item.name !== "会议总时长").map(item=>item.name)
        // YItem = [...new Set(YItem)]
        let YItem = getData.yAxisData
        // legend排列
        let XOffectList = ['15%', '25%', '35%', '45%', '55%', '65%',]
        let YOffectList = [25]
        for (let i = 0; i < getData.data.length; i++) {
          if (i % 6 === 0 && i !== 0) {
            YOffectList.push(parseInt(YOffectList.slice(-1)) + 25)
          }
        }
        // console.log(YOffectList)
        // console.log(XOffectList,YOffectList)
        let newLegend = getData.data.map((litem, index) => {
          let XOffect = Math.floor(index % 6)
          let YOffect = Math.floor(index / 6)
          // console.log(XOffect,YOffect)
          let temLegend = {
            itemWidth: 10,
            itemHeight: 5,
            // width:'20%',
            icon: 'roundRect',
            textStyle: {
              color: '#b5b5b6',
              fontSize: 14,
              padding: [1, 0, 0, 5]
            },
            left: XOffectList[XOffect],
            top: YOffectList[YOffect],
            data: [litem.legendName]
          }

          return temLegend
        })

        // legend排列 end

        let baseConf = {
          type: 'custom',
          renderItem: (params, api) => {
            var categoryIndex = api.value(0);
            let bgStyle = api.style()
            if (categoryIndex === 0) {
              var start = api.coord([api.value(1), categoryIndex]);
              var end = api.coord([api.value(2), categoryIndex]);
              var height = api.size([0, 1])[1];
              var rectShape = this.$echarts.graphic.clipRectByRect({
                x: start[0],
                y: start[1] - height / 4,
                width: end[0] - start[0],
                height: height / 2
              }, {
                x: params.coordSys.x,
                y: params.coordSys.y,
                width: params.coordSys.width,
                height: params.coordSys.height
              })
              return rectShape && {
                type: 'rect',
                shape: rectShape,
                style: bgStyle
              };
            }
          },
          encode: {
            x: [1, 2],
            y: 0
          },
          data: []
        }
        let seriseDataConfData = getData.data.map((item, index) => {
          let dataConf = {...baseConf}
          let dataColor = colorLibrary[index]
          dataConf["name"] = item.legendName
          dataConf["itemStyle"] = {
            color: dataColor,
            // opacity:0.5,
          }
          dataConf['z'] = index + 20
          dataConf["data"] = item.value.map(i => {
            let tempDict = {}
            tempDict.name = YItem[i[0]] ? YItem[i[0]] : '会议总时长'
            tempDict.value = i
            return tempDict
          })

          return dataConf
        })

        // console.log(YItem,seriseDataConfData)

        this.chartBaseInstance.setOption({
          yAxis: {
            data: YItem,
          },
          legend: newLegend,
          series: seriseDataConfData
        })
      },
      // chart渲染end：会议事件chart

      // chart渲染start：基础柱状图chart
      async renderChartTypeBaseBar(defaultConf, chartConf, renderChartDataMethod, isNewChart) {
        // 柱状图类图形配置
        let chartBaseOptionBar = {
          backgroundColor: defaultConf.echartsBackgroudColor,
          color: ['#25a5c5', '#63cd81', '#a0a7e6', '#c4ebad', '#96dee8', '#626c91'],
          grid: {
            left: '7%',
            right: '9%',
            bottom: 15,
            top: 45,
            containLabel: true
          },
          tooltip: {
            trigger: 'item',
            padding: [18, 14],
            backgroundColor: '#141414',
            borderColor: '#383b3c',
            borderWidth: 1,
            textStyle: {
              color: '#9ca9b1',
            },
          },
          xAxis: {},
          yAxis: {},
          series: []
        };
        // 柱状图类图形配置end

        // 用于后续增加的整体样式调整 options
        let optionsAppend = {}
        // 颜色库初始化
        let colorLibrary = this.colorCustomer
        // 判断是否是新的一张表，若是，则重新渲染整张表，否，则只渲染数据
        if (isNewChart) {

          this.chartBaseInstance.setOption(chartBaseOptionBar, true)

          // 判断是否需要配置grid start
          if (chartConf.options.grid) {
            optionsAppend["grid"] = chartConf.options.grid
            // optionsAppend["grid"]["containLabel"]=true
          }
          // 判断是否需要配置grid end

          // 判断是否需要配置legend start
          if (chartConf.options.legend) {
            optionsAppend["legend"] = chartConf.options.legend
          }
          // 判断是否需要配置legend end

          // 判断坐标轴
          if (chartConf.chartRenderMethod === "barYaxis") {
            optionsAppend["xAxis"] = {
              type: 'value',
              axisLabel: {
                fontSize: 10,
                color: '#9ca9b1',
                margin: 10,
                // interval:20,
              },
              axisLine: {
                lineStyle: {
                  color: '#5f656a'
                },
              },
              splitLine: {
                lineStyle: {
                  color: ['#5f656a'],
                  type: 'dotted'
                },
              },
              axisTick: {
                show: false,
              },
            }
            optionsAppend["yAxis"] = {
              type: "category",
              // name:'使用率%',
              nameTextStyle: {
                fontSize: 12,
              },
              axisLabel: {
                fontSize: 10,
                margin: 10,
                color: '#9ca9b1',
                formatter: (value, index) => {
                  let newValue = value.toString();
                  let maxlength = chartConf.options.yAxisLabelLength || 7;
                  if (newValue.length > maxlength) {
                    return newValue.substring(0, maxlength - 1) + '...';
                  } else {
                    return newValue;
                  }
                  return newValue
                },
              },
              axisLine: {
                lineStyle: {
                  color: '#5f656a',
                },
              },
              axisTick: {
                show: true,
                color: '#5f656a',
              },
            };
          }
          else if (chartConf.chartRenderMethod === "barXaxis") {
            optionsAppend["xAxis"] = {
              type: 'category',
              nameTextStyle: {
                fontSize: 12,
              },
              axisTick: {
                show: true,
                color: '#5f656a',
              },
              axisLabel: {
                fontSize: 10,
                margin: 10,
                interval: 0,//代表显示所有x轴标签
                color: '#9ca9b1',
                formatter: (value, index) => {
                  let newValue = value.toString();
                  let maxlength = 10;
                  if (newValue.length > maxlength) {
                    return newValue.substring(0, maxlength - 1) + '...';
                  } else {
                    return newValue;
                  }
                  return newValue
                },
              },
              axisLine: {
                lineStyle: {
                  color: '#5f656a',
                },
              },
            }
            optionsAppend["yAxis"] = {
              type: "value",
              // name:'使用率%',
              axisLabel: {
                fontSize: 10,
                margin: 10,
                color: '#9ca9b1'
                // interval:20,
              },
              axisTick: {
                show: false,
              },
              axisLine: {
                lineStyle: {
                  color: '#5f656a'
                },
              },
              splitLine: {
                lineStyle: {
                  color: ['#5f656a'],
                  type: 'dotted'
                },
              },
            };
          }
          // 判断坐标轴end

          // 对于自定义项目的修改
          if (chartConf.options && chartConf.options.echartsCustom) {
            for (let key in chartConf.options.echartsCustom) {
              key ? optionsAppend[key] = chartConf.options.echartsCustom[key] : ''
            }
          }
        }
        // end判断是否是新的一张表，若是，则重新渲染整张表，否，则只渲染数据
        this.chartBaseInstance.setOption(optionsAppend)
        // 数据处理部分
        // 根据chartConf.dataRenderMethon判断data渲染方式
        // console.log(chartConf.dataRenderMethon)
        renderChartDataMethod[chartConf.dataRenderMethon](defaultConf, chartConf, isNewChart)
        // 数据处理部分end
      },
      // chart渲染end：基础柱状图chart

      // 数据渲染start：Y轴类目轴柱状图渲染数据方法
      async renderChartDataMethodBarYaxis(defaultConf, chartConf, isNewChart) {
        let series = []
        let seriseData = {}
        let YAxisData = []
        let colorLibrary = this.chartBaseInstance.getOption().color
        let urlParams = chartConf.urlParams
        // console.log(colorLibrary)
        let getData = await this.getApiData(defaultConf, chartConf)
        if (!getData) {
          return false
        }
        // 柱状图渐变
        let linearColor = new this.$echarts.graphic.LinearGradient(
          1, 0, 0, 0,
          [
            // {offset: 0, color: this.colorCustomer[0]},
            // {offset: 0, color: '#1790cf'},
            // {offset: 1, color: 'rgba(0,0,0,0)'}
            // {offset: 1, color: 'rgba(63,177,227,0)'}
            {offset: 0, color: '#5eb9ef'},
            {offset: 1, color: '#1a79ae'}
          ])

        seriseData["type"] = 'bar'
        seriseData["itemStyle"] = {
          color: linearColor,
          // opacity:0.7,
        }
        // seriseData["barMaxWidth"] = 8
        seriseData["barWidth"] = '50%'
        // 配置每个系列的数据
        seriseData["data"] = getData.reverse().map((item, index) => {
          // 图例名称和数据系列标识
          // 对有数据处理的数据做处理后返回
          YAxisData.push(item.description)
          let dataFront = [item.data, item.description]
          if (chartConf.dataCalculation) {
            let data = [item.data, item.description]
            let dataCalculation = eval(chartConf.dataCalculation)
            // console.log(temdata)
            dataFront = dataCalculation
          }
          return dataFront
        })
        // 对有数据处理的数据做处理后返回end
        series.push(seriseData)
        this.chartBaseInstance.setOption({
          // series:seriseData
          yAxis: {
            data: YAxisData,
          },
          series: series
        })
      },
      // 数据渲染end：Y轴类目轴柱状图渲染数据方法

      // 数据渲染start：X轴类目轴柱状图渲染数据方法
      async renderChartDataMethodBarXaxis(defaultConf, chartConf, isNewChart) {

        let getData = await this.getApiData(defaultConf, chartConf)
        if (!getData) {
          return false
        }
        let seriseData = {}
        let colorLibrary = this.chartBaseInstance.getOption().color
        // console.log(colorLibrary)

        // 柱状图渐变
        let linearColor = new this.$echarts.graphic.LinearGradient(
          0, 0, 0, 1,
          [
            // {offset: 0, color: this.colorCustomer[0]},
            // {offset: 0, color: '#1790cf'},
            // {offset: 1, color: 'rgba(0,0,0,0)'}
            // {offset: 1, color: 'rgba(63,177,227,0)'}
            {offset: 0, color: '#5db9ef'},
            {offset: 1, color: '#1a79ae'}
          ])

        seriseData["type"] = 'bar'
        seriseData["itemStyle"] = {
          color: linearColor,
          // opacity:0.7,
        }
        seriseData["barWidth"] = '50%'
        let fontSize = 10
        if (chartConf.options.labelFontSize) {
          fontSize = chartConf.options.labelFontSize
        }
        seriseData["label"] = {
          normal: {
            show: true,
            position: 'inside',
            color: '#fff',
            fontSize: fontSize,
          }
        }
        // seriseData["barMaxWidth"] = 16


        // 配置每个系列的数据
        seriseData["data"] = getData.map((item, index) => {
          // 图例名称和数据系列标识
          // 对有数据处理的数据做处理后返回
          let dataFront = [item.description, item.data]
          if (chartConf.dataCalculation) {
            let data = [item.description, item.data]
            let dataCalculation = eval(chartConf.dataCalculation)
            // console.log(temdata)
            dataFront = dataCalculation
          }
          if (item.detail) {
            dataFront.push(item.detail)
          }
          return dataFront
        })
        // 对有数据处理的数据做处理后返回end

        if (chartConf.seriseDataReverse) seriseData["data"] = seriseData["data"].reverse() //数据是否翻转

        this.chartBaseInstance.setOption({
          series: seriseData
        })
      },
      // 数据渲染end：X轴类目轴柱状图渲染数据方法

      // 数据渲染start：Y轴多类目轴柱状图渲染数据方法
      async renderChartDataMethodBarYaxisMoreCategory(defaultConf, chartConf, isNewChart) {
        let series = []
        let YAxisData = chartConf.options.YAxisData || []
        let axisData = {
          yAxis: {
            data: YAxisData,
          },
        }
        // 兼容X轴多类目 渲染
        if (chartConf.options.XAxisData) {
          axisData = {
            xAxis: {
              data: chartConf.options.XAxisData,
            },
          }
        }
        ;
        let getData = await this.getApiData(defaultConf, chartConf)
        if (!getData) {
          return false
        }
        // 柱状图渐变

        let defaultSeriesLabel = {
          show: true,
          position: 'right'
        }
        // seriseData["barMaxWidth"] = 8
        // seriseData["barWidth"] = '50%'
        // 配置每个系列的数据
        series = getData.map((item, index) => {
          let eachData = {}
          eachData['type'] = 'bar'
          eachData['name'] = item.description
          eachData["barWidth"] = chartConf.options.barWidth || '30%'
          eachData['label'] = chartConf.options.seriesLabel || defaultSeriesLabel
          eachData['data'] = item.data
          return eachData
        })

        // 对有数据处理的数据做处理后返回end
        this.chartBaseInstance.setOption({
          ...axisData,
          series: series
        })
      },
      // 数据渲染end：Y轴多类目轴柱状图渲染数据方法

      // 数据渲染start：会议时长柱状图渲染数据方法
      async renderChartDataMethodBarConfContinueTime(defaultConf, chartConf, isNewChart) {
        let seriseData = {}
        let colorLibrary = this.chartBaseInstance.getOption().color
        // console.log(colorLibrary)
        let getData = await this.getApiData(defaultConf, chartConf)
        if (!getData) {
          return false
        }
        // 柱状图渐变
        let linearColor = new this.$echarts.graphic.LinearGradient(
          0, 0, 0, 1,
          [
            // {offset: 0, color: this.colorCustomer[0]},
            // {offset: 0, color: '#1790cf'},
            // {offset: 1, color: 'rgba(0,0,0,0)'}
            // {offset: 1, color: 'rgba(63,177,227,0)'}
            {offset: 0, color: '#5db9ef'},
            {offset: 1, color: '#1a79ae'}
          ])

        seriseData["type"] = 'bar'
        seriseData["itemStyle"] = {
          color: linearColor,
          // opacity:0.7,
        }
        seriseData["barWidth"] = '50%'

        let fontSize = 10
        if (chartConf.options.labelFontSize) {
          fontSize = chartConf.options.labelFontSize
        }
        seriseData["label"] = {
          normal: {
            show: true,
            position: 'inside',
            color: '#fff',
            fontSize: fontSize,
          }
        }
        // seriseData["barMaxWidth"] = 16

        seriseData["name"] = chartConf.name

        seriseData["stack"] = "conf"
        // 配置辅助柱状图
        let seriseDataAssist = {
          name: "辅助",
          type: 'bar',
          stack: 'conf',
          itemStyle: {
            normal: {
              barBorderColor: 'rgba(0,0,0,0)',
              color: 'rgba(0,0,0,0)'
            },
            emphasis: {
              barBorderColor: 'rgba(0,0,0,0)',
              color: 'rgba(0,0,0,0)'
            }
          },
          tooltip: {
            show: false,
          },
        }

        seriseDataAssist["data"] = [0]

        // 配置每个系列的数据
        getData.reverse()
        seriseData["data"] = getData.map((item, index) => {
          // 图例名称和数据系列标识
          // 对有数据处理的数据做处理后返回
          let dataFront = [item.description, item.data]
          if (chartConf.dataCalculation) {
            let data = [item.description, item.data]
            let dataCalculation = eval(chartConf.dataCalculation)
            // console.log(temdata)
            dataFront = dataCalculation
          }
          seriseDataAssist["data"].unshift(seriseDataAssist[0])
          seriseDataAssist["data"][0] = seriseDataAssist["data"][1] + item.data
          return dataFront
        })
        // 对有数据处理的数据做处理后返回end
        // seriseDataAssist["data"].reverse()
        seriseData["data"].reverse()
        seriseData["data"].unshift(["会议总数", seriseDataAssist["data"][0]])
        seriseDataAssist["data"][0] = 0
        // console.log(seriseData["data"],seriseDataAssist["data"])
        this.chartBaseInstance.setOption({
          series: [seriseDataAssist, seriseData]
        })
      },
      // 数据渲染end：会议时长柱状图渲染数据方法

      // chart渲染start：基础饼图chart
      async renderChartTypeBasePie(defaultConf, chartConf, renderChartDataMethod, isNewChart) {
        // 柱状图类图形配置
        let chartBaseOptionPie = {
          backgroundColor: defaultConf.echartsBackgroudColor,
          color: defaultConf.colorCustomer,
          grid: {
            left: '7%',
            right: '9%',
            bottom: 15,
            top: 45,
            containLabel: true
          },
          tooltip: {
            trigger: 'item',
            padding: [18, 14],
            backgroundColor: '#141414',
            borderColor: '#383b3c',
            borderWidth: 1,
            textStyle: {
              color: '#9ca9b1',
            },
          },
          series: []
        };
        // 柱状图类图形配置end

        // 用于后续增加的整体样式调整 options
        let optionsAppend = {}
        // 颜色库初始化
        let colorLibrary = defaultConf.colorCustomer
        // 判断是否是新的一张表，若是，则重新渲染整张表，否，则只渲染数据
        if (isNewChart) {
          this.chartBaseInstance.setOption(chartBaseOptionPie, true)
        }

        // 判断是否需要配置legend start
        if (chartConf.options.legend) {
          optionsAppend["legend"] = chartConf.options.legend
        }
        // 判断是否需要配置legend end

        // 判断是否需要Title start
        if (chartConf.options.title) {
          optionsAppend["title"] = chartConf.options.title
        }
        // 判断是否需要Title end

        // 对于自定义项目的修改
        if (chartConf.options && chartConf.options.echartsCustom) {
          for (let key in chartConf.options.echartsCustom) {
            key ? optionsAppend[key] = chartConf.options.echartsCustom[key] : ''
          }
        }

        // end判断是否是新的一张表，若是，则重新渲染整张表，否，则只渲染数据
        this.chartBaseInstance.setOption(optionsAppend)

        // 数据处理部分
        // 根据chartConf.dataRenderMethon判断data渲染方式
        // console.log(chartConf.dataRenderMethon)
        renderChartDataMethod[chartConf.dataRenderMethon](defaultConf, chartConf, isNewChart)
        // 数据处理部分end
      },
      // chart渲染end：基础饼图chart

      // 数据渲染start：基础饼图渲染数据方法
      async renderChartDataMethodPie(defaultConf, chartConf, isNewChart) {
        let seriseData = {}
        let colorLibrary = this.chartBaseInstance.getOption().color

        let getData = await this.getApiData(defaultConf, chartConf)
        if (!getData) {
          return false
        }
        seriseData["type"] = 'pie'
        seriseData["name"] = chartConf.name
        seriseData["radius"] = chartConf.options.radius || '55%'
        seriseData["center"] = ['50%', '50%']
        // seriseData["selectedMode"]='single'
        seriseData["label"] = {
          color: '#9ca9b1',
          formatter: '{b}： {d} %'
        }
        // 判断是否自定义label
        if (chartConf.options.label) {
          seriseData["label"] = chartConf.options.label
        }
        seriseData["labelLine"] = chartConf.options.labelLine || {lineStyle: {width: 2}}

        // 判断是否需要限制扇区最小角度
        if (chartConf.options.minAngle) {
          seriseData["minAngle"] = chartConf.options.minAngle
        }

        // 判断是否需要调整图形中心位置
        if (chartConf.options.center) {
          seriseData["center"] = chartConf.options.center
        }


        // 配置每个系列的数据
        seriseData["data"] = getData.map((item, index) => {
          // 颜色渐变
          // let linearColor=new this.$echarts.graphic.LinearGradient(
          //   0, 0, 1,1,
          //   [
          //     {offset: 0.1, color: defaultConf.colorCustomer[index]},
          //     // {offset: 1, color: 'rgba(0,0,0,0)'}
          //     {offset: 1, color: 'rgba(63,177,227,0)'}
          //   ])
          // 图例名称和数据系列标识
          // 数据为0的扇区不展示
          if (!item.data) {
            return null
          }
          // 对有数据处理的数据做处理后返回
          let dataFront = {
            value: item.data,
            name: item.description,
            itemStyle: {
              color: defaultConf.colorCustomer[index],
            }
          }
          // 判断饼图扇区是否选中
          if (chartConf.options.selectedMode && chartConf.options.selectedMode.indexOf(item.description) != -1) {
            seriseData['selectedMode'] = true
            dataFront['selected'] = true
          }

          return dataFront
        })
        // 对有数据处理的数据做处理后返回end

        this.chartBaseInstance.setOption({
          series: seriseData
        })
      },
      // 数据渲染end：基础饼图渲染数据方法

      // 数据渲染start：只有一个数据的环形图数据渲染方法
      async renderChartDataMethodRingHalf(defaultConf, chartConf, isNewChart) {
        let seriseData = {}

        let getData = await this.getApiData(defaultConf, chartConf)
        if (!getData) {
          return false
        }

        seriseData["type"] = 'pie'
        seriseData["name"] = chartConf.name
        seriseData["radius"] = ['50%', '55%'],
          seriseData["center"] = ['50%', '50%']
        seriseData["avoidLabelOverlap"] = false
        seriseData["hoverAnimation"] = false
        seriseData["labelLine"] = {
          normal: {
            show: false
          }
        }

        let usePercent = getData.data
        let itemStyleColor = usePercent > 80 ? '#e45959' : '#4796c4'

        seriseData["data"] = [{
          name: "已使用",
          itemStyle: {
            color: itemStyleColor,
          },
          label: {
            normal: {
              show: true,
              fontSize: 16,
              color: itemStyleColor,
              position: 'center',
              formatter: function () {
                return Math.ceil(usePercent) + "%"
              }
            },
          },
          value: Math.ceil(usePercent),
        }, {
          name: "剩余",
          label: {
            normal: {
              show: false,
            },
          },
          itemStyle: {
            color: '#43494d',
          },
          // 原
          // value:100-usePercent,
          // yp__start
          value: 100 - Math.ceil(usePercent),
          // yp__end
        },]

        this.chartBaseInstance.setOption({
          series: seriseData
        })
      },
      // 数据渲染end：只有一个数据的环形图数据渲染方法

      // chart渲染start：基础散点图chart
      async renderChartTypeBaseScatter(defaultConf, chartConf, renderChartDataMethod, isNewChart) {
        // 散点图类图形配置
        let chartBaseOptionScatter = {
          backgroundColor: defaultConf.echartsBackgroudColor,
          color: ['#25a5c5', '#63cd81', '#a0a7e6', '#c4ebad', '#96dee8', '#626c91'],
          grid: {
            left: '7%',
            right: '9%',
            bottom: 15,
            top: 45,
            containLabel: true
          },
          legend: {
            // data:[],
            itemWidth: 10,
            itemHeight: 5,
            width: '70%',
            icon: 'roundRect',
            itemGap: 22,
            right: 53,
            // left:100,
            textStyle: {
              color: '#9ca9b1',
              fontSize: 12,
              padding: [1, 0, 0, 5]
            },
            top: 20,
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
                if (item.value[1] !== null && item.value[1] !== undefined) showValue = Math.ceil(item.value[1])
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
          xAxis: {
            type: 'time',
            splitNumber: 10,
            // maxInterval: 3600 * 1000,
            axisLine: {

              lineStyle: {
                color: '#5f656a'
              },
            },
            axisTick: {
              show: false,
            },
            splitLine: {
              show: false,
              lineStyle: {
                color: ['#5f656a'],
                type: 'dotted'
              },
            },
            axisLabel: {
              fontSize: 10,
              margin: 10,
              color: '#9ca9b1',
              // interval:20,
              formatter: (value, index) => {
                // console.log(params)
                let time = this.$echarts.format.formatTime('hh:mm', value);
                return time
              },
              rotate: 90,
            },
          },
          yAxis: {
            // name:'使用率%',
            nameTextStyle: {
              fontSize: 12,
            },
            axisLabel: {
              fontSize: 10,
              margin: 10,
              color: '#9ca9b1',
            },
            axisTick: {
              show: false,
            },
            axisLine: {
              lineStyle: {
                color: '#5f656a'
              },
            },
            splitLine: {
              lineStyle: {
                color: ['#5f656a'],
                type: 'dotted'
              },
            },
          },
          series: []
        };
        // 散点图类图形配置end

        // 用于后续增加的整体样式调整 options
        let optionsAppend = {}
        // 颜色库初始化
        let colorLibrary = this.colorCustomer
        // 判断是否是新的一张表，若是，则重新渲染整张表，否，则只渲染数据
        if (isNewChart) {

          this.chartBaseInstance.setOption(chartBaseOptionScatter, true)


          // 判断是否需要配置grid start
          if (chartConf.options.grid) {
            optionsAppend["grid"] = chartConf.options.grid
            // optionsAppend["grid"]["containLabel"]=true
          }
          // 判断是否需要配置grid end

          // 判断是否需要配置legend start
          if (chartConf.options.legend) {
            optionsAppend["legend"] = chartConf.options.legend
          }
          // 判断是否需要配置legend end

          // 对于自定义项目的修改
          if (chartConf.options && chartConf.options.echartsCustom) {
            for (let key in chartConf.options.echartsCustom) {
              key ? optionsAppend[key] = chartConf.options.echartsCustom[key] : ''
            }
          }
        }
        // end判断是否是新的一张表，若是，则重新渲染整张表，否，则只渲染数据
        this.chartBaseInstance.setOption(optionsAppend)
        // 数据处理部分
        // 根据chartConf.dataRenderMethon判断data渲染方式
        // console.log(chartConf.dataRenderMethon)
        renderChartDataMethod[chartConf.dataRenderMethon](defaultConf, chartConf, isNewChart)
        // 数据处理部分end
      },
      // chart渲染end：基础散点图chart

      // 数据渲染start：基础散点图渲染数据方法
      async renderChartDataMethodScatter(defaultConf, chartConf, isNewChart) {
        // console.log(chartConf.name)
        let colorLibrary = this.chartBaseInstance.getOption().color
        let getData = await this.getApiData(defaultConf, chartConf)
        if (!getData) {
          return false
        }
        let seriseData = getData.map((item, index) => {
          let seriseDataConf = {}

          // 图例名称和数据系列标识
          seriseDataConf["name"] = item.description
          seriseDataConf["type"] = "scatter"
          seriseDataConf["symbolSize"] = 6
          seriseDataConf["markPoint"] = {
            itemStyle: {
              opacity: 0.8
            },
            label: {
              color: '#fff',
            },
            data: [
              {
                name: "max",
                type: 'max'
              }
            ],
          }

          // 对有数据处理的数据做处理后返回
          let dataFront = item.data
          if (chartConf.dataCalculation) {
            let temData = item.data.map((data) => {
              let dataCalculation = eval(chartConf.dataCalculation)
              // console.log(temdata)
              return dataCalculation
            });
            dataFront = temData
          }
          seriseDataConf["data"] = dataFront
          return seriseDataConf
        })
        // 对有数据处理的数据做处理后返回end

        this.chartBaseInstance.setOption({
          series: seriseData
        })

      },
      // 数据渲染end：基础散点图渲染数据方法


      // chart events emit  暂时不用---

      // chart Action Func start
      chartAction(action) {
        let ObjAction = {
          'legend': this.chartActionLegend, //图例相关action
        }
        for (let act in action) {
          ObjAction[act](action[act])
        }
      },

      //图例相关action start
      chartActionLegend(action) {
        // console.log(action)
        if (this.chartBaseInstance) {
          let options = this.chartBaseInstance.getOption()
          let serise = options.series
          // console.log(serise)
          let legendConf = {}
          if (serise) {
            serise.forEach((item) => {
              // legendConf[item.name] = false
              this.chartBaseInstance.dispatchAction({
                type: action.type,
                name: item.name
              })
            })
          }
          // console.log(legendConf)
          // this.chartBaseInstance.setOption({
          //   legend:{
          //     selected:legendConf
          //   }
          // })
        }
      },
      //图例相关action end

      // chart Action Func end

      // chart 插件 Func start
      pluginEvents(act) {
        if (act === 'dataRoomLeft' && this.extraPlugin.dataRoom.leftButtonDisabled) return false
        else if (act === 'dataRoomRight' && this.extraPlugin.dataRoom.rightButtonDisabled) return false

        this.$emit('plugin-event', act);
      },
      // chart 插件 Func end

      // 其他功能函数start
      // 图片下载按钮
      downloadImg() {
        let $chartImg = document.createElement('a');
        let url = this.chartBaseInstance.getConnectedDataURL({
          type: 'png',
          pixelRatio: 2,
          // backgroundColor: '#2b2b2b'
        })
        $chartImg.download = 'download.png';
        $chartImg.target = '_blank';
        $chartImg.href = url;
        // Chrome and Firefox
        let evt = new MouseEvent('click', {
          view: window,
          bubbles: true,
          cancelable: false
        });
        $chartImg.dispatchEvent(evt);
        // console.log(chartImg.src)
      },
      // 其他功能函数end

      // 组件chart初始化
      init() {
        this.chartBaseInstance = this.$refs[this.ChartID].getChartInstance();
        // this.chartBaseInstance.setOption(this.chartOpitons)
        if (this.chartConf) {
          this.renderChartInit(this.chartConf)
        }
      },
    },
    mounted() {
      this.init()
    },
    beforeDestroy() {
    },
  }
</script>

<style>
  .component-chart-extend {
    height: 100%;
    width: 100%;
    position: relative;
  }

  .area-chart-extend-extra {
    position: absolute;
    /*top:5px;*/
    /*right: 20px;*/
    z-index: 198;
  }

  .chart--dialog {
    width: 100%;
    height: 100%;
    position: absolute;
    background-color: #232629;
    top: 0;
    left: 0;
    z-index: 199;
    font-size: 16px;
    vertical-align: middle;
    text-align: center;
  }

  .lchart-tootip-block__left {
    display: inline-block;
  }

  .lchart-tootip-block__right {
    display: inline-block;
  }

  .lchart-tootip-content-legendicon {
    display: inline-block;
    text-align: left;
    width: 10px;
    height: 5px;
    z-index: 199;
    vertical-align: 2px;
    border-radius: 1px;
    margin-right: 5px;
  }

  .lchart-tootip-content--block {
    font-size: 14px;
    width: 100%;
    /*padding: 0 8px;*/
    box-sizing: border-box;
    text-align: left;
  }

  .lchart-tootip-content-left {
    /*float: left;*/
    display: inline-block;
    text-align: left;
    /*width: calc(100% - 70px);*/
    /*text-align: left;*/
    /*width: 60%;*/
  }

  .lchart-tootip-content-right {
    /*float: right;*/
    display: inline-block;
    /*width: 100px;*/
    /*max-width: 100px;*/
    text-align: left;
    padding-left: 10px;
  }

  .plugin-imgexport {
    display: inline-block;
    margin-left: 20px;
  }

  .plugin-datainterval {
    display: inline-block;
    margin-left: 20px;
  }

  .plugin-datainterval .datainterval__input {
    /*display: inline-block;*/
    /*width: 38px;*/
    text-align: center;
    vertical-align: 7px;
    margin-left: 5px;
  }

  .plugin-datainterval .datainterval__suffix {
    /*display: inline-block;*/
    /*width: 12px;*/
    text-align: center;
    vertical-align: 7px;
    margin-right: 5px;
  }

  .plugin-dataroom .dataroom__left {
    position: absolute;
    z-index: 99;
  }

  .plugin-dataroom .dataroom__right {
    position: absolute;
    z-index: 99;
  }
</style>
