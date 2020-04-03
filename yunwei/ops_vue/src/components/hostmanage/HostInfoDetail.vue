<template>
	<div class="host-info-detail">
    <div class="button-back" style="">
      <el-button icon="ops-icons-bg icon-arrow-circle-left" @click="back" circle></el-button>
    </div>
    <div class="area-host-detail">
      <div style="font-size: 14px;line-height: 52px;">服务器信息</div>
      
      <div class="tbody-content" style="">
        <div class="tbody">
          <el-row>
            <el-col :span="5">
            <div class="detail-content">
              <span>主机名称</span>
              <span>{{hostDetailinfo.name}}</span>
            </div>
            </el-col>
            <el-col :span="5">
            <div class="detail-content">
              <span>IP地址</span>
              <span>{{hostDetailinfo.local_ip}}</span>
            </div>
            </el-col>
            <el-col :span="5">
            <div class="detail-content">
              <span>主机类型</span>
              <span>{{hostDetailinfo.machine_type}}</span>
            </div>
            </el-col>
            <el-col :span="5">
            <div class="detail-content">
              <span>所属机框</span>
              <span>{{hostDetailinfo.frame_name}}</span>
            </div>
            </el-col>
            <el-col :span="4">
            </el-col>
          </el-row>
          <el-row>
            <el-col :span="5">
            <div class="detail-content">
              <span >所属平台域</span>
              <span>{{hostDetailinfo.domain_name}}</span>
            </div>
            </el-col>
            <el-col :span="5">
            <div class="detail-content">
              <span>所属机房</span>
              <span>{{hostDetailinfo.room_name}}</span>
            </div>
            </el-col>
            <el-col :span="5">
            <div class="detail-content">
              <span>所属分组</span>
              <span>{{hostDetailinfo.group}}</span>
            </div>
            </el-col>
            <el-col :span="5">
            <div class="detail-content">
              <span>主机状态</span>
              <span @click="alarmInfoRouter(hostDetailinfo)" v-if="hostDetailinfo.status === 1" class="button-alarm-hostdetailinfo">异常</span>

              <span v-else>正常</span>
              <!--span :style="{'color':hostDetailinfo.status === 1 ? '#e45959':''}">
                {{hostDetailinfo.status ? '异常' : '正常'}}
              </span>-->
            </div>
            </el-col>
            <el-col :span="4">
            </el-col>
          </el-row>
          <el-row>
            <el-col :span="5">
            <div class="detail-content">
              <span>工作模式</span>
              <span>{{hostDetailinfo.cluster}}</span>
            </div>
            </el-col>
            <el-col :span="5">
            <div class="detail-content">
              <span>服务器运行时间</span>
              <span :style="{'color':hostDetailinfo.uptime === '异常' ? '#e45959':''}">
                {{hostDetailinfo.uptime === '异常' ? '异常': hostDetailinfo.uptime}}
              </span>
            </div>
            </el-col>
            <el-col :span="5">
            </el-col>
            <el-col :span="5">
            </el-col>
            <el-col :span="4">
            </el-col>
          </el-row>
        </div>
      </div>
    
      <div class="tab-hostdetail">
        <KdTabCommon :tab-list="tabList" :active-tab="activeTab" class-name="" @tab-change="tabChange" :width=18></KdTabCommon>
      </div>
      <div class="area-tab-content">
        <div style="min-width: 1200px;">
          <component :is="activeTab" :host_moid="host_moid" ref="chartInstance"></component>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// import ChartCpuUtilization from "@/components/monitor/ChartCpuUtilization.vue"
// import ChartMemUtilization from "@/components/monitor/ChartMemUtilization.vue"
// import ChartLoadUtilization from "@/components/monitor/ChartLoadUtilization.vue"
// import ChartNetworkUtilization from "@/components/monitor/ChartNetworkUtilization.vue"
// import ChartPartitionUtilization from "@/components/monitor/ChartPartitionUtilization.vue"
// import TOPNProcess from "@/components/monitor/TOPNProcess.vue"
// import HostInfoDetailIPinfo from "@/components/hostmanage/HostInfoDetailIPinfo.vue"
export default {
  components: {
    HostInfoDetailIPinfo: () => import('@/components/hostmanage/HostInfoDetailIPinfo.vue'),
    ChartCpuUtilization: () => import('@/components/monitor/ChartCpuUtilization.vue'),
    ChartMemUtilization: () => import('@/components/monitor/ChartMemUtilization.vue'),
    ChartLoadUtilization: () => import('@/components/monitor/ChartLoadUtilization.vue'),
    ChartNetworkUtilization: () => import('@/components/monitor/ChartNetworkUtilization.vue'),
    ChartPartitionUtilization: () => import('@/components/monitor/ChartPartitionUtilization.vue'),
    TOPNProcess: () => import('@/components/monitor/TOPNProcess.vue'),
    KdTabCommon: () => import('@/components/common/KdTabCommon.vue'),
  },
  props:{
    host_moid:String,
  },
  data() {
  	return {
      activeTab:'HostInfoDetailIPinfo',
      tabList:[
        ['HostInfoDetailIPinfo','服务器多个IP信息'],
        ['ChartCpuUtilization','CPU使用率'],
        ['ChartLoadUtilization','CPU平均负载值'],
        ['ChartMemUtilization','内存使用率'],
        ['ChartPartitionUtilization','磁盘状态'],
        ['ChartNetworkUtilization','网口进出口带宽'],
        ['TOPNProcess','应用统计'],],
      hostDetailinfo:'',
      // hostDetailIPinfo:[],
    };
    },
  methods: {
    back(){
      this.$emit('back',true);
    },
    // tab页变化函数
    tabChange(val){
      // console.log(val)
      this.activeTab=val
    },
    // 获取单台主机详情
    getSingleHostInfo(host_moid){
      this.$api.hostManageApi.getSingleHostInfo(host_moid)
      	.then(res => {
      		this.hostDetailinfo = res.data.data
          // console.log(this.hostDetailinfo)
          for(let key in this.hostDetailinfo){
            if(this.hostDetailinfo[key]===''){
              // console.log(item[key]);
              this.hostDetailinfo[key]='   ----'
            }
          }
          // 获取服务器运行时间
          this.$api.monitor.getUptime(host_moid)
            .then(res=>{
              let uptime=res.data.data["system.uptime.duration.ms"]
              if(uptime===-1 || uptime===undefined){
                this.$set(this.hostDetailinfo,"uptime","异常")
              }else{
                let time=this.timeMillisecondAnalysis(uptime)
                this.$set(this.hostDetailinfo,"uptime",time)
              }
          })
      	})
    },

    //告警异常点击跳转
    alarmInfoRouter(row){
      // console.log(row.name)
      this.$router.push({
        name:'monitor-alarm',
        // path:chartConf.routerPush
        params:{
          type:'alarmDev',
          urlParams:{
            search:row.name
          }
        }
      });
    },

    // 其他函数（频繁使用可放置通用js）
    timeMillisecondAnalysis(val){
      let temData;
      // temData=val/1000
      if(parseInt(val/31104000000)){
        temData=parseInt(val/31104000000) + "年"
      }else if(parseInt(val/2592000000)){
        temData=parseInt(val/2592000000) + "个月"
      }else if(parseInt(val/86400000)){
        temData=parseInt(val/86400000) + "天"
      }else if(parseInt(val/3600000)){
        temData=parseInt(val/3600000) + "小时"
      }else{
        temData=parseInt(val/60000) + "分钟"
      }
      return temData
    },

    //初始化函数
    initSingleHostInfo(){
      this.getSingleHostInfo(this.host_moid);
    }
  },
  mounted() {
    this.initSingleHostInfo();
  	// this.getHostInfoList();
  }
}
</script>

<style>
  .host-info-detail .button-back{
    position:absolute;
    top:13px;
    left:20px;
  }
  .area-host-detail{
    margin-left: 60px;
    margin-right: 60px;
    color: #9ca9b1;
  }
  .tbody-content{
    margin: 10px 0px;
    height: 140px;
    border-bottom: #3d4046 1px dashed ;
  }
  .detail-content{
    color: #9ca9b1;
    font-size: 14px;
    line-height: 38px;
  }
  .detail-content span{
    /*margin-right: 20px;*/
    display: inline-block;
    width: 110px;
  }
  /*.detail-content span:last-child{*/
    /*margin-right: 0px;*/
  /*}*/
  .detail-content span:first-child{
    color: #5d6266;
  }
  .tab-hostdetail{
    margin-top: 40px;
    margin-bottom: 20px;
  }
  .button-alarm-hostdetailinfo{
    color: #e45959;
    cursor: pointer;
    text-decoration: underline;
    font-size: 14px;
  }
</style>
