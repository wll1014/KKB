<template>
<div class="theme-dark" style="padding: 20px 20px 20px 27px;">
  <KdTabCommon :tab-list="tabList" :active-tab="activeTab" class-name="tab-alarm" @tab-change="tabChange"></KdTabCommon>
  <div class="area-tab-content">
      <component :is="activeTab"></component>
  </div>
</div>

</template>

<script>
export default {
  components: {
    KdTabCommon: () => import('@/components/common/KdTabCommon.vue'),
    MonitorAlarmSubscription: () => import('@/view/monitor/MonitorAlarmSubscription.vue'),
    MonitorAlarmNotification: () => import('@/view/monitor/MonitorAlarmNotification.vue'),
    MonitorAlarmSettings: () => import('@/view/monitor/MonitorAlarmSettings.vue'),
  },
	data(){
		return{
		  activeTab:'MonitorAlarmSubscription',
      tabList:[['MonitorAlarmSubscription','订阅告警'],
               ['MonitorAlarmNotification','告警通知人员'],
               ['MonitorAlarmSettings','告警设置'],],
		}
	},
	methods: {
    tabChange(val){
      this.activeTab=val
    },
	},
	mounted(){

	},
		
// 	beforeDestroy () {
// 		this.cpuChartInstance.clear()
// 	},

}
</script>

<style>
  .tab-alarm{
    margin-bottom: 20px;
  }
</style>
