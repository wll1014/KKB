<template>
  <div class="theme-dark" style="position: relative;background-color: #232629;">
    <!--下拉菜单区域-->
    <!-- <div style="position: absolute;top:8px;left: 16px;z-index: 1000"> -->
		<div style="position: absolute;top:8px;left: 16px;z-index: 1">
      <el-dropdown placement="bottom-start" trigger="click" @command="handleChartChange" v-if="chartList.length>1">
        <span class="el-dropdown-link" style="font-size: 14px;color:#9ca9b1;cursor: pointer;">
          {{activeChart.name}}<i style="font-size: 13px;" class="el-icon-arrow-down el-icon--right"></i>
        </span>
        <el-dropdown-menu slot="dropdown" class="theme-dark" style="width: 150px">
          <el-dropdown-item v-for="item in chartList" :command="chartConfSupport[item]" :key="item" >{{chartConfSupport[item].name}}</el-dropdown-item>
        </el-dropdown-menu>
      </el-dropdown>
      <div style="font-size: 14px;color:#9ca9b1;" v-else>{{chartConfSupport[chartList[0]].name}}</div>
    </div>
    <!--更多按钮区域-->
    <!-- <div style="position: absolute;top:9px;right: 20px;z-index: 1000"> -->
		<div style="position: absolute;top:9px;right: 20px;z-index: 1">	
      <button type="button" class="ops-button-text" @click="buttonMore(activeChart)">
        <span style="font-size: 12px;">更多</span>
      </button>
    </div>

    <div style="height: 100%;width:100%;">
      <!--<ChartBase :chartID="ChartID" :ref="ChartID" @chartInstanceOver="chartInstanceOver"></ChartBase>-->
      <ChartBase :chartID="ChartID" :ref="ChartID" ></ChartBase>
    </div>
  </div>
</template>

<script>
import ChartBase from "@/components/home/ChartBase.vue"
export default {
  name: "AreaChildChartExtend",
  components:{
    // ChartBase: () => import('@/components/home/ChartBase.vue'),
    ChartBase,
  },
  props:{
    // echart实例化ID
    ChartID:String,
    // 下拉菜单选择项
    chartList:Array,
  },
  data() {
    return {
      // 定时器实例
      timer:null,
      // 此组件所支持的表的相关配置
      chartConfSupport:{
        cpu:{
          name:"CPU使用率",
          chartType:"timeline",
          dataRenderMethod:"timeline",
          dataCalculation:"[data[0],data[1]*100]",
          url:"/statistics/cpu/",
          api:"common",
          params:{
            paramsCalculation:{
              start_time:"timestamp-3600000",
            },
          },
          routerPush:'/ops/hostmanage/hostinfo',
          timerInterver:30,
          options:{
            legendPosition:['bottom','top5'],
            dataFormat:['percent']
          }
        },
        mem:{
          name:"MEM使用率",
          chartType:"timeline",
          dataRenderMethod:"timeline",
          dataCalculation:"[data[0],data[1]*100]",
          url:"/statistics/memory/",
          api:"common",
          params:{
            paramsCalculation:{
              start_time:"timestamp-3600000",
            },
          },
          routerPush:'/ops/hostmanage/hostinfo',
          timerInterver:30,
          options:{
            legendPosition:['bottom','top5'],
            dataFormat:['percent']
          }
        },
        network_in:{
          name:"网口进口带宽",
          chartType:"timeline",
          dataRenderMethod:"timeline",
          dataCalculation:"[data[0],data[1]/1048576]",
          url:"/statistics/network_in/",
          api:"common",
          params:{
            paramsCalculation:{
              start_time:"timestamp-3600000",
            },

          },
          routerPush:'/ops/hostmanage/hostinfo',
          timerInterver:30,
          options:{
            legendPosition:['bottom','top5'],
            echartsCustom:{
              tooltip:{
                formatter:  (params,) => {
                  // console.log(params)
                  let time = this.$echarts.format.formatTime('yyyy-MM-dd', params[0].value[0])
                    + ' ' + this.$echarts.format.formatTime('hh:mm:ss', params[0].value[0]);
                  let usedFormatter=[]
                  let leftHtml='<div class="chart-tootip-block__left">'
                  let rightHtml='<div class="chart-tootip-block__right">'
                  for(let item of params){
                    let lstyle = 'style="background: ' + item.color + ';"'
                    let leftHtmlContent = '<div class="chart-tootip-content--block">' +
                      '<div class="chart-tootip-content-legendicon"' + lstyle + '></div>' +
                      '<div class="chart-tootip-content-left">'+item.seriesName + '</div>' +
                      '</div>'
                    // usedFormatter.push(item.seriesName + ': ' + showValue)
                    leftHtml+=leftHtmlContent

                    let showValue=null
                    if(item.value[1]!==null&&item.value[1]!==undefined) showValue = item.value[1].toFixed(2) + " MB/s"
                    let rightHtmlContent = '<div class="chart-tootip-content--block">' +
                      '<div class="chart-tootip-content-right">'+':&nbsp' + showValue + '</div>'+
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
        network_out:{
          name:"网口出口带宽",
          chartType:"timeline",
          dataRenderMethod:"timeline",
          dataCalculation:"[data[0],data[1]/1048576]",
          url:"/statistics/network_out/",
          api:"common",
          params:{
            paramsCalculation:{
              start_time:"timestamp-3600000",
            },

          },
          routerPush:'/ops/hostmanage/hostinfo',
          timerInterver:30,
          options:{
            legendPosition:['bottom','top5'],
            echartsCustom:{
              tooltip:{
                formatter:  (params,) => {
                  // console.log(params)
                  let time = this.$echarts.format.formatTime('yyyy-MM-dd', params[0].value[0])
                    + ' ' + this.$echarts.format.formatTime('hh:mm:ss', params[0].value[0]);
                  let usedFormatter=[]
                  let leftHtml='<div class="chart-tootip-block__left">'
                  let rightHtml='<div class="chart-tootip-block__right">'
                  for(let item of params){
                    let lstyle = 'style="background: ' + item.color + ';"'
                    let leftHtmlContent = '<div class="chart-tootip-content--block">' +
                      '<div class="chart-tootip-content-legendicon"' + lstyle + '></div>' +
                      '<div class="chart-tootip-content-left">'+item.seriesName + '</div>' +
                      '</div>'
                    // usedFormatter.push(item.seriesName + ': ' + showValue)
                    leftHtml+=leftHtmlContent

                    let showValue=null
                    if(item.value[1]!==null&&item.value[1]!==undefined) showValue = item.value[1].toFixed(2) + " MB/s"
                    let rightHtmlContent = '<div class="chart-tootip-content--block">' +
                      '<div class="chart-tootip-content-right">'+':&nbsp' + showValue + '</div>'+
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
        mt_online:{
          name:"终端在线统计",
          chartType:"timeline",
          dataRenderMethod:"timeline",
          url:"/statistics/curr_terminals/",
          api:"common",
          params:{
            paramsCalculation:{
              start_time:"timestamp-3600000",
            },
          },
          routerPush:'/ops/monitor/stats_resource_conf?tab=AmountTerminal',
          timerInterver:30,
          options:{
            isArea:true
          }
        },
        mt_call:{
          name:"终端呼叫数量",
          chartType:"timeline",
          dataRenderMethod:"timeline",
          url:"/statistics/calling_terminals/",
          api:"common",
          params:{
            paramsCalculation:{
              start_time:"timestamp-3600000",
            },
          },
          routerPush:'/ops/monitor/stats_data_summary',
          timerInterver:30,
          options:{
            isArea:true
          }
        },
        conf_time:{
          name:"会议时长",
          chartType:"barConfTime",
          dataRenderMethod:"barYaxis",
          url:"/conf_time/",
          api:"common",
          params:{
            paramsCalculation:{
              start_time:"new Date().setHours(0, 0, 0, 0)",
            },
          },
          routerPush:'/ops/monitor/stats_data_summary',
          timerInterver:30,
          options:{
            customer:'conf_time',
          }
        },
        number_live_broadcasts:{
          name:"直播资源使用率",
          chartType:"timeline",
          dataRenderMethod:"timeline",
          url:"getStatisticsVrsResources",
          api:"api",
          params:{
            paramsCalculation:{
              start_time:"timestamp-3600000",
            },
          },
          routerPush:'/ops/monitor/stats_data_summary',
          timerInterver:30,
          options:{
            isArea:true,
            // color:['#d8a77e','#cb7579']
            echartsCustom:{
              yAxis:{
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
                  let leftHtml='<div class="chart-tootip-block__left">'
                  let rightHtml='<div class="chart-tootip-block__right">'
                  for(let item of params){
                    let lstyle = 'style="background: ' + item.color + ';"'
                    let leftHtmlContent = '<div class="chart-tootip-content--block">' +
                      '<div class="chart-tootip-content-legendicon"' + lstyle + '></div>' +
                      '<div class="chart-tootip-content-left">'+ item.seriesName + '使用率' + '</div>' +
                      '</div>' +
                      '<div class="chart-tootip-content--block">' +
                      '<div class="chart-tootip-content-legendicon"' + lstyle + '></div>' +
                      '<div class="chart-tootip-content-left">'+ item.seriesName + '已用' + '</div>' +
                      '</div>' +
                      '<div class="chart-tootip-content--block">' +
                      '<div class="chart-tootip-content-legendicon"' + lstyle + '></div>' +
                      '<div class="chart-tootip-content-left">'+ item.seriesName + '总数'+ '</div>' +
                      '</div>'

                    // usedFormatter.push(item.seriesName + ': ' + showValue)
                    leftHtml+=leftHtmlContent

                    let showValue=null
                    if(item.value[1]!==null&&item.value[1]!==undefined) showValue = item.value[1].toFixed(2) + " %"
                    let rightHtmlContent = '<div class="chart-tootip-content--block">' +
                      '<div class="chart-tootip-content-right">'+':&nbsp' + showValue + '</div>'+
                      '</div>' +
                      '<div class="chart-tootip-content--block">' +
                      '<div class="chart-tootip-content-right">'+':&nbsp' + item.value[2][1] + '</div>'+
                      '</div>' +
                      '<div class="chart-tootip-content--block">' +
                      '<div class="chart-tootip-content-right">'+':&nbsp' + item.value[2][0] + '</div>'+
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
        reservation_resources:{
          name:"预约资源",
          chartType:"timeline",
          dataRenderMethod:"timeline",
          url:"/statistics/appointment/",
          api:"common",
          params:{
            paramsCalculation:{
              start_time:"timestamp-3600000",
            },
          },
          routerPush:'/ops/monitor/stats_data_summary',
          timerInterver:30,
          options:{
            isArea:true,
            echartsCustom:{
              yAxis:{
                max:function (v) {
                  let  l=v.max.toString().length
                  if(l){
                    let x = ('1' + new Array(l).join('0'))
                    return v.max + parseInt(x)
                  }
                }
              },
            },
            // color:['#d8a77e','#cb7579']
          }
        },
        statistics_curr_confs:{
          name:"会议数量",
          chartType:"timeline",
          dataRenderMethod:"timeline",
          url:"/statistics/curr_confs/",
          api:"common",
          params:{
            paramsCalculation:{
              start_time:"timestamp-3600000",
            },
          },
          routerPush:'/ops/monitor/stats_resource_conf?tab=OnGoingConference',
          timerInterver:30,
          options:{
            isArea:true
          }
        },
        disk_use:{
          name:"磁盘分区使用率",
          chartType:"barYaxis",
          dataRenderMethod:"barYaxis",
          dataCalculation:"[data[0]*100,data[1]]",
          url:"/statistics/disk/",
          api:"common",
          params:{
            paramsCalculation:{
              start_time:"timestamp-3600000",
            },
          },
          routerPush:'/ops/hostmanage/hostinfo',
          timerInterver:30,
          options:{
            echartsCustom:{
              tooltip:{
                formatter:  (params,) => {
                  let data=params.value
                  let leftHtmlContent = '<div style="max-width: 200px;white-space:normal;word-break:break-all;display: inline-block;vertical-align: top;">' +
                    data[1] +
                    '</div>'+
                    '<div style="max-width: 200px;white-space:normal;word-break:break-all;display: inline-block;vertical-align: top;">' +
                    "&nbsp&nbsp:&nbsp&nbsp"+ data[0].toFixed(1)+"%" +
                    '</div>'
                  return leftHtmlContent;
                },
              },
            },
          }
        },
        disk_age:{
          name:"磁盘使用寿命",
          chartType:"barYaxis",
          dataRenderMethod:"barYaxis",
          url:"/statistics/diskage/",
          api:"common",
          params:{
            paramsCalculation:{
              start_time:"timestamp-3600000",
            },
          },
          routerPush:'/ops/hostmanage/hostinfo',
          timerInterver:30,
          options:{
            echartsCustom:{
              tooltip:{
                formatter:  (params,) => {
                  let data=params.value
                  let tootipInfo=data[1]+"&nbsp&nbsp:&nbsp&nbsp"+data[0].toFixed(0)+"%"
                  return tootipInfo;
                },
              },
            },
          }
        },

      },
      // 当前激活的表的配置
      activeChart:'',

      // activeTabVal:this.activeTab,
      // echarts实例
      chartBaseInstance:'',
      // 其他配置
      // chartOption:{},


      // echarts颜色库
      // colorCustomer:['#5eb9ef','#09a206','#f78600','#db4c4c','#ac5af2','#626c91'],
      colorCustomer:['#23acd4','#63cd81','#fb265d','#f1ac17','#d66ef8','#1d4ff4','#db6b08'],
      colorCustomerRGBA:['rgba(35,172,212,0.1)','rgba(99,205,129,0.1)','rgba(251,38,93,0.1)',
                        'rgba(241,172,23,0.1)','rgba(214,110,248,0.1)','rgba(29,79,244,0.1)','rgba(219,107,8,0.1)'],
    }
  },
  methods: {
    // 封装echart参数配置函数start

    // 封装echart参数配置函数end

    // 界面按钮功能函数start
    // 下拉菜单处理函数
    handleChartChange(command){
      // console.log(command)
      this.activeChart=command
      this.clearTimer()
      this.renderChartDataInit(this.activeChart,true)
    },
    buttonMore(chartConf){
      // console.log(chartConf.routerPush)
      this.$router.push({
        path:chartConf.routerPush
      });
    },

    // 界面按钮功能函数end

    // echart渲染
    async renderChartDataInit(chartConf,isNewChart=true){
      let defaultConf={
        colorCustomer:this.colorCustomer,
        colorCustomerRGBA:this.colorCustomerRGBA,
        // urlParams:this.urlParams,
      }
      // 根据chartConf.chartRenderMethod判断chart渲染方法
      let renderChartTypeMethod={
        'timeline':this.renderChartTypeTimeline, //横轴时间线chart
        'barYaxis':this.renderChartTypeBaseBar, //Y轴类目轴柱状图chart-->基础柱状图chart
        'barConfTime':this.renderChartTypeBaseBar, //会议时长类目轴柱状图chart-->基础柱状图chart
      };
      let renderChartDataMethod={
        'timeline':this.renderChartDataMethodTimeline, //横轴时间线渲染数据方法
        'barYaxis':this.renderChartDataMethodBarYaxis, //Y轴类目轴柱状图渲染数据方法
        'barConfTime':this.renderChartDataMethodBarYaxis, //会议时长类目轴柱状图chart-->基础柱状图chart
      };
      // console.log(chartConf.chartType)

      renderChartTypeMethod[chartConf.chartType](defaultConf,chartConf,renderChartDataMethod,isNewChart)

      if(chartConf.timerInterver && isNewChart){
        this.setTimer(chartConf.timerInterver)
      }
    },

    // chart渲染start：横轴时间线chart
    async renderChartTypeTimeline(defaultConf,chartConf,renderChartDataMethod,isNewChart){
      // 时间线类图形配置
      let chartBaseOptionLine = {
          backgroundColor: '#232629',
          color:defaultConf.colorCustomer,
          grid: {
            left: '7%',
            right: '9%',
            bottom: 15,
            top:48,
            containLabel: true
          },
          legend: {
            // data:[],
            itemWidth:10,
            itemHeight:5,
            width:'70%',
            icon:'roundRect',
            itemGap:22,
            right:'15%',
            // left:100,
            textStyle:{
              color:'#9ca9b1',
              padding:[1,0,0,5]
            },
            top: 8,
            // left: 'center',
          },
          tooltip: {
            trigger: 'axis',
            padding: [14,14],
            backgroundColor:'#141414',
            borderColor:'#383b3c',
            borderWidth:1,
            textStyle:{
              color:'#9ca9b1',
              fontSize:12,
            },
            formatter:  (params,) => {
              // console.log(params)
              let time = this.$echarts.format.formatTime('yyyy-MM-dd', params[0].value[0])
                + ' ' + this.$echarts.format.formatTime('hh:mm:ss', params[0].value[0]);
              let usedFormatter=[]
              let leftHtml='<div class="chart-tootip-block__left">'
              let rightHtml='<div class="chart-tootip-block__right">'
              for(let item of params){
                let lstyle = 'style="background: ' + item.color + ';"'
                let lhtmlContent = '<div class="chart-tootip-content--block">' +
                  '<div class="chart-tootip-content-legendicon"' + lstyle + '></div>' +
                  '<div class="chart-tootip-content-left">'+item.seriesName + '</div>' +
                  '</div>'
                // usedFormatter.push(item.seriesName + ': ' + showValue)
                leftHtml+=lhtmlContent

                let showValue=null
                if(item.value[1]!==null&&item.value[1]!==undefined) showValue=Math.ceil(item.value[1])
                let rhtmlContent = '<div class="chart-tootip-content--block">' +
                  '<div class="chart-tootip-content-right">'+':&nbsp' + showValue + '</div>'+
                  '</div>'
                rightHtml+=rhtmlContent
              }
              leftHtml+='</div>'
              rightHtml+='</div>'

              usedFormatter=[leftHtml,rightHtml]
              let header='<div style="font-size: 12px;margin-bottom: 8px;">'+time+'</div>'
              let content=[...usedFormatter].join('\n')
              return header+content;
            }
          },
          xAxis: {
            type: 'time',
            splitNumber:10,
            // maxInterval: 3600 * 1000,
            axisLine: {
              lineStyle: {
                color: '#5f656a'
              },
            },
            axisTick:{
              show:false,
            },
            splitLine: {
              show:false,
              lineStyle:{
                color: ['#5f656a'],
                type:'dotted'
              },
            },
            axisLabel:{
              fontSize:10,
              color:'#9ca9b1',
              // interval:20,
              formatter:  (value,index) => {
                // console.log(params)
                let time =this.$echarts.format.formatTime('hh:mm', value);
                return time
              },
              rotate:90,
            },
          },
          yAxis: {
            // name:'使用率%',
            nameTextStyle:{
              fontSize:12,
            },
            axisLabel:{
              fontSize:10,
              color:'#9ca9b1',
              formatter: function (name) {
                if(String(name).indexOf(".") >-1){
                  return ''
                }else{
                  return name;
                }
              }
            },
            axisLine: {
              lineStyle: {
                color: '#5f656a'
              },
            },
            axisTick:{
              show:false,
            },
            splitLine: {
              lineStyle:{
                color: ['#5f656a'],
                type:'dotted'
              },
            },
          },
          series: []
        };
      // 时间线类图形配置end

      // 用于后续增加的整体样式调整 options
      let optionsAppend={}
      // 颜色库初始化
      let colorLibrary = this.colorCustomer
      // 判断是否是新的一张表，若是，则重新渲染整张表，否，则只渲染数据
      if(isNewChart){

        this.chartBaseInstance.setOption(chartBaseOptionLine,true)
        // 判断是否自定义颜色
        if(chartConf.options.color){
          colorLibrary = chartConf.options.color.concat(this.colorCustomer)
          this.chartBaseInstance.setOption({
            color:colorLibrary,
          })
        };
        // 判断是否自定义颜色end

        // 判断数据的tootip格式
        if(chartConf.options.dataFormat){
          if(chartConf.options.dataFormat[0]==="percent"){
            optionsAppend['tooltip']={
              // tooltip: {
              formatter:  (params,) => {
                let time = this.$echarts.format.formatTime('yyyy-MM-dd', params[0].value[0])
                  + ' ' + this.$echarts.format.formatTime('hh:mm:ss', params[0].value[0]);
                let usedFormatter=[]
                let leftHtml='<div class="chart-tootip-block__left">'
                let rightHtml='<div class="chart-tootip-block__right">'
                for(let item of params){
                  let lstyle = 'style="background: ' + item.color + ';"'
                  let lhtmlContent = '<div class="chart-tootip-content--block">' +
                    '<div class="chart-tootip-content-legendicon"' + lstyle + '></div>' +
                    '<div class="chart-tootip-content-left">'+item.seriesName + '</div>' +
                    '</div>'
                  // usedFormatter.push(item.seriesName + ': ' + showValue)
                  leftHtml+=lhtmlContent

                  let showValue=Math.round(item.value[1]*100)/100 + "%"
                  if(item.value[1]===null||item.value[1]===undefined){
                    showValue=null
                  }
                  let rhtmlContent = '<div class="chart-tootip-content--block">' +
                    '<div class="chart-tootip-content-right">'+':&nbsp' + showValue + '</div>'+
                    '</div>'
                  rightHtml+=rhtmlContent
                }

                leftHtml+='</div>'
                rightHtml+='</div>'

                usedFormatter=[leftHtml,rightHtml]
                // console.log(freeFormatter)
                let header='<div style="font-size: 12px;margin-bottom: 8px;">'+time+'</div>'
                let content=[...usedFormatter].join('\n')
                return header+content;
              }
            }
            optionsAppend["yAxis"]={
              ...optionsAppend["yAxis"],
              axisLabel: {
                formatter: '{value}%'
              }
            }
          };
        };
        // 判断数据的tootip格式end


        // 对于自定义项目的修改
        if(chartConf.options && chartConf.options.echartsCustom){
          for(let key in chartConf.options.echartsCustom){
            key ? optionsAppend[key]=chartConf.options.echartsCustom[key] : ''
          }
        }
      }
      // end判断是否是新的一张表，若是，则重新渲染整张表，否，则只渲染数据
      this.chartBaseInstance.setOption(optionsAppend)
      // 数据处理部分
      // 根据chartConf.dataRenderMethon判断data渲染方式
      // console.log(chartConf.dataRenderMethon)
      renderChartDataMethod[chartConf.dataRenderMethod](defaultConf,chartConf,isNewChart)
      // 数据处理部分end
    },
    // chart渲染end：横轴时间线chart

    // 数据渲染start：横轴时间线渲染数据方法
    async renderChartDataMethodTimeline(defaultConf,chartConf,isNewChart){
      // console.log(chartConf.name)
      let optionsAppend={}
      let getData=''
      let colorLibrary=this.chartBaseInstance.getOption().color
      // 提供计算的变量start
      let timestamp = (new Date()).getTime()

      // 对请求参数做处理
      let params={}
      if(chartConf.params){
        for(let key in chartConf.params){
          if(key === "paramsCalculation"){ //如果是需要计算的参数
            for(let calparams in chartConf.params["paramsCalculation"]){
              params[calparams]=eval(chartConf.params["paramsCalculation"][calparams])
            }
          }else{
            params[key]=chartConf.params[key]
          }
        }
      }

      if(chartConf.api==="common"){
        getData=await this.$api.homePage.getUrlDataSync(chartConf.url,params,true)
      }else{
        getData= await this.$api.homePage[chartConf.url](params)
        // getData=await this.$api.homePage.getUrlDataSync(chartConf.url,chartConf)
      }
      if(!getData){
        return false
      }

      let isExistence = this.chartBaseInstance.getDom()
      // let aaa = this.chartBaseInstance
      if(isExistence.getAttribute("_echarts_instance_")){

      }else{
        return false
      }

      // 判断是否需要调整legend的位置
      if(chartConf.options.legendPosition){
        let legendPosition=chartConf.options.legendPosition
        let newGrid={}
        newGrid[legendPosition[0]]=legendPosition[1]
        optionsAppend["grid"]=newGrid
        // console.log(newGrid)
        // 对top5一类的图标做自定义
        if(legendPosition[0]==="bottom" && legendPosition[1]==='top5'){
          let XOffectList=['10%','40%','70%']
          let YOffectList=[7]
          for(let i=0;i<getData.length;i++){
            if(i%3===0 && i!==0){
              YOffectList.unshift(YOffectList[0]+15)
            }
          }
          // 设置grid值
          newGrid[legendPosition[0]]=YOffectList[0]+23
          optionsAppend["grid"]=newGrid
          // console.log(XOffectList,YOffectList)
          let newLegend=getData.map((item,index)=>{
            let XOffect=Math.floor(index%3)
            let YOffect=Math.floor(index/3)
            // console.log(XOffect,YOffect)
            let temLegend= {
              itemWidth:10,
              itemHeight:5,
              // width:'20%',
              icon:'roundRect',
              // itemGap:18,
              formatter: (name)=>{
                let newValue = name.toString();
                let maxlength=14;
                if (newValue.length>maxlength) {
                  newValue=newValue.substring(0, maxlength-2)+'...'
                }
                return newValue;
              },
              // left:100,
              textStyle:{
                color:'#b5b5b6',
                padding:[1,0,0,5]
              },
              left:XOffectList[XOffect],
              bottom: YOffectList[YOffect],
              data:[item.description]
            }
            return temLegend
          })
          // console.log(newLegend)
          optionsAppend["legend"]=newLegend
          optionsAppend["yAxis"]={
            splitNumber: 2,
          };
        };
      }
      // 判断是否需要调整legend的位置end

      // 对各数据项的配置
      // 线的基础配置
      let confTimeLine={
        symbolSize: 1,
        // symbol: 'none',
        type:"line",
        showSymbol: false,
        smooth:true,
        smoothMonotone:'x',
        sampling:'max',
        lineStyle:{
          width: 2,
        },
      }
      // 配置每个系列的数据
      let seriseData=getData.map((item,index)=>{
        let backData={...confTimeLine}

        // 图例名称和数据系列标识
        backData["name"]=item.description

        // 判断曲线区域是否需要填充颜色
        if(chartConf.options.isArea){
          // let colorLibrary = this.colorCustomer
          // if(chartConf.options.color){
          //   colorLibrary = chartConf.options.color
          // }
          // console.log(this.colorCustomer)
          // let linearColor=new this.$echarts.graphic.LinearGradient(
          //   0, 0, 0, 1,
          //   [
          //     {offset: 0, color: defaultConf.colorCustomerRGBA[index]},
          //     {offset: 1, color: 'rgba(0,0,0,0)'}
          //     // {offset: 1, color: 'rgba(63,177,227,0)'}
          //   ])

          backData["areaStyle"] = {
            // type: 'linear',
            // color:linearColor,
            color:defaultConf.colorCustomer[index],
            opacity:0.1,
          }
        };
        this.chartBaseInstance.setOption(optionsAppend)
        // 对有数据处理的数据做处理后返回
        let dataFront=item.data
        if(chartConf.dataCalculation) {
          let temData = item.data.map((data) => {
            let dataCalculation = eval(chartConf.dataCalculation)
            // console.log(temdata)
            return dataCalculation
          });
          dataFront=temData
        }

        backData["data"] = dataFront
        return backData
      })

      if(this.chartBaseInstance){
        this.chartBaseInstance.setOption({
          series:seriseData
        })
      }
    },
    // 数据渲染end：横轴时间线渲染数据方法

    // chart渲染start：基础柱状图chart
    async renderChartTypeBaseBar(defaultConf,chartConf,renderChartDataMethod,isNewChart){
      // 时间线类图形配置
      let chartBaseOptionBar = {
        backgroundColor: '#232629',
        color:['#25a5c5','#63cd81','#a0a7e6','#c4ebad','#96dee8','#626c91'],
        grid: {
          left: '7%',
          right: '9%',
          bottom: 15,
          top:48,
          containLabel: true
        },
        tooltip: {
          trigger: 'item',
          padding: [14,14],
          backgroundColor:'#141414',
          borderColor:'#383b3c',
          borderWidth:1,
          textStyle:{
            color:'#9ca9b1',
          },
        },
        xAxis: {
          // name:"%",
          // nameLocation:'start',
          // nameTextStyle:{
          //   padding:[27,0,0,0]
          // },
          type: 'value',
          axisLabel:{
            fontSize:10,
            color: '#9ca9b1',
            margin:10,
            // interval:20,
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
          axisTick:{
            show:false,
          },
        },
        yAxis: {
          type:"category",
          // name:'使用率%',
          nameTextStyle:{
            fontSize:12,
          },
          axisLabel:{
            fontSize:12,
            fontFamily:'Microsoft YaHei',
            color:'#9ca9b1',
            formatter:(value,index)=>{
              let newValue = value.toString();
              let maxlength=15;
              if (newValue.length>maxlength) {
                return newValue.substring(0, maxlength-1)+'...';
              } else{
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
          axisTick:{
            show:true,
            color:'#5f656a',
          },
        },
        series: []
      };
      // 时间线类图形配置end
      // 用于后续增加的整体样式调整 options
      let optionsAppend={}
      // 颜色库初始化
      let colorLibrary = this.colorCustomer
      // 判断是否是新的一张表，若是，则重新渲染整张表，否，则只渲染数据
      if(isNewChart){

        this.chartBaseInstance.setOption(chartBaseOptionBar,true)
        // 判断是否自定义颜色
        if(chartConf.options.color){
          colorLibrary = chartConf.options.color.concat(this.colorCustomer)
          this.chartBaseInstance.setOption({
            color:colorLibrary,
          })
        };
        // 判断是否自定义颜色end

        // 判断坐标轴
        if(chartConf.chartType==="barYaxis"){

        }
        else if(chartConf.chartType==="barConfTime"){
          optionsAppend={
            grid: {
              left: '7%',
              right: '30%',
              bottom: 15,
              top:48,
              containLabel: true
            },
            xAxis:{
              show:false,
            },
            yAxis: {
              axisLine: {
                show:false,
              },
              axisTick:{
                show:false
              },
              axisLabel:{
                fontSize:12,
                fontFamily:'Microsoft YaHei',
                color:'#9ca9b1',
                margin:20,
              },
            },
          }
          // this.chartBaseInstance.setOption(optionsAppend)
        }
        // 判断坐标轴end

        // 自定义tootip
        // if(chartConf.options.tootip){
        //   let tootip=chartConf.options.tootip
        //   // console.log(tootip.slice(1))
        //   optionsAppend['tooltip']={
        //     formatter:  (params,) => {
        //       let data=params.value
        //
        //       let tootipInfo=tootip.slice(1).map(item => eval(item))
        //       // console.log(tootipInfo)
        //       // usedFormatter.push(item.seriesName + ': ' + Math.round(item.value[1]*100)/100 + "%")
        //       // console.log(freeFormatter)
        //       return tootipInfo.join('<br>');
        //     }
        //   }
        // }

        // 对于自定义项目的修改
        if(chartConf.options && chartConf.options.echartsCustom){
          for(let key in chartConf.options.echartsCustom){
            key ? optionsAppend[key]=chartConf.options.echartsCustom[key] : ''
          }
        }
      }
      // end判断是否是新的一张表，若是，则重新渲染整张表，否，则只渲染数据
      this.chartBaseInstance.setOption(optionsAppend)
      // 数据处理部分
      // 根据chartConf.dataRenderMethon判断data渲染方式
      // console.log(chartConf.dataRenderMethon)
      renderChartDataMethod[chartConf.dataRenderMethod](defaultConf,chartConf,isNewChart)
    },
    // chart渲染end：基础柱状图chart

    // 数据渲染start：Y轴类目轴柱状图渲染数据方法
    async renderChartDataMethodBarYaxis(defaultConf,chartConf,isNewChart){
// console.log(chartConf.name)
      let series=[]
      let seriseData={}
      let optionsAppend={}
      let getData=''
      let colorLibrary=this.chartBaseInstance.getOption().color
      // 提供计算的变量start
      let timestamp = (new Date()).getTime()
      // console.log(colorLibrary)
      // if(chartConf.url[0]==='common'){
      //   getData= await this.$api.getChartData.getUrlDataSync(chartConf.url[1])
      //   // 获取通用格式数据
      //   if(chartConf.dataKey){
      //     chartConf.dataKey.forEach((item)=>{
      //       getData=getData[item]
      //     })
      //   }
      // }else{
      //   getData= await this.$api.getChartData[chartConf.url[1]]()
      //   // console.log(getData)
      // }
      if(chartConf.api==="common"){
        let params={}
        if(chartConf.params){
          for(let key in chartConf.params){
            if(key === "paramsCalculation"){ //如果是需要计算的参数
              for(let calparams in chartConf.params["paramsCalculation"]){
                params[calparams]=eval(chartConf.params["paramsCalculation"][calparams])
              }
            }else{
              params[key]=chartConf.params[key]
            }
          }
        }
        getData=await this.$api.homePage.getUrlDataSync(chartConf.url,params,true)
      }else{
        getData=await this.$api.homePage.getUrlDataSync(chartConf.url,chartConf)
      }
      if(!getData){
        return false
      }
      let isExistence = this.chartBaseInstance.getDom().attributes
      // let aaa = this.chartBaseInstance
      if(isExistence._echarts_instance_ && isExistence._echarts_instance_.value){
      }else{
        return false
      }

      seriseData["type"]="bar"

      // 柱状图渐变
      let linearColor=new this.$echarts.graphic.LinearGradient(
        1, 0, 0, 0,
        [
          // {offset: 0, color: this.colorCustomer[0]},
          // {offset: 0, color: '#1790cf'},
          // {offset: 1, color: 'rgba(0,0,0,0)'}
          // {offset: 1, color: 'rgba(63,177,227,0)'}
          {offset: 0, color: '#5eb9ef'},
          {offset: 1, color: '#1a79ae'}
        ])

      seriseData["itemStyle"] = {
        color:linearColor,
        // opacity:0.7,
      }

      // 如果是会议时长chart，itemStyle重新定义
      if(chartConf.chartType==="barConfTime"){
        seriseData["itemStyle"]={
          // color:linearColor,
          normal:{
            color:linearColor,
            label:{
              show:true,
              formatter:'{@[0]} 个',
              color:'#4796c4',
              position:'right',
              fontSize:14,
              distance:14,
            }
          }
        };
      };

      seriseData["barWidth"] = '40%'
      let YAxisData=[]
      // console.log(seriseData)

      seriseData["name"]=chartConf.name
      // 配置每个系列的数据
      seriseData["data"]=getData.reverse().map((item,index)=>{
        let backData={}
        // backData["name"]=item.description
        // 图例名称和数据系列标识
        // 对有数据处理的数据做处理后返回
        YAxisData.push(item.description)
        let dataFront=[item.data,item.description]
        if(chartConf.dataCalculation) {
          let data=[item.data,item.description]
          let dataCalculation = eval(chartConf.dataCalculation)
          // console.log(temdata)
          dataFront=dataCalculation
        }
        // backData["data"] = dataFront
        return dataFront
      })

      // seriseData["data"].reverse()

      // console.log(seriseData)
      series.push(seriseData)
      if(this.chartBaseInstance) {
        this.chartBaseInstance.setOption({
          yAxis: {
            data: YAxisData,
          },
          series: series
        })
      }
    },
    // 数据渲染end：Y轴类目轴柱状图渲染数据方法

    // echart渲染end

    // 其他功能函数start
    // 16进制颜色转rgb格式
    colorRgb(sColor){
      sColor = sColor.toLowerCase();
      //十六进制颜色值的正则表达式
      let reg = /^#([0-9a-fA-f]{3}|[0-9a-fA-f]{6})$/;
      // 如果是16进制颜色
      if (sColor && reg.test(sColor)) {
        if (sColor.length === 4) {
          let sColorNew = "#";
          for (let i=1; i<4; i+=1) {
            sColorNew += sColor.slice(i, i+1).concat(sColor.slice(i, i+1));
          }
          sColor = sColorNew;
        }
        //处理六位的颜色值
        let sColorChange = [];
        for (let i=1; i<7; i+=2) {
          sColorChange.push(parseInt("0x"+sColor.slice(i, i+2)));
        }
        return "rgb(" + sColorChange.join(",") + ")";
      }
      return sColor;
    },
    // 其他功能函数end

    // 定时器函数start
    // 设置定时器
    setTimer(interver=60,range=3600000){
      this.clearTimer();
      this.timer = setInterval(() => {
        // console.log(range)
        // console.log(interver)
        this.renderChartDataInit(this.activeChart,false)
      },interver*1000)
    },
    // 清除定时器
    clearTimer(){
      clearInterval(this.timer);
      this.timer = null;
    },
    // 定时器函数end

    // 组件chart初始化
    init(){
      // this.chartBaseInstance=val
        // this.chartInstanceOver()
      this.activeChart=this.chartConfSupport[this.chartList[0]]
      // console.log(this.activeChart)
      this.chartBaseInstance=this.$refs[this.ChartID].getChartInstance();
      // console.log(this.chartBaseInstance)
      // this.active = this.ChartchartList[0]
      this.renderChartDataInit(this.activeChart)
      // this.chartBaseInstance.setOption(this.chartBaseOptionLine)
        // this.getData()

        // console.log(this.chartBaseInstance)
        // console.log(this.$refs[this.ChartID].test())
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
  .chart-tootip-block__left{
    display: inline-block;
  }
  .chart-tootip-block__right{
    display: inline-block;
  }
  .chart-tootip-content--block{
    font-size: 12px;
    width: 100%;

    /*padding: 0 8px;*/
    box-sizing: border-box;
    text-align: left;
    position: relative;
  }
  .chart-tootip-content-legendicon{
    display: inline-block;
    text-align: left;
    width: 10px;
    height: 5px;
    z-index: 199;
    vertical-align: 2px;
    border-radius: 1px;
    margin-right: 5px;
  }
  .chart-tootip-content-left{
    /*float: left;*/
    display: inline-block;
    text-align: left;
    /*width: calc(100% - 70px);*/
    /*text-align: left;*/
    /*width: 60%;*/
  }
  .chart-tootip-content-right{
    /*float: right;*/
    display: inline-block;
    /*width: 80px;*/
    /*max-width: 90px;*/
    /*width: 40%;*/
    text-align: left;
    padding-left: 10px;
  }
</style>
