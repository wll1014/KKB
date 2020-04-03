<template>
  <div class="area-conference-topology theme-dark">
    <div class="conference-topology__search">
      <div v-if="showContent==='machineRoom'">
        <!-- <div style="font-size: 14px;margin-bottom: 10px;">会议拓扑</div> -->
        <el-input style="width: 360px;margin-right: 7px;" v-model="_inputIDConf" placeholder="请输入会议名称、会议号码、发起人、终端名称、终端号码" maxlength="7"
                  @keyup.enter.native="clickSearch" clearable></el-input>
        <el-button @click="clickSearch" :disabled="disabledSearchButton">搜索</el-button>
      </div>
      <div v-else>
        <el-button icon="ops-icons-bg icon-arrow-circle-left" @click="back" circle></el-button>
        <div style="font-size: 14px;display: inline-block;margin-left: 10px;vertical-align: 7px;">{{'会议：' + pageTitle}}</div>
      </div>
    </div>

    <!--图例-->
    <div class="conference-topology__lenged">
      <div>
        <span class="legend-icon info"></span>
        <span class="legend-text">正常</span>
      </div>
      <div>
        <span class="legend-icon alarm"></span>
        <span class="legend-text">异常</span>
      </div>
    </div>

    <div style="height: 100%;width:100%;box-sizing: border-box;">
      <!--<ChartBase :chartID="ChartID" :ref="ChartID" @chartInstanceOver="chartInstanceOver"></ChartBase>-->
      <ChartBase :chartID="ChartID" :ref="ChartID"></ChartBase>
    </div>
    <!--终端外设蒙版-->
    <div class="conference-topology__newchart" id="dialog__confnewchart" :style="newchartPosition"
         v-if="showChildChart">
      <i class="el-icon-close" @click="closeChildChart"
         style="position: absolute;z-index: 199;font-size: 14px;cursor: pointer;right: 20px;top:20px;"></i>
      <ChartBase :chartID="childChartID" :ref="childChartID"></ChartBase>
      <!--无数据时展示页面-->
      <div class="chart--dialog" v-if="childChartNoData">
        <i class="el-icon-close" @click="closeChildChart"
           style="position: absolute;z-index: 199;font-size: 14px;cursor: pointer;right: 20px;top:20px;"></i>
        <span style="position: absolute;top:63px;left: 95px;">暂无数据</span>
      </div>
      <!--无数据时展示页面 end-->
    </div>
  </div>
</template>

<script>
  import ChartBase from "@/components/home/ChartBase.vue"

  export default {
    name: "ConferenceTopology",
    components: {
      ChartBase,
    },
    data() {
      return {
        // 定时器实例
        timer: null,

        pageTitle: '',
        inputIDConf: '',
        otherParams: {},

        showContent: 'machineRoom',
        showConfInfo: null,
        disabledSearchButton: false,
        childChartNoData: true,
        // 外设chart相关变量
        showChildChart: false,
        newchartPosition: {},
        childChartID: 'ConferenceTopologyChildChart',
        childChartInstance: '',
        // 图形类静态数据 start
        // 不同的终端展示不同的样式
        iconMtType: {
          '1': 'pathMT',
          '7': 'pathMTJiLian',
          '8': 'pathMTJiLian',
          '10': 'pathDev',
        },
        iconPath: {
          pathMachineRoom: 'path://M77.1,81.7v824h254v-824H77.1z M276.8,396.3h-148v-38h148V396.3z M276.8,474.3h-148v-38h148V474.3z M276.8,318.3h-148v-38\n' +
            '\th148V318.3z M276.8,166.3h-148v-38h148V166.3z M276.8,244.3h-148v-38h148V244.3z M378.1,81.7v824h254v-824H378.1z M577.8,396.3h-148\n' +
            '\tv-38h148V396.3z M577.8,474.3h-148v-38h148V474.3z M577.8,318.3h-148v-38h148V318.3z M577.8,166.3h-148v-38h148V166.3z M577.8,244.3\n' +
            '\th-148v-38h148V244.3z M679.1,81.7v824h254v-824H679.1z M878.8,396.3h-148v-38h148V396.3z M878.8,474.3h-148v-38h148V474.3z\n' +
            '\t M878.8,318.3h-148v-38h148V318.3z M878.8,166.3h-148v-38h148V166.3z M878.8,244.3h-148v-38h148V244.3z',

          pathDev: 'path://M211.1,70.2v880h600v-880H211.1z M511.1,843.1c-49.7,0-90-40.3-90-90c0-49.7,40.3-90,90-90c49.7,0,90,40.3,90,90 C601.1,802.8,560.8,843.1,511.1,843.1z M686.1,475h-350v-40h350V475z M686.1,319.4h-350v-40h350V319.4z',

          pathConfRoom: 'path://M934,583.4c0,35.8-18.2,70.1-51.3,96.4c-10.8,8.6-26.5,6.8-35.1-4c-8.6-10.8-6.8-26.5,4-35.1\n' +
            '\tc14.8-11.7,32.4-31.2,32.4-57.2c0-22.6-13.2-44.4-37.2-61.5c-26.6-18.9-62.4-29.3-100.8-29.3H270.6c-38.4,0-74.3,10.4-100.9,29.3\n' +
            '\tc-24,17-37.2,38.9-37.2,61.5c0,26,17.6,45.4,32.5,57.2c10.8,8.6,12.6,24.3,4,35.1c-4.9,6.2-12.2,9.5-19.6,9.5\n' +
            '\tc-5.4,0-10.9-1.8-15.5-5.4c-33.1-26.3-51.4-60.5-51.4-96.4c0-39.2,20.7-75.6,58.3-102.2c35-24.8,81.1-38.5,129.8-38.5h101.1\n' +
            '\tc-14.5-14.2-16.5-56.2-0.7-84.5c9.9-17.6,42.5-55.5,71.4-55.5c33.9,0,49.6,35.5,63.4,35.5c13.8,0,29.5-35.5,63.4-35.5\n' +
            '\tc28.9,0,61.6,37.9,71.4,55.5c15.8,28.3,13.8,70.3-0.7,84.5h106c48.7,0,94.8,13.7,129.8,38.5C913.3,507.8,934,544.1,934,583.4z\n' +
            '\t M534.8,665.7h-53.2c-13.8,0-25,11.2-25,25s11.2,25,25,25h53.2c13.8,0,25-11.2,25-25S548.6,665.7,534.8,665.7z M505.7,267.4\n' +
            '\tc39,0,70.6-31.6,70.6-70.6c0-39-31.6-70.7-70.6-70.7c-39,0-70.7,31.7-70.7,70.7C435.1,235.8,466.7,267.4,505.7,267.4z M229.5,595.3\n' +
            '\tc0-39,31.6-70.7,70.7-70.7c39,0,70.6,31.7,70.6,70.7S339.2,666,300.2,666C261.1,666,229.5,634.4,229.5,595.3z M423,846.1H177.5\n' +
            '\tc-24.1,0-31.3-54.9-12-89.4c9.9-17.6,42.5-55.5,71.4-55.5c33.9,0,49.6,35.5,63.4,35.5c13.8,0,29.5-35.5,63.4-35.5\n' +
            '\tc28.9,0,61.6,37.9,71.4,55.5C454.3,791.2,447.1,846.1,423,846.1z M648,595.3c0-39,31.6-70.7,70.7-70.7c39,0,70.6,31.7,70.6,70.7\n' +
            '\tS757.7,666,718.6,666C679.6,666,648,634.4,648,595.3z M841.5,846.1H595.9c-24.1,0-31.3-54.9-12-89.4c9.9-17.6,42.5-55.5,71.4-55.5\n' +
            '\tc33.9,0,49.6,35.5,63.4,35.5c13.8,0,29.5-35.5,63.4-35.5c28.9,0,61.6,37.9,71.4,55.5C872.8,791.2,865.6,846.1,841.5,846.1z',

          pathMT: 'path://M737.8,695V347.1h-38.2c-7-98.6-89.1-176.4-189.5-176.4s-182.5,77.8-189.5,176.4h-38.2V695H81.6v94h857v-94H737.8z\n' +
            '\t M340.4,446.3c31.3,61.9,95.5,104.4,169.7,104.4s138.3-42.5,169.7-104.4V695H340.4V446.3z',

          pathMTJiLian: 'path://M201.5,595.3c0-39,31.6-70.7,70.7-70.7c39,0,70.6,31.7,70.6,70.7S311.2,666,272.2,666\n' +
            '\tC233.1,666,201.5,634.4,201.5,595.3z M395,846.1H149.5c-24.1,0-31.3-54.9-12-89.4c9.9-17.6,42.5-55.5,71.4-55.5\n' +
            '\tc33.9,0,49.6,35.5,63.4,35.5c13.8,0,29.5-35.5,63.4-35.5c28.9,0,61.6,37.9,71.4,55.5C426.3,791.2,419.1,846.1,395,846.1z M680,595.3\n' +
            '\tc0-39,31.6-70.7,70.7-70.7c39,0,70.6,31.7,70.6,70.7S789.7,666,750.6,666C711.6,666,680,634.4,680,595.3z M873.5,846.1H627.9\n' +
            '\tc-24.1,0-31.3-54.9-12-89.4c9.9-17.6,42.5-55.5,71.4-55.5c33.9,0,49.6,35.5,63.4,35.5c13.8,0,29.5-35.5,63.4-35.5\n' +
            '\tc28.9,0,61.6,37.9,71.4,55.5C904.8,791.2,897.6,846.1,873.5,846.1z M438,197.3c0-39,31.6-70.7,70.7-70.7c39,0,70.6,31.7,70.6,70.7\n' +
            '\tS547.7,268,508.6,268C469.6,268,438,236.4,438,197.3z M631.5,448.1H385.9c-24.1,0-31.3-54.9-12-89.4c9.9-17.6,42.5-55.5,71.4-55.5\n' +
            '\tc33.9,0,49.6,35.5,63.4,35.5c13.8,0,29.5-35.5,63.4-35.5c28.9,0,61.6,37.9,71.4,55.5C662.8,393.2,655.6,448.1,631.5,448.1z\n' +
            '\t M649.6,597.7h-56v-6c0-11-9-20-20-20h-39c0.3-1.6,0.5-3.2,0.5-4.8v-66.4c0-13.8-11.2-25-25-25s-25,11.2-25,25v66.4\n' +
            '\tc0,1.6,0.2,3.3,0.5,4.8h-39c-11,0-20,9-20,20v6h-55.8c-13.8,0-25,11.2-25,25s11.2,25,25,25h55.8v6c0,11,9,20,20,20h127.1\n' +
            '\tc11,0,20-9,20-20v-6h56c13.8,0,25-11.2,25-25S663.5,597.7,649.6,597.7z',

          pathPC: 'path://M881.1,165.3h-720c-11,0-20,9-20,20v480c0,11,9,20,20,20h335v106.5h-225v50h500v-50h-225V685.3h335c11,0,20-9,20-20v-480\n' +
            '\tC901.1,174.3,892.1,165.3,881.1,165.3z',
          pathMKF: 'path://M370.3,506.6V219.3c0-32.3,15.5-62.2,43.6-84.3c26.3-20.7,61-32.1,97.6-32.1c36.6,0,71.3,11.4,97.6,32.1\n' +
            '\tc28.1,22.1,43.6,52.1,43.6,84.3v287.3c0,32.3-15.5,62.2-43.6,84.3c-26.3,20.7-61,32.1-97.6,32.1s-71.3-11.4-97.6-32.1\n' +
            '\tC385.7,568.8,370.3,538.9,370.3,506.6z M739,385.3c-13.8,0-25,11.2-25,25v92.4c0,102.3-90.9,185.6-202.5,185.6\n' +
            '\tc-111.7,0-202.6-83.3-202.6-185.6v-92.4c0-13.8-11.2-25-25-25s-25,11.2-25,25v92.4c0,63.3,26.5,122.7,74.7,167.3\n' +
            '\tc41.7,38.6,95.2,62,152.9,67.2v103.6h-81.7c-13.8,0-25,11.2-25,25s11.2,25,25,25h213.4c13.8,0,25-11.2,25-25s-11.2-25-25-25h-81.7\n' +
            '\tV737.1c57.7-5.3,111.2-28.7,152.9-67.2c48.2-44.6,74.7-104,74.7-167.3v-92.4C764,396.5,752.8,385.3,739,385.3z',

        },
        // 图形类静态数据 end

        ChartID: 'ConferenceTopology',


        // 判断chart渲染状态，防止监听状态重复导致表格重复渲染
        chartRenderStatu: false,
        // echarts实例
        chartBaseInstance: '',
        // 缓存数据
        // 设备数据
        MachineRoomDataCache: [],
        // huiyi数据
        ConfRoomDataCache: [],
        // 外设数据
        MTDataCache: [],
        // 机房交互连线数据
        interactiveMachineRoomDataCache: [],
        // 会议交互连线数据
        interactiveConfDataCache: [],
        // 终端交互连线数据
        interactiveMTDataCache: [],
        // 缓存数据end

        // echarts颜色库
        colorCustomer: ['#5eb9ef', '#63cd81', '#fb265d', '#f1ac17', '#d66ef8', '#1d4ff4', '#db6b08'],
        colorCustomerRGBA: ['rgba(94,185,239,0.1)', 'rgba(99,205,129,0.1)', 'rgba(251,38,93,0.1)',
          'rgba(241,172,23,0.1)', 'rgba(214,110,248,0.1)', 'rgba(29,79,244,0.1)', 'rgba(219,107,8,0.1)'],
        // echarts背景色
        echartsBackgroudColor: '#232629',

        // 拓扑上图标颜色和状态
        iconColor: ['#25a5c5', '#c30d23', '#9fa0a0', '#fff'],
        iconStatus: ['正常', '异常', '离线', '未知'],

        chartConfSupport: {
          ConferenceTopology: {
            name: "会议拓扑",
            chartRenderMethod: "ConferenceTopology",
            dataRenderMethod: "ConferenceTopology",
            options: {}
          },
        },
      };
    },
    computed: {
      _inputIDConf: {
        set: function (value) {
          this.inputIDConf = value;
        },
        get: function () {
          return this.inputIDConf.replace(/[ ]+/g, '')
        }
      },
      //监听数据变化
      dataChange() {
        let seriseData = {
          name: 'ConferenceTopology',
          categories: ['机房', '会议', '终端'],
          data: [],
          links: [],
          // center:null,
        }
        seriseData.data = seriseData.data.concat(this.MachineRoomDataCache, this.ConfRoomDataCache, this.MTDataCache)
        seriseData.links = seriseData.links.concat(this.interactiveMachineRoomDataCache, this.interactiveConfDataCache, this.interactiveMTDataCache)
        return seriseData
      },
    },
    watch: {
      dataChange(newVal) {
        this.domEchatsIsExist()
        this.chartBaseInstance.setOption({
          // legend: legendConf,
          series: newVal
        })
      }
    },
    methods: {
      clickSearch() {
        this.$set(this.otherParams, 'inputKeywords', this.inputIDConf)
        this.renderDataConfRoom()
      },

      // 渲染会议数据前后的处理
      async renderContentConf(confID) {
        this.disabledSearchButton = true
        this.clearTimer();
        this.domEchatsIsExist()
        this.chartBaseInstance.setOption({
          series: {
            name: 'ConferenceTopology',
            center: null,
          }
        })
        if (confID) await this.renderDataConfMT(confID)
        this.disabledSearchButton = false
        this.pageTitle = this.showConfInfo.name
        this.setTimer(30);
      },

      async back() {
        this.showContent = 'machineRoom'
        this.showConfInfo = null
        this.interactiveMTDataCache = []
        this.MTDataCache = []
        this.closeChildChart()
        this.domEchatsIsExist()
        this.chartBaseInstance.setOption({
          series: {
            name: 'ConferenceTopology',
            center: null,
          }
        })
        await this.renderDataMachineRoom()
        await this.renderDataConfRoom()
      },
      closeChildChart() {
        this.showChildChart = false
      },

      // 判断echatrs 实例是否还在
      domEchatsIsExist() {
        if (this.chartBaseInstance) {
          let isExistence = this.chartBaseInstance.getDom().attributes
          // let aaa = this.chartBaseInstance
          if (isExistence._echarts_instance_ && isExistence._echarts_instance_.value) {
          } else {
            throw "echarts instance no exist "
          }
        }
        else {
          throw "echarts dom no exist "
        }
      },

      // 定时器函数start
      // 设置定时器
      setTimer(interver = 60, range = 3600000) {
        this.clearTimer();
        this.timer = setInterval(() => {
          if (this.showContent === 'conf') {
            if (this.showConfInfo) this.renderDataConfMT(this.showConfInfo)
          } else {
            this.domEchatsIsExist()
            this.renderChartInit(this.chartConfSupport.ConferenceTopology, false)
          }
        }, interver * 1000)
      },
      // 清除定时器
      clearTimer() {
        clearInterval(this.timer);
        this.timer = null;
      },

      // 定时器函数end

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
          'ConferenceTopology': this.renderChartTypeConferenceTopology, //会议拓扑chart
        };
        let renderChartDataMethod = {};

        if (chartConf.options && chartConf.options.customerColor) {
          defaultConf.colorCustomer = chartConf.options.customerColor.concat(this.colorCustomer)
        }
        if (chartConf.chartRenderMethod) {
          await renderChartTypeMethod[chartConf.chartRenderMethod](defaultConf, chartConf, renderChartDataMethod, isNewChart)
          this.chartRenderStatu = false
        }
      },


      // chart渲染start：会议拓扑chart
      async renderChartTypeConferenceTopology(defaultConf, chartConf, renderChartDataMethod, isNewChart) {
        // 会议信息终端参会chart options
        let chartOpitonsConferenceTopology = {
          backgroundColor: defaultConf.echartsBackgroudColor,
          scaleLimit: {
            min: 0.7,
          },
          tooltip: {
            padding: [18, 14],
            backgroundColor: '#141414',
            borderColor: '#383b3c',
            borderWidth: 1,
            textStyle: {
              color: '#9ca9b1',
            },
            formatter: (params,) => {
              let bd = ''
              let objStatu = {
                0: '正常',
                1: '异常'
              }
              if (params.dataType === 'edge') {
                bd = params.value.s.name + "  至  " + params.value.t.name
              } else {
                if (params.data.category === "机房") {
                  let textList = [
                    {left: '机房名称', right: params.value.domain_name},
                    {left: '所属平台域', right: params.value.machine_room_name},
                    {left: '运行状态', right: objStatu[params.value.status]}
                  ]
                  bd = this.renderTooltip(textList)
                } else if (params.data.category === "会议") {
                  bd = params.value.name
                } else {
                  let textList = [
                    {left: '终端名称', right: params.value.name},
                    {left: 'E164号', right: params.value.e164},
                    {left: '终端IP', right: params.value.ip || '无'},
                    {left: 'NatIP', right: params.value.mtip || '无'},
                    {left: '所属用户域', right: params.value.user_domain_name},
                    {left: '运行状态', right: objStatu[params.value.status]},
                  ]
                  // 区分不同的终端
                  let mttype = Number(params.value.mttype)
                  if (mttype === 10) {
                    textList = [
                      {left: '外设名称', right: params.value.name},
                      {left: 'IP地址', right: params.value.mtip},
                      {left: '所属用户域', right: params.value.user_domain_name},
                      {left: '运行状态', right: objStatu[params.value.status]},
                    ]
                  } else if (mttype === 7 || mttype === 8) {
                    textList = [
                      {left: '级联会议名称', right: params.value.name},
                      {left: 'E164号', right: params.value.e164},
                      {left: 'IP地址', right: params.value.mtip},
                      {left: '所属用户域', right: params.value.user_domain_name},
                      {left: '运行状态', right: objStatu[params.value.status]},
                    ]
                  }
                  bd = this.renderTooltip(textList)
                }
              }
              return bd
            },
          },
          series: [
            {
              name: 'ConferenceTopology',
              type: 'graph',
              layout: 'none',
              data: [],
              links: [],
              roam: true,
              focusNodeAdjacency: true,
              animationDelay: 1000,
              itemStyle: {
                normal: {
                  color: (params) => {
                    let index = params.data.value.status ? params.data.value.status : 0
                    return this.iconColor[index]
                  },
                  opacity: 1,
                }
              },
              label: {
                show: true,
                position: 'top',
                formatter: (params) => {
                  return params.value.name
                }
              },
              lineStyle: {
                color: '#25a5c5',
                width: 2,
                curveness: 0.2
              },
              emphasis: {
                lineStyle: {
                  width: 3
                },
              },
            },
          ]
        }

        // 用于后续增加的整体样式调整 options
        let optionsAppend = {}
        // 颜色库初始化
        let colorLibrary = defaultConf.colorCustomer
        // start判断是否是新的一张表，若是，则重新渲染整张表，否，则只渲染数据
        if (isNewChart) {
          this.chartBaseInstance.setOption(chartOpitonsConferenceTopology, true)
          this.chartBaseInstance.on('click', async (params) => {
            if (params.dataType === 'edge') {
              if (params.value.type === 'confToMachine' && this.showContent === 'machineRoom') {
                this.pageTitle = params.value.s.name
                this.renderContentConf(params.value.s)
              }
              else if (params.value.type === 'mtToConf') {
                // this.renderDataPeripheral(params)
                let val = {
                  module: 'mtInfo',
                  params: {
                    conf_id: this.showConfInfo.e164,
                    mt_id: params.value.s.e164,
                    conf_type: 3,
                    conf_status: 1,
                  }
                }
                this.emitChange(val)
                // TODO: 待页面改完删掉此段 -- 20200317
                // this.$router.push({
                //   name: 'monitor-meetinginfo',
                //   params: {
                //     module: 'mtInfo',
                //     params: {
                //       conf_id: this.showConfInfo.e164,
                //       mt_id: params.value.s.e164,
                //       conf_type: 3,
                //       conf_status: 1,
                //     }
                //   },
                // });
              }
            }
            else if (params.data.category === '会议' && this.showContent === 'machineRoom') {
              this.pageTitle = params.value.name
              this.renderContentConf(params.value)
            }
            else if (params.data.category === '终端') {
              // this.renderDataPeripheral(params)
              let val = {
                module: 'mtInfo',
                params: {
                  conf_id: this.showConfInfo.e164,
                  mt_id: params.value.e164,
                  conf_type: 3,
                  conf_status: 1,
                }
              }
              this.emitChange(val)
              // TODO: 待页面改完删掉此段 -- 20200317
              // this.$router.push({
              //   name: 'monitor-meetinginfo',
              //   params: {
              //     module: 'mtInfo',
              //     params: {
              //       conf_id: this.showConfInfo.e164,
              //       mt_id: params.value.e164,
              //       conf_type: 3,
              //       conf_status: 1,
              //     }
              //   },
              // });
            }
          });
        }
        // end判断是否是新的一张表，若是，则重新渲染整张表，否，则只渲染数据
        // let getData=await this.getApiData(defaultConf,chartConf)
        // if(!getData){
        //   return false
        // }

        let dataMR = await this.renderDataMachineRoom()
        await this.renderDataConfRoom()

      },
      // chart渲染end：会议拓扑chart
      // 机房数据渲染
      async renderDataMachineRoom() {
        let machineRoomData = await this.$api.conferenceTopology.getMachineRoom()

        let machineRoomLen = machineRoomData.length
        let temInteractive = []
        let renderMachineRoomData = machineRoomData.map((item, index) => {
          let coordinate = this.calculationMRCoordinate(index, index, machineRoomLen, 110)
          item.name = item.machine_room_name
          let tempD = {
            name: item.machine_room_moid,
            x: coordinate[0],
            y: coordinate[1],
            // fixed:true,
            symbolKeepAspect: true,
            category: '机房',
            value: item,
            symbol: this.iconPath.pathMachineRoom,
            symbolSize: 30,
          }

          if (item.link.length > 0) {
            item.link.forEach((itemLink, index) => {
              let s = machineRoomData.find(i => i.machine_room_moid === itemLink.machine_room_moid)
              temInteractive.push({
                source: itemLink.machine_room_moid,
                target: item.machine_room_moid,
                value: {
                  s: s,
                  t: item,
                  type: 'machineToMachine'
                }
              })
            })
          }
          return tempD
        })
        this.interactiveMachineRoomDataCache = temInteractive
        this.MachineRoomDataCache = renderMachineRoomData
        // return [renderMachineRoomData,temInteractive]
      },
      // 会议数据渲染
      async renderDataConfRoom() {
        let tempDataConf = []
        let tempDataConfLink = []
        if (this.MachineRoomDataCache.length > 0) {
          //遍历机房
          for (let item of this.MachineRoomDataCache) {
            let params = {
              machine_room_moid: item.value.machine_room_moid,
              keywords: this.otherParams.inputKeywords,
            }
            let res = await this.$api.conferenceTopology.getConfRoom(params)
            if (!res) return false
            let confRoomData = res.info
            let confRoomLen = confRoomData ? confRoomData.length : 0
            if (confRoomLen > 0) {
              let center = [item.x, item.y]
              let radius = 50 / (Math.ceil(confRoomLen / 6) + 1)
              let count = confRoomLen > 6 ? 6 : confRoomLen
              //遍历会议
              confRoomData.forEach((confItem, confIndex) => {
                // center,radius,index,total,count,range
                let coordinate = this.calculationCRCoordinate(center, radius, confIndex, confRoomLen, count, radius)
                let tempD = {
                  name: confItem.e164,
                  x: coordinate[0],
                  y: coordinate[1],
                  // fixed:true,
                  category: '会议',
                  value: confItem,
                  symbolKeepAspect: true,
                  symbol: this.iconPath.pathConfRoom,
                  symbolSize: 35,
                }
                tempDataConf.push(tempD)

                let tempDLink = {
                  source: confItem.e164,
                  target: item.name,
                  value: {
                    s: confItem,
                    t: item.value,
                    type: 'confToMachine'
                  }
                }
                tempDataConfLink.push(tempDLink)
              });
              //遍历会议 end
            }
            ;
          }
          ;
          //遍历机房 end
        }
        ;

        this.ConfRoomDataCache = tempDataConf
        this.interactiveConfDataCache = tempDataConfLink
        // return [tempDataConf,tempDataConfLink]
      },
      // 终端数据渲染
      async renderDataConfMT(conf) {
        // let resConfRoom = await this.$api.conferenceTopology.getConfRoom({e164: conf})
        // if (!resConfRoom.info[0]) {
        //   this.$message({
        //     message: '会议不存在',
        //   })
        //   return false
        // }
        let confRoomData = conf
        this.showConfInfo = confRoomData
        let machineRoomData = await this.$api.conferenceTopology.getSingleMachineRoom(confRoomData.machine_room_moid)
        if (!machineRoomData) {
          this.$message({
            message: '会议数据有误',
          })
          return false
        }
        machineRoomData.name = machineRoomData.machine_room_name
        let machineRoomIsExist = this.MachineRoomDataCache.find(i => i.name === machineRoomData.machine_room_moid)
        let confRoomIsExist = this.ConfRoomDataCache.find(i => i.name === confRoomData.e164)

        if (!machineRoomIsExist || !confRoomIsExist) {
          machineRoomIsExist = {
            x: 0,
            y: 0,
          }
          confRoomIsExist = {
            x: 0,
            y: 50,
          }
        }

        let tempChartDataMachineRoom = {
          name: machineRoomData.machine_room_moid,
          x: machineRoomIsExist.x,
          y: machineRoomIsExist.y,
          // fixed:true,
          category: '机房',
          value: machineRoomData,
          symbol: this.iconPath.pathMachineRoom,
          symbolSize: 30,
        }
        let tempChartDataConfRoom = {
          name: confRoomData.e164,
          x: confRoomIsExist.x,
          y: confRoomIsExist.y,
          value: confRoomData,
          category: '会议',
          symbolKeepAspect: true,
          symbol: this.iconPath.pathConfRoom,
          symbolSize: 35,
        }
        let tempChartDataConfToMachineLink = {
          source: confRoomData.e164,
          target: machineRoomData.machine_room_moid,
          value: {
            s: confRoomData,
            t: machineRoomData,
            type: 'confToMachine'
          }
        }

        this.MachineRoomDataCache = [tempChartDataMachineRoom]
        this.ConfRoomDataCache = [tempChartDataConfRoom]
        this.interactiveConfDataCache = [tempChartDataConfToMachineLink]

        let tempDataMT = []
        let tempDataMTLink = []

        let confMTData = await this.$api.conferenceTopology.getConfMt(confRoomData.e164)
        let confMTLen = confMTData.length
        // 获取会议位置，及会议至机房的距离
        let center = [confRoomIsExist.x, confRoomIsExist.y]
        let confToMachineX = Math.abs(confRoomIsExist.x - machineRoomIsExist.x)
        let confToMachineY = Math.abs(confRoomIsExist.y - machineRoomIsExist.y)
        let confToMachineDis = Math.sqrt(Math.pow(confToMachineX, 2) + Math.pow(confToMachineY, 2));

        let radius = confToMachineDis / (Math.ceil(confMTLen / 20) + 1)
        let count = confMTLen > 60 ? 10 : Math.ceil(confMTLen / 6)

        // 当终端数量过多时，不显示lable
        let labelConf = {}
        if (confMTLen >= 20) {
          labelConf = {
            normal: {
              show: false,
            },
            emphasis: {
              show: true,
            },
          }
        }
        ;
        // 当终端数量过多时，不显示lable end
        confMTData.forEach((item, index) => {
          let iconPathKey = this.iconMtType[item.mttype] ? this.iconMtType[item.mttype] : 'pathMT'
          let coordinate = this.calculationMTCoordinate(center, radius, index, confMTLen, count, radius / 1.5)
          let tempD = {
            name: item.e164 ? item.e164 : item.name + index,
            x: coordinate[0],
            y: coordinate[1],
            // fixed:true,
            category: '终端',
            value: item,
            symbolKeepAspect: true,
            symbol: this.iconPath[iconPathKey],
            symbolSize: 20,
            label: labelConf,
          }
          tempDataMT.push(tempD)
          let tempDLink = {
            source: item.e164 ? item.e164 : item.name + index,
            target: tempChartDataConfRoom.name,
            value: {
              s: item,
              t: confRoomData,
              type: 'mtToConf'
            }
          }
          tempDataMTLink.push(tempDLink)
        })
        this.MTDataCache = tempDataMT
        this.interactiveMTDataCache = tempDataMTLink

        // 修改当前显示标志
        this.showContent = 'conf'
      },

      // 外设数据渲染
      async renderDataPeripheral(mtconf) {
        let parentE = document.getElementById("ConferenceTopology")
        // console.log(mtconf.event.offsetX,parentE)
        let mtLeft = mtconf.event.offsetX
        let mtTop = mtconf.event.offsetY

        if ((mtLeft + 260) > parentE.clientWidth) mtLeft = parentE.clientWidth - 260
        mtTop = (mtTop - 160) > 10 ? mtTop - 160 : mtTop + 10
        this.newchartPosition = {
          top: mtTop + 'px',
          left: mtLeft + 'px'
        }
        this.showChildChart = true
        return false
        this.$nextTick(() => {
          this.childChartInit(mtconf)
        })
      },

      // 组件 child chart 初始化
      async childChartInit(mtconf) {
        this.childChartInstance = this.$refs[this.childChartID].getChartInstance();
        // let res = await this.$api.conferenceTopology.getConfMt(conf.data.value.confID)
        let chartOpitonsConferenceTopologyChild = {
          backgroundColor: '#373d41',
          // tooltip:{
          //   formatter:(params,)=>{
          //     console.log(params.value)
          //   },
          // },
          series: [
            {
              name: 'ConferenceTopologyChild',
              type: 'graph',
              layout: 'none',
              data: [],
              links: [],
              roam: true,
              left: 50,
              right: 50,
              bottom: 30,
              top: 30,
              focusNodeAdjacency: true,
              itemStyle: {
                normal: {
                  color: '#25a5c5',
                }
              },
              label: {
                position: 'right',
                formatter: '{b}'
              },
              lineStyle: {
                color: '#25a5c5',
                curveness: 0
              },
              emphasis: {
                lineStyle: {
                  width: 3
                }
              }
            },
          ]
        }
        this.childChartInstance.setOption(chartOpitonsConferenceTopologyChild, true)
        let seriseData = {
          name: 'ConferenceTopologyChild',
          categories: ['终端', '外设'],
          data: [],
          links: [],
        }
        let peripheralData = [{
          name: mtconf.data.name,
          x: 5,
          y: 0,
          // fixed:true,
          category: '终端',
          value: 99,
          // symbolKeepAspect:true,
          symbol: this.iconPath.pathMT,
          symbolSize: 40,
        }, {
          name: '外设1',
          x: 0,
          y: 10,
          // fixed:true,
          category: '外设',
          value: 99,
          symbolKeepAspect: true,
          symbol: this.iconPath.pathPC,
          symbolSize: 30,
        }, {
          name: '外设2',
          x: 10,
          y: 10,
          // fixed:true,
          category: '外设',
          value: 99,
          symbolKeepAspect: true,
          symbol: this.iconPath.pathMKF,
          symbolSize: 30,
        }]
        let peripheralLinks = [{
          source: '外设1',
          target: mtconf.data.name,
        }, {
          source: '外设2',
          target: mtconf.data.name,
        },]
        seriseData.data = seriseData.data.concat(peripheralData)
        seriseData.links = seriseData.links.concat(peripheralLinks)
        this.childChartInstance.setOption({
          // legend: legendConf,
          series: seriseData
        })
      },

      //其他功能函数封装 start
      // 范围内随机取值
      randomFrom(lowerValue, upperValue) {
        return Math.floor(Math.random() * (upperValue - lowerValue + 1) + lowerValue);
      },


      /*机房平均平均分布生成坐标函数
       * @method calculationCoordinate
       * @param {Array} center 围绕的圆心
       * @param {Number} index 第几个数据
       * @param {Number} total 总共多少数据
       * @param {Number} range 点与点之间的间距
       * @return {Array} 返回生成的数据
      */
      calculationMRCoordinate(center, index, total, range) {
        let x = null
        let y = null

        let baseNum = Math.ceil(Math.sqrt(total))

        let tempX = index % baseNum
        let tempY = parseInt(index / baseNum)

        x = tempX * range + 0
        y = tempY * range + 0

        // 如果是最后一排且数量小于baseNum，重新计算range X
        if ((total % baseNum) > 0 && tempY === parseInt(total / baseNum)) {
          range = range * (baseNum - 1) / ((total % baseNum) + 1)
          x = tempX * range + 0 + range
        }

        return [x, y]
      },

      /*会议围绕中心点圆形分布生成坐标函数
       * @method calculationCoordinate
       * @param {Array} center 围绕的圆心
       * @param {Number} radius 圆的半径
       * @param {Number} index 第几个数据
       * @param {Number} total 总共多少数据
       * @param {Number} count 一个圆上显示多少个
       * @param {Number} range 圆与圆之间的间距
       * @return {Array} 返回生成的数据
      */
      calculationCRCoordinate(center, radius, index, total, count, range) {
        let x = null
        let y = null

        let baseNum = parseInt(index / count)
        let offset = baseNum % 2 === 0 ? 0 : (360 / count) / 2

        let hudu = (2 * Math.PI / 360) * ((360 / count) * parseInt(index % count) + offset)

        radius = radius + baseNum * range

        x = center[0] + Math.sin(hudu) * radius
        y = center[1] + Math.cos(hudu) * radius

        return [x, y]
      },
      /*终端围绕圆心随机生成坐标函数
       * @method calculationCoordinate
       * @param {Array} center 围绕的圆心
       * @param {Number} radius 圆的半径
       * @param {Number} offset 在半径产生的圆的周围浮动偏差
       * @param {Number} index 第几个数据
       * @param {Number} total 总共多少数据
       // * @param {Array} total 总共多少数据
       * @return {Array} 返回生成的数据
      */
      calculationMTCoordinate(center, radius, index, total, count, range) {
        let x = null
        let y = null

        let fxList = [0, 180, 60, 240, 120, 300]
        let fangxiang = parseInt(index / count) % 6
        // console.log(((90/10) * index + 90 * fangxiang))
        let hudu = (2 * Math.PI / 360) * ((90 / count) * parseInt(index % count) + fxList[fangxiang])

        let baseLen = parseInt(parseInt(index / count) / 2)
        radius = radius + range * baseLen

        x = center[0] + Math.sin(hudu) * radius
        y = center[1] + Math.cos(hudu) * radius

        return [x, y]
      },
      calculationMTCoordinate2(center, radius, offset, index, total) {
        let x = null
        let y = null

        // let fxList = [0,180,60,240,120,300]
        let fangxiang = parseInt((index - 1) % 30)
        let avgHudu = 360 / 30
        let offsetHudu = this.randomFrom(avgHudu * fangxiang, avgHudu * (fangxiang + 1))
        // console.log(((90/10) * index + 90 * fangxiang))
        let hudu = (2 * Math.PI / 360) * offsetHudu

        let baseIndex = parseInt((index - 1) / 30)
        let offsetLen = this.randomFrom(radius * 0.4 * baseIndex, radius * 0.4 * (baseIndex + 1))
        radius = radius + offsetLen

        x = center[0] + Math.sin(hudu) * radius + this.randomFrom(0, offset)
        y = center[1] + Math.cos(hudu) * radius + this.randomFrom(0, offset)

        return [x, y]
      },

      // tooltip渲染函数
      renderTooltip(textList) {
        let htmlContent = textList.map((item) => {
          return '<div class="conf-tootip-content--block">' +
            '<div class="conf-tootip-content-left">' + item.left + '</div>' +
            '<div class="conf-tootip-content-right">' + ':&nbsp' + item.right +
            '</div></div>'
        })
        return htmlContent.join('\n')
      },

      // 点击空白地方关闭终端外设弹框
      listenerCloseDialog(e) {
        if (this.showChildChart) {
          let dialogE = document.getElementById("dialog__confnewchart")
          if (!this.isDOMContains(dialogE, e.target)) {
            this.closeChildChart()
          }
        }
      },
      // 判断一个元素是否包含一个指定节点
      isDOMContains(parentEle, ele) {
        //parentEle: 要判断节点的父级节点
        //ele:要判断的子节点
        //container : 二者的父级节点

        //如果parentEle h和ele传的值一样，那么两个节点相同
        if (parentEle == ele) {
          return true
        }
        if (!ele || !ele.nodeType || ele.nodeType != 1) {
          return false;
        }
        //如果浏览器支持contains
        if (parentEle.contains) {
          return parentEle.contains(ele)
        }
        //火狐支持
        if (parentEle.compareDocumentPosition) {
          return !!(parentEle.compareDocumentPosition(ele) & 16);
        }
      },
      //其他功能函数封装 end

      // 组件chart初始化
      init() {
        this.chartBaseInstance = this.$refs[this.ChartID].getChartInstance();
        let chartConf = this.chartConfSupport.ConferenceTopology
        if (chartConf) {
          this.renderChartInit(chartConf)
        }
        document.addEventListener("mouseup", this.listenerCloseDialog);
      },

      // emit函数
      emitChange(val) {
        this.$emit('change', val)
      },
    },

    mounted() {
      this.init()
      this.setTimer(30)
    },
    beforeDestroy() {
      this.clearTimer()
      document.removeEventListener("mouseup", this.listenerCloseDialog);
      // if(this.chartBaseInstance){
      //   this.chartBaseInstance.dispose()
      // }
    },
  }
</script>

<style>
  .area-conference-topology {
    width: 100%;
    height: calc(100vh - 232px);
    box-sizing: border-box;
    position: relative;

  }

  .conference-topology__newchart {
    width: 250px;
    height: 150px;
    z-index: 100;
    position: absolute;
  }

  .conference-topology__lenged {
    z-index: 101;
    top: 20px;
    right: 20px;
    position: absolute;
  }

  .conference-topology__lenged .legend-icon {
    width: 10px;
    height: 5px;
    border-radius: 1px;
    display: inline-block;
    vertical-align: 1px;
    margin-right: 4px;
  }

  .conference-topology__lenged .legend-icon.info {
    background-color: #25a5c5;
  }

  .conference-topology__lenged .legend-icon.alarm {
    background-color: #c30d23;
  }

  .conference-topology__lenged .legend-text {
    font-size: 14px;
  }

  .conference-topology__search {
    z-index: 10;
    top: -43px;
    /* left: 20px; */
    position: absolute;
  }

  .conference-topology__newchart .chart--dialog {
    width: 100%;
    height: 100%;
    position: absolute;
    box-sizing: border-box;
    padding: 20px;
    background-color: #232629;
    top: 0;
    left: 0;
    z-index: 199;
    font-size: 16px;
    vertical-align: bottom;
    text-align: center;
    box-shadow: 0px 2px 20px #23BFF9 inset
  }

  .conf-tootip-content--block {
    font-size: 14px;
    width: 100%;
    /*padding: 0 8px;*/
    box-sizing: border-box;
    text-align: left;
  }

  .conf-tootip-content-left {
    /*float: left;*/
    display: inline-block;
    text-align: right;
    width: 100px;

    /*width: calc(100% - 70px);*/
    /*text-align: left;*/
    /*width: 60%;*/
  }

  .conf-tootip-content-right {
    /*float: right;*/
    display: inline-block;
    /*max-width: 100px;*/

    text-align: left;
    padding-left: 10px;
  }
</style>
