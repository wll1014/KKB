<template>
  <div>
    <div style="height: 280px;width: 100%;position: relative;">
      <el-checkbox v-model="checkboxLegendSelected" @change="toggleLegend" class="checkbox-terminal-confsummary">全部
      </el-checkbox>
      <ChartExtendLargeModel ChartID="IDMeetingInfoConfEvent"
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
      apiParams: null,
    },
    watch: {
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

        // 延迟函数
        timeOutTimer: null,

        // 最后一次请求的urlParams
        lastUrlParams: null,

        // chart是否在渲染flag
        isChartRender: false,

        // chart封装组件的传参
        extraPlugin: {
          imgExport: true,
          // dataInterval:{
          //   interval:150,
          //   suffix:'秒'
          // },
          // dataRoom:{
          //   className:'terminal-survey',
          //   leftTooltip:'后退五分钟',
          //   rightTooltip:'前进五分钟',
          // },
        },

        // 会议概况图例选择框
        checkboxLegendSelected: true,

        // ChartID
        // ChartID: '',
        chartChange: '',
        activeChartConf: {},
        keepAliveParams: null,

        showChart: 'confEvent',
        // 此组件支持的chartConf
        chartConfSupport: {
          confEvent: {
            name: "会议事件概况",
            chartRenderMethod: "confEvent",  //此处定义图表渲染方式
            dataRenderMethon: "timeline",              //此处定义数据渲染方式
            // dataKey:['data','info'],
            url: ['api', 'getConfEventSummary'],  //此处定义数据获取方式
            // url:"cpu",
            urlParams: 'nextReFresh',
            routerPush: '跳转cpu',
            timerInterver: 60,
            action: {},
            options: {
              // customerColor:['#373b3f','#719cba','#67e0e3','#fae373','#8aab90','#9fe6b8',
              //   '#369a48','#00695c','#008dcc','#b39ddb','#747ffa','#fac864','#514aff',
              //   '#fa7373','#e062ae','#c75922','#c93248','#ff0000'
              // ]
              customerColor: ['#373b3f', '#719cba', '#67e0e3', '#fae373', '#9fe6b8',
                '#369a48', '#fa7373', '#e062ae', '#c93248', '#ff0000'
              ]
            }
          },
        },
      };
    },
    methods: {
      // 页面内功能start

      toggleLegend(flag) {
        // console.log(flag)
        let type = flag ? 'legendSelect' : 'legendUnSelect'
        let newAction = {
          legend: {
            type: type,
          },
        }
        this.$set(this.chartConfSupport[this.showChart], 'action', newAction)
      },

      // chart精度调整和时间范围变化
      chartPluginChange(act) {
        if (act === 'over') {
          let timestamp = (new Date()).getTime();
          let maxEndTime = this.apiParams.endTime === 'now' ? timestamp : this.apiParams.endTime

          let dataRoomConf = {...this.extraPlugin.dataRoom}

          // console.log(this.lastUrlParams.endTime,maxEndTime,this.apiParams.startTime)
          dataRoomConf.leftButtonDisabled = this.lastUrlParams.endTime - 1800000 <= this.apiParams.startTime ? true : false
          dataRoomConf.rightButtonDisabled = this.lastUrlParams.endTime + 65000 >= maxEndTime ? true : false
          this.$set(this.extraPlugin, 'dataRoom', dataRoomConf)
          return
        }
        // 如果是时间轴控制按钮
        if (act === 'dataRoomLeft' || act === 'dataRoomRight') {
          this.clearTimer()
          let timestamp = (new Date()).getTime();
          let maxEndTime = this.apiParams.endTime === 'now' ? timestamp : this.apiParams.endTime

          let endTime = this.lastUrlParams ? this.lastUrlParams.endTime : this.apiParams.endTime === 'now' ? maxEndTime : this.apiParams.endTime
          // this.$set(this.activeChartConf,'urlParams',params)

          endTime = act === 'dataRoomLeft' ? endTime - 300000 : act === 'dataRoomRight' ? endTime + 300000 : endTime

          if (endTime - 1800000 <= this.apiParams.startTime) {
            // let resetEndTime =
            endTime = this.apiParams.startTime + 1800000
          }
          if (endTime >= maxEndTime) {
            endTime = maxEndTime
            // 如果实时会议，打开定时器
            if (this.apiParams.endTime === 'now') this.setTimer(this.activeChartConf.timerInterver)
          }

          // this.$set(this.extraPlugin,'dataInterval',newConf)
          let params = this.getUrlParams(endTime)

          if (this.timeOutTimer) {
            clearTimeout(this.timeOutTimer);
          }
          this.timeOutTimer = setTimeout(() => {
            if (this.lastUrlParams) this.$set(this.activeChartConf, 'urlParams', this.lastUrlParams)
          }, 500);
        }
        ;

      },
      // 页面内功能end


      // 定时器函数start
      // 设置定时器
      setTimer(interver = 60, range = 3600000) {
        this.clearTimer();
        this.timer = setInterval(() => {
          // console.log(range)
          let timestamp = (new Date()).getTime();
          // console.log(timestamp,timestamp-range)
          let params = this.getUrlParams(timestamp)
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

      // 其他函数
      // 获取请求参数
      getUrlParams(endTime) {
        let params = {...this.apiParams}

        if (!endTime) {
          endTime = this.lastUrlParams ? this.lastUrlParams.endTime : this.apiParams.endTime
        }

        if (endTime === "now") {
          let timestamp = (new Date()).getTime();
          endTime = timestamp
        } else {
          endTime += 10000  //历史会议额外加段时间
        }
        params["endTime"] = endTime
        // let start = params["endTime"] - 1800000
        // if(start > params.startTime){
        //   params.startTime = start
        // }
        // params["interval"] = this.extraPlugin.dataInterval.interval * 1000
        // console.log(params["interval"])

        this.lastUrlParams = params
        return params
      },

      // 组件chart初始化
      async init() {
        // this.setTimer(2)
        // console.log(this.apiParams.endTime)
        if (this.apiParams && this.apiParams.confID) {
          if (this.showChart === 'confEvent') {
            this.activeChartConf = this.chartConfSupport[this.showChart]
            this.chartChange = this.showChart
            if (this.apiParams.confStatus === 1 || this.apiParams.endTime === 'now') {
              this.setTimer(this.activeChartConf.timerInterver)
            }

            let params = this.getUrlParams(this.apiParams.endTime)
            this.$set(this.activeChartConf, 'urlParams', params)
          }
          // console.log(this.activeChartConf)
          // let params={
          //   confID: 6660951,
          //   startTime:1564588800000,
          //   endTime: 1566144000000,
          //   confType:0,
          //   confStatus:0
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

  .terminal-survey.plugin-dataroom .dataroom__left {
    /*position: absolute;*/
    bottom: 48px;
    left: 64px;
    /*z-index: 99;*/
  }

  .terminal-survey.plugin-dataroom .dataroom__right {
    /*position: absolute;*/
    bottom: 48px;
    right: 16px;
    /*z-index: 99;*/
  }
</style>
