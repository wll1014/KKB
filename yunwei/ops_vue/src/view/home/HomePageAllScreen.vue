<template>
  <div class="homepage--flex">
    <!-- 第一行 -->
    <div class="row" style="min-height: 75%;">
      <div class="col col-3">
        <div class="row vertical">
          <div class="col col-h-3">
            <div class="content">
              <AreaConferenceQuality ChartID="area1_1" :chartList="['conf_quality']"></AreaConferenceQuality>
            </div>
          </div>
          <div class="col col-h-3">
            <div class="content">
              <AreaConferenceResources ChartID="area2_1" :chartList="['conf_resources']"></AreaConferenceResources>
            </div>
          </div>
          <div class="col col-h-3">
            <div class="content">
              <AreaChildChartExtend ChartID="area3_1" :chartList="['statistics_curr_confs']"></AreaChildChartExtend>
            </div>
          </div>
        </div>
      </div>
      <div class="col col-6" >
        <div class="content" style="min-height: 660px;">
          <AreaMapInfo ></AreaMapInfo>
        </div>
      </div>
      <div class="col col-3">
        <div class="row">
          <div class="col col-h-3">
            <div class="content">
              <AreaAlarmInfoShort ChartID="area1_2" :chartList="['alarm_info']"></AreaAlarmInfoShort>
            </div>
          </div>
          <div class="col col-h-3">
            <div class="content">
              <AreaChildChartExtend ChartID="area2_2" :chartList="['cpu','mem','network_in','network_out','disk_use','disk_age']"></AreaChildChartExtend>
            </div>
          </div>
          <div class="col col-h-3">
            <div class="content">
              <AreaChildChartExtend ChartID="area3_2" :chartList="['reservation_resources']"></AreaChildChartExtend>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- 第二行 -->
    <div class="row" style="min-height: 25%;">
      <div class="col col-3" >
        <div class="content">
          <div class="homechart_errtip" v-if="errInfo.errConfTime" style="width: 19px;height: 19px;">
            <el-tooltip effect="dark" :content="errInfo.errConfTime" placement="top-start">
              <i class="ops-icons-bg icon-errinfo"></i>
            </el-tooltip>
          </div>
          <AreaChildChartExtend ChartID="area4_1" :chartList="['conf_time']"></AreaChildChartExtend>
        </div>
      </div>
      <div class="col col-3">
        <div class="content">
          <AreaChildChartExtend ChartID="area4_2" :chartList="['mt_call']"></AreaChildChartExtend>
        </div>
      </div>
      <div class="col col-3">
        <div class="content">
          <AreaChildChartExtend ChartID="area4_3" :chartList="['mt_online']"></AreaChildChartExtend>
        </div>
      </div>
      <div class="col col-3">
        <div class="content">
          <AreaChildChartExtend ChartID="area4_4" :chartList="['number_live_broadcasts']"></AreaChildChartExtend>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
	export default {
    components: {
      AreaConferenceQuality: () => import('@/components/home/AreaConferenceQuality.vue'),
      AreaConferenceResources: () => import('@/components/home/AreaConferenceResources.vue'),
      AreaMapInfo: () => import('@/components/home/AreaMapInfo.vue'),
      AreaChildChartExtend: () => import('@/components/home/AreaChildChartExtend.vue'),
      AreaAlarmInfoShort: () => import('@/components/home/AreaAlarmInfoShort.vue'),
    },
    data(){
      return {
        errInfo:{},
      }
    },
    
    methods:{
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
      this.initDiagnose()
    },
    
	}
</script>

<style>
  .homepage--flex{
    display:flex;
    flex: 1;
    flex-wrap:wrap;
    margin:0;
    padding: 5px;
    width: 100%;
    height:calc(100vh - 54px);
    min-width: 400px;
    box-sizing: border-box;
  }

  .row{
    display:-webkit-flex;
    display:flex;
    flex: 1;
    flex-wrap:wrap;
    flex-basis: 100%;
    max-width: 100%;
    box-sizing: border-box;
    background-color:#1e2224;
    align-content:stretch;
  }

  .col{
    display:-webkit-flex;
    display:flex;
    flex: 1;
    box-sizing: border-box;
    background-color: #1e2224;
    min-width: 390px;
    align-content:stretch;
    /*border: #299dff 1px solid;*/
  }

  .col-3{
    flex-basis: 25%;
  }
  .col-6{
    flex-basis: 50%;
  }
  .col-h-3{
    min-height: 33.3%;
  }
  .row.vertical .col-h-3{
    flex-basis: 33.3%;
    align-self: stretch;
  }
  .col .content{
    display:-webkit-flex;
    display:flex;
    flex: auto;
    position: relative;
    background-color: #1e2224;
    /*height: 100%;*/
    flex-basis: 100%;
    padding: 5px;
    box-sizing: border-box;
    min-height: 210px;
    /*align-content:stretch;*/
  }
  .content>div{
    flex: 1;
    flex-basis: 100%;
    align-self: stretch;
    height: 100%;

  }
  .content>.homechart_errtip{
    position: absolute;
    z-index: 10;
    left: 85px;
    top:15px;
  }
</style>
