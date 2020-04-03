export default [
  {
    path: 'diagnose',
    redirect: '/ops/diagnose/terminal_diagnose/',
    component: resolve=>(require(["@/view/diagnose/DiagnoseLayout.vue"],resolve)),
    children:[
      {
        path: 'intelligentcapture',
        component: resolve=>(require(["@/view/diagnose/IntelligentWireshark.vue"],resolve)),
      },
			{
			  path:'linkdetection',
			  component: resolve=>(require(["@/view/monitor/LinkDetection/LinkDetection.vue"],resolve)),
			},
      {
			  path:'applicationdetection',
			  component: resolve=>(require(["@/view/monitor/ApplicationDetection.vue"],resolve)),
			},
      {
        path:'terminal',
				name:'terminal_diagnose',
        component: resolve=>(require(["@/view/diagnose/terminalDiagnosis.vue"],resolve))
      },
    ]
  },]
