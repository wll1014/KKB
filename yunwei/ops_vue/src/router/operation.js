export default [
  {
    path: 'operation',
    redirect: '/ops/operation/distribution',
    component: resolve=>(require(["@/view/hostmanage/HostLayout.vue"],resolve)),
    children:[
      {
        path: 'script',
        component: resolve=>(require(["@/view/hostmanage/ScriptManager.vue"],resolve)),
      },
      {
        path: 'distribution',
        component: resolve=>(require(["@/view/hostmanage/FileDistribution.vue"],resolve)),
      },
      {
        path: 'version',
        component: resolve=>(require(["@/view/version/VersionManagement.vue"],resolve)),
      },{
        path: 'maintenance',
        component: resolve=>(require(["@/view/operationrecord/MaintainRecords/MaintainRecords.vue"],resolve)),

      },{
        path: 'problemtrack',
        component: resolve=>(require(["@/view/problemtrack/ProblemTrack.vue"],resolve))
      },{
        path: 'reporter',
        component: resolve=>(require(["@/view/reporter/ReportDay.vue"],resolve)),
      },
    ]
  },]
