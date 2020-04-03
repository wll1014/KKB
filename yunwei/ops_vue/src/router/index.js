import Vue from 'vue'
import Router from 'vue-router'
import homepage from './homepage'
// import hostmanage from './hostmanage.js'
import monitor from './monitor.js'
import manage from './manage.js'
import operation from './operation.js'
import security from './security.js'
// import faq from './Faq.js'
import diagnose from './diagnose.js'
import assistant from './assistant.js'
// import recorder from './recorder.js'
// import version from './versionManagement.js'
// import report from './report.js'
// import problemtrack from './problemtrack.js'
// import license from './license.js'

Vue.use(Router)


export default new Router({
		routes:[
			{
				path: '/', 
				redirect: '/ops/homepage' 
			},
			{
			path: '/ops',
      component: resolve=>(require(["@/components/TheMainLayout.vue"],resolve)),
      redirect: '/ops/homepage',
			children:[
        ...homepage,
				...monitor,
        ...manage,
        ...operation,
        ...security,
        ...diagnose,
        ...assistant,
        {
          path: 'lab',
          component: resolve=>(require(["@/view/lab/lab.vue"],resolve)),
        }
			]
			},
// 			{
// 			path: '/test',
// 			component: testone,
// 			},
		]
	})
