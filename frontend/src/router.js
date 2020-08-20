import Vue from 'vue'
import VueRouter from 'vue-router'
import Login from './components/Login'
import Main from './components/Main'
import Browse from "./components/Browse"
import Trash from "./components/Trash"
import NotFound from "./components/NotFound";

//解决ElementUI导航栏中的vue-router重复点菜单报错问题
const originalPush = VueRouter.prototype.push
VueRouter.prototype.push = function push(location) {
    return originalPush.call(this, location).catch(err => err)
}

Vue.use(VueRouter)

//定义routes路由的集合，数组类型
const routes = [
    {path: '', redirect: '/login'},
    {
        path: '/login', component: Login, meta: {
            title: '登录'
        }
    },
    {
        path: '/photo', component: Main, children: [
            {
                path: '/photo', component: Browse, meta: {
                    title: '照片'
                }
            },
            {
                path: '/trash', component: Trash, meta: {
                    title: '回收站'
                }
            },
        ]
    },
    {path: '*', component: NotFound},
]

//实例化VueRouter并将routes添加进去
const router = new VueRouter({
    mode: 'history',
    routes  //ES6简写，等于routes:routes
})

//路由拦截
const defaultTitle = '芒果相册'
router.beforeEach((to, from, next) => {
    document.title = to.meta.title ? to.meta.title + ' - ' + defaultTitle : defaultTitle  //动态改变页面的title值
    if (to.path == '/login') {
        next();
    } else {
        if (localStorage.getItem('token')) {
            next();
        } else {
            next('/login');
        }
    }
})

//抛出这个实例对象方便外部读取以及访问
export default router