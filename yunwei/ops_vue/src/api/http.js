import axios from 'axios';
import router from '../router/index';
import store from '../store/index';
import { Notification } from 'element-ui';

/**
 * 请求失败后的错误统一处理
 * @param {Number} status 请求失败的状态码
 */
const errorHandle = (response) => {
  // 状态码判断
  switch (response.status) {
    // 401: 未登录状态，跳转登录页
    case 401:
      // console.log(response.data.data.url)
      document.location = response.data.data.url
      break;
    // 403 token过期
    // 清除token并跳转登录页
    case 403:
      console.log('登录过期，请重新登录');
//             localStorage.removeItem('token');
//             store.commit('loginSuccess', null);
//             setTimeout(() => {
//                 toLogin();
//             }, 1000);
      document.location = response.data.data.url
      break;
    // 404请求不存在
    case 404:
      // console.log("请求的资源不存在");
      throw "请求的资源不存在"
      break;
    default:
      // Notification({
      //   title:response.status + "   " +response.request.statusText,
      //   type:"error",
      //   customClass:"theme-dark",
      //   message:response.request.responseURL
      // })
      throw response
  }}


// 创建axios实例
var instance = axios.create({timeout: 1000 * 30});
// `withCredentials` 表示跨域请求时是否需要使用凭证
instance.defaults.withCredentials = true; //默认的false
// 设置post请求头
// instance.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded';


// 添加请求拦截器
instance.interceptors.request.use(function (config) {
    // 在发送请求之前做些什么
    config.headers={
      'Content-Type':'application/json'
    }
    config.headers['X-Requested-With'] = 'XMLHttpRequest';
    let regex = /.*csrftoken=([^;.]*).*$/; // 用于从cookie中匹配 csrftoken值
    config.headers['X-CSRFToken'] = document.cookie.match(regex) === null ? null : document.cookie.match(regex)[1];
    return config;
  }, function (error) {
    // 对请求错误做些什么
    return Promise.reject(error);
  });


// 响应拦截器
instance.interceptors.response.use(    
    // 请求成功
    res => res.status >= 200 && res.status < 300 ? Promise.resolve(res) : Promise.reject(res),
    // 请求失败
    error => {
        const { response } = error;
        if (response) {
            // 请求已发出，但是不在2xx的范围
          errorHandle(response);
          return Promise.reject(response);
              // console.log(response.status, response.data.message)
        } else {
            // 处理断网的情况
            // eg:请求超时或断网时，更新state的network状态
            // network状态在app.vue中控制着一个全局的断网提示组件的显示隐藏
            // 关于断网组件中的刷新重新获取数据，会在断网组件中说明
          throw "请求超时"
        }
    });

// element组件移到instance上
instance.Notification=Notification

export default instance;
