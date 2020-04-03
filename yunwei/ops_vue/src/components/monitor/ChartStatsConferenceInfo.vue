<template>
  <div class="theme-dark" style="height: 100%;width:100%;position: relative">
    <div style="position: absolute;top:0px;left:20px;z-index: 9;">
      <div class="conf-filter--layout">
        <el-select style="margin-right: 7px;width: 240px;" @change="filterChangeDomainPlatform" filterable :popper-append-to-body="false" popper-class="theme-dark" v-model="optionSelectedDomainPlatform" placeholder="请选择" >
          <el-option
            v-for="item in optionsDomainPlatform" :key="item.moid" :label="item.name" :value="item.moid">
          </el-option>
        </el-select>
      </div>
      <div class="conf-filter--layout">
        <el-select style="margin-right: 7px;width: 240px;" @change="filterChangeMachineRoom" filterable :popper-append-to-body="false" popper-class="theme-dark" v-model="optionSelectedMachineRoom" placeholder="请选择" >
          <el-option
            v-for="item in optionsMachineRoom" :key="item.moid" :label="item.name" :value="item.moid">
          </el-option>
        </el-select>
      </div>
    </div>
    <div style="height: 100%;width:100%;">
      <!--<ChartBase :chartID="ChartID" :ref="ChartID" @chartInstanceOver="chartInstanceOver"></ChartBase>-->
      <ChartBase :chartID="ChartID" :ref="ChartID"></ChartBase>
    </div>
      <div style="width:370px;position: absolute;top: 58px; left:15%;z-index: 5;">
        <div style="left:67px;position: absolute;font-size: 16px;color:#9ca9b1;">传统会议</div>
        <div style="left:67px;position: absolute;top: 29px;text-align: left;font-size: 14px;color: #5d6266;">
          <div style="margin-bottom: 8px">已召开：{{confResourcesInfo.tra_conf_convened_num}}</div>
          <div style="margin-bottom: 8px">可召开：1080P30会议(大方/小方)：{{confResourcesInfo.tra_conf_conveyable_num_1080_30_l}}/{{confResourcesInfo.tra_conf_conveyable_num_1080_30_s}}</div>
          <div style="margin-bottom: 8px;margin-left: 56px;">1080P60会议(大方/小方)：{{confResourcesInfo.tra_conf_conveyable_num_1080_60_l}}/{{confResourcesInfo.tra_conf_conveyable_num_1080_60_s}}</div>
          <div style="margin-bottom: 8px;margin-left: 56px;">720P30会议(大方/小方)&nbsp&nbsp：{{confResourcesInfo.tra_conf_conveyable_num_720_30_l}}/{{confResourcesInfo.tra_conf_conveyable_num_720_30_s}}</div>
          <div style="margin-bottom: 8px;margin-left: 56px;">720P60会议(大方/小方)&nbsp&nbsp：{{confResourcesInfo.tra_conf_conveyable_num_720_60_l}}/{{confResourcesInfo.tra_conf_conveyable_num_720_60_s}}</div>
          <!--<div style="margin-left: 56px;">
            &lt;!&ndash;<div style="">1080P30会议：{{confResourcesInfo.tra_conf_conveyable_num_1080_30}}</div>&ndash;&gt;
            &lt;!&ndash;<div style="">端口会议：{{confResourcesInfo.port_num}}</div>&ndash;&gt;
          </div>-->
        </div>
      </div>
      <div style="width:330px;position: absolute;top: 58px; left:45%;z-index: 5;">
        <div style="left:67px;position: absolute;font-size: 16px;color:#9ca9b1;">端口会议</div>
        <div style="left:67px;position: absolute;top: 29px;text-align: left;font-size: 14px;color: #5d6266;">
          <div style="margin-bottom: 8px">已召开：{{confResourcesInfo.port_conf_convened_num}}</div>
          <div style="margin-bottom: 8px;">已用端口数：{{confResourcesInfo.total_port_num-confResourcesInfo.free_port_num}}</div>
          <div style="">端口剩余数：{{confResourcesInfo.free_port_num}}</div>
        </div>
      </div>
      <div style="width:330px;position: absolute;top: 58px; left:70%;z-index: 5;">
        <div style="left:67px;position: absolute;font-size: 16px;color:#9ca9b1;">点对点会议</div>
        <div style="left:67px;position: absolute;top: 29px;text-align: left;font-size: 14px;color: #5d6266;">
          <div style="margin-bottom: 8px">已召开：{{confResourcesInfo.p2p_conf_convened_num}}</div>
          <div style="">可召开：{{confResourcesInfo.p2p_conf_conveyable_num}}</div>
        </div>
      </div>
  </div>
</template>

<script>
import ChartBase from "@/components/home/ChartBase.vue"
export default {
  name: "ChartStatsConferenceInfo",
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
  watch: {
    urlParams: {
      deep: true,
      handler: function (newVal, oldVal) {
        // console.log("ChartStatsConferenceInfo --- > urlParams : " + newVal.moid)
        // this.$refs[this.ChartID].init();
        this.$set(this.activeChart,'params',newVal)
        this.renderChartDataInit(this.activeChart,false)
      }
    },
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
          params:'nextReFresh',
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
      urlParams:null,
      // 过滤信息
      optionSelectedDomainPlatform: '',
      optionsDomainPlatform: [],
      optionSelectedMachineRoom: '',
      optionsMachineRoom: [],

      defaultDomainPlatform:'',//默认显示的第一个平台域

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
          top:55,
          containLabel: true
        },
        series: [{
          name:'多点会议',
          type:'pie',
          center: ['15%', '50%'],
          radius: ['47%', '49%'],
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
          center: ['45%', '50%'],
          radius: ['47%', '49%'],
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
          center: ['70%', '50%'],
          radius: ['47%', '49%'],
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
      // this.$router.push({
      //   path:routerPath
      // });
    },

    // 过滤项变化
    async filterChangeDomainPlatform(val,reFresh=false){
      this.optionSelectedMachineRoom= '',
      this.optionsMachineRoom= []
      if(val) {
        await this.getMachineRoomInfo(val)
      }
    },
    filterChangeMachineRoom(val){
        let newFilterParams={
          platform_moid:this.optionSelectedDomainPlatform === 'all' ? null : this.optionSelectedDomainPlatform,
          room_moid:this.optionSelectedMachineRoom === 'all' ? null : val,
        }
        this.urlParams={...newFilterParams}
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
        switch(chartConf.dataProcessingMethod){
          case "conf_resources":
            if(isNewChart) {
              this.chartBaseInstance.setOption(this.chartOptionConfResources, true)
            }

            if(this.activeChart.params==="nextReFresh"){
              return false
            }

            getData = await this.$api.getChartData.getStaticConfResource(this.activeChart.params)
            if(!getData){
              return false
            }

            let isExistence = this.chartBaseInstance.getDom().attributes
            if(isExistence._echarts_instance_ && isExistence._echarts_instance_.value){
            }else{
              return false
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
                    color:PMoreUsePercent>79?'#e45959':'#4796c4',
                    position: 'center',
                    formatter: function(){
                      return PMoreUsePercent.toFixed(0) + "%"
                    }
                  },
                },
                itemStyle:{
                  color:PMoreUsePercent>79?'#e45959':'#4796c4',
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
                    color:portUsePercent>79?'#e45959':'#4796c4',
                    position: 'center',
                    formatter: function(){
                      return portUsePercent.toFixed(0) + "%"
                    }
                  },
                },
                itemStyle:{
                  color:portUsePercent>79?'#e45959':'#4796c4',
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
                    color:P2pUsePercent>79?'#e45959':'#4796c4',
                    position: 'center',
                    formatter: function(){
                      return P2pUsePercent.toFixed(0) + "%"
                    }
                  },
                },
                itemStyle:{
                  color:P2pUsePercent>79?'#e45959':'#4796c4',
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

    // api start
    async getAllPlatformDomainInfo(){
      let platformDomainInfo = await this.$api.globalData.allPlatformDomain()

      this.optionsDomainPlatform= []
      let filterDomain = platformDomainInfo.filter(item => item.domain_type===1) //过滤出平台域
      this.optionsDomainPlatform = this.optionsDomainPlatform.concat(filterDomain)
      this.defaultDomainPlatform=filterDomain[0].moid
      this.$nextTick(function () {
        this.optionSelectedDomainPlatform = filterDomain[0].moid
      });
      await this.getMachineRoomInfo(filterDomain[0].moid)

    },
    async getMachineRoomInfo(id){
      // this.optionSelectedMachineRoom= 'all',
      this.optionsMachineRoom= []
      let machineRoomInfo = await this.$api.homePage.getMachineRoomInfo(id)
      this.optionsMachineRoom=machineRoomInfo
      this.$nextTick(function () {
        this.optionSelectedMachineRoom=machineRoomInfo[0] ? machineRoomInfo[0].moid : ''
        this.filterChangeMachineRoom(this.optionSelectedMachineRoom)
      });

    },
    // api end

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

<style scoped>

</style>
