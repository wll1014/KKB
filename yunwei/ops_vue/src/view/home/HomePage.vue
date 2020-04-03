<template>
  <div>
    <div class="home-page-class" v-if="!showAllScreen">
      <div class="upper-row-class">
        <el-row :gutter="10" style="height: 100%;padding-bottom: 5px;">
          <el-col :span="6" style="height: 100%;">
            <el-row >
              <el-col >
                <div class="grid-content bg-purple ">
                  <AreaConferenceQuality ChartID="area1_1" :chartList="['conf_quality']"></AreaConferenceQuality>
                </div>
              </el-col>
            </el-row>
            <el-row>
              <el-col>
                <div class="grid-content bg-purple">
                  <AreaConferenceResources ChartID="area2_1" :chartList="['conf_resources']"></AreaConferenceResources>
                </div>
              </el-col>
            </el-row>
            <el-row >
              <el-col>
                <div class="grid-content bg-purple">
                  <AreaChildChartExtend ChartID="area3_1" :chartList="['statistics_curr_confs']"></AreaChildChartExtend>
                </div>
              </el-col>
            </el-row>
          </el-col>
          <el-col :span="12" style="height:100%">
            <div class="grid-content bg-purple-dark">
              <AreaMapInfo style="height:100%"></AreaMapInfo>
            </div>
          </el-col>
          <el-col :span="6">
            <el-row >
              <el-col>
                <div class="grid-content bg-purple">
                  <AreaAlarmInfoShort ChartID="area1_2" :chartList="['alarm_info']"></AreaAlarmInfoShort>
                </div>
              </el-col>
            </el-row >
            <el-row>
              <el-col>
                <div class="grid-content bg-purple">
                  <AreaChildChartExtend ChartID="area2_2" :chartList="['cpu','mem','network_in','network_out','disk_use','disk_age']"></AreaChildChartExtend>
                </div>
              </el-col>
            </el-row>
            <el-row >
              <el-col>
                <div class="grid-content bg-purple">
                  <AreaChildChartExtend ChartID="area3_2" :chartList="['reservation_resources']"></AreaChildChartExtend>
                </div>
              </el-col>
            </el-row>
          </el-col>
        </el-row>
      </div>
      <div class="below-row-class">
        <el-row :gutter="10" >
          <el-col :span="6">
            <div class="grid-content bg-purple">
              <div class="homechart_errtip" v-if="errInfo.errConfTime" style="width: 19px;height: 19px;">
                <el-tooltip effect="dark" :content="errInfo.errConfTime" placement="top-start">
                  <i class="ops-icons-bg icon-errinfo"></i>
                </el-tooltip>
              </div>
              <AreaChildChartExtend ChartID="area4_1" :chartList="['conf_time']"></AreaChildChartExtend>
            </div>
          </el-col>
          <el-col :span="6"><div class="grid-content bg-purple">
            <AreaChildChartExtend ChartID="area4_2" :chartList="['mt_call']"></AreaChildChartExtend>
          </div></el-col>
          <el-col :span="6"><div class="grid-content bg-purple">
            <AreaChildChartExtend ChartID="area4_3" :chartList="['mt_online']"></AreaChildChartExtend>
          </div></el-col>
          <el-col :span="6"><div class="grid-content bg-purple">
            <AreaChildChartExtend ChartID="area4_4" :chartList="['number_live_broadcasts']"></AreaChildChartExtend>
          </div></el-col>
        </el-row>
      </div>
    </div>
    <div v-if="showAllScreen">
      <HomePageAllScreen></HomePageAllScreen>
    </div>
  </div>
</template>

<script>
	// import AreaConferenceStatistics from "@/components/home/AreaConferenceResources.vue"
	// import AreaMapInfo from "@/components/home/AreaMapInfo.vue"
  // import AreaMapInfo2 from "@/components/home/AreaMapInfo2.vue"
  // import ChartBase from "@/components/home/ChartBase.vue"
	export default {
		// components:{
		// 	AreaConferenceStatistics,
    //   AreaMapInfo,
    //   AreaMapInfo2,
    //   // ChartBase,
		// },
    components: {
      HomePageAllScreen: () => import('@/view/home/HomePageAllScreen.vue'),
      AreaConferenceQuality: () => import('@/components/home/AreaConferenceQuality.vue'),
      AreaConferenceResources: () => import('@/components/home/AreaConferenceResources.vue'),
      AreaMapInfo: () => import('@/components/home/AreaMapInfo.vue'),
      AreaChildChartExtend: () => import('@/components/home/AreaChildChartExtend.vue'),
      AreaAlarmInfoShort: () => import('@/components/home/AreaAlarmInfoShort.vue'),
    },
    data(){
      return {
        showAllScreen:false,
        errInfo:{},
      }
    },
    
    methods:{
      screenIsAdaptation(){
        let pageWidth=window.innerWidth
        let pageHeight=window.innerHeight
        // console.log(pageWidth,pageHeight)
        if(parseInt(pageWidth) < 1600 || parseInt(pageHeight) < 900) {
          let msg = "当前浏览器非最佳适配分辨率， 建议分辨率1600 * 900以上，以获取更好的浏览体验。"
          this.$message(msg)
          // this.showAllScreen = true
        }
      },

      async initDiagnose(){

        // 会议时长图表诊断
        let params={
          start_time:new Date().setHours(0, 0, 0, 0)
        }

        // 当前正在召开的会议数
        let data1 = await this.$api.homePage.getStatisticsConfNumber(params)
        let confInfo={}
        data1.forEach((item,index)=>{
          let total=0
          Object.values(item.data).forEach(i => total += i)
          // console.log(total)
          confInfo[item.name]=total
        })

        // 当前会议时长统计的会议数量
        let data2 = await this.$api.homePage.getUrlDataSync('/conf_time/',params)

        let onGoingConf = confInfo.on_going_conf
        let sum = data2.reduce((total, item) => total + Number(item.data), 0)

        // 如果正在召开的会议数>当前会议时长统计的会议数量:则判断原始数据有创会消息丢失
        if((onGoingConf - sum) > 0) {
          this.$set(this.errInfo,'errConfTime','可能存在数据丢失，部分会议时长未统计')
        }else{
          this.$set(this.errInfo,'errConfTime',false)
        }
      },
    },
    mounted() {
    	// this.setHeight()
      // this.screenIsAdaptation()
      this.initDiagnose()
    },
    
	}
  // :style='homePageStyle'
</script>

<style>
  .home-page-class{
    height:calc(100vh - 70px);
    max-width:100%;
    padding: 5px 10px 10px 10px;
    /*padding: 10px;*/
    /*margin-bottom: 10px;*/
    min-height: 768px;
    /*overflow: hidden;*/
  }
  .upper-row-class{
    /* height:calc((100vh - 70px) / 4 * 3); */
    height: 75%;
  }
  .below-row-class{
    /* height:calc((100vh - 70px) / 4); */
    height: 25%;
  }
  .el-row {
    /* margin-bottom: 10px; */
    /* height: 25%; */
    /* padding: 5px 0; */
  }
  .el-row:last-child {
    margin-bottom: 0;
  }
  .el-col {
    border-radius: 4px;
    height:100%
  }
  .bg-purple {
    background: #232629;
  }
  .bg-purple-dark {
    background: #232629;
  }
  .grid-content {
    position: relative;
    border-radius: 0px;
    height: 100%;
  }
  .row-bg {
    padding: 10px 0;
    background-color: #f9fafc;
  }
  .upper-row-class>.el-row>.el-col>.el-row {
    height: 33.3%;padding: 5px 0;
  }
  .upper-row-class > .el-row > .el-col-12 {
    padding: 5px 0;
  }
  .below-row-class>.el-row {
    height: 100%;
  }
  .grid-content.bg-purple>div{
    height: 100%;
    width: 100%;
  }
  .grid-content>.homechart_errtip{
    position: absolute;
    z-index: 10;
    left: 80px;
    top:9px;
  }
</style>
