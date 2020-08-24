import Vue from 'vue'
import App from './App.vue'
import router from './router.js'
import store from "./store";
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import axios from 'axios'
import './assets/style/default.css'
import common from './common.js'
import { Notification } from 'element-ui'

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
	Notification({
		type: 'error',
		title: '提示',
		message: err.response.data.msg,
		position: 'top-right'
	})
	if (err.response.status === 401) {  //未通过后台身份验证
		if (localStorage.getItem('userid')) {
			localStorage.removeItem('userid')  //清除本地token
			localStorage.removeItem('token')
		}
		router.push('/login')
	}
	return Promise.reject(err)
})

Vue.prototype.$axios = axios //全局注册，使用方法为:this.$axios
Vue.prototype.$common = common  //引入公共js方法

Vue.config.productionTip = false

new Vue({
    render: h => h(App),
    router,  //路由
    store,  //全局状态管理
}).$mount('#app')
