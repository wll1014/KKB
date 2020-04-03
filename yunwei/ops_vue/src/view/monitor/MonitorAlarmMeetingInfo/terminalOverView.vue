<template>
  <!-- 参会概况 -->
  <div >
    <MonitorMeetingInfoTerminalSurvey :apiParams="mtParams" showChart="terminalConfSummary"></MonitorMeetingInfoTerminalSurvey>
  </div>
</template>

<script>
  export default {
    components: {
      MonitorMeetingInfoTerminalSurvey: () => import('@/components/monitor/MonitorMeetingInfoTerminalSurvey.vue'),
    },
    props:{
      callDetailTable:{
        type:Array
      }
    },
    data() {
      return {
        mtParams:{},
      }
    },
    methods: {
      getData() {
        if (this.callDetailTable[0]){
          if(!this.callDetailTable[0].mt_e164){
            var mtE164 = null
          }else {
            var mtE164 = this.callDetailTable[0].mt_e164
          }
          if (this.callDetailTable[0].conf_status === 1){
            this.mtParams = {
              confID: this.callDetailTable[0].conf_id,
              mtE164: mtE164,
              startTime:this.callDetailTable[0].start_time,
              endTime: "now",
              confType:this.callDetailTable[0].conf_type,
              confStatus:this.callDetailTable[0].conf_status,
							time_on:this.callDetailTable[0].start_time,
            }
          }else if(this.callDetailTable[0].conf_status === 0){
            this.mtParams = {
              confID: this.callDetailTable[0].conf_id,
              mtE164: mtE164,
              startTime:this.callDetailTable[0].start_time,
              endTime: this.callDetailTable[0].end_time,
              confType:this.callDetailTable[0].conf_type,
              confStatus:this.callDetailTable[0].conf_status,
							time_on:this.callDetailTable[0].start_time,
            }
          }
        }
      },

    },

    mounted(){
      this.getData()
    },
    watch: {																	//监听数据变化
      callDetailTable(newV,oldV) {
        this.getData()
      }
    },
  }
</script>

<style>
</style>
