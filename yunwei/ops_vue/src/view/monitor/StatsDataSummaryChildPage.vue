<template>
  <div class="theme-dark" style="position: relative">
    <div class="button-back" style="">
      <el-button icon="ops-icons-bg icon-arrow-circle-left" @click="back" circle></el-button>
    </div>
    <div style="padding: 18px 20px 0px 60px">
      {{pageConf.name}}
    </div>
    <!--内容区-->
    <div style="padding: 34px 20px 0px 60px">
      <!--筛选区-->
      <div style="line-height: 26px;">

        <div style="display: inline-block;line-height: 26px;margin-right: 7px;">
          <el-select style="margin-right: 7px;width: 240px;" @change="filterChangeDomainPlatform" filterable :popper-append-to-body="false" popper-class="theme-dark" v-model="optionSelectedDomainPlatform" placeholder="请选择" >
            <el-option
              v-for="item in optionsDomainPlatform" :key="item.moid" :label="item.name" :value="item.moid">
            </el-option>
          </el-select>
        </div>

        <div style="display: inline-block;line-height: 26px;margin-right: 7px;">
          <el-select style="margin-right: 7px;width: 240px;" @change="filterChangeMachineRoom" filterable :popper-append-to-body="false" popper-class="theme-dark" v-model="optionSelectedMachineRoom" placeholder="请选择" >
            <el-option
              v-for="item in optionsMachineRoom" :key="item.moid" :label="item.name" :value="item.moid">
            </el-option>
          </el-select>
        </div>

        <div style="display: inline-block;line-height: 26px;margin-right: 7px;" v-if="!pageConf.noDateFilter">
        <el-select @change="selectDataChange" popper-class="theme-dark" v-model="timeRnageSelectedOptions" placeholder="请选择平台域" style="width: 120px;">
          <el-option
            v-for="item in timeRnageList" :key="item[0]" :label="item[0]" :value="item[1]">
          </el-option>
        </el-select>
        </div>
        <div style="display: inline-block;line-height: 26px;margin-right: 7px;vertical-align: top;" v-if="!pageConf.noDateFilter">
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
          style="width: 322px;"
          range-separator=""
          class="clear-close-icon"
          prefix-icon="ops-icons-bg icon-calendar"
          :clearable=false
        >
        </el-date-picker>
        </div>
        <div style="display: inline-block;line-height: 26px;margin-right: 7px;vertical-align: top;" v-if="pageConf.startTimeFilter">
          <span>开始时间：</span>
          <el-date-picker
            v-model="datePickerTimeRange[0]"
            type="datetime"
            placeholder="选择日期时间"
            popper-class="theme-dark"
            value-format="timestamp"
            format="yyyy-MM-dd HH:mm"
            @focus="recoderDatePicker(datePickerTimeRange[0])"
            @blur="judgeDatePickerChange(datePickerTimeRange[0])"
            style="width: 180px;margin-right: 10px;"
            range-separator=""
            class="clear-close-icon custom__sdscp"
            prefix-icon="ops-icons-bg icon-calendar"
            :clearable=false>
          </el-date-picker>
          <span style="display: inline-block;width: 180px;">结束时间：{{resourceReservationEndTime}}</span>
        </div>

        <div style="display: inline-block;line-height: 26px;margin-right: 7px;" v-if="pageConf.inputSearch">
        <el-input style="width: 180px;" v-model="inputSearch" maxlength="100" placeholder="请输入关键字搜索"></el-input>
        </div>
        <el-button @click="searchMonitor">搜索</el-button>
        <el-button @click="exportTable" v-if="areaDetailShow==='table'" style="float: right;">导出</el-button>
      </div>
      <!--详情区-->
      <!-- 表格区域 -->
      <div v-if="areaDetailShow==='table'" class="area-table" style="margin-top: 18px;">
        <el-table ref="hostinfoMultipleTable" tooltip-effect="dark"
                  stripe
                  border
                  style="width: 100%;"
                  :data="tableData"
        >
          <el-table-column show-overflow-tooltip type="index" label="序号" width="48">
          </el-table-column>
          <!--<el-table-column :reserve-selection="true" type="selection" width="30">-->
          <!--</el-table-column>-->
          <el-table-column show-overflow-tooltip v-for="item in tableTitle" :prop="item.prop" :label="item.label" :width="item.width" :key="item.prop">
          </el-table-column>
        </el-table>
        <div style="margin-top: 20px;">
          <KdPagination
            @current-change="pageHandleCurrentChange"
            :page-size="pageSize"
            :current-page.sync="currentPage"
            :total="pageTotal"></KdPagination>
        </div>
      </div>
      <!-- 表格区域end -->

      <!--图表区域-->
      <div style="width: 100%;height: 600px;margin-top: 10px;" v-if="areaDetailShow==='chartCommon'">
        <ChartExtendLargeModel ChartID="IDStatsDataSummaryChildPage"
                               :chartConf="activeChartConf"
                               :extraPlugin="extraPlugin"
                               extraPluginClass="area-chart-plugin--datasummary"
                               @chart-data="chartDataCallback"></ChartExtendLargeModel>
      </div>
      <!--图表区域end-->
      <!--详情区end-->
    </div>
  </div>
</template>

<script>
export default {
  name: "StatsDataSummaryChildPage",
  components: {
    ChartExtendLargeModel: ()=> import('@/components/monitor/ChartExtendLargeModel.vue'),
    KdPagination: () => import('@/components/common/KdPagination.vue'),
  },
  props:{
    chartConf:Object,
    pageConf:Object,
  },
  data(){
    return{
      timer:null,

      // 过滤信息
      optionSelectedDomainPlatform: '',
      optionsDomainPlatform: [],
      optionSelectedMachineRoom: '',
      optionsMachineRoom: [],

      fixedUrlParams:null,

      theTimeRange:3600000,
      datePickerTimeRange:'',
      timeRnageSelectedOptions:'最近 一小时',
      timeRnageList:[["自定义","customer"],
        ["最近 一小时",3600000],
        ["最近 一天",86400000],
        ["最近 七天",86400000*7],
        ["最近 十五天",86400000*15],
        ["最近 一个月",86400000*30],
        ["最近 半年",86400000*180],
      ],

      // 针对预约资源的图做特殊处理
      resourceReservationEndTime:'',
      // 记录上一次时间的选择
      frontDatePickerTimeRange:null,

      activeChartConf:{},

      inputSearch:'',
      keepAliveInputSearch:null,

      tableTitle:[],
      tableData:[],

      areaDetailShow:null,  // 详情区域展现内容

      // chart封装组件的传参
      extraPlugin:{
        imgExport:true,
      },

      // 分页数据
      currentPage: 1,
      pageSize: 16,
      pageTotal:0,

      // start 此组件支持的chartConf
      chartConfSupport: {
        enterprise_conf_stats_number: {
          name: "企业会议数统计",
          chartRenderMethod: "barYaxis",
          dataRenderMethon: "barYaxis",
          chartKey:'enterprise_conf_stats_number',
          // dataKey:['data','info'],
          url: ['common', '/statistics/company_conf/'],
          timerInterver:60,
          urlParams:{
            // count:10
          },
          // url:"cpu",
          routerPush: '跳转cpu',
          timerInterver: 300,
          options: {
            grid: {
              left: 93,
              right: 40,
              bottom: 35,
              top:50,
              containLabel: false
            },
          },
        },
        stats_created_conf: {
          name: "创会数量统计",
          chartRenderMethod: "scatter",
          dataRenderMethon: "scatter",
          // dataKey:['data','info'],
          url: ['common', '/statistics/create_conf_type/'],
          // url:"cpu",
          chartKey:'stats_created_conf',

          routerPush: '跳转cpu',
          timerInterver: 60,
          options: {
            grid: {
              left: 93,
              right: 40,
              bottom: 50,
              top:50,
              containLabel: false
            },
            legend:{
              top:8,
            },
          },
        },
        stats_enterprise_info: {
          name: "企业信息统计",
          chartRenderMethod: "pie",
          dataRenderMethon: "pie",
          chartKey:'stats_enterprise_info',
          // dataKey:['data','info'],
          url: ['common', '/statistics/company_info/'],
          urlParams:'nextReFresh',
          // url:"cpu",
          routerPush: '跳转cpu',
          timerInterver: 300,
          options: {
            customerColor:['#2c8dc5','#e45959'],
            selectedMode:['停用企业'],
            minAngle:10,
            label:{
              color:'#9ca9b1',
              formatter: function(params) {
                return "{label|" + params.name + "}" + "{value|：" + params.value + "个}\n" +
                  "{label|占比}" + "{value|：" + params.percent + "%}"
              },
              rich: {
                label: {
                  fontSize: 14,
                  height:18,
                  width:62,
                  color:'#9ca9b1',
                  align:'left',
                  padding:[0,0,0,10]
                },
                value: {
                  fontSize: 14,
                  height:18,
                  align:'left',
                  color:'#9ca9b1',
                },
              }
            },
          }
        },
        stats_terminal_info: {
          name: "账号信息统计",
          chartRenderMethod: "pie",
          dataRenderMethon: "pie",
          chartKey:'stats_terminal_info',
          // dataKey:['data','info'],
          url: ['common', '/statistics/terminal_info/'],
          urlParams:'nextReFresh',
          // url:"cpu",
          routerPush: '跳转cpu',
          timerInterver: 300,
          options: {
            customerColor:['#2c8dc5','#e45959'],
            selectedMode:['停用账号'],
            minAngle:10,
            label:{
              color:'#9ca9b1',
              formatter: function(params) {
                return "{label|" + params.name + "}" + "{value|：" + params.value + "个}\n" +
                  "{label|占比}" + "{value|：" + params.percent + "%}"
              },
              rich: {
                label: {
                  fontSize: 14,
                  height:18,
                  width:62,
                  color:'#9ca9b1',
                  align:'left',
                  padding:[0,0,0,10]
                },
                value: {
                  fontSize: 14,
                  height:18,
                  color:'#9ca9b1',
                  align:'left',
                },
              }
            },
          }
        },
        conf_created_time: {
          name: "创建会议时长统计",
          chartRenderMethod: "barXaxis",
          dataRenderMethon: "barXaxis",
          // dataKey:['data','info'],
          url: ['api', 'getCreateConfTime'],
          // url:"cpu",
          urlParams:'nextReFresh',
          routerPush: '跳转cpu',
          timerInterver: 300,
          options: {
            labelFontSize:14,
            echartsCustom: {
              grid: {
                left: 162,
                right: 162,
                bottom: 110,
                top:110,
                containLabel: false
              },
              yAxis: {
                name: "个数",
                nameTextStyle: {
                  color: '#9ca9b1',
                  fontSize: 14,
                },
                type:"value",
                // name:'使用率%',
                axisLabel:{
                  fontSize:10,
                  margin:10,
                  color: '#9ca9b1'
                  // interval:20,
                },
                axisTick:{
                  show:false,
                },
                axisLine: {
                  lineStyle: {
                    color: '#5f656a'
                  },
                },
                splitLine: {
                  lineStyle:{
                    color: ['#5f656a'],
                    type:'dotted'
                  },
                },
              },
              tooltip:{
                enterable:true,
                hideDelay:500,
                formatter:  (params,) => {
                  let title='<div class="tooltip-title-create-conf-time">'+'<span>'+ params.value[0] + '</span>'+
                    '<span>'+ ':&nbsp' + params.value[1] + '个' + '</span>'+'</div>'
                  let detail=params.value[2]
                  let htmlContent=[]
                  let ct = '<div class="tooltip-content-create-conf-time" >'+
                                '<span>'+ '会议号' + '</span>'+
                                '<span>'+  '会议名' +  '</span>'+
                            '</div>'
                  if(detail.length>0){
                    htmlContent.push(ct)
                    detail.forEach((item)=>{
                      let temHtml = '<div class="tooltip-content-create-conf-time" >'+
                                      '<span>'+ item.confE164+ '</span>'+
                                      '<span>'+  item.confname+  '</span>'+
                                    '</div>'
                      htmlContent.push(temHtml)
                    })
                  }

                  let content=htmlContent.join('\n')
                  return '<div class="tooltip-block-create-conf-time">' + title + content + '</div>'
                },
              },
            }
          },
        },
        conf_continue_time: {
          name: "会议时长统计",
          chartRenderMethod: "barXaxis",
          dataRenderMethon: "confContinueTime",
          // dataKey:['data','info'],
          url: ['common', '/conf_time/'],
          // url:"cpu",
          urlParams:'nextReFresh',
          routerPush: '跳转cpu',
          timerInterver: 300,
          options: {
            labelFontSize:14,
            echartsCustom: {
              grid: {
                left: 162,
                right: 162,
                bottom: 110,
                top:110,
                containLabel: false
              },
              yAxis: {
                name: "个数",
                nameTextStyle: {
                  color: '#9ca9b1',
                  fontSize: 14,
                },
                type:"value",
                // name:'使用率%',
                axisLabel:{
                  fontSize:10,
                  margin:10,
                  color: '#9ca9b1'
                  // interval:20,
                },
                axisTick:{
                  show:false,
                },
                axisLine: {
                  lineStyle: {
                    color: '#5f656a'
                  },
                },
                splitLine: {
                  lineStyle:{
                    color: ['#5f656a'],
                    type:'dotted'
                  },
                },
              },
            }
          }
        },

        stats_terminal_call: {
          name: "终端呼叫数量",
          chartRenderMethod: "timeline",
          dataRenderMethon:"timeline",
          // dataKey:['data','info'],
          url: ['common','/statistics/calling_terminals/'],
          // url:"cpu",
          routerPush: '跳转cpu',
          urlParams:'nextReFresh',
          timerInterver: 300,
          options: {
            isArea:true,
            echartsCustom: {
              grid: {
                left: 162,
                right: 162,
                bottom: 110,
                top:110,
                containLabel: false
              },
              legend:{
                top:20,
                right:162,
              },
              yAxis: {
                name: "个数",
                nameTextStyle: {
                  color: '#9ca9b1',
                  fontSize: 14,
                }
              },
            },
          }
        },
        stats_living_terminal: {
          name: "观看直播人数",
          chartRenderMethod: "timeline",
          dataRenderMethon:"timeline",
          // dataKey:['data','info'],
          url: ['common','/statistics/vrs/'],
          // url:"cpu",
          routerPush: '跳转cpu',
          urlParams:'nextReFresh',
          timerInterver: 300,
          options: {
            isArea:true,
            echartsCustom: {
              grid: {
                left: 162,
                right: 162,
                bottom: 110,
                top:110,
                containLabel: false
              },
              legend:{
                top:20,
                right:162,
              },
              yAxis: {
                name: "个数",
                nameTextStyle: {
                  color: '#9ca9b1',
                  fontSize: 14,
                }
              },
            },
          }
        },
        utilization_live_broadcasts:{
          name:"直播资源使用率",
          chartRenderMethod: "timeline",
          dataRenderMethon:"timeline",
          chartKey:'utilization_live_broadcasts',
          url: ['api','getStatisticsVrsResources'],
          urlParams:'nextReFresh',
          timerInterver: 30,
          options:{
            isArea:true,
            // color:['#d8a77e','#cb7579']
            echartsCustom:{
              grid: {
                left: 162,
                right: 162,
                bottom: 110,
                top:110,
                containLabel: false
              },
              legend:{
                top:20,
                right:162,
              },
              yAxis:{
                name: "%",
                nameTextStyle: {
                  color: '#9ca9b1',
                  fontSize: 14,
                },
                max:function (v) {
                  let  l=(v.max.toString().length > 3 ? v.max.toString().length - 3 : v.max.toString().length)
                  if(l){
                    let x = ('1' + new Array(l).join('0'))
                    return Math.ceil(v.max) + parseInt(x)
                  }
                }
              },
              tooltip:{
                formatter:  (params,) => {
                  // console.log(params)
                  let time = this.$echarts.format.formatTime('yyyy-MM-dd', params[0].value[0])
                    + ' ' + this.$echarts.format.formatTime('hh:mm:ss', params[0].value[0]);
                  let usedFormatter=[]
                  let leftHtml='<div class="lchart-tootip-block__left">'
                  let rightHtml='<div class="lchart-tootip-block__right">'
                  for(let item of params){
                    let lstyle = 'style="background: ' + item.color + ';"'
                    let leftHtmlContent = '<div class="lchart-tootip-content--block">' +
                      '<div class="lchart-tootip-content-legendicon"' + lstyle + '></div>' +
                      '<div class="lchart-tootip-content-left">'+ item.seriesName + '使用率' + '</div>' +
                      '</div>' +
                      '<div class="lchart-tootip-content--block">' +
                      '<div class="lchart-tootip-content-legendicon"' + lstyle + '></div>' +
                      '<div class="lchart-tootip-content-left">'+ item.seriesName + '已用' + '</div>' +
                      '</div>' +
                      '<div class="lchart-tootip-content--block">' +
                      '<div class="lchart-tootip-content-legendicon"' + lstyle + '></div>' +
                      '<div class="lchart-tootip-content-left">'+ item.seriesName + '总数'+ '</div>' +
                      '</div>'

                    // usedFormatter.push(item.seriesName + ': ' + showValue)
                    leftHtml+=leftHtmlContent

                    let showValue=null
                    if(item.value[1]!==null&&item.value[1]!==undefined) showValue = item.value[1].toFixed(2) + " %"
                    let rightHtmlContent = '<div class="chart-tootip-content--block">' +
                      '<div class="lchart-tootip-content-right">'+':&nbsp' + showValue + '</div>'+
                      '</div>' +
                      '<div class="lchart-tootip-content--block">' +
                      '<div class="lchart-tootip-content-right">'+':&nbsp' + item.value[2][1] + '</div>'+
                      '</div>' +
                      '<div class="lchart-tootip-content--block">' +
                      '<div class="lchart-tootip-content-right">'+':&nbsp' + item.value[2][0] + '</div>'+
                      '</div>'
                    // usedFormatter.push(item.seriesName + ': ' + showValue)
                    rightHtml+=rightHtmlContent
                  }
                  leftHtml+='</div>'
                  rightHtml+='</div>'
                  usedFormatter=[leftHtml,rightHtml]
                  let header='<div style="font-size: 12px;margin-bottom: 8px;">'+time+'</div>'
                  let content=[...usedFormatter].join('\n')
                  return header+content;
                }
              },
            },
          }
        },
        resource_reservation: {
          name: "预约资源",
          chartRenderMethod: "timeline",
          dataRenderMethon:"timeline",
          // dataKey:['data','info'],
          url: ['common','/statistics/appointment/'],
          // url:"cpu",
          routerPush: '跳转cpu',
          urlParams:'nextReFresh',
          timerInterver: 60,
          options: {
            isArea:true,
            echartsCustom: {
              grid: {
                left: 162,
                right: 162,
                bottom: 110,
                top:110,
                containLabel: false
              },
              legend:{
                top:20,
                right:162,
              },
              yAxis: {
                name: "个数",
                nameTextStyle: {
                  color: '#9ca9b1',
                  fontSize: 14,
                }
              },
            },
          }
        },
      },
      // end 此组件支持的chartConf
    }
  },
  methods: {
    // 返回回调
    back(){
      this.$emit('back',true);
    },

    // echarts url数据回调
    chartDataCallback(data){
      if(this.chartConf.chartKey === 'resource_reservation') {
        let index = data[0].data.length - 1
        let time = new Date(data[0].data[index][0]);
        this.resourceReservationEndTime = time.format('Y-m-d H:i')
      }
    },
    // 选择器函数
    selectDataChange(val){
      // console.log(val)
      this.theTimeRange=val
      if(val==="customer"){
        // this.clearTimer();
        this.datePickerTimeRange='';
      }else{
        let timestamp = (new Date()).getTime();
        // console.log(timestamp,timestamp-val)
        this.datePickerTimeRange=[timestamp-val,timestamp]
      }
      // this.getData(timestamp-3600000,timestamp)
    },
    // 过滤项变化
    async filterChangeDomainPlatform(val,reFresh=false){
      this.optionSelectedMachineRoom= '',
      this.optionsMachineRoom= []
      if(val) {
        await this.getMachineRoomInfo(val)
        if (reFresh) {
          this.$nextTick(function () {
            this.renderDataMethod(true)
          });
        }
      }
    },
    filterChangeMachineRoom(val){

    },
    // 搜索按钮
    searchMonitor(){
      this.resourceReservationEndTime=''
      this.keepAliveInputSearch=this.inputSearch

      this.fixedUrlParams={
        platform_moid : this.optionSelectedDomainPlatform,
        room_moid : this.optionSelectedMachineRoom,
      }

      let urlParams = {
        platform_moid : this.optionSelectedDomainPlatform,
        room_moid : this.optionSelectedMachineRoom,
        start:(this.currentPage-1)*this.pageSize,
        count:this.pageSize,
        start_time:this.datePickerTimeRange ? this.datePickerTimeRange[0]:null,
        end_time:this.datePickerTimeRange ? this.datePickerTimeRange[1]:null,
        key:this.keepAliveInputSearch,
      }
      if(this.theTimeRange==="customer"){
        this.clearTimer();
        this.$set(this.activeChartConf,'urlParams',urlParams)
        // this.dataChange(this.datePickerTimeRange)
        this.renderDataMethod()

      }else{
        // this.dataChange(this.datePickerTimeRange)
        this.$set(this.activeChartConf,'urlParams',urlParams)
        this.setTimer(this.activeChartConf.timerInterver,this.theTimeRange)
        this.renderDataMethod(true)
      }
    },
    // 选中时间组件时判断时间是否有改变，若改变下拉框改为“自定义”
    recoderDatePicker(val){
      this.frontDatePickerTimeRange=val
    },
    judgeDatePickerChange(val){
      if(this.frontDatePickerTimeRange!==this.datePickerTimeRange){
        this.timeRnageSelectedOptions="自定义"
        this.theTimeRange="customer"
      }
    },

    // 定时器
    setTimer(interver=60,range=3600000){
      this.clearTimer();
      this.timer = setInterval(() => {
        // console.log(range)
        let timestamp = (new Date()).getTime();
        // console.log(timestamp,timestamp-range)
        let urlParams = {
          start:(this.currentPage-1)*this.pageSize,
          count:this.pageSize,
          start_time:timestamp-range,
          end_time:timestamp,
          key:this.keepAliveInputSearch,
        }

        urlParams={...this.fixedUrlParams,...urlParams}
        this.$set(this.activeChartConf,'urlParams',urlParams)

        this.renderDataMethod()
        // this.datePickerTimeRange=[timestamp-range,timestamp]
        // this.dataChange([timestamp-range,timestamp])
      },interver*1000)
    },
    // 清楚定时器
    clearTimer(){
      clearInterval(this.timer);
      this.timer = null;
    },
    // 定时器end

    // 分页相关函数start
    pageHandleCurrentChange(val) {
      this.currentPage = val
      let params={
        start:(this.currentPage-1)*this.pageSize,
        count:this.pageSize,
        start_time:this.datePickerTimeRange ? this.datePickerTimeRange[0]:null,
        end_time:this.datePickerTimeRange ? this.datePickerTimeRange[1]:null,
        key:this.keepAliveInputSearch,
      }
      this.$set(this.activeChartConf,'urlParams',params)
      this.renderDataMethod()
    },
    // 分页相关函数end

    // 数据处理
    renderDataMethod(isFirst=false){
      let method=this.pageConf.dataRender
      let processMethod = {
        table:this.renderDataMethodTable,
        chartCommon:this.renderDataMethodChartCommon,
      }
      // console.log(method)
      processMethod[method](this.activeChartConf,isFirst)
    },

    // 表格类数据处理
    async renderDataMethodTable(conf,isFirst=false){
      // console.log(conf)
      if(isFirst){

        this.fixedUrlParams={
          platform_moid : this.optionSelectedDomainPlatform,
          room_moid : this.optionSelectedMachineRoom,
        }

        let params={
          platform_moid : this.optionSelectedDomainPlatform,
          room_moid : this.optionSelectedMachineRoom,
          start:0,
          count:this.pageSize,
          start_time:this.datePickerTimeRange ? this.datePickerTimeRange[0]:null,
          end_time:this.datePickerTimeRange ? this.datePickerTimeRange[1]:null,
          key:this.keepAliveInputSearch,
        }
        let backData = await this.getApiTableData(params)
        if(backData){
          this.pageTotal=backData.total
          this.tableData=backData.info
        }
      }else{
        let params=conf.urlParams
        let backData = await this.getApiTableData(params)
        if(backData){
          this.pageTotal=backData.total
          this.tableData=backData.info
        }
      }
    },

    // 通用chart数据处理
    renderDataMethodChartCommon(conf,isFirst){

    },

    // api start
    async getAllPlatformDomainInfo(){
      let platformDomainInfo = await this.$api.homePage.getAllPlatformDomainInfo()
      this.optionsDomainPlatform= []
      // this.optionSelectedDomainPlatform= 'all'

      let filterDomain = platformDomainInfo.filter(item => item.domain_type===1) //过滤出平台域
      this.optionsDomainPlatform=this.optionsDomainPlatform.concat(filterDomain)
      this.defaultDomainPlatform=filterDomain[0].moid
      this.$nextTick(function () {
        this.optionSelectedDomainPlatform = filterDomain[0].moid
      });
      await this.getMachineRoomInfo(filterDomain[0].moid)
      this.$nextTick(function () {
        // this.renderDataMethod(true)
        this.searchMonitor()
      });
    },
    async getMachineRoomInfo(id){
      // this.optionSelectedMachineRoom= 'all',
      this.optionsMachineRoom= []
      let machineRoomInfo = await this.$api.homePage.getMachineRoomInfo(id)
      this.optionsMachineRoom=machineRoomInfo
      this.$nextTick(function () {
        this.optionSelectedMachineRoom=machineRoomInfo[0].moid
      });

    },

    // 表格类数据api
    async getApiTableData(params){
      let getData = this.$api.getChartData[this.pageConf.dataUrl](params)
      return getData
    },
    // 导出数据api
    exportTable(){
      let params={
        platform_moid:this.optionSelectedDomainPlatform,
        room_moid:this.optionSelectedMachineRoom,
        start_time:this.datePickerTimeRange ? this.datePickerTimeRange[0]:null,
        end_time:this.datePickerTimeRange ? this.datePickerTimeRange[1]:null,
        key:this.keepAliveInputSearch,
      }

      this.$api.getChartData[this.pageConf.exportUrl](params)
        .then(res=>{
          // console.log(res)
          const content = res.data
          const blob = new Blob([content])
          const fileName = res.headers["content-disposition"].split("filename=")[1]
          if ('download' in document.createElement('a')) { // 非IE下载
            const elink = document.createElement('a')
            elink.download = fileName
            elink.style.display = 'none'
            elink.href = URL.createObjectURL(blob)
            document.body.appendChild(elink)
            elink.click()
            URL.revokeObjectURL(elink.href) // 释放URL 对象
            document.body.removeChild(elink)
          } else { // IE10+下载
            navigator.msSaveBlob(blob, fileName)
          }
        })
    },

    // 数据处理end
    init(){
      this.areaDetailShow=this.pageConf.areaDetailShow
      this.tableTitle=this.pageConf.tableTitle
      if(this.pageConf.timeRange && this.pageConf.timeRange==='today'){
        this.timeRnageSelectedOptions='自定义'
        this.theTimeRange = 'customer'
        let timestamp = (new Date()).getTime();
        let today = new Date().setHours(0, 0, 0, 0)
        this.datePickerTimeRange=[today,timestamp]
      }else{
        this.selectDataChange(this.theTimeRange);
        this.setTimer(60,this.theTimeRange)
      }
      // this.activeChartConf={...this.chartConf}
      this.activeChartConf=this.chartConfSupport[this.chartConf.chartKey]
      this.getAllPlatformDomainInfo()
    },
  },
  mounted(){
      this.init()
  },
  beforeDestroy () {
    this.clearTimer()
  },
}
</script>

<style>
  .button-back{
    position:absolute;
    top:13px;
    left:20px;
    z-index: 100;
  }
  .custom__sdscp.el-date-editor .el-input__prefix {
    top: 5px;
    left: 10px;
  }
  .area-chart-plugin--datasummary{
    top:20px;
    right: 20px;
  }
  .tooltip-block-create-conf-time{
    overflow-y:auto;
    overflow-x: hidden;
    max-height: 200px;
  }
  .tooltip-title-create-conf-time span{
    /*width: 40px;*/
    display: inline-block;
    padding: 4px 5px;
    font-size: 16px;
  }
  .tooltip-content-create-conf-time{
    border-bottom:  #272c2e 1px solid ;

  }
  .tooltip-content-create-conf-time span{
    display: inline-block;
    word-wrap: break-word;
    word-break: break-all;
    white-space: pre-wrap;
    box-sizing: border-box;
    padding: 2px 5px;
    vertical-align: middle;
  }
  .tooltip-content-create-conf-time span:first-child{
    width: 80px;
  }
  .tooltip-content-create-conf-time span:last-child{
    max-width: 400px;
  }
</style>
