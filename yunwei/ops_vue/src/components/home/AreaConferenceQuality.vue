<template>
  <div class="theme-dark" style="position: relative;background-color: #232629;">
    <!--下拉菜单区域-->
		<!-- <div style="position: absolute;top:8px;left: 16px;z-index: 1000"> -->
    <div style="position: absolute;top:8px;left: 16px;z-index: 2">
      <div style="font-size: 14px;color:#9ca9b1;">会议客观质量</div>
    </div>
    <!--更多按钮区域-->
    <!--<div style="position: absolute;top:5px;right: 10px;z-index: 1000">
      <button type="button" class="ops-button-text" @click="buttonMore(activeChart.routerPush)">
        <span style="text-decoration: underline;">更多</span>
      </button>
    </div>-->
    <div style="height:calc(100% - 10px);width:calc(100% - 100px);position: absolute;z-index: 1;left: 0px;top: 0px;">
      <!--<ChartBase :chartID="ChartID" :ref="ChartID" @chartInstanceOver="chartInstanceOver"></ChartBase>-->
      <ChartBase :chartID="ChartID" :ref="ChartID" ></ChartBase>
    </div>
    <!-- <div style="z-index:200;height: 100%;position: absolute;right: 20px;top: 9%"> -->
		<div style="z-index:1;height: 100%;position: absolute;right: 20px;top: 9%;">
      <div class="conf-quality-statistics-info" >
        <span class="conf-quality-statistics-info-number">{{confResourcesInfo[2]}}</span>
        <br/>
        <span class="conf-quality-statistics-info-text">活跃会议</span>
      </div>
      <div class="conf-quality-statistics-info" style="">
        <span class="conf-quality-statistics-info-number" style="">{{confResourcesInfo[0]}}</span>
        <br/>
        <span class="conf-quality-statistics-info-text">正在召开会议</span>
      </div>
      <div class="conf-quality-statistics-info" >
        <p class="conf-quality-statistics-info-number">{{confResourcesInfo[1]}}</p>
        <br/>
        <p class="conf-quality-statistics-info-text">历史会议</p>
      </div>
    </div>
  </div>
</template>

<script>
  import ChartBase from "@/components/home/ChartBase.vue"
  export default {
    name: "AreaConferenceResources",
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
        timer:'',
        // 此组件所支持的表的相关配置
        chartConfSupport:{
          conf_quality:{
            name:"会议客观质量",
            dataProcessingMethod:"conf_quality",
            // dataCalculation:"[data[0]*100,data[1]]",
            url:"/confs/summary-quality/",
            // chartType:"barYaxis",
            routerPush:'跳转cpu',
            timerInterver:30,
            params:{
              paramsCalculation:{
                start_time:"new Date().setHours(0, 0, 0, 0)",
              },
            },
            options:{

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
        // colorCustomer:['#1790cf','#63cd81','#a0a7e6','#c4ebad','#96dee8','#626c91'],
        colorCustomer:['#71c6f9','#4face3','#288fcb','#247aac','#96dee8','#626c91'],

        // 会议资源配置
        chartOptionConfQuality:{
          backgroundColor: '#232629',

          series : [
            {
              name:'辅助',
              type:'pie',
              radius: [0, '11%'],
              center: ['50%', '55%'],
              silent:true,
              label: {
                normal: {
                  show: false
                }
              },
              labelLine: {
                normal: {
                  show: false
                }
              },
              itemStyle:{
                color:'#fff',
              },

              data:[
                {value:1, name:'fuzhu'},
              ]
            },
            {
              name:'辅助',
              type:'pie',
              radius: ['10%','21%'],
              center: ['50%', '55%'],
              silent:true,
              label: {
                normal: {
                  show: false
                }
              },
              labelLine: {
                normal: {
                  show: false
                }
              },
              itemStyle:{
                color:'#bfdef0',
              },

              data:[
                {value:1, name:'fuzhu'},
              ]
            },
            {
              name:'辅助',
              type:'pie',
              radius: ['59%','60%'],
              center: ['50%', '55%'],
              silent:true,
              label: {
                normal: {
                  show: false
                }
              },
              labelLine: {
                normal: {
                  show: false
                }
              },
              itemStyle:{
                color:'#43494d',
              },

              data:[
                {value:1, name:'fuzhu'},
              ]
            },
            {
              name: 'conf_quality',
              type: 'pie',
              radius: ['20%', '50%'],
              center: ['50%', '55%'],
              silent:true,
              roseType: 'radius',
              startAngle:0,
              minAngle:20,
              hoverAnimation:false,
              label: {
                align:'left',
                verticalAlign:'bottom',
                formatter:(params) => {
                  // console.log(params.value)
                  let content = params.value ? params.name + ": "  + params.value.toFixed(0) + '%' : null
                  return content
                },
                textStyle: {
                  color: '#9ca9b1'
                }
              },
              labelLine: {
                lineStyle: {
                  color: '#4796c4'
                },
                smooth: 0,
                length:3,
                // length2:1,
              },
              data: [],
            }
          ]
        },

        // 会议信息
        confResourcesInfo:[],
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
        this.renderChartDataInit(this.activeChart,true)
      },
      buttonMore(routerPath){
        // console.log(routerPath)
        // this.$router.push({
        //   path:routerPath
        // });
      },

      // 界面按钮功能函数end

      // echart数据渲染
      async renderChartDataInit(chartConf,isNewChart=true){
        if(chartConf){
          if(chartConf.timerInterver && isNewChart){
            this.setTimer(chartConf.timerInterver)
          }
          let getData=''
          let timestamp = (new Date()).getTime()
          switch(chartConf.dataProcessingMethod){
            case "conf_quality":
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
              // getData=false
              // getData=await this.$api.homePage.getUrlDataSync(chartConf.url,chartConf,false)
              if(!getData){
                return false
              }

              let isExistence = this.chartBaseInstance.getDom().attributes
              // let aaa = this.chartBaseInstance
              if(isExistence._echarts_instance_ && isExistence._echarts_instance_.value){
              }else{
                return false
              }

              // getData=await this.$api.homePage.getUrlDataSync(chartConf.url,chartConf)
              if(isNewChart) {
                this.chartBaseInstance.setOption(this.chartOptionConfQuality, true)
              }
              // console.log(getData)
              let seriseData=[]
              getData.reverse()
              seriseData=getData.map((item,index)=>{
                let backData={}
                if(item.percent !== 0){
                  backData["name"]=item.description

                  // let linearColor=new this.$echarts.graphic.LinearGradient(
                  //   0, 0, 1,1,
                  //   [
                  //     {offset: 0.1, color: this.colorCustomer[index]},
                  //     // {offset: 1, color: 'rgba(0,0,0,0)'}
                  //     {offset: 1, color: 'rgba(63,177,227,0)'}
                  //   ])
                  backData["itemStyle"]={
                    // color:linearColor
                    color:this.colorCustomer[index]
                  }

                  backData["value"]=(item.percent*100)
                }
                return backData
              })
              // console.log(seriseData)

              this.chartBaseInstance.setOption({
                series:{
                  name: 'conf_quality',
                  data:seriseData,
                }
              })

              break;
            default:
              console.log("不支持的操作")
          }
        }

        // this.chartBaseInstance.getOption()
      },

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

      // api接口处理函数start
      async getStatisticsConfNumber(){
        // let timestamp = (new Date()).getTime()

        let params={
          start_time:new Date().setHours(0, 0, 0, 0)
        }

        // // 测试调整临时params固定时间
        // let now = new Date()
        // let t = new Date('2019-09-23').setHours(now.getHours(), now.getMinutes(), now.getSeconds(), 0)
        // params.start_time=new Date('2019-09-23').setHours(0,0,0,0)
        // params.end_time=t
        // // 测试调整临时params固定时间end

        let getData=await this.$api.homePage.getStatisticsConfNumber(params)
        // console.log(getData)
        let confInfo={}
        getData.forEach((item,index)=>{
          let total=0
          Object.values(item.data).forEach(i => total += i)
          // console.log(total)
          confInfo[item.name]=total
        })
        // this.$set(this.confResourcesInfo,"conf_statistics",[item.data.used,item.data.available])
        this.confResourcesInfo=[confInfo.on_going_conf,
                                confInfo.on_going_conf+confInfo.complete_conf,
                                confInfo.active_conf
                               ]

        // console.log(confInfo)
      },
      // api接口处理函数end

      // 定时器函数start
      // 设置定时器
      setTimer(interver=60,range=3600000){
        this.clearTimer();
        this.timer = setInterval(() => {
          // console.log(range)
          // console.log(interver)
          this.renderChartDataInit(this.activeChart,false)
          this.getStatisticsConfNumber()
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
        this.getStatisticsConfNumber()
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

  .conf-quality-statistics-info{
    height: 30%;
    vertical-align:middle;
    line-height: 20px;

  }
  .conf-quality-statistics-info-number{
    float: right;
    font-size: 20px;
    color:#4796c4;
  }
  .conf-quality-statistics-info-text{
    float: right;
    font-size: 12px;
    color:#9ca9b1;
  }
</style>
