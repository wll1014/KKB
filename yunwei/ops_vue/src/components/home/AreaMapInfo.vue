<template>
  <div id="component-map" class="theme-dark"
       style="position: relative;padding: 0 20px;box-sizing: border-box;background-color: #232629;height:100%;width: 100%;">

    <!--面包屑start-->
    <div style="height:100%;width: 100%" v-if="!isSetting">
      <div class="breadcrumb-map">
        <div style="font-size: 14px;color: #9ca9b1;display: inline-block;">电子地图</div>
        <div style="display: inline-block;height: 100%;width: 400px;margin-left: 28px;height: 13px;">
          <el-breadcrumb separator-class="el-icon-arrow-right">
            <el-breadcrumb-item v-for="item in breadcrumbMap" :key="item" @click.native="breadcrumbChangeMap(item)">
              {{item}}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
      </div>
      <!--面包屑end-->

      <!--地图上按钮组start-->
      <el-button class="map-button--setting" icon="ops-icons-bg icon-arrow-circle-setting"
                 @click='buttonHanderMap("setting")' circle></el-button>
      <div class="button-group-map">
        <el-button class="button-map" icon="ops-icons-bg icon-plus" @click='buttonHanderMap("enlarge")'></el-button>
        <el-button class="button-map" icon="ops-icons-bg icon-minus" @click='buttonHanderMap("narrow")'></el-button>
        <el-button class="button-map"
                   :icon="fullScreenStatu?'ops-icons-bg icon-fullscreen':'ops-icons-bg icon-fullscreen'"
                   @click='buttonHanderMap("fullScreen")'></el-button>
        <!--<el-button class="button-map" icon="el-icon-refresh" @click='buttonHanderMap("home")'></el-button>-->
      </div>
      <!--地图上按钮组end-->

      <!--地图echarts-->
      <div :id="chartID" :style="{height:'100%'}"></div>
      <!--地图echarts end-->

      <!--蒙版区域start-->
      <el-dialog
        title="电子地图配置"
        :visible.sync="dialogVisibleSetting"
        width="1020px"
        @close="exitSetting"
      >
        <div style="margin-top: 20px;">
          <GeoInfoMaintenance></GeoInfoMaintenance>
        </div>
        <div style="padding: 30px;text-align: center;box-sizing: border-box;">
          <span style="text-align: center;">
            <el-button @click="dialogVisibleSetting = false">确 定</el-button>
          </span>
        </div>
      </el-dialog>
      <!--蒙版区域end-->
    </div>


    <div style="height:100%;width: 100%" v-else>
      <GeoInfoMaintenance @back="exitSetting"></GeoInfoMaintenance>
    </div>
  </div>
</template>

<script>
  export default {
    components: {
      GeoInfoMaintenance: () => import('@/view/home/GeoInfoMaintenance.vue'),
    },
    data() {
      return {
        // 定时器实例
        timer: null,

        dialogVisibleSetting: false,
        // 全局数据
        dataMapGlobal: '',

        // 展示的地图
        mapGolablConfig: '',

        // 地图上图标颜色和状态
        iconColor: ['#22ac38', '#c30d23', '#9fa0a0', '#fff'],
        iconStatus: ['正常', '异常', '离线', '未知'],
        lineColor: ['#23acd4', '#c30d23'],

        // 数据的坐标维护
        dataGeoCoordMap: {},

        // 设备数据
        devDataCache: {},
        // 终端数据
        TerminalDataCache: {},
        // 外设数据
        peripheralDataCache: {},
        // 交互连线数据
        interactiveDataCache: [],
        //直辖市和特别行政区-只有二级地图，没有三级地图
        specialMap: ["北京", "天津", "上海", "重庆", "香港", "澳门"],

        // props
        chartID: "chartMap",

        // 面包屑数据
        breadcrumbMap: ['全国地图'],
        // 过滤项
        optionSelectedMapDomainType: '',
        optionsMapDomainType: '',
        optionSelectedMapHost: '',
        optionsMapHost: '',
        inputSearchFilter: '',

        // 是否是设置页面
        isSetting: false,
        // 是否全屏
        fullScreenStatu: false,

        // 当前连线tip的内容
        lineTipActive: null,
        lineTipRequestTimeOut: null,

        // 延迟绑定告警异常按钮的click事件
        tipErrorButtonTimeOut:null,

        // 表的实例化
        chartInstance: '',
        chartOption: {
          tooltip: {
            trigger: 'item',
            padding: [14, 14],
            backgroundColor: '#141414',
            borderColor: '#383b3c',
            borderWidth: 1,
            textStyle: {
              color: '#9ca9b1',
            },
            enterable: true,
            hideDelay: 300,
            transitionDuration: 0,
            extraCssText: 'z-index:100',
          },
          geo: {
            selectedMode: 'single',
            zoom: 1.2,
            scaleLimit: {
              min: 1,
            },
            // layoutCenter:['50%','50%'],
            label: {
              normal: {
                color: '#5d6266',
                show: true,
                fontSize: 12,
              },
              emphasis: {
                color: '#5d6266',
                show: true,
                fontSize: 12,
              }
            },
            roam: true,
            itemStyle: {
              normal: {
                areaColor: 'rgba(51, 69, 89, .5)',
                // areaColor: 'rgba(0, 0, 0, 0)',
                borderColor: '#516a89',
                // borderColor: '#2269a7',
              },
              emphasis: {
                areaColor: 'rgba(37, 43, 61, .5)'
              }
            }
          },
          series: [{
            name: 'dev',
            type: 'scatter',
            zlevel: 20,
            coordinateSystem: 'geo',
            symbolSize: 14,
            // symbol: this.dataMapGlobal.iconPath["dev"],
            // symbol:'image://http://172.16.80.93:8000/static/IDC.png',
            symbolRotate: 0,
            symbolKeepAspect: true,
            label: {
              normal: {
                formatter: '{b}',
                position: 'right',
                show: false
              },
              emphasis: {
                show: true
              }
            },
            itemStyle: {
              normal: {
                color: (params) => {
                  // console.log(params.data)
                  return this.iconColor[params.data.value[2].status]
                  // return 'fff'
                },
                opacity: 1,
              }
            },
            tooltip: {
              formatter: (params) => {
                // console.log(params)
                let machineNum = params.value[2].machine_num < 0 ? '无' : params.value[2].machine_num
                let textList = [
                  {left: '机房名称', right: params.value[2].name},
                  {left: '所属域', right: params.value[2].platform_name},
                  {left: '服务器数量', right: machineNum},
                  {left: '状态', right: this.iconStatus[params.data.value[2].status]}
                ]
                this.setTipErrorButton(params)
                let bd = this.renderTooltip(textList)
                return bd
              },
            },
          }, {
            name: "mt",
            type: 'scatter',
            coordinateSystem: 'geo',
            zlevel: 20,
            // rippleEffect: { //涟漪特效
            //   period: 4, //动画时间，值越小速度越快
            //   brushType: 'stroke', //波纹绘制方式 stroke, fill
            //   scale: 2 //波纹圆环最大限制，值越大波纹越大
            // },
            // symbol: 'circle',
            // symbol:this.dataMapGlobal.iconPath["terminal"],
            symbolSize: 14,
            symbolKeepAspect: true,
            itemStyle: {
              normal: {
                show: true,
                color: (params) => {
                  // console.log(params.data)
                  return this.iconColor[params.data.value[2].status]
                  // return 'fff'
                },
              }
            },
            tooltip: {
              formatter: (params) => {
                // console.log(params)data.audio.lost!==undefined ? data.audio.lost.toFixed(1) + ' %' : ''
                let textList = [
                  {left: '终端名称', right: params.value[2].name},
                  {left: '所属用户域', right: params.value[2].user_domain_name},
                  {left: '终端IP', right: params.value[2].mtip ? params.value[2].mtip : '无数据'},
                  {left: '终端型号', right: params.value[2].mttype ? params.value[2].mttype : '无数据'},
                  {left: '状态', right: this.iconStatus[params.data.value[2].status]}
                ]
                this.setTipErrorButton(params)
                let bd = this.renderTooltip(textList)
                return bd
              },
            },
          }, {
            name: 'peripheral',
            type: 'scatter',
            zlevel: 20,
            coordinateSystem: 'geo',
            symbolSize: 14,
            // symbol: this.dataMapGlobal.iconPath["dev"],
            // symbol:'image://http://172.16.80.93:8000/static/IDC.png',
            symbolRotate: 0,
            symbolKeepAspect: true,
            label: {
              normal: {
                formatter: '{b}',
                position: 'right',
                show: false
              },
              emphasis: {
                show: true
              }
            },
            itemStyle: {
              normal: {
                color: (params) => {
                  // console.log(params.data)
                  return this.iconColor[params.data.value[2].status]
                  // return 'fff'
                },
                opacity: 1,
              }
            },
            tooltip: {
              formatter: (params) => {
                let textList = [
                  {left: '服务器名称', right: params.value[2].name},
                  {left: '状态', right: this.iconStatus[params.data.value[2].status]}
                ]
                let bd = this.renderTooltip(textList)
                return bd
              },
            },
          }, {
            name: "link",
            type: 'lines',
            zlevel: 5,
            coordinateSystem: 'geo',
            lineStyle: {
              normal: {
                color: (params) => {
                  // console.log(params.data)
                  return this.lineColor[params.data.status]
                },
                width: 2,
                curveness: 0.4,
                // opacity:0.4,
              }
            },
            tooltip: {
              // show:false,
              formatter: (params, ticket, callback) => {
                // console.log(params)
                let type = params.value.detail.link_type
                let textList = []
                if (type === 0) {
                  if (this.lineTipActive && this.lineTipActive.src === params.value.src_moid) {
                    return this.lineTipActive.content
                  }
                  if (this.lineTipRequestTimeOut) {
                    clearTimeout(this.lineTipRequestTimeOut);
                  }
                  this.lineTipRequestTimeOut = setTimeout(() => {
                    this.$api.homePage.getMapLinkDetail(params.value.detail.mt_e164)
                      .then(res => {
                        if (res.data.success) {
                          let data = res.data.data
                          textList = [
                            {left: '终端名称', right: params.value.detail.user_name},
                            {left: '会议名称', right: data.conf_name},
                            {
                              left: '音频丢包率',
                              right: data.audio.lost !== undefined ? data.audio.lost.toFixed(1) + ' %' : '无数据'
                            },
                            {
                              left: '音频码率',
                              right: data.audio.rate !== undefined ? data.audio.rate.toFixed(2) + ' kbps' : '无数据'
                            },
                            {
                              left: '主视频丢包率',
                              right: data.video.lost !== undefined ? data.video.lost.toFixed(2) + ' %' : '无数据'
                            },
                            {
                              left: '主视频码率',
                              right: data.video.rate !== undefined ? data.video.rate.toFixed(2) + ' kbps' : '无数据'
                            },
                          ]
                          let bd = this.renderTooltip(textList)
                          this.lineTipActive = {
                            src: params.value.src_moid,
                            content: bd
                          }
                          setTimeout(() => {
                            this.lineTipActive = null
                          }, 30000);
                          callback(ticket, bd);
                        } else {
                          return "未获取到相关数据"
                        }
                      })
                  }, 300);
                } else {
                  return params.data.fromName + " 至 " + params.data.toName
                }
                return "<div style='width: 40px;text-align:center; ' class='el-icon-loading'></div>"
              },
            },
            // data: this.convertData(dataInteractive,this.dataGeoCoordMap)
          }, {
            name: "linkEffect",
            type: 'lines',
            zlevel: 10,
            coordinateSystem: 'geo',
            effect: {
              show: true,
              period: 6,
              constantSpeed: 30,
              trailLength: 0.1,
              symbolSize: 3,
              color: '#fff',
            },
            lineStyle: {
              color: (params) => {
                // console.log(params.data)
                return this.lineColor[params.data.status]
              },
              width: 0,
              curveness: 0.4,
            },
            tooltip: {
              show: false,
            },
          }],
        },
      }
    },
    computed: {
      // 监听左侧导航栏变化
      isCollapse() {
        return this.$store.getters.getsiderbarCollapseStatu
      },
      //监听数据变化
      dataChange() {
        return [
          this.devDataCache,
          this.TerminalDataCache,
          this.peripheralDataCache,
          this.interactiveDataCache[0],
          this.interactiveDataCache[1],
        ]
      },
    },
    watch: {
      // 写法二：配合computed实现监听
      isCollapse(newStatu, oldStatu) {
        this.chartsResize()
      },
      dataChange(newVal) {
        this.domEchatsIsExist()
        this.chartInstance.setOption({
          // legend: legendConf,
          series: newVal
        })
      },
    },
    methods: {
      // 面包屑点击操作
      breadcrumbChangeMap(val) {
        // console.log(val)
        let mapFullName = val
        let mapName = ''
        if (mapFullName === "全国地图") {
          mapName = "china"
          this.breadcrumbMap = ["全国地图"]
        } else if (mapFullName in this.dataMapGlobal.cityMap) {
          mapName = mapFullName
          this.$set(this.breadcrumbMap, 2, mapFullName)
        } else {
          for (let i in this.dataMapGlobal.provinces) {
            // console.log(i)
            if (this.dataMapGlobal.provinces[i].fullName === mapFullName) {
              mapName = i
              this.$set(this.breadcrumbMap, 1, this.dataMapGlobal.provinces[i].fullName)
              this.$delete(this.breadcrumbMap, 2)
              break;
            }
          }
          ;
        }

        if (mapName) {
          this.renderMap(mapName)
        }
      },
      // 设置页面返回地图
      exitSetting() {
        // this.isSetting=false
        this.initMounted()
      },
      // 地图按钮操作
      buttonHanderMap(operation) {
        let options = this.chartInstance.getOption();
        let zoomNew = options.geo[0].zoom
        switch (operation) {
          case "enlarge":
            this.chartInstance.setOption({
              // legend:{show:false}, //此配置必须在地图重新绘制前取消掉
              geo: {
                zoom: zoomNew + 0.2,
              },
            })

            break;
          case "narrow":
            if (zoomNew > 1) {
              this.chartInstance.setOption({
                // legend:{show:false}, //此配置必须在地图重新绘制前取消掉
                geo: {
                  zoom: zoomNew - 0.2,
                },
              })
            }
            break;
          case "fullScreen":
            if (this.isFullscreen()) {
              // this.fullScreenStatu=false
              this.exitFullscreen()
            } else {
              let full = document.getElementById("component-map");
              this.launchIntoFullscreen(full)
              // this.fullScreenStatu=true
            }
            // let full = document.getElementById("component-map");
            // this.launchIntoFullscreen(full)
            break;
          case "setting":
            this.clearTimer()
            // window.removeEventListener("resize",this.chartsResize)
            // this.isSetting=true
            this.dialogVisibleSetting = true
            break;
          case "home":
            this.getData()
          // this.renderMap("china")
        }
        // this.renderMapData(1)
        this.domEchatsIsExist()
        this.chartInstance.setOption({
          // legend: legendConf,
          series: this.dataChange
        })
      },

      // 首次加载地图
      getData() {
        let initMap = this.mapGolablConfig
        // 获取默认地图
        // let mapName="china"
        // let mapPath="../../../static/json/china.json"
        let mapName = ""
        this.breadcrumbMap = ["全国地图"]
        let mapNameLoadMap = {
          1: () => {
            mapName = "china"
          },
          2: () => {
            for (let i in this.dataMapGlobal.provinces) {
              // console.log(i)
              if (this.dataMapGlobal.provinces[i].fullName === initMap[1]) {
                mapName = i
                this.$set(this.breadcrumbMap, 1, this.dataMapGlobal.provinces[i].fullName)
                break;
              }
            }
          },
          3: () => {
            mapName = initMap[2]
            this.$set(this.breadcrumbMap, 1, initMap[1])
            this.$set(this.breadcrumbMap, 2, initMap[2])
          },
        }
        // if(initMap.length===3){
        //   mapName=initMap[2]
        // }
        mapNameLoadMap[initMap.length]()
        // console.log(initMap.length)
        // let mapPath="../../../static/json/province/guizhou.json"
        // console.log(this.dataMapGlobal.provinces)
        // 地图拓扑配置
        this.chartInstance.on('geoselectchanged', params => {
          // console.log(params)

          this.renderMap(params.batch[0].name)
          // let temdata=this.chartInstance.getOption()
          // console.log(temdata.geo[0].center);

        })

        // // 图标点击配置
        this.chartInstance.on('click', (params) => {
          if (params.seriesType && params.seriesType === "scatter") {
            // console.log(params,params.value[2].type,this.interactiveDataCache[0].data[0].value);
            let type = params.value[2].type
            if (type === '机房') {
              if (params.value[2].machine_num < 0) {
                this.$message("此类型机房不支持跳转");
                return false
              }
              this.$router.push({  // 跳转至机房
                name: 'hostmanage-hostinfo',
                // path:chartConf.routerPush
                params: {
                  domainMoid: params.value[2].platform_moid,
                  roomMoid: params.value[2].moid
                }
              });
            }
            else if (type === '终端') {
              let confList = this.interactiveDataCache[0] ? this.interactiveDataCache[0].data : []
              let mtInConf = confList.find(item => item.value.src_moid === params.value[2].moid)

              if (!mtInConf) {
                this.$message("终端不在会议中，不支持跳转");
                return false
              }
              // console.log(mtInConf.value.detail,mtInConf.value.detail.conf_e164,mtInConf.value.detail.mt_e164)
              this.$router.push({  // 跳转至会议中的终端
                name: 'monitor-meetinginfo',
                // path:chartConf.routerPush
                params: {
                  module: 'mtInfo',
                  params: {
                    conf_id: mtInConf.value.detail.conf_e164,
                    mt_id: mtInConf.value.detail.mt_e164,
                    conf_type: 3,
                    conf_status: 1,
                  }
                }
              });
            }
          }
          ;
        })

        // 第一次载入地图
        this.renderMap(mapName)
      },


      // 地图渲染
      async renderMap(mapName) {
        this.clearTimer()
        // 获取map信息
        let mapPath = ''

        if (mapName in this.dataMapGlobal.provinces) {
          // console.log(this.dataMapGlobal.provinces[mapName].fullName)
          mapPath = "../../../ops/static/json/province/" + this.dataMapGlobal.provinces[mapName].jsonName + ".json"
          this.$set(this.breadcrumbMap, 1, this.dataMapGlobal.provinces[mapName].fullName)
          this.$delete(this.breadcrumbMap, 2)
        } else if (mapName in this.dataMapGlobal.cityMap) {
          // console.log(this.dataMapGlobal.cityMap[mapName])
          // mapName = params.batch[0].name
          this.$set(this.breadcrumbMap, 2, mapName)
          mapPath = "../../../ops/static/json/city/" + this.dataMapGlobal.cityMap[mapName] + ".json"
        } else if (mapName === "china") {
          mapPath = "../../../ops/static/json/china.json"
        } else {
          return "no map"
        }

        await this.$api.homePage.getMapJson(mapPath)
          .then(res => {
            // console.log(res.data)

            this.domEchatsIsExist()

            this.$echarts.registerMap(mapName, res.data);
            this.chartInstance.setOption({
              // legend:{show:false}, //此配置必须在地图重新绘制前取消掉
              geo: {
                map: mapName,
                center: null,
              },
            })
          })
        // 必须要在地图渲染完成后渲染
        this.renderMapData(1)
        this.setTimer()
      },

      // 地图数据渲染
      async renderMapData(dataFilter) {
        // this.renderMapDataRoom()
        // this.renderMapDataTerminal()
        // await this.renderMapDataPeripheral()
        let [res1, res2, res3] = await Promise.all([this.renderMapDataRoom(), this.renderMapDataTerminal(), this.renderMapDataPeripheral()])
        this.renderMapDataInteractive()
      },


      // 机房数据渲染
      async renderMapDataRoom() {
        let start = 0
        let count = 20
        let temCacheLength = 20  //记录每次请求返回的长度，当长度小于count，则不继续请求
        let temCache = []
        while (temCacheLength >= count) {
          let params = {
            start: start,
            count: count
          }
          let dataLocationMachineRoom = await this.$api.homePage.getMapRoomInfo()
          temCacheLength = dataLocationMachineRoom.length
          start = start + count
          let itemDev = dataLocationMachineRoom.map((dataItem) => {
            this.$set(this.dataGeoCoordMap, dataItem.moid, dataItem)
            // console.log(dataItem)
            dataItem['type'] = '机房'
            return {
              // name: dataItem.name,
              value: this.dataGeoCoordMap[dataItem.moid].coordinate.concat([dataItem])
            };
          })
          temCache = temCache.concat(itemDev)

          this.devDataCache = {
            name: 'dev',
            symbol: this.dataMapGlobal.iconPath["dev"],
            data: temCache
          }

          // let seriesDev = [{
          //   name: 'dev',
          //   symbol: this.dataMapGlobal.iconPath["dev"],
          //   data: temCache
          // }];
          //
          // this.domEchatsIsExist()
          //
          // this.chartInstance.setOption({
          //   // legend: legendConf,
          //   series: seriesDev
          // })
        }
      },
      // 终端数据渲染
      async renderMapDataTerminal() {
        let start = 0
        let count = 30
        let temCacheLength = 30
        let temCache = []
        while (temCacheLength >= count) {
          let params = {
            start: start,
            count: count
          }
          let dataLocationTerminal = await this.$api.homePage.getMapTerminalsInfo(params)
          temCacheLength = dataLocationTerminal.length
          start = start + count
          // dataLocationTerminal.forEach((item)=>{
          //   if(item){
          //     this.$set(this.dataGeoCoordMap,item.moid,item)
          //   }
          // })
          let itemTerminal = dataLocationTerminal.map((dataItem) => {
            this.$set(this.dataGeoCoordMap, dataItem.moid, dataItem)
            // console.log(dataLocationTerminal)
            dataItem['type'] = '终端'
            return {
              // name: dataItem.name,
              value: this.dataGeoCoordMap[dataItem.moid].coordinate.concat([dataItem])
            };
          })

          temCache = temCache.concat(itemTerminal)

          this.TerminalDataCache = {
            name: 'mt',
            symbol: this.dataMapGlobal.iconPath["terminal"],
            data: temCache
          }

        }
      },
      // 外设服务器渲染
      async renderMapDataPeripheral() {
        let start = 0
        let count = 20
        let temCacheLength = 20
        let temCache = []
        while (temCacheLength >= count) {
          let params = {
            start: start,
            count: count
          }

          let dataLocationPeripheral = await this.$api.homePage.getMapPeripheralInfo()
          temCacheLength = dataLocationPeripheral.length
          start = start + count

          let itemPeripheral = dataLocationPeripheral.map((dataItem) => {
            this.$set(this.dataGeoCoordMap, dataItem.moid, dataItem)
            // console.log(dataItem)
            dataItem['type'] = '外设服务器'
            return {
              // name: dataItem.name,
              value: this.dataGeoCoordMap[dataItem.moid].coordinate.concat([dataItem])
            };
          })
          temCache = temCache.concat(itemPeripheral)

          this.peripheralDataCache = {
            name: 'peripheral',
            symbol: this.dataMapGlobal.iconPath["peripheral"],
            data: temCache
          }

        }
      },
      // 数据连接渲染
      async renderMapDataInteractive() {
        let dataInteractive = await this.$api.homePage.getMapLinksInfo()
        if (!dataInteractive) {
          console.log("获取Map上连接信息失败")
          return false
        }

        let linkData = this.convertData(dataInteractive, this.dataGeoCoordMap)

        // 此段代码为在连线状态下，离线终端设置为在线
        linkData.forEach(item => {
          let mtIndex = this.TerminalDataCache.data.findIndex(i => {
            if (i.value[2].moid === item.value.src_moid) return i
          })
          if (mtIndex !== -1) {
            let newMtInfo = {...this.TerminalDataCache.data[mtIndex]}
            newMtInfo.value[2].status = newMtInfo.value[2].status === 2 ? 0 : newMtInfo.value[2].status
            this.$set(this.TerminalDataCache.data, mtIndex, newMtInfo)
          }
        })
        // 此段代码为在连线状态下，离线终端设置为在线end

        this.interactiveDataCache = [{
          name: "link",
          data: linkData
        }, {
          name: "linkEffect",
          data: linkData
        },]

      },

      // 数据转换成echarts样式
      convertData(data, geoData) {
        let res = [];
        for (let i = 0; i < data.length; i++) {
          let dataItem = data[i];
          let fromCoord = null
          let toCoord = null

          if (geoData[dataItem.src_moid] && geoData[dataItem.dest_moid]) {
            fromCoord = geoData[dataItem.src_moid].coordinate;
            toCoord = geoData[dataItem.dest_moid].coordinate;
          }

          if (fromCoord && toCoord) {
            res.push({
              fromName: geoData[dataItem.src_moid].name,
              toName: geoData[dataItem.dest_moid].name,
              value: dataItem,
              status: dataItem.status,
              coords: [fromCoord, toCoord]
            });
          }
        }
        return res;
      },

      // tooltip渲染函数
      renderTooltip(textList) {
        let htmlContent = textList.map((item) => {
          let rightText = item.right
          if (item.left === '状态' && item.right === '异常') {
            rightText = '<button type="button" id="mapTipErrorButton" class="ops-button-text error">' +
              '<span style="text-decoration: underline;">异常</span>' +
              '</button>'
          }
          return '<div class="map-tootip-content--block">' +
            '<div class="map-tootip-content-left">' + item.left + '</div>' +
            '<div class="map-tootip-content-right">' + ':&nbsp' + rightText +
            '</div></div>'
        })
        return htmlContent.join('\n')
      },

      // 绑定Tip里告警异常按钮的click
      setTipErrorButton(v) {
        if (this.tipErrorButtonTimeOut) clearTimeout(this.tipErrorButtonTimeOut)
        this.tipErrorButtonTimeOut = setTimeout(() => {
          let buttonObj = document.getElementById("mapTipErrorButton")
          if (buttonObj) {
            buttonObj.onclick = (e) => {
              if(v.seriesName === 'mt'){
                this.routerToMtAlarm(v.value[2])
              }else if(v.seriesName === 'dev'){
                this.routerToDevAlarm(v.value[2])
              }
            }
          }
        }, 300)
      },

      // 调整至终端告警
      routerToMtAlarm(mt){
        this.$router.push({
          name: 'monitor-alarm',
          params: {
            type: 'alarmMt',
            urlParams: {
              search: mt.name
            }
          }
        });
      },
      routerToDevAlarm(dev){
        // console.log(dev)
      },
      // resize函数
      chartsResize() {
        this.chartInstance.resize()
      },

      // 图表销毁
      chartDispose() {
        if (this.chartInstance) {
          this.chartInstance.dispose()
        }
      },

      // 定时器函数start
      // 设置定时器
      setTimer(interver = 60, range = 3600000) {
        this.clearTimer();
        this.timer = setInterval(() => {
          // console.log(range)
          // console.log(interver)
          this.renderMapData()
        }, interver * 1000)
      },
      // 清除定时器
      clearTimer() {
        clearInterval(this.timer);
        this.timer = null;
      },
      // 定时器函数end

      // 全屏和退出全屏方法封装
      launchIntoFullscreen(element) {
        if (element.requestFullscreen) {
          element.requestFullscreen();
        }
        else if (element.mozRequestFullScreen) {
          element.mozRequestFullScreen();
        }
        else if (element.webkitRequestFullscreen) {
          element.webkitRequestFullscreen();
        }
        else if (element.msRequestFullscreen) {
          element.msRequestFullscreen();
        }
      },

      exitFullscreen() {
        if (document.exitFullscreen) {
          document.exitFullscreen();
        } else if (document.mozCancelFullScreen) {
          document.mozCancelFullScreen();
        } else if (document.webkitExitFullscreen) {
          document.webkitExitFullscreen();
        }
      },

      // 非F11全屏状态监测
      isFullscreen() {
        return document.fullscreenElement ||
          document.msFullscreenElement ||
          document.mozFullScreenElement ||
          document.webkitFullscreenElement || false;
      },

      // 全屏监听方法
      fullscreenchange() {
        if (this.isFullscreen()) {
          this.fullScreenStatu = true
        } else {
          this.fullScreenStatu = false
        }
      },
      // 全屏和退出全屏方法封装end

      // 判断echatrs 实例是否还在
      domEchatsIsExist() {
        if (this.chartInstance) {
          let isExistence = this.chartInstance.getDom().attributes
          // let aaa = this.chartBaseInstance
          if (isExistence._echarts_instance_ && isExistence._echarts_instance_.value) {
          } else {
            // console.log("map echarts instance no exist ")
            throw "map echarts instance no exist "
          }
        }
        else {
          // console.log("map echarts dom no exist ")
          throw "map echarts dom no exist "
        }
      },

      // 载入初始化
      async initMounted() {
        this.dataMapGlobal = await this.$api.homePage.getJsonFileSync("DataMapGlobal")

        this.chartInstance = this.$echarts.init(document.getElementById(this.chartID));
        // 获取初始地图
        let baseConfig = await this.$api.homePage.getMapBaseConfig()
        if (baseConfig && baseConfig.length > 0) {
          baseConfig = baseConfig[0]
          if (baseConfig.city) {
            let mapProvince = baseConfig.province.name
            let mapCity = baseConfig.city.name
            this.mapGolablConfig = ["全国地图", mapProvince, mapCity]
          } else if (baseConfig.province) {
            let mapProvince = baseConfig.province.name
            this.mapGolablConfig = ["全国地图", mapProvince]
          } else {
            this.mapGolablConfig = ["全国地图"]
          }
        } else if (baseConfig.length === 0) {
          this.mapGolablConfig = ["全国地图"]
        } else {
          console.log("地图初始化失败")
        }
        // console.log(this.mapGolablConfig)
        // 获取初始地图end
        this.domEchatsIsExist()
        // if(this.chartBaseInstance){
        //   let isExistence = this.chartBaseInstance.getDom().attributes
        //   // let aaa = this.chartBaseInstance
        //   if(isExistence._echarts_instance_ && isExistence._echarts_instance_.value){
        //     console.log(isExistence._echarts_instance_.value)
        //   }else{
        //     console.log("no echarts ............")
        //     return false
        //   }
        // }
        // else {
        //   console.log("no dom ............")
        //   return false
        // }
        this.chartInstance.setOption(this.chartOption)
        this.getData()
        window.addEventListener("resize", this.chartsResize)

        // 监测全屏
        document.addEventListener("fullscreenchange", this.fullscreenchange);
        document.addEventListener("mozfullscreenchange", this.fullscreenchange);
        document.addEventListener("webkitfullscreenchange", this.fullscreenchange);
        document.addEventListener("msfullscreenchange", this.fullscreenchange);
      },

    },
    mounted() {
      this.initMounted()

    },
    beforeDestroy() {
      this.clearTimer()
      window.removeEventListener("resize", this.chartsResize)
      document.removeEventListener("fullscreenchange", this.fullscreenchange);
      document.removeEventListener("mozfullscreenchange", this.fullscreenchange);
      document.removeEventListener("webkitfullscreenchange", this.fullscreenchange);
      document.removeEventListener("msfullscreenchange", this.fullscreenchange);
      this.chartDispose()
    },
  }
</script>

<style>
  .button-group-map {
    position: absolute;
    bottom: 10px;
    right: 10px;
    width: 30px;
    z-index: 100;
  }

  .button-map {
    width: 26px;
    height: 26px;
    cursor: pointer;
  }

  .button-map .iconfont {
    font-size: 12px;
  }

  .button-group-map .el-button {
    margin-left: 0px;
    margin-bottom: 1px;
    padding: 0px;
    cursor: pointer;
  }

  .breadcrumb-map {
    position: absolute;
    top: 11px;
    left: 20px;
    z-index: 100;
    vertical-align: top;
  }

  .breadcrumb-map .el-breadcrumb__inner {
    color: #4a4e52;
    cursor: pointer;
  }

  .breadcrumb-map .el-breadcrumb__separator {
    color: #4a4e52;
    font-size: 14px;
  }

  .breadcrumb-map .el-breadcrumb__item:last-child .el-breadcrumb__inner,
  .breadcrumb-map .el-breadcrumb__item:last-child .el-breadcrumb__inner a,
  .breadcrumb-map .el-breadcrumb__item:last-child .el-breadcrumb__inner a:hover,
  .breadcrumb-map .el-breadcrumb__item:last-child .el-breadcrumb__inner:hover {
    color: #4a4e52;
    cursor: pointer;
  }

  .breadcrumb-map .el-picker-panel__icon-btn,
  .breadcrumb-map .el-cascader-menu__item--extensible::after,
  .breadcrumb-map .el-icon-arrow-right::before {
    color: #4a4e52;
  }

  .map-button--setting {
    position: absolute;
    top: 6px;
    right: 7px;
    /* z-index: 199; */
    z-index: 1;
  }

  .map-tootip-content--block {
    font-size: 14px;
    width: 100%;
    box-sizing: border-box;
    text-align: left;
  }

  .map-tootip-content-left {
    display: inline-block;
    text-align: right;
    width: 80px;
  }

  .map-tootip-content-right {
    display: inline-block;
    text-align: left;
    padding-left: 10px;
  }
</style>
