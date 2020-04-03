<template>
	<!-- 状态信息 -->
  <div>
  <div style="background: #232629 ;margin-bottom:20px;padding: 20px;" class="theme-dark" v-if="callDetailTable[0].conf_status===1">
    <div style="font-size: 14px;margin-bottom: 20px;">
      <span>终端状态</span>
      <span style="color:#5d6266 ;margin-left: 30px;">上次刷新时间 : </span>
      <span style="color:#5d6266 ;">{{ f5Time }}</span>
    </div>
    <div style="font-size: 14px;">
      <div style="margin-bottom: 37px">
      	<span style="width: 335px;display: inline-block">
       <!--    静音 silence 哑音 mute 双流 dual 混音 mix 轮询 poll 电视墙 tvwall 合成 vmp 自主多画面 mtvmp 选看 select 是否在上传	upload 录像	rec 是否多流终端 multistream -->
      		<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">静音</span>
          <span v-if='terminalFormInfo.silence===0'>否</span>
          <span v-if='terminalFormInfo.silence===1'>是</span>
      	</span>
      	<span style="width: 335px;display: inline-block">
      		<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">哑音</span>
          <span v-if='terminalFormInfo.mute===0'>否</span>
          <span v-if='terminalFormInfo.mute===1'>是</span>
      	</span>
      	<span style="width: 335px;display: inline-block">
      		<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">发送双流</span>
          <span v-if='terminalFormInfo.dual===0'>否</span>
          <span v-if='terminalFormInfo.dual===1'>是</span>
      	</span>
      	<span style="display: inline-block">

          <template>
            <el-tooltip content="智能混音时，参与混音代表是否进混音深度" v-if='terminalFormInfo.mix===0'>
              <span>
                <span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">参与混音</span>
                <span >否</span>
              </span>
            </el-tooltip>
            <el-tooltip content="智能混音时，参与混音代表是否进混音深度" v-if='terminalFormInfo.mix===1'>
              <span>
                <span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">参与混音</span>
                <span >是</span>
              </span>
            </el-tooltip>
          </template>


      	</span>
      </div>
      <div style="margin-bottom: 37px">
      	<span style="width: 335px;display: inline-block">
      		<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">参与轮询</span>
          <span v-if='terminalFormInfo.poll===0'>否</span>
          <span v-if='terminalFormInfo.poll===1'>是</span>
      	</span>
      	<span style="width: 335px;display: inline-block">
      		<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">电视墙</span>
          <span v-if='terminalFormInfo.tvwall===0'>否</span>
          <span v-if='terminalFormInfo.tvwall===1'>是</span>
      	</span>
      	<span style="width: 335px;display: inline-block">
      		<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">参与合成</span>
          <span v-if='terminalFormInfo.vmp===0'>否</span>
          <span v-if='terminalFormInfo.vmp===1'>是</span>
      	</span>
      	<span style="display: inline-block">
      		<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">自主多画面</span>
          <span v-if='terminalFormInfo.mtvmp===0'>否</span>
          <span v-if='terminalFormInfo.mtvmp===1'>是</span>
      	</span>
      </div>
      <div style="margin-bottom: 37px">
      	<span style="width: 335px;display: inline-block">
      		<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">参与选看</span>
          <span v-if='terminalFormInfo.select===0'>否</span>
          <span v-if='terminalFormInfo.select===1'>是</span>
      	</span>
      	<span style="width: 335px;display: inline-block">
      		<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">是否在上传</span>
          <span v-if='terminalFormInfo.upload===0'>否</span>
          <span v-if='terminalFormInfo.upload===1'>是</span>
      	</span>
      	<span style="width: 335px;display: inline-block">
      		<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">录像</span>
          <span v-if='terminalFormInfo.rec===0'>否</span>
          <span v-if='terminalFormInfo.rec===1'>是</span>
      	</span>
      	<span style="display: inline-block">
      		<span style="width: 110px;display:inline-block;color: #5d6266;font-size: 14px">多流终端</span>
          <span v-if='terminalFormInfo.multistream===0'>否</span>
          <span v-if='terminalFormInfo.multistream===1'>是</span>
      	</span>
      </div>
    </div>
  </div>

	<div >
		<MonitorMeetingInfoTerminalSummary :apiParams="mtParams" showChart="networkUtilizationIn"></MonitorMeetingInfoTerminalSummary>
	</div>
  </div>
</template>

<script>
	export default {
    components: {
      MonitorMeetingInfoTerminalSummary: () => import('@/components/monitor/MonitorMeetingInfoTerminalSummary.vue'),
    },
		props:{
      callDetailTable:{
				type:Array
			}
		},
		data() {
			return {
        mtParams:{},
        f5Time:'',
        terminalFormInfo:{},
			}
		},
		methods: {
      getData() {
        // console.log(this.callDetailTable)
        if (this.callDetailTable[0]){
          if (this.callDetailTable[0].conf_status === 1){
            var end_time = 'now'
          }else{
            var end_time = this.callDetailTable[0].end_time
          }
          if(!this.callDetailTable[0].mt_e164){
            var mtE164 = this.callDetailTable[0].mt_addr
          }else {
            var mtE164 = this.callDetailTable[0].mt_e164
          }
          this.mtParams = {
            confID: this.callDetailTable[0].conf_id,
            mtE164: mtE164,
            startTime:this.callDetailTable[0].start_time,
            endTime: end_time,
            confStatus:this.callDetailTable[0].conf_status,
            confType:this.callDetailTable[0].conf_type,
          }
        }
      },
			timestampToTime(timestamp) {                            //时间转换
			  var date = new Date(timestamp);//时间戳为10位需*1000，时间戳为13位的话不需乘1000
			  var Y = date.getFullYear() + '-';
			  var M = (date.getMonth()+1 < 10 ? '0'+(date.getMonth()+1) : date.getMonth()+1) + '-';
			  var D = (date.getDate()<10 ? '0'+date.getDate() : date.getDate()) + ' ';
			  var h = (date.getHours()<10 ? '0'+date.getHours():date.getHours())  + ':';
			  var m = (date.getMinutes()<10 ? '0'+date.getMinutes():date.getMinutes()) + ':';;
			  var s = (date.getSeconds()<10 ? '0'+date.getSeconds():date.getSeconds()) ;
			  return Y+M+D+h+m+s;
			},
      getForm(){
				this.f5Time =this.timestampToTime(new Date().getTime()) 
         if(this.callDetailTable[0]){
           var params={
             mt_e164:this.callDetailTable[0].mt_e164,
             conf_e164:this.callDetailTable[0].conf_id
           }
           this.$api.monitor.getTerminalStatusForm(params).then(res=>{
             if(res.data.success===1){
               this.terminalFormInfo = res.data.data
             }else if(res.data.success===0){
               
             }
           })
					 this.setTimer(30)
         }
				 
      },
			setTimer(interver=60,range=3600000){
				this.clearTimer();
					this.timer = setInterval(() => {
						
							this.getForm()
						
			
					},interver*1000)
			},
			// 清除定时器
			clearTimer(){
				clearInterval(this.timer);
				this.timer = null;
			},
    },

    mounted(){
		  this.getData()
      this.getForm()
			
    },
    watch: {																	//监听数据变化
      callDetailTable(newV,oldV) {
        this.getData()
        this.getForm()
      }
    },
		beforeDestroy () {
			this.clearTimer()
		},
	}
</script>

<style>
</style>
