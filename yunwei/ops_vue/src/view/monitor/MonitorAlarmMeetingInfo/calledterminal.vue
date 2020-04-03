<!-- 点对点会议被叫终端 -->
<template>
	<div>
    <div style="padding-top: 34px;color: #9ca9b1;font-size: 14px;position: relative" class='callterminal'>
    <div style="margin-bottom: 25px">
      <span style="width: 335px;display: inline-block">
        <span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">终端名称</span><span>{{ terminalFormInfo.mt_name}}</span>
      </span>
      <span style="width: 335px;display: inline-block">
        <span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">设备IP</span><span>{{ terminalFormInfo.mt_addr}}</span>
      </span>
      <span style="width: 335px;display: inline-block">
        <span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">E164号</span><span>{{ terminalFormInfo.mt_e164}}</span>
      </span>
      <span style="display: inline-block">
        <span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">协议类型</span><span>{{ terminalFormInfo.mt_prot}}</span>
      </span>
    </div>
    <div style="margin-bottom: 37px">
      <span style="width: 335px;display: inline-block">
        <span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">软件版本</span><span>{{ terminalFormInfo.mt_soft}}</span>
      </span>
      <span style="width: 335px;display: inline-block">
        <span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">设备型号</span><span>{{ terminalFormInfo.mt_type}}</span>
      </span>
      <span style="width: 335px;display: inline-block">
        <span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">会议体验</span><span>{{ terminalFormInfo.mt_expe}}</span>
      </span>
      <span style="display: inline-block">
        <span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">呼叫码率</span><span>{{ terminalFormInfo.bitrate}}</span>
      </span>
    </div>
  </div>
		<div>
			<!--<KdTabCommon :tab-list="tabListTerminalDetail" :active-tab="activeTabTerminalDetail" class-name="tab-alarm" @tab-change="tabChangeTerminalDetail"></KdTabCommon>-->
			<!--<div class="area-tab-content">-->
				<!--<component :is="activeTabTerminalDetail" :callDetailTable='terminalDeraildata'></component>-->
			<!--</div>-->
      <videoSource :callDetailTable='terminalDeraildata'></videoSource>
		</div>
	</div>
</template>

<script>
	export default{
		props:{
			peertopeerdata:Object
		},
		data() {
			return {
				terminalFormInfo: {},
				activeTabTerminalDetail:'videoSource',		//点对点会议终端详情下方图表
				tabListTerminalDetail:[																					//点对点会议终端详情tab分页
          ['videoSource','视频源'],
					// ['terminalOverView','参会概况'],
					// ['statusInfo','状态信息'],
					// ['terminalCallLink','呼叫链路'],
					// ['terminalCallDetail','呼叫详情'],
					// ['terminalLink','码流链路'],
				],
				terminalDeraildata:[],										//点对点会议传入终端各个图标的数据
			}
		},
		methods: {
			getdata() {
				this.$api.monitor.meetingDevice(this.peertopeerdata).then(res=>{
					if (res.data.success === 1){
            this.terminalFormInfo = res.data.data.info[1]
            if(res.data.data.info[1].bitrate){
              this.terminalFormInfo.bitrate= res.data.data.info[1].bitrate +"kbps"
            }
            if(res.data.data.info[1].mt_expe){
              this.terminalFormInfo.mt_expe= res.data.data.info[1].mt_expe +"分"
            }
            for(var item in this.terminalFormInfo) {
              if(this.terminalFormInfo[item]===''){
                this.terminalFormInfo[item]='   ----'
              }
            }
            this.terminalDeraildata = [{
              conf_id: this.peertopeerdata.caller_id,
              mt_e164: this.peertopeerdata.callee_id,
              start_time:this.peertopeerdata.start_time,
              end_time:this.peertopeerdata.end_time,
              conf_type:this.peertopeerdata.conf_type,
              conf_status:this.peertopeerdata.conf_status
            },this.terminalFormInfo]
          }
				}).catch(err=>{
				  console.log(err)
        })
			},
			tabChangeTerminalDetail(val){
				this.activeTabTerminalDetail = val
			},
		},
		mounted() {
			this.getdata()
		},
		watch:{
			peertopeerdata(val,oldval){
				this.getdata()
			}
		},
		components:{
      KdTabCommon: () => import('@/components/common/KdTabCommon.vue'),
			// terminalOverView: () => import('@/view/monitor/MonitorAlarmMeetingInfo/terminalOverView.vue'),
			// terminalCallDetail: () => import('@/view/monitor/MonitorAlarmMeetingInfo/terminalCallDetail.vue'),
			// statusInfo: () => import('@/view/monitor/MonitorAlarmMeetingInfo/statusInfo.vue'),
			// terminalCallLink: () => import('@/view/monitor/MonitorAlarmMeetingInfo/terminalCallLink.vue'),
			// terminalLink: () => import('@/view/monitor/MonitorAlarmMeetingInfo/terminalLink.vue'),
      videoSource:() => import('@/view/monitor/MonitorAlarmMeetingInfo/videoSource.vue'),
    },
	}
</script>

<style>
  .tab-alarm{
    margin-bottom: 20px;
  }
</style>
