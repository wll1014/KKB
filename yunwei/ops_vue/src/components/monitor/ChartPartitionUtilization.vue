<template>
  <div style="width: 100%;height:100%;">
  <div class="area-partitions" style="width: 100%">
    <ChartDiskAge :host_moid="host_moid"></ChartDiskAge>
    <div style="color: #9ca9b1;font-size: 14px;height: 30px;line-height: 30px;">分区使用率</div>
      <div class="area-cores" style="width: 100%;margin-top:10px">
        <el-row style="margin-bottom: 12px;" :gutter="12" v-for="row,index in diskUsageNodes" :key="index">
          <el-col :span="6" v-for="item in row" :key="item.chartID">
            <el-tooltip :content="item.name" placement="top-start">
              <div class="diskusage--nodetitle">{{item.name}}</div>
            </el-tooltip>
            <ChartExtendLargeModel  :ChartID="item.chartID" :chartConf="item"></ChartExtendLargeModel>
          </el-col>
        </el-row>
      </div>
   </div>
  </div>
</template>

<script>
// import ChartDiskAge from "@/components/monitor/ChartDiskAge.vue"
export default {
  components: {
    ChartDiskAge: ()=> import('@/components/monitor/ChartDiskAge.vue'),
    ChartExtendLargeModel: ()=> import('@/components/monitor/ChartExtendLargeModel.vue'),
  },
  props:{
    host_moid:String,
  },
  data(){

    return{
      // new start

      // chart封装组件的传参
      baseChartConf:{
        name: "DiskUse",
        chartID:'',
        chartRenderMethod: "pie",
        dataRenderMethon:"ringHalf",
        // dataKey:['data','info'],
        url: ['api','getPartitionNodeData'],
        urlParams:'nextReFresh',
        // dataKey:['info'],
        // url:"cpu",
        routerPush: '跳转cpu',
        timerInterver: 300,
        options: {
          echartsCustom:{
            legend: {
              // data:[],
              orient:'vertical',
              itemWidth:10,
              itemHeight:5,
              icon:'roundRect',
              itemGap:22,
              right:20,
              // left:100,
              textStyle:{
                color:'#9ca9b1',
                padding:[1,0,0,5]
              },
              top: 20,
            },
            tooltip: {
              trigger: 'item',
              padding: [18,14],
              backgroundColor:'#141414',
              borderColor:'#383b3c',
              borderWidth:1,
              textStyle:{
                color:'#9ca9b1',
              },
              formatter:(params)=>{
                let showValue=Math.ceil(params.value) + '%'
                let htmlContent = '<div class="lchart-tootip-content--block">' +
                  '<div class="lchart-tootip-content-left">'+params.name+'</div>' +
                  '<div class="lchart-tootip-content-right">'+'&nbsp&nbsp:&nbsp' + showValue +
                  '</div></div>'
                let header='<div class="diskusage-tooltip--title">'+ '分区名称&nbsp:&nbsp&nbsp' + params.seriesName+'</div>'
                let content=htmlContent
                return header+content;
              },
            },
          },
        },
      },

      diskUsageNodes:[],

    }
  },
  methods: {
    async getDiskUseData(){
      this.diskUsageNodes=[]
      let temChildList=[]

      let res = await this.$api.getChartData.getPartitionNode(this.host_moid)
      let diskUseList=res.partitions
      for(let index in diskUseList){

        let params = {
          moid:this.host_moid,
          partition: diskUseList[index],
        }

        let chartConf = {...this.baseChartConf}
        this.$set(chartConf,'name',diskUseList[index])
        this.$set(chartConf,'chartID','diskUsage' + index)
        this.$set(chartConf,'urlParams',params)

        let options = {...this.baseChartConf.options}
        // options.title={
        //   text:diskUseList[index],
        //   top:17,
        //   left:14,
        //   textStyle:{
        //     color:'#9ca9b1',
        //     fontSize:14,
        //   },
        // }
        this.$set(chartConf,'options',options)

        let tem=parseInt(index)+1
        // console.log(tem,diskUseList.length,tem%4)

        if (tem%4 === 0){
          temChildList.push(chartConf)
          this.diskUsageNodes.push(temChildList)
          temChildList=[]
        }
        else if(tem===diskUseList.length){
          temChildList.push(chartConf)
          this.diskUsageNodes.push(temChildList)
        }
        else{
          temChildList.push(chartConf)
        }

        // let diskData = await this.$api.getChartData.getDiskageNodeData(params)
      }
      // console.log(this.diskUsageNodes)

    },
    init(){
      this.getDiskUseData()
    },
  },
  mounted(){
    this.init()
  },
  
	beforeDestroy () {

	},

}
</script>

<style>
  .area-cores .el-col{
    height: 240px;
    position: relative;
  }
  .diskusage--nodetitle{
    position: absolute;
    cursor: pointer;
    top:17px;
    left:24px;
    z-index: 99;
    color: #9ca9b1;
    font-size: 14px;
    text-align: left;
    text-overflow: ellipsis;
    white-space: nowrap;
    word-break: keep-all;
    overflow: hidden;
    max-width: 150px;
  }
  .diskusage-tooltip--title{
    max-width: 220px;
    white-space:normal;
    word-break:break-all;
    word-wrap:break-word
  }
</style>
