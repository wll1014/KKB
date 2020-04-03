<template>
  <div style="width: 100%;height:100%;">
  <div class="diskages" style="width: 100%">
    <div style="color: #9ca9b1;font-size: 14px;height: 30px;line-height: 30px;">磁盘寿命</div>
    <div class="area-cores" style="width: 100%;margin-top:10px">
      <!--<el-row style="margin-bottom: 12px;" :gutter="12" v-for="row,index in diskageNodes" :key="index">
        <el-col :span="6" v-for="item in row" :key="item.chartID" style="height: 240px;">
          <ChartExtendLargeModel  :ChartID="item.chartID" :chartConf="item"></ChartExtendLargeModel>
        </el-col>
      </el-row>-->
      <div style="height: 40px;background-color: #232629;font-size: 16px;text-align: center;margin-bottom: 10px;" v-if="noData">
        <span style="vertical-align: -10px;">该磁盘不支持寿命检测</span>
      </div>

      <el-row style="margin-bottom: 12px;background-color: #232629;" :gutter="12" v-for="row,index in diskageNodes" :key="index">
        <el-col :span="12" v-for="item in row" :key="item.drive" style="height: 240px;">
          <!--<ChartExtendLargeModel  :ChartID="item.chartID" :chartConf="item"></ChartExtendLargeModel>-->
          <div class="diskage--block">
            <div style="position: absolute;left: 235px;top:68px;font-size: 16px;">{{item.drive}}</div>
            <div style="position: absolute;left: 235px;top:127px;font-size: 16px;width:calc(100% - 375px);">
              <span :class='["diskage--usepercent",item.data>= 80? "alarm" : ""]'>
                {{item.data + "%"}}
              </span>
              <span style="float: right;">
                {{(100 - item.data) + "%"}}
              </span>
            </div>
            <div style="display: inline-block;"><i class="ops-icons-bg icon-disk"></i></div>
            <div style="display: inline-block;width:calc(100% - 160px);margin-left: 30px;vertical-align: 45px;">
              <el-progress :percentage="item.data" :color="item.data >= 80 ? '#e45959':'#4796c4'" :show-text=false></el-progress>
            </div>
          </div>
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
        name: "DiskAge",
        chartID:'',
        chartRenderMethod: "pie",
        dataRenderMethon:"ringHalf",
        // dataKey:['data','info'],
        url: ['api','getDiskageNodeData'],
        urlParams:'nextReFresh',
        // dataKey:['info'],
        // url:"cpu",
        routerPush: '跳转cpu',
        timerInterver: 300,
        options: {
          legend:{
            show:false,
          },
          title:{}
        }
      },

      diskageNodes:[],
      noData:false,
    }
  },
  methods: {
    async getDiskAgeData(){
      this.diskageNodes=[]
      let temChildList=[]

      let res = await this.$api.getChartData.getDiskageNode(this.host_moid)
      let diskAgeList=res.drives

      if(diskAgeList.length>0){
        this.noData=false
      }else{
        this.noData=true
      }

      for(let index in diskAgeList){
        let params = {
          moid:this.host_moid,
          drive: diskAgeList[index],
        }

        // let chartConf = {...this.baseChartConf}
        // this.$set(chartConf,'chartID','diskAge' + index)
        // this.$set(chartConf,'urlParams',params)
        //
        // let options = {...this.baseChartConf.options}
        // options.title={
        //   text:diskAgeList[index],
        //   top:17,
        //   left:14,
        //   textStyle:{
        //     color:'#9ca9b1',
        //     fontSize:14,
        //   },
        // }
        // this.$set(chartConf,'options',options)

        let diskData = await this.$api.getChartData.getDiskageNodeData(params)
        this.$set(diskData,'drive',diskAgeList[index])

        let tem=parseInt(index)+1
        if (tem % 2 === 0){
          temChildList.push(diskData)
          this.diskageNodes.push(temChildList)
          temChildList=[]
        }
        else if(tem===diskAgeList.length){
          temChildList.push(diskData)
          this.diskageNodes.push(temChildList)
        }
        else{
          temChildList.push(diskData)
        }
        // if (tem % 2 === 0){
        //   temChildList.push(chartConf)
        //   this.diskageNodes.push(temChildList)
        //   temChildList=[]
        // }
        // else if(tem===diskAgeList.length){
        //   temChildList.push(chartConf)
        //   this.diskageNodes.push(temChildList)
        // }
        // else{
        //   temChildList.push(chartConf)
        // }

      }

    },
    init(){
      this.getDiskAgeData()
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
  .diskage--block{
    box-sizing: border-box;
    padding: 64px 110px;
    position: relative;
  }
  .diskage--usepercent{
    color: #4796c4;
  }
  .diskage--usepercent.alarm{
    color: #e45959;
  }
</style>
