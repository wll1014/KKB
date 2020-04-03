// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import ElementUI from 'element-ui';
import '@/assets/css/ops-icon.css'
import '@/assets/css/kd-common.css'
import '@/assets/css/overwrite-el.css'
import '@/assets/css/script.css'
import router from './router/index.js'
import store from './store/index'
import api from '@/api/index'
import echarts from 'echarts' //引入echarts


// Vue.config.productionTip = false
Vue.use(ElementUI)
Vue.prototype.$api = api; // 将api挂载到vue的原型上
Vue.prototype.$echarts = echarts 
/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
	store,
  components: { App },
  template: '<App/>'
})
