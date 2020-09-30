import Vue from 'vue'
import VueRouter from 'vue-router'
import Login from './components/Login'
import UserInfo from "./components/UserInfo";
import Main from './components/Main'
import Photos from "./components/Photos"
import Photo from "./components/Photo";
import Albums from "./components/Albums";
import Album from "./components/Album";
import PickPhoto from "./components/PickPhoto";
import Cover from "./components/Cover";
import Trash from "./components/Trash"
import Favorites from "./components/Favorites";
import Peoples from "./components/Peoples";
import People from "./components/People";
import PickFace from "./components/PickFace";
import NotFound from "./components/NotFound";

//解决ElementUI导航栏中的vue-router重复点菜单报错问题
const originalPush = VueRouter.prototype.push
VueRouter.prototype.push = function push(location) {
    return originalPush.call(this, location).catch(err => err)
}

Vue.use(VueRouter)

//定义routes路由的集合，数组类型
const routes = [
    {path: '', redirect: '/photos'},
    {
        path: '/login', name: 'login', component: Login, meta: {
            title: '登录'
        }
    },
    {
        path: '/main', component: Main, children: [
            {
                path: '/photos', name: 'photos', component: Photos, meta: {
                    title: '照片'
                }
            },
            {
                path: '/favorites', name: 'favorites', component: Favorites, meta: {
                    title: '收藏夹'
                }
            },
            {
                path: '/albums', name: 'albums', component: Albums, meta: {
                    title: '影集'
                }
            },
            {
                path: '/album/:uuid', name: 'album', component: Album, meta: {
                    title: '影集'
                }
            },
            {
                path: '/peoples', name: 'peoples', component: Peoples, meta: {
                    title: '人物'
                }
            },
            {
                path: '/people/:uuid/:type', name: 'people', component: People, meta: {
                    title: '人物'
                }
            },
            {
                path: '/trash', name: 'trash', component: Trash, meta: {
                    title: '回收站'
                }
            },
            {
                path: '/user_info', name: 'user_info', component: UserInfo, meta: {
                    title: '管理账号'
                }
            },
        ]
    },
    {
        path: '/photo/:uuid/:callMode/:albumUUID/:peopleUUID', name: 'photo', component: Photo, meta: {
            title: '照片'
        }
    },
    {
        path: '/pick_photo/:albumUUID', name: 'pick_photo', component: PickPhoto, meta: {
            title: '添加照片到影集'
        }
    },
    {
        path: '/cover/:albumUUID', name: 'cover', component: Cover, meta: {
            title: '选择影集封面'
        }
    },
    {
        path: '/pick_face/:peopleUUID', name: 'pick_face', component: PickFace, meta: {
            title: '添加面孔到人物'
        }
    },
    {path: '*', component: NotFound},
]

//实例化VueRouter并将routes添加进去
const router = new VueRouter({
    mode: 'history',
    routes,  //ES6简写，等于routes:routes
    scrollBehavior(to, from, savedPosition) {
        //点击浏览器后退按钮时，定位到之前的滚动条位置
        if (savedPosition) {
            return new Promise((resolve) => {
                setTimeout(() => {
                    resolve(savedPosition)
                }, 500)
            })
        } else {
            return {x: 0, y: 0}
        }
    }
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