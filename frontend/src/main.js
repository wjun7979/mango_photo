import Vue from 'vue'
import App from './App.vue'
import router from './router.js'
import store from "./store";
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import 'element-ui/lib/theme-chalk/display.css';
import { Notification } from 'element-ui'
import axios from 'axios'
import lodash from 'lodash'
import './assets/style/default.css'
import common from './common.js'

Vue.use(ElementUI)  //前端UI

//定义axios全局配置
axios.interceptors.request.use(config => {
	//当本地存在token时，通过headers传递给api
	if (localStorage.getItem('token')) {
		config.headers.userid = localStorage.getItem('userid')
		config.headers.token = localStorage.getItem('token')
	}
	return config
})
axios.interceptors.response.use(response => {
	//当api调用成功后更新本地token
	const path = response.config.url
	if (localStorage.getItem('userid') && path.indexOf('/api/refresh_token') === -1) {
		axios({
			method: 'post',
			url: store.state.apiUrl + '/api/refresh_token',
			data: {
				userid: localStorage.getItem('userid')
			}
		}).then(res => {
			localStorage.userid = res.data.userid  //存储token
			localStorage.token = res.data.token
		})
	}
	return Promise.resolve(response)
}, err => {
	//当后台返回错误时提示信息，但控制同一时间只出现一个通知框
	if (document.getElementsByClassName('el-notification').length === 0) {
		Notification({
			type: 'error',
			title: '提示',
			message: err.response.data.msg,
			position: 'top-right'
		})
	}
	if (err.response.status === 401) {  //未通过后台身份验证
		if (localStorage.getItem('userid')) {
			localStorage.removeItem('userid')  //清除本地token
			localStorage.removeItem('token')
		}
		router.push('/login')
	}
	return Promise.reject(err)
})

//禁止移动端双击放大
let touchTime = 0;
document.addEventListener('touchend', function (event) {
	//记录当前点击的时间与下一次时间的间隔
	let nowTime = new Date();
	if (nowTime.getTime() - touchTime <= 300) {
		event.preventDefault();
	}
	touchTime = nowTime.getTime();
}, false);

Vue.prototype.$axios = axios //全局注册，使用方法为:this.$axios
Vue.prototype.$lodash = lodash  //全局注册losash工具库
Vue.prototype.$common = common  //引入公共js方法

Vue.config.productionTip = false

new Vue({
    render: h => h(App),
    router,  //路由
    store,  //全局状态管理
}).$mount('#app')

