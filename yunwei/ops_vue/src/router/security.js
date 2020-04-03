export default [
  {
    path: 'security',
    redirect: '/ops/security/operationlog',
    component: resolve=>(require(["@/view/operationrecord/OperationLog/RecoderLayout.vue"],resolve)),
    children:[
      {
        path: 'operationlog',
        component: resolve=>(require(["@/view/operationrecord/OperationLog/OperationLog.vue"],resolve)),
      },
    ]
  },]
