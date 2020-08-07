import Vue from 'vue'
import VueRouter from 'vue-router'
import Browse from "./components/Browse"
import Trash from "./components/Trash"

//解决ElementUI导航栏中的vue-router重复点菜单报错问题
const originalPush = VueRouter.prototype.push
VueRouter.prototype.push = function push(location) {
    return originalPush.call(this, location).catch(err => err)
}

Vue.use(VueRouter)

//定义routes路由的集合，数组类型
const routes = [
    {path: '/', component: Browse},
    {path: '/trash', component: Trash},
]

//实例化VueRouter并将routes添加进去
const router = new VueRouter({
    mode: 'history',
    routes  //ES6简写，等于routes:routes
})

//抛出这个实例对象方便外部读取以及访问
export default router