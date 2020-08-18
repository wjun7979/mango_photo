import Vue from 'vue'
import App from './App.vue'
import router from '../../router.js'
import store from "../../store";
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import VueResource from "vue-resource"
import '../../assets/style/default.css'
import common from '../../common.js'

Vue.use(ElementUI)  //前端UI
Vue.use(VueResource)  //发起请求并处理响应
Vue.prototype.$common = common  //引入公共js方法

Vue.config.productionTip = false

new Vue({
    render: h => h(App),
    router,  //路由
    store,  //全局状态管理
}).$mount('#app')
