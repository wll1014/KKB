<template>
  <div style="width: 100%;height:100%;">
    <SelectDataRange @dataChange="dataChange" :firstLoad=false></SelectDataRange>
    <div style="width: 100%;height: 462px;margin-top: 10px;">
      <ChartExtendLargeModel ChartID="IDCpuUtilization" :chartConf="activeChartConf" :extraPlugin="extraPlugin" extraPluginClass="area-chart-plugin--cpu"></ChartExtendLargeModel>
    </div>
    <div class="area-cores" style="width: 100%;margin-top:10px">
      <el-row style="margin-bottom: 12px;" :gutter="12" v-for="row,index in cpuCores" :key="index">
        <el-col :span="6" v-for="item in row" :key="item.chartID" style="height: 240px;">
          <ChartExtendLargeModel  :ChartID="item.chartID" :chartConf="item" :extraPlugin="extraPlugin" extraPluginClass="area-chart-plugin--cpucore"></ChartExtendLargeModel>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
// import SelectDataRange from "@/components/monitor/SelectDataRange.vue"
export default {
  components: {
    SelectDataRange: ()=> import('@/components/monitor/SelectDataRange.vue'),
    ChartExtendLargeModel: ()=> import('@/components/monitor/ChartExtendLargeModel.vue'),
  },
  props:{
    host_moid:String,
  },
  data(){
    let echartsTimeFormat = this.$echarts.format.formatTime;
    return{

      // new start

      // chart封装组件的传参
      activeChartConf:{
        name: "CPU",
        chartRenderMethod: "timeline",
        dataRenderMethon:"timeline",
        // dataKey:['data','info'],
        url: ['api','getSingleHostCpuData'],
        urlParams:'nextReFresh',
        dataKey:['info'],
        // url:"cpu",
        routerPush: '跳转cpu',
        timerInterver: 300,
        options: {
          isArea:true,
          dataFormat:["percent"],
          stack:[{
              name:"user",
              data:'cpu'
            },{
              name:'system',
              data:'cpu'
            },{
              name:'iowait',
            data:'cpu'
            },{
              name:'nice',
            data:'cpu'
            },{
              name:'irq',
            data:'cpu'
            },{
              name:'softirq',
            data:'cpu'
            },{
              name:'steal',
              data:'cpu'
            },],
          grid: {
            left: 73,
            right: 58,
            bottom: 80,
            top:76,
            containLabel: false
          },
          legend:{
            top:32,
            right:162,
            textStyle:{
              color:'#9ca9b1',
              padding:[1,0,0,5],
              fontSize:14
            },
          },
        }
      },
      baseConfCpuCore:{
        name: "CPU Core",
        chartID:'',
        chartRenderMethod: "timeline",
        dataRenderMethon:"timeline",
        // dataKey:['data','info'],
        url: ['api','getCpuCoreData'],
        urlParams:'nextReFresh',
        // dataKey:['info'],
        // url:"cpu",
        routerPush: '跳转cpu',
        timerInterver: 300,
        options: {
          isArea:true,
          dataFormat:["percent"],
          grid: {
            left: 48,
            right: 44,
            bottom: 65,
            top:76,
            containLabel: false
          },
          legend:{
            show:false,
          },
          title:{}
        }
      },

      extraPlugin:{
        imgExport:true,
      },

      // new end

      // 表的实例化
      cpuCores:[],

    }
  },
  methods: {
    async getSingleHostCpu(){
      let params={
        moid:this.host_moid
      }
      // this.$set(this.activeChartConf,'urlParams',params)
      let backData = await this.$api.getChartData.getSingleHostCpuData(params)
      if(!backData){
        return false
      }

      this.cpuCores=[]
      let cpuCoresNum = backData.coreCount
      let temChildList=[]
      for(let i = 1;i <= cpuCoresNum;i++){
        let chartConf = {...this.baseConfCpuCore}
        this.$set(chartConf,'chartID','cpuCore' + i)

        // let coreParams={
        //   moid:this.host_moid,
        //   coreid:i-1
        // }
        this.$set(chartConf,'coreID',i-1)

        let options = {...this.baseConfCpuCore.options}
        options.title={
          text:'Core' + (i-1),
          top:17,
          left:14,
          textStyle:{
            color:'#9ca9b1',
            fontSize:14,
          },
        }
        this.$set(chartConf,'options',options)
        // console.log(chartConf)
        if (i % 4 === 0){
          temChildList.push(chartConf)
          this.cpuCores.push(temChildList)
          temChildList=[]
        }
        else if(i===cpuCoresNum){
          temChildList.push(chartConf)
          this.cpuCores.push(temChildList)
        }
        else{
          temChildList.push(chartConf)
        }
      }
      let defaultTimeRange=[(new Date()).getTime()-3600000,(new Date()).getTime()]
      this.dataChange(defaultTimeRange)
    },


    dataChange(val){
      if(!val){
        val=[undefined,undefined]
      }
      let params={
        moid:this.host_moid,
        start_time: val[0],
        end_time: val[1],
      }

      this.$set(this.activeChartConf,'urlParams',params)

      for(let row of this.cpuCores){
        row.forEach(item => {
          let coreParams = {...params}
          coreParams.coreid=item.coreID
          this.$set(item,'urlParams',coreParams)
        })
      }

    },

    init(){
      this.getSingleHostCpu(this.host_moid)
    },
  },
  mounted(){
    // console.log(this.host_moid)
    // this.getData()
    this.init()

  },
  
	beforeDestroy () {

	},

}
</script>

<style>
  .area-chart-plugin--cpu{
    top:20px;
    right: 38px;
  }
  .area-chart-plugin--cpucore{
    top:16px;
    right: 22px;
  }
</style>
