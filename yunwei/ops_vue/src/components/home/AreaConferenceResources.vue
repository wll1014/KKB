<template>
  <div class="theme-dark" style="position: relative;background-color: #232629;">
    <!--下拉菜单区域-->
		<!-- <div style="position: absolute;top:8px;left: 16px;z-index: 1000"> -->
    <div style="position: absolute;top:8px;left: 16px;z-index: 1">
      <div style="font-size: 14px;color:#9ca9b1;">会议资源</div>
    </div>
    <!--更多按钮区域-->
		<!-- <div style="position: absolute;top:9px;right: 20px;z-index: 1000"> -->
    <div style="position: absolute;top:9px;right: 20px;z-index: 1">
      <button type="button" class="ops-button-text" @click="buttonMore(activeChart.routerPush)">
        <span style="font-size: 12px;">更多</span>
      </button>
    </div>

    <div style="height: 50%;width:100%;">
      <!--<ChartBase :chartID="ChartID" :ref="ChartID" @chartInstanceOver="chartInstanceOver"></ChartBase>-->
      <ChartBase :chartID="ChartID" :ref="ChartID"></ChartBase>
    </div>
    <div style="height: 50%;width:100%;position: relative;box-sizing: border-box;padding-top: 6px;">
      <div style="height: 100%;width:100px;position: absolute;left:20%;">
        <div style="left:-28px;position: absolute;font-size: 14px;color:#9ca9b1;">传统会议</div>
        <div style="color: #5d6266; top:25px; left:-50px;position: absolute;bottom: 10px;text-align: center;width: 100%;">
          <div style="margin-bottom: 3px;">已召开：{{confResourcesInfo.tra_conf_convened_num}}</div>
          <el-tooltip effect="dark" placement="bottom-start">
            <div slot="content">
              <div style="margin-bottom: 6px;">
                <span>可召开：1080P30会议(大方/小方)：{{confResourcesInfo.tra_conf_conveyable_num_1080_30_l}}/{{confResourcesInfo.tra_conf_conveyable_num_1080_30_s}}</span>
              </div>
              <div style="margin-left: 48px;">
                <div style="margin-bottom: 6px;">
                  <span>1080P60会议(大方/小方)：{{confResourcesInfo.tra_conf_conveyable_num_1080_60_l}}/{{confResourcesInfo.tra_conf_conveyable_num_1080_60_s}}</span>
                </div>
                <div style="margin-bottom: 6px;">
                  <span>720P30会议(大方/小方)&nbsp&nbsp：{{confResourcesInfo.tra_conf_conveyable_num_720_30_l}}/{{confResourcesInfo.tra_conf_conveyable_num_720_30_s}}</span>
                </div>
                <div style="">
                  <span>720P60会议(大方/小方)&nbsp&nbsp：{{confResourcesInfo.tra_conf_conveyable_num_720_60_l}}/{{confResourcesInfo.tra_conf_conveyable_num_720_60_s}}</span>
                </div>
              </div>
              <!--<div style="">
                <span class="conf-detail--tooltip-left">端口会议</span>
                <span>{{"：" + confResourcesInfo.port_num}}</span>
              </div>-->
            </div>
            <div style="margin-bottom: 3px;cursor: pointer;">可召开：{{confResourcesInfo.tra_conf_conveyable_num_1080_30_l}}</div>
          </el-tooltip>
        </div>
      </div>
      <div style="height: 100%;width:100px;position: absolute;left:50%;">
        <div style="color: #5d6266;left:-28px;position: absolute;font-size: 14px;color:#9ca9b1;">端口会议</div>
        <div style="color: #5d6266;top:25px;left:-50px;position: absolute;bottom: 10px;text-align: center;width: 100%;">
          <div style="margin-bottom: 3px;">已召开：{{confResourcesInfo.port_conf_convened_num}}</div>
          <div style="margin-bottom: 3px;">已用端口数：{{confResourcesInfo.total_port_num-confResourcesInfo.free_port_num}}</div>
          <div style="">剩余端口数：{{confResourcesInfo.free_port_num}}</div>
        </div>
      </div>
      <div style="height: 100%;width:100px;position: absolute;left:80%;">
        <div style="color: #5d6266;left:-35px;position: absolute;font-size: 14px;color:#9ca9b1;">点对点会议</div>
        <div style="color: #5d6266;top:25px;left:-50px;position: absolute;bottom: 10px;text-align: center;width: 100%;">
          <div style="margin-bottom: 3px;">已召开：{{confResourcesInfo.p2p_conf_convened_num}}</div>
          <div style="">可召开：{{confResourcesInfo.p2p_conf_conveyable_num}}</div>
        </div>
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
        timer:null,
        // 此组件所支持的表的相关配置
        chartConfSupport:{
          conf_resources:{
            name:"会议资源",
            dataProcessingMethod:"conf_resources",
            // dataCalculation:"[data[0]*100,data[1]]",
            url:"/conf_resources/",
            api:"common",
            params:{
              paramsCalculation:{
                start_time:"timestamp-86400000",
              },
            },
            // chartType:"barYaxis",
            routerPush:'/ops/monitor/stats_resource_conf',
            timerInterver:30,
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
        colorCustomer:['#1790cf','#63cd81','#a0a7e6','#c4ebad','#96dee8','#626c91'],

        // 会议资源配置
        chartOptionConfResources:{
          backgroundColor: '#232629',
          color:['#3fb1e3','#6be6c1','#626c91','#a0a7e6','#c4ebad','#96dee8'],
          grid: {
            left: '3%',
            right: '7%',
            bottom: 5,
            top:44,
            containLabel: true
          },
          series: [{
            name:'多点会议',
            type:'pie',
            center: ['20%', '70%'],
            radius: ['50%', '55%'],
            silent:true,
            avoidLabelOverlap: false,
            hoverAnimation:false,
            labelLine: {
              normal: {
                show: false
              }
            },
            data:[]
          },{
            name:'端口会议',
            type:'pie',
            center: ['50%', '70%'],
            radius: ['50%', '55%'],
            silent:true,
            avoidLabelOverlap: false,
            hoverAnimation:false,
            labelLine: {
              normal: {
                show: false
              }
            },
            data:[]
          },{
            name:'点对点会议',
            type:'pie',
            center: ['80%', '70%'],
            radius: ['50%', '55%'],
            silent:true,
            avoidLabelOverlap: false,
            hoverAnimation:false,
            labelLine: {
              normal: {
                show: false
              }
            },
            data:[]
          },
          ]
        },

        // 会议信息
        confResourcesInfo:{},
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
        this.$router.push({
          path:routerPath
        });
      },

      // 界面按钮功能函数end

      // echart数据渲染
      async renderChartDataInit(chartConf,isNewChart=true){
        if(chartConf){
          if(chartConf.timerInterver && isNewChart){
            this.setTimer(chartConf.timerInterver)
          }
          let getData=''
          // 提供计算的变量start
          let timestamp = (new Date()).getTime()
          // 提供计算的变量end
          switch(chartConf.dataProcessingMethod){
            case "conf_resources":

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

              // // 测试调整临时params固定时间
              // let now = new Date()
              // let t = new Date('2019-09-23').setHours(now.getHours(), now.getMinutes(), now.getSeconds(), 0)
              // params.start_time=new Date('2019-09-23').setHours(0,0,0,0)
              // params.end_time=t
              // // 测试调整临时params固定时间end

              getData=await this.$api.getChartData.getStaticConfResource(params)

              if(!getData){
                return false
              }

              let isExistence = this.chartBaseInstance.getDom().attributes
              if(isExistence._echarts_instance_ && isExistence._echarts_instance_.value){
              }else{
                return false
              }

              if(isNewChart) {
                this.chartBaseInstance.setOption(this.chartOptionConfResources, true)
              }

              getData.forEach(item => {
                this.$set(this.confResourcesInfo,item.name,item.data)
              })
              let seriseData=[]
              let PMoreUsePercent = 0
              let portUsePercent = 0
              let P2pUsePercent = 0
              if(this.confResourcesInfo.tra_conf_conveyable_num_1080_30_l || this.confResourcesInfo.tra_conf_convened_num){
                PMoreUsePercent = this.confResourcesInfo.tra_conf_convened_num / (this.confResourcesInfo.tra_conf_convened_num + this.confResourcesInfo.tra_conf_conveyable_num_1080_30_l) * 100
              }
              if(this.confResourcesInfo.total_port_num || this.confResourcesInfo.free_port_num){
                portUsePercent = (this.confResourcesInfo.total_port_num - this.confResourcesInfo.free_port_num) / this.confResourcesInfo.total_port_num * 100
              }
              if(this.confResourcesInfo.p2p_conf_convened_num || this.confResourcesInfo.p2p_conf_conveyable_num){
                P2pUsePercent = this.confResourcesInfo.p2p_conf_convened_num / (this.confResourcesInfo.p2p_conf_convened_num + this.confResourcesInfo.p2p_conf_conveyable_num) * 100
              }

              let sPMoreItemData={
                name:"多点会议",
                data:[{
                  name:"已使用",
                  label: {
                    normal: {
                      show: true,
                      fontSize:16,
                      color:PMoreUsePercent>=80?'#e45959':'#4796c4',
                      position: 'center',
                      formatter: function(){
                        return PMoreUsePercent.toFixed(0) + "%"
                      }
                    },
                  },
                  itemStyle:{
                    color:PMoreUsePercent>=80?'#e45959':'#4796c4',
                  },
                  value:PMoreUsePercent,
                },{
                  name:"剩余",
                  label: {
                    normal: {
                      show: false,
                    },
                  },
                  itemStyle:{
                    color:'#43494d',
                    // borderColor:'#3a3a3a',
                    // borderWidth:1,
                  },
                  value:100-PMoreUsePercent,
                },]
              };
              let sPortItemData={
                name:"端口会议",
                data:[{
                  name:"已使用",
                  label: {
                    normal: {
                      show: true,
                      fontSize:16,
                      color:portUsePercent>=80?'#e45959':'#4796c4',
                      position: 'center',
                      formatter: function(){
                        return portUsePercent.toFixed(0) + "%"
                      }
                    },
                  },
                  itemStyle:{
                    color:portUsePercent>=80?'#e45959':'#4796c4',
                  },
                  value:portUsePercent,
                },{
                  name:"剩余",
                  label: {
                    normal: {
                      show: false,
                    },
                  },
                  itemStyle:{
                    color:'#43494d',
                    // borderColor:'#3a3a3a',
                    // borderWidth:1,
                  },
                  value:100-portUsePercent,
                },]
              };
              let sP2pItemData={
                name:"点对点会议",
                data:[{
                  name:"已使用",
                  label: {
                    normal: {
                      show: true,
                      fontSize:16,
                      color:P2pUsePercent>=80?'#e45959':'#4796c4',
                      position: 'center',
                      formatter: function(){
                        return P2pUsePercent.toFixed(0) + "%"
                      }
                    },
                  },
                  itemStyle:{
                    color:P2pUsePercent>=80?'#e45959':'#4796c4',
                  },
                  value:P2pUsePercent,
                },{
                  name:"剩余",
                  label: {
                    normal: {
                      show: false,
                    },
                  },
                  itemStyle:{
                    color:'#43494d',
                  },
                  value:100-P2pUsePercent,
                },]
              }

              seriseData=[sPMoreItemData,sPortItemData,sP2pItemData]

              // console.log(seriseData)
              this.chartBaseInstance.setOption({
                series:seriseData
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
.conf-detail--tooltip-left{
  display: inline-block;
  width: 80px;
  text-align: right;
}
</style>
