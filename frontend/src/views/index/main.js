import Vue from 'vue'
import App from './App.vue'
import router from '../../router.js';
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
import VueResource from "vue-resource";
import '../../assets/style/default.css';

Vue.use(ElementUI);
Vue.use(VueResource);

Vue.config.productionTip = false

new Vue({
  render: h => h(App),
  router,
}).$mount('#app')
