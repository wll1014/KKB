<template>
  <div class="area-host-topology">
    <!--图例-->
    <div class="host-topology__lenged">
      <div>
        <span class="legend-icon info"></span>
        <span class="legend-text">正常</span>
      </div>
      <div>
        <span class="legend-icon alarm"></span>
        <span class="legend-text">异常</span>
      </div>
    </div>

    <div style="height: 100%;width:100%;box-sizing: border-box;"
         v-loading="chartRenderStatu"
         element-loading-text="正在加载，请稍后..."
         element-loading-background="rgba(0, 0, 0, 0.3)">
      <!--<ChartBase :chartID="ChartID" :ref="ChartID" @chartInstanceOver="chartInstanceOver"></ChartBase>-->
      <ChartBase :chartID="ChartID" :ref="ChartID"></ChartBase>
    </div>

    <!-- 蒙版 -->
    <el-dialog
      :title="frameType"
      :visible.sync="frameDialog"
      width="800px"
      top="5%"
    >
      <div style="height: 350px;margin-top: 43px;text-align: center;">
        <TheHsotFrame :tipFormatter="tipFormatter"
                      :data="frameData"
                      lableKey="name"
                      tipZIndex=3000
                      :type="frameType"
                      :contentClass="setContentClass"
                      @onClick="hostFrameClick"></TheHsotFrame>
      </div>
    </el-dialog>
    <!-- 蒙版结束 -->
  </div>
</template>

<script>
  import ChartBase from "@/components/home/ChartBase.vue"

  export default {
    name: "HostTopology",
    components: {
      ChartBase,
      TheHsotFrame: () => import('@/view/hostmanage/TheHsotFrame.vue'),
    },
    props: {
      urlParams: null,
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
          name: 'HostTopology',
          categories: ['机房', '服务器'],
          data: [],
          links: [],
          // center:null,
        }
        seriseData.data = seriseData.data.concat(this.MachineRoomDataCache, this.DevDataCache)
        seriseData.links = seriseData.links.concat(this.interactiveDevDataCache)
        return seriseData
      },
    },
    watch: {
      urlParams: {
        deep: true,
        handler: function (newVal, oldVal) {
          if (!this.chartRenderStatu) {
            this.renderChartInit(this.hostTopologyConf, false)
          }
        }
      },
      dataChange(newVal) {
        this.domEchatsIsExist()
        this.chartBaseInstance.setOption({
          // legend: legendConf,
          series: newVal
        })
      }
    },
    data() {
      return {
        // 蒙版数据
        // 蒙版状态
        dialogTitle: '机框图',
        frameDialog: false,
        // 机框组件数据
        frameData: [],
        frameType: '',
        // 蒙版数据 end
        ChartID: 'HostTopology',
        chartBaseInstance: '',
        // 判断chart渲染状态，防止监听状态重复导致表格重复渲染
        chartRenderStatu: false,

        // 缓存数据
        // 设备数据
        MachineRoomDataCache: [],
        // 服务器数据
        DevDataCache: [],
        // 机房交互连线数据 TODO: 后续确认无用后可删除 -- 20200320
        // interactiveMachineRoomDataCache: [],
        // 服务器数据
        interactiveDevDataCache: [],

        // 单台主机tip缓存
        hostTipTimeOut: null,
        hostTipContent: null,  // eg.: {key:hostMoid,content:tipHtmlText}
        errorButtonTipTimeOut: null, // 用于延迟绑定告警异常按钮click事件
        // 缓存数据end

        // 静态数据 start
        frameTypeList: ['jd6000', 'jd10000', 'jds6000'], // 用于判断哪些类型属于机框的类型
        hostStatus: {
          0: '正常',
          1: '异常'
        },
        // 图形类
        iconPath: {
          pathMachineRoom: 'path://M77.1,81.7v824h254v-824H77.1z M276.8,396.3h-148v-38h148V396.3z M276.8,474.3h-148v-38h148V474.3z M276.8,318.3h-148v-38\n' +
            '\th148V318.3z M276.8,166.3h-148v-38h148V166.3z M276.8,244.3h-148v-38h148V244.3z M378.1,81.7v824h254v-824H378.1z M577.8,396.3h-148\n' +
            '\tv-38h148V396.3z M577.8,474.3h-148v-38h148V474.3z M577.8,318.3h-148v-38h148V318.3z M577.8,166.3h-148v-38h148V166.3z M577.8,244.3\n' +
            '\th-148v-38h148V244.3z M679.1,81.7v824h254v-824H679.1z M878.8,396.3h-148v-38h148V396.3z M878.8,474.3h-148v-38h148V474.3z\n' +
            '\t M878.8,318.3h-148v-38h148V318.3z M878.8,166.3h-148v-38h148V166.3z M878.8,244.3h-148v-38h148V244.3z',

          dev: 'path://M524.5,331.6H503H150.5v361.1H503h21.5h351.6V331.6H524.5z M258.5,471c-25.9,0-46.8-20.9-46.8-46.8\n' +
            '\tc0-25.9,20.9-46.8,46.8-46.8c25.9,0,46.8,20.9,46.8,46.8C305.1,450,284.2,471,258.5,471z M396.1,471c-25.9,0-46.8-20.9-46.8-46.8\n' +
            '\tc0-25.9,20.9-46.8,46.8-46.8c25.9,0,46.8,20.9,46.8,46.8C442.8,450,421.9,471,396.1,471z M655.5,665h-25.1v-25.1h25.1V665z\n' +
            '\t M694.5,665h-25.1v-25.1h25.1V665z M733.6,665h-25.1v-25.1h25.1V665z M772.6,665h-25.1v-25.1h25.1V665z M811.6,665h-25.1v-25.1h25.1\n' +
            '\tV665z M850.6,665h-25.1v-25.1h25.1V665z M93.4,268.7v486.8h839.9V268.7H93.4z M920.3,742.4h-814V281.8h814V742.4z',

          jd6000: 'path://M85,212.2v606.1h856.1V212.2H85z M928.1,805.2H98V225.3h830.2V805.2z M146.5,492.2h356.1h21.7h355.2v-217H524.4h-21.7H146.5\n' +
            '\tV492.2z M417,426c-25.1,0-45.4-20.3-45.4-45.4c0-25.1,20.3-45.4,45.4-45.4c25,0,45.3,20.3,45.4,45.4C462.4,405.7,442.1,426,417,426z\n' +
            '\t M264.3,426c-25.1,0-45.4-20.3-45.4-45.4c0-25.1,20.3-45.4,45.4-45.4c25,0,45.3,20.3,45.4,45.4C309.7,405.7,289.4,426,264.3,426z\n' +
            '\t M146.6,755.3h356.1h21.7h355.2v-217H524.4h-21.7H146.6V755.3z M417,689c-25.1,0-45.4-20.3-45.4-45.4c0-25.1,20.3-45.4,45.4-45.4\n' +
            '\tc25,0,45.3,20.3,45.4,45.4C462.5,668.7,442.2,689,417,689z M264.3,689c-25.1,0-45.4-20.3-45.4-45.4c0-25.1,20.3-45.4,45.4-45.4\n' +
            '\tc25,0,45.3,20.3,45.4,45.4C309.8,668.7,289.5,689,264.3,689z',

          jd10000: 'path://M368,522.4v-18.8V194.6H139.4v308.9v18.8v308.1H368V522.4z M211.3,312.4c0-25.1,20.3-45.4,45.4-45.4\n' +
            '\tc25.1,0,45.4,20.3,45.4,45.4c0,25.1-20.3,45.4-45.4,45.4C231.6,357.7,211.3,337.4,211.3,312.4 M211.3,465.1\n' +
            '\tc0-25.1,20.3-45.4,45.4-45.4c25.1,0,45.4,20.3,45.4,45.4c0,25.1-20.3,45.4-45.4,45.4C231.6,510.4,211.3,490.1,211.3,465.1\n' +
            '\t M628.4,522.4v-18.8V194.6H399.8v308.9v18.8v308.1h228.6V522.4z M471.6,312.4c0-25.1,20.3-45.4,45.4-45.4\n' +
            '\tc25.1,0,45.4,20.3,45.4,45.4c0,25.1-20.3,45.4-45.4,45.4C492,357.7,471.6,337.4,471.6,312.4 M471.6,465.1\n' +
            '\tc0-25.1,20.3-45.4,45.4-45.4c25.1,0,45.4,20.3,45.4,45.4c0,25.1-20.3,45.4-45.4,45.4C492,510.4,471.6,490.1,471.6,465.1\n' +
            '\t M888.7,522.4v-18.8V194.6H660.1v308.9v18.8v308.1h228.6V522.4z M732,312.4c0-25.1,20.3-45.4,45.4-45.4c25.1,0,45.4,20.3,45.4,45.4\n' +
            '\tc0,25.1-20.3,45.4-45.4,45.4C752.3,357.7,732,337.4,732,312.4 M732,465.1c0-25.1,20.3-45.4,45.4-45.4c25.1,0,45.4,20.3,45.4,45.4\n' +
            '\tc0,25.1-20.3,45.4-45.4,45.4C752.3,510.4,732,490.1,732,465.1 M79.4,129.5v766.1h869.3V129.5H79.4z M935.5,879.1h-843v-733h843\n' +
            '\tV879.1z',

          jds6000: 'path://M83.4,209v606.1h856.1V209H83.4z M926.5,802H96.4V222.1h830.2V802z M322.2,273.1h-10.2h-168v217h168h10.2h167.5v-217H322.2z\n' +
            '\t M261.7,423.8c-25.1,0-45.4-20.3-45.4-45.4c0-25.1,20.3-45.4,45.4-45.4c25,0,45.3,20.3,45.4,45.4\n' +
            '\tC307.1,403.5,286.8,423.8,261.7,423.8z M322.2,534.1h-10.2h-168v217h168h10.2h167.5v-217H322.2z M261.7,684.9\n' +
            '\tc-25.1,0-45.4-20.3-45.4-45.4c0-25.1,20.3-45.4,45.4-45.4c25,0,45.3,20.3,45.4,45.4C307.1,664.5,286.8,684.9,261.7,684.9z\n' +
            '\t M711.4,534.1h-10.2h-168v217h168h10.2h167.5v-217H711.4z M650.9,684.9c-25.1,0-45.4-20.3-45.4-45.4c0-25.1,20.3-45.4,45.4-45.4\n' +
            '\tc25,0,45.3,20.3,45.4,45.4C696.4,664.5,676.1,684.9,650.9,684.9z M711.4,273.1h-10.2h-168v217h168h10.2h167.5v-217H711.4z\n' +
            '\t M650.9,423.8c-25.1,0-45.4-20.3-45.4-45.4c0-25.1,20.3-45.4,45.4-45.4c25,0,45.3,20.3,45.4,45.4\n' +
            '\tC696.4,403.5,676.1,423.8,650.9,423.8z',
        },
        // 静态数据 end

        // echarts背景色
        echartsBackgroudColor: '#232629',

        // 拓扑上图标颜色和状态
        iconColor: ['#25a5c5', '#c30d23', '#9fa0a0', '#fff'],
        iconStatus: ['正常', '异常', '离线', '未知'],

        hostTopologyConf: {
          name: "会议拓扑",
          chartRenderMethod: "hostTopology",
          dataRenderMethod: "hostTopology",
          options: {}
        },
      }
    },
    methods: {
      // emit 函数
      emitSelect(v) {
        this.$emit('select', v)
      },
      // 对外提供的方法
      chartsResize() {
        this.$refs[this.ChartID].chartsResize()
      },
      // chart初始化
      async renderChartInit(chartConf, isNewChart = true) {
        this.chartRenderStatu = true
        let defaultConf = {
          echartsBackgroudColor: this.echartsBackgroudColor,
          colorCustomer: this.colorCustomer,
          colorCustomerRGBA: this.colorCustomerRGBA,
        }
        // 根据chartConf.chartRenderMethod判断chart渲染方法
        let renderChartTypeMethod = {
          'hostTopology': this.renderChartTypeHostTopology, //会议拓扑chart
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

      // chart渲染start：主机拓扑chart
      async renderChartTypeHostTopology(defaultConf, chartConf, renderChartDataMethod, isNewChart) {
        // 会议信息终端参会chart options
        let chartOptions = {
          backgroundColor: defaultConf.echartsBackgroudColor,
          scaleLimit: {
            min: 0.7,
          },
          tooltip: {
            enterable: true,
            hideDelay: 300,
            padding: [18, 14],
            backgroundColor: '#141414',
            borderColor: '#383b3c',
            borderWidth: 1,
            textStyle: {
              color: '#9ca9b1',
            },
            formatter: (params, ticket, callback) => {
              let bd = ''
              if (params.dataType === 'edge') {  // 如果是连线
                return null
                // return this.chartHostTip(params.value.s, ticket, callback)
              } else {  // 如果是图标
                if (params.data.category === "机房") {
                  let textList = [
                    {left: '机房名称', right: params.value.room_name},
                  ]
                  bd = this.renderTooltip(textList)
                } else {  // 如果是服务器或机框
                  return this.chartHostTip(params.value, ticket, callback)
                }
              }
              return bd
            },
          },
          series: [
            {
              name: 'HostTopology',
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
                    let index = params.data.value.status || 0
                    return this.iconColor[index]
                  },
                  opacity: 1,
                }
              },
              label: {
                show: true,
                position: 'top',
                formatter: (params) => {
                  return params.value.devName
                }
              },
              lineStyle: {
                color: '#25a5c5',
                width: 2,
                curveness: 0
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
          this.chartBaseInstance.setOption(chartOptions, true)
          this.chartBaseInstance.on('click', async (params) => {
            if (params.dataType === 'edge') {
              this.chartHostClick(params.value.s)
            }
            else if (params.data.category === '服务器') {
              this.chartHostClick(params.value)
            }
          });
        }
        // end判断是否是新的一张表，若是，则重新渲染整张表，否，则只渲染数据

        let dataMR = await this.renderDataMachineRoom()
        await this.renderDataDevRoom()
      },
      // chart渲染start：主机拓扑chart end

      // 机房数据渲染
      async renderDataMachineRoom() {
        if (!this.urlParams.domain_moid) return false
        let params = {domain_moid: this.urlParams.domain_moid}
        let machineRoomData = await this.$api.hostManageApi.hostGroups(params)
        let selectMachineRoom = machineRoomData.info.find(i => i.room_moid === this.urlParams.room_moid)
        if (selectMachineRoom) machineRoomData = [selectMachineRoom]

        let machineRoomLen = machineRoomData.length
        // let temInteractive = []
        let renderMachineRoomData = machineRoomData.map((item, index) => {
          let coordinate = this.calculationMRCoordinate(index, index, machineRoomLen, 110)
          item.devName = item.room_name
          let tempD = {
            name: item.room_moid,
            x: coordinate[0],
            y: coordinate[1],
            // fixed:true,
            symbolKeepAspect: true,
            category: '机房',
            value: item,
            symbol: this.iconPath.pathMachineRoom,
            symbolSize: 30,
          }

          return tempD
        })
        this.MachineRoomDataCache = renderMachineRoomData
        // return [renderMachineRoomData,temInteractive]
      },

      // 服务器数据渲染
      async renderDataDevRoom() {
        let renderDataDev = []
        let renderDataDevLink = []
        if (this.MachineRoomDataCache.length > 0) {
          //遍历机房
          for (let machineRoom of this.MachineRoomDataCache) {
            let start = 0
            let count = 30
            let temCacheLength = 30
            let hostCache = []  // 此机房下所有服务器列表
            while (temCacheLength >= count) {  // 循环查询此机房下所有服务器
              let params = {
                domain_moid: this.urlParams.domain_moid,
                room_moid: machineRoom.value.room_moid,
                query: this.urlParams.query,
                start: start,
                count: count,
              }
              let res = await this.$api.hostManageApi.hostList(params)

              let hostList = res.data
              temCacheLength = hostList.length
              start = start + count
              hostCache = hostCache.concat(hostList)
            }

            let uniqueDevList = hostCache.map(i => {
              i.devID = i.frame_moid || i.moid
              i.devName = i.frame_name || i.name
              return i.devID
            })
            uniqueDevList = [...new Set(uniqueDevList)]
            // console.log(uniqueDevList)
            // return false

            let devLen = uniqueDevList.length
            if (devLen > 0) {
              let center = [machineRoom.x, machineRoom.y]
              let radius = 50 / (Math.ceil(devLen / 6) + 1)
              let count = devLen > 6 ? 6 : devLen
              // 遍历服务器
              uniqueDevList.forEach((devID, index) => {
                // center,radius,index,total,count,range
                let coordinate = this.calculationCRCoordinate(center, radius, index, devLen, count, radius)
                let value = hostCache.filter(i => i.devID === devID)
                let devType = value[0].frame_type || value[0].machine_type
                let status = value.map(i => i.status).includes(1) ? 1 : 0
                let devData = {
                  devID: devID,
                  devName: value[0].devName,
                  devType: devType,
                  status: status,
                  value: value
                }
                let tempD = {
                  name: devID,
                  x: coordinate[0],
                  y: coordinate[1],
                  // fixed:true,
                  category: '服务器',
                  value: devData,
                  symbolKeepAspect: true,
                  symbol: this.iconPath[devType] || this.iconPath['dev'],
                  symbolSize: 35,
                }
                renderDataDev.push(tempD)
                let tempDLink = {
                  source: devID,
                  target: machineRoom.name,
                  value: {
                    s: devData,
                    t: machineRoom.value,
                    type: 'devToMachineRoom'
                  }
                }
                renderDataDevLink.push(tempDLink)
              })
              // 遍历服务器 end
            }
          }
          //遍历机房 end
        }
        ;

        this.DevDataCache = renderDataDev
        this.interactiveDevDataCache = renderDataDevLink
        return [renderDataDev, renderDataDevLink]
      },

      // frame 组件相关函数
      tipFormatter(e, params, callback) {
        if (params) {
          let bd = ''
          let devData = params
          if (this.hostTipContent && devData.moid === this.hostTipContent.key) {
            this.setTipErrorButton(devData)
            return this.hostTipContent.content
          }
          if (this.hostTipTimeOut) {
            clearTimeout(this.hostTipTimeOut);
          }
          this.hostTipTimeOut = setTimeout(async () => {
            bd = await this.getHostTooltip(devData)
            this.setTipErrorButton(devData)
            callback(e, bd);
          }, 100)
          return "<div style='width: 40px;text-align:center; ' class='el-icon-loading'></div>"
        }
        return "空机框"
      },
      hostFrameClick(e, params) {
        if (!params) return false
        this.frameDialog = false
        this.emitSelect(params)
      },
      setContentClass(val) {
        let objStatuClass = {
          0: 'normal',
          1: 'error',
        }
        if (val) {
          return objStatuClass[val.status]
        }
      },
      // frame 组件相关函数 end

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

      // echarts图标（连线）点击
      chartHostClick(host) {
        if (this.frameTypeList.includes(host.devType)) { // 如果是机框类型
          this.frameData = []
          this.frameType = host.value[0].frame_type
          let frameSlot = {
            jd10000: {A: 14, B: 15},
            jd6000: {A: 6, B: 7},
          }
          let slotToIndex = frameSlot[this.frameType]
          host.value.forEach(i => {
            let index = slotToIndex && slotToIndex[i.frame_slot] ? slotToIndex[i.frame_slot] : parseInt(i.frame_slot) - 1
            this.$set(this.frameData, index, i)
          })
          // console.log(this.frameData)
          this.frameDialog = true
        } else {  // 如果是单台主机
          this.emitSelect(host.value[0])
        }
      },

      // echarts图标（连线）tip
      chartHostTip(host, ticket, callback) {
        let textList = []
        if (this.frameTypeList.includes(host.devType)) {  // 如果是机框类型
          textList = [
            {left: '机框名称', right: host.devName},
            {left: '机框类型', right: host.devType},
          ]
          return this.renderTooltip(textList)
        } else {  // 单台主机tip
          let devData = host.value[0]
          if (this.hostTipContent && devData.moid === this.hostTipContent.key) {
            this.setTipErrorButton(host.value[0])
            return this.hostTipContent.content
          }
          if (this.hostTipTimeOut) {
            clearTimeout(this.hostTipTimeOut);
          }
          this.hostTipTimeOut = setTimeout(async () => {
            let bd = await this.getHostTooltip(devData)
            this.domEchatsIsExist()
            this.setTipErrorButton(host.value[0])
            callback(ticket, bd);
          }, 100)
          return "<div style='width: 40px;text-align:center; ' class='el-icon-loading'></div>"
        }
      },

      // 绑定Tip里告警异常按钮的click
      setTipErrorButton(host) {
        if (this.errorButtonTipTimeOut) clearTimeout(this.errorButtonTipTimeOut)
        this.errorButtonTipTimeOut = setTimeout(() => {
          let buttonObj = document.getElementById("hostTopologyTipButton")
          if (buttonObj) {
            buttonObj.onclick = (e) => {
              this.alarmInfoRouter(host)
            }
          }
        }, 300)
      },

      //其他功能函数封装 start
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

      // tooltip渲染函数
      renderTooltip(textList) {
        let htmlContent = textList.map((item) => {
          let rightText = item.right
          if (item.left === '主机状态' && item.right === '异常') {
            rightText = '<button type="button" id="hostTopologyTipButton" class="ops-button-text error">' +
              '<span style="text-decoration: underline;">异常</span>' +
              '</button>'
          }
          return '<div class="host-topology-tootip-content--block">' +
            '<div class="content-left">' + item.left + '</div>' +
            '<div class="content-right">' + ':&nbsp' + rightText +
            '</div></div>'
        })
        return htmlContent.join('\n')
      },

      // 单台主机tip渲染
      async getHostTooltip(host) {
        let hostData = host
        await this.setHostDisk(hostData)
        await this.setHostOnLine(hostData)
        let textList = [
          {left: '主机名称', right: hostData.name},
          {left: 'IP地址', right: hostData.local_ip},
          {left: '主机类型', right: hostData.machine_type},
          {left: '主机状态', right: this.hostStatus[hostData.status]},
          {left: '工作模式', right: hostData.cluster || '----'},
          {left: '磁盘寿命', right: hostData.diskage},
          {left: '运行时间', right: hostData.uptime},
        ]
        this.hostTipContent = {
          key: hostData.moid,
          content: this.renderTooltip(textList)
        }
        return this.hostTipContent.content
      },
      // 单台主机数据：磁盘寿命
      async setHostDisk(host) {
        // 磁盘寿命
        let res = await this.$api.monitor.handlerGetAllDiskageNodeData(host.moid)
        let diskage = res.map(item => item["system.diskage.count"])
        let max = Math.max.apply(null, diskage)
        if (max && max !== -Infinity) {
          this.$set(host, "diskage", (max * 100).toFixed() + "%")
        } else {
          this.$set(host, "diskage", "该磁盘不支持寿命检测")
        }
      },
      // 单台主机数据：服务器运行时长
      async setHostOnLine(host) {
        await this.$api.monitor.getUptime(host.moid)
          .then(res => {
            let uptime = res.data.data["system.uptime.duration.ms"]
            if (uptime === -1 || uptime === undefined) {
              if (host.has_detail) {
                this.$set(host, "uptime", "异常")
              } else {
                this.$set(host, "uptime", "----")
              }
            } else {
              let time = this.timeMillisecondAnalysis(uptime)
              this.$set(host, "uptime", time)
            }
          })
      },
      //告警异常点击跳转
      alarmInfoRouter(row) {
        // console.log(row)
        this.$router.push({
          name: 'monitor-alarm',
          params: {
            type: 'alarmDev',
            urlParams: {
              search: row.name
            }
          }
        });
      },
      // 时间转换
      timeMillisecondAnalysis(val) {
        let temData;
        if (val > 31536000000) {
          temData = parseInt(val / 31536000000) + "年"
        } else if (val > 2592000000) {
          temData = parseInt(val / 2592000000) + "个月"
        } else if (val > 86400000) {
          temData = parseInt(val / 86400000) + "天"
        } else if (val > 3600000) {
          temData = parseInt(val / 3600000) + "小时"
        } else {
          temData = parseInt(val / 60000) + "分钟"
        }
        return temData
      },
      // 组件chart初始化
      init() {
        this.chartBaseInstance = this.$refs[this.ChartID].getChartInstance();
        let chartConf = this.hostTopologyConf
        if (chartConf) {
          this.renderChartInit(chartConf)
        }
      },
    },
    mounted() {
      this.init()
      // console.log('onload',this.urlParams.domain_moid)
    },
  }
</script>

<style>
  .area-host-topology {
    width: 100%;
    height: calc(100vh - 125px);
    box-sizing: border-box;
    position: relative;
    background: #232629;
  }

  .host-topology__lenged {
    z-index: 101;
    top: 20px;
    right: 20px;
    position: absolute;
  }

  .host-topology__lenged .legend-icon {
    width: 10px;
    height: 5px;
    border-radius: 1px;
    display: inline-block;
    vertical-align: 1px;
    margin-right: 4px;
  }

  .host-topology__lenged .legend-icon.info {
    background-color: #25a5c5;
  }

  .host-topology__lenged .legend-icon.alarm {
    background-color: #c30d23;
  }

  .host-topology__lenged .legend-text {
    font-size: 14px;
  }

  .host-topology-tootip-content--block {
    font-size: 14px;
    width: 100%;
    /*padding: 0 8px;*/
    box-sizing: border-box;
    text-align: left;
  }

  .host-topology-tootip-content--block .content-left {
    /*float: left;*/
    display: inline-block;
    text-align: right;
    width: 65px;
    /*width: calc(100% - 70px);*/
    /*text-align: left;*/
    /*width: 60%;*/
  }

  .host-topology-tootip-content--block .content-right {
    /*float: right;*/
    display: inline-block;
    /*max-width: 100px;*/
    text-align: left;
    padding-left: 10px;
  }
</style>
