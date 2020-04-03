export default[ 

{
    path: 'monitor',
    redirect: '/ops/monitor/meetinginfo',
  component: resolve=>(require(["@/view/monitor/MonitorLayout.vue"],resolve)),
  children:[
    {
      path: 'stats_resource_conf',
      component: resolve=>(require(["@/view/monitor/StatsResourceConference.vue"],resolve)),
    },{
      path: 'stats_data_summary',
      component: resolve=>(require(["@/view/monitor/StatsDataSummary.vue"],resolve)),
    },{
      path: 'meetinginfo',
      name: 'monitor-meetinginfo',
      component: resolve=>(require(["@/view/monitor/MonitorAlarmMeetingInfo/MonitorAlarmMeeting.vue"],resolve)),
    },{
      path:'stats_app_request',
      component: resolve=>(require(["@/view/monitor/StatsAppRequest.vue"],resolve)),
    }]
},]
