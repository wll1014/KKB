export default [
  {
    path: 'manage',
    redirect: '/ops/manage/alarm',
    component: resolve=>(require(["@/view/hostmanage/HostLayout.vue"],resolve)),
    children:[
      {
        path: 'alarm',
        name: 'monitor-alarm',
        component: resolve=>(require(["@/view/monitor/MonitorAlarm.vue"],resolve)),
      },
      {
        path: 'hostinfo',
        name: 'hostmanage-hostinfo',
        props: true,
        component: resolve=>(require(["@/view/hostmanage/HostInfo.vue"],resolve)),
      },
    ]
  },]
