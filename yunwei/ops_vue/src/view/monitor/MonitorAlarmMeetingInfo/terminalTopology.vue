<template>
    <div class="theme-dark" style="height:100%;width: 100%;background-color: #232629">
      <div v-if="withoutInfo" style="font-size: 16px;color:#9ca9b1;padding-top: 200px;padding-left: 520px;padding-bottom: 150px">
        <span style="padding-right: 10px;"><i class="el-icon-info"></i></span>
        <span >
        尚 无 终 端 外 设 上 报 信 息
        </span>
      </div>


      <!--图例-->
      <div v-if="allshow">
      <div style="float: right;margin: 30px 0 0 0;">
        <span style="color: #9ca9b1;float: right;margin-right: 39px;font-size: 14px;">异常</span>
        <i class="ops-icons-bg icon-legend-orange" style="float: right;margin-right: 7px;margin-top: 8px"></i>
        <span style="color: #9ca9b1;float: right;margin-right: 35px;font-size: 14px;">正常</span>
        <i class="ops-icons-bg icon-legend-blue" style="float: right;margin-right: 7px;margin-top: 8px"></i>
      </div>
      <span><i class='ops-icons-bg icon-model-topology-normal' style='margin-left: 274px;margin-top: 250px;margin-right: 10px;float: left' ></i></span><terminalTopologyCharts style="display:inline-block;float: left"></terminalTopologyCharts><i class='ops-icons-bg icon-topology-meetRoom-normal' style='margin-left: 10px;margin-top:250px;margin-right:10px;float: left'></i><terminalTopologyChartsMore style="display:inline-block;float: left"></terminalTopologyChartsMore>
      <div style="height: 190px">
        <el-tooltip placement="bottom-start">
          <div slot="content" style="width:300px;height: 20px" v-if="tooptipData[2]" v-for="(tooptip,index) in tooptipData[2]" :key="index">{{tooptip}}</div>
          <!--<div v-if="callDetailTable[1].protocol_info[2]['video_resource_name']">-->
          <i class='ops-icons-bg icon-topology-television-normal' style='margin-left: 10px;margin-top: 110px;float: left' v-if="callDetailTable[1].protocol_info[2]['video_resource_name'].dev_status === 0"></i>
          <i class='ops-icons-bg icon-topology-television-abnormal' style='margin-left: 10px;margin-top: 110px;float: left' v-if="callDetailTable[1].protocol_info[2]['video_resource_name'].dev_status === 1"></i>
          <!--</div>-->
        </el-tooltip>
      </div>
      <div>
        <el-tooltip placement="bottom-start">
          <div slot="content" style="width:300px;height: 20px" v-if="tooptipData[1]" v-for="(tooptip,index) in tooptipData[1]" :key="index">{{tooptip}}</div>
          <!--<div v-if="callDetailTable[1].protocol_info[2]['loudspeakers']">-->
            <i class='ops-icons-bg icon-topology-microphone-normal' style='margin-left: 10px;margin-top: 60px' v-if="callDetailTable[1].protocol_info[2]['loudspeakers'].dev_status === 0"></i>
            <i class='ops-icons-bg icon-topology-microphone-abnormal' style='margin-left: 10px;margin-top: 60px' v-if="callDetailTable[1].protocol_info[2]['loudspeakers'].dev_status === 1"></i>
          <!--</div>-->
        </el-tooltip>
      </div>
      <div>
        <el-tooltip placement="bottom-start">
          <div slot="content" style="width:300px;height: 20px" v-if="tooptipData[0]" v-for="(tooptip,index) in tooptipData[0]" :key="index">{{tooptip}}</div>
          <!--<div v-if="callDetailTable[1].protocol_info[2]['microphones']">-->
            <i class='ops-icons-bg icon-topology-microphone-normal' style='margin-left: 10px;margin-top: 60px' v-if="callDetailTable[1].protocol_info[2]['microphones'].dev_status=== 0"></i>
            <i class='ops-icons-bg icon-topology-microphone-abnormal' style='margin-left: 10px;margin-top: 60px' v-if="callDetailTable[1].protocol_info[2]['microphones'].dev_status=== 1"></i>
          <!--</div>-->
        </el-tooltip>
      </div>
      <div style="height: 50px">
      </div>
      </div>
    </div>
</template>

<script>
    export default {
      components: {
        terminalTopologyCharts: () => import('@/view/monitor/MonitorAlarmMeetingInfo/terminalTopologyCharts.vue'),
        terminalTopologyChartsMore: () => import('@/view/monitor/MonitorAlarmMeetingInfo/terminalTopologyChartsMore.vue'),
      },
      name: "terminalTopology",
      props: {
        callDetailTable: {
          type:Array,
          defaultList: [],
        },
      },
      data(){
        return{
          withoutInfo:true,
          allshow:false,
          data :[],
          tooptipData:[],
        }
      },
      methods:{
        getData(){
					var params={
						"start_time":this.callDetailTable[0].start_time,
						"end_time":this.callDetailTable[0].end_time,
						"conf_status":this.callDetailTable[0].conf_status,
						"mt_e164":this.callDetailTable[0].mt_e164,
						"conf_id":this.callDetailTable[0].conf_id
					}
					this.$api.monitor.getTopology(params).then(res=>{
						if(res.data.success===1){
							this.info = res.data.data.info
							if(this.info[0].protocol_info[2]){
							  if(this.info[0].protocol_info[2]["microphones"]&&this.info[0].protocol_info[2]["video_resource_name"]&&this.info[0].protocol_info[2]["loudspeakers"]){
							    this.allshow = true
							    this.withoutInfo = false
							  }
							  this.data = this.info[0].protocol_info
							  if (this.data){
							    var list = []
							    if(this.data[2]["microphones"]){
							      for (var index in this.data[2]["microphones"]["dev_info"]){
							        for (var datas in this.data[2]["microphones"]["dev_info"][index]){
							          if(datas==='name'){
							            if(this.data[2]["microphones"]["dev_info"][index][datas]){
							              var value = "设备名称 "+": "+ this.data[2]["microphones"]["dev_info"][index][datas]
							              list.push(value)
							            }else {
							              var value = "设备名称 : 无"
							              list.push(value)
							            }
							          }
							          if(datas === "status"){
							            if(this.data[2]["microphones"]["dev_info"][index][datas]===0){
							              var value = "设备状态 : 正常"
							            }else if(this.data[2]["microphones"]["dev_info"][index][datas]===1){
							              var value = "设备状态 : 异常"
							            }
							            list.push(value)
							          }
							        }
							      }
							      this.tooptipData.push(list)
							    }
							    var list = []
							    if(this.data[2]["loudspeakers"]){
							      for (var index in this.data[2]["loudspeakers"]["dev_info"]){
							        for (var datas in this.data[2]["loudspeakers"]["dev_info"][index]){
							          if(datas==='name'){
							            if(this.data[2]["loudspeakers"]["dev_info"][index][datas]){
							              var value = "设备名称 "+": "+ this.data[2]["loudspeakers"]["dev_info"][index][datas]
							              list.push(value)
							            }else {
							              var value = "设备名称 : 无"
							              list.push(value)
							            }
							          }
							          if(datas === "status"){
							            if(this.data[2]["loudspeakers"]["dev_info"][index][datas]===0){
							              var value = "设备状态 : 正常"
							            }else if(this.data[2]["loudspeakers"]["dev_info"][index][datas]===1){
							              var value = "设备状态 : 异常"
							            }
							            list.push(value)
							          }
							        }
							      }
							      this.tooptipData.push(list)
							    }
							    var list = []
							    if(this.data[2]["video_resource_name"]){
							      for (var index in this.data[2]["video_resource_name"]["dev_info"]){
							        for (var datas in this.data[2]["video_resource_name"]["dev_info"][index]){
							          if(datas==='video_index'){
							            if( this.data[2]["video_resource_name"]["dev_info"][index][datas]){
							              var value = "视频源名称 "+": "+ this.data[2]["video_resource_name"]["dev_info"][index][datas]
							              list.push(value)
							            }else {
							              var value = "视频源名称 : 无"
							              list.push(value)
							            }
							          }
							          if(datas === "type"){
							            if(this.data[2]["video_resource_name"]["dev_info"][index][datas]===0){
							              var value = "视频源类型 : 主流"
							              list.push(value)
							            }else if(this.data[2]["video_resource_name"]["dev_info"][index][datas]===1){
							              var value = "视频源类型 : 双流"
							              list.push(value)
							            }
							          }
							        }
							      }
							      this.tooptipData.push(list)
							    }
							  }
							}
						}else if(res.data.success===0){}
					}).catch(err=>{})

        },
      },
      mounted(){
        this.getData()
      },
      watch:{
        callDetailTable(NewValue,OldValue){
          this.getData()
        }
      }
    }
</script>

<style scoped>

</style>
