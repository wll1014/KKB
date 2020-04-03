<template>
	<!-- 呼叫链路 -->
  <div style="background: #232629 ;width:100%;height:100%" class="theme-dark" >
    <div style="font-size: 16px;color:#9ca9b1;padding-top: 200px;padding-left: 520px;padding-bottom: 150px" v-show="withoutDetection">
      <span style="padding-right: 10px;"><i class="el-icon-info"></i></span>
      <span >
        尚 无 呼 叫 链 路 数 据
      </span>
    </div>
    <div style="height: 100%" v-if="showAll">
      <linkdetectioncharts style='width: 1500px;' :leth='leth' :timeOptions='timeOptions' :type='1' :getData='linkGetCallData' @timeOptionId='timeOptionId'></linkdetectioncharts>
    </div>
  </div>
</template>

<script>
	export default {
		props: {
			callDetailTable: {
				type:Array,
				defaultList: []
			},
		},
		components:{
			linkdetectioncharts: () => import('@/view/monitor/LinkDetection/LinkDetectionCharts.vue'),
		},
		data() {
			return {
				linkGetMeetingData:{},
				linkGetCallData:{},
				timeOptions:[],											//呼叫用户时间选项
				start_time:'',
				end_time:'',
        withoutDetection:false,
        showAll:true,
				leth:10,
        call_type:'',
			}
		},
		methods: {
			//查询呼叫链路Call_id以及显示的时间选项
			getData(){
				// console.log(this.callDetailTable[1])
				if(this.callDetailTable[1].mt_prot==="SIP"){
					if(!this.callDetailTable[0].mt_e164){
					  var mtE164 = this.callDetailTable[0].mt_addr
					}else {
					  var mtE164 = this.callDetailTable[0].mt_e164
					}
					var params = {
					  "conf_id":this.callDetailTable[0].conf_id,
					  "mt_e164":mtE164,
					  "start_time":this.callDetailTable[0].start_time,
					  "end_time":this.callDetailTable[0].end_time
					}
					this.$api.monitor.meetingInfoLinkCallId(params).then(res=>{
					  if(res.data.success === 1){
					    if(res.data.data.info!==[]&&res.data.data.info.length!==0){
					      for (var i in res.data.data.info){
					        res.data.data.info[i].timestamp = res.data.data.info[i].timestamp.replace("T", " ");
					        res.data.data.info[i].timestamp = res.data.data.info[i].timestamp.replace("Z", " ");
					      }
					    }
					    this.timeOptions =[...res.data.data.info]
					    this.start_time = res.data.data.start_time
					    this.end_time = res.data.data.end_time
					  }
					}).catch(err=>{
					  console.log(err)
					})
				}else{
					this.showAll=false
					this.withoutDetection=true
				}
        
			},
			timeOptionId(val){
				//用传来的时间call_id获取呼叫链路的信息
        for(var i in this.timeOptions){
          if(this.timeOptions[i].call_id===val){
            this.call_type = this.timeOptions[i].call_type
          }
        }
        if(!this.callDetailTable[0].mt_e164){
          var mtE164 = this.callDetailTable[0].mt_addr
        }else {
          var mtE164 = this.callDetailTable[0].mt_e164
        }
        var params = {
          "conf_id":this.callDetailTable[0].conf_id,
          "mt_e164":mtE164,
					"call_id":val,
					"start_time":this.start_time,
					"end_time":this.end_time,
          "call_type":this.call_type
				}
				this.$api.monitor.meetingInfoLinkCallInfo(params).then(res=>{
					if (res.data.success === 1){
						if(res.data.data.info.length>this.leth){
							this.leth = res.data.data.info.length
						}
						this.linkGetCallData = res.data.data
					}else if(res.data.success===0){
					  console.log(res.data.msg)
          }
				}).catch(err=>{
          console.log(err)
        })
			},
		},
		mounted(){
			this.getData()
		},
		watch: {
			callDetailTable(newValue, oldValue) {
				this.getData()
			}
		},
	}
</script>

<style>
</style>
