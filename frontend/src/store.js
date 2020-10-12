import Vue from "vue";
import Vuex from 'vuex'

Vue.use(Vuex)  //全局状态管理

const store = new Vuex.Store({
    state: {
        apiUrl: 'http://127.0.0.1:8000',  //后台api调用地址
        refreshPhoto: false,  //是否刷新照片列表
        refreshAlbum: false,  //是否刷新影集列表
        refreshFace: false,  //是否刷新面孔列表
        refreshPhotoStatistics: false,  //是否刷新照片库统计信息
        refreshUserInfo: false,  //是否刷新用户基本信息
        cancelSelectPhoto: false,  //是否取消已选中的照片
        infoSideStatus: false,  //信息侧边栏的最后一次显示状态
        photoCheckList: [],  //选中的照片列表
        faceCheckList: [],  //选中的面孔列表
        cancelSelectFace: false,  //是否取消已选中的面孔
        showMenu: false,  //小尺寸屏幕下是否显示菜单
        pickPhotoMode: false,  //移动设备下是否进入选择照片模式
    },
    mutations: {
        setApiUrl(state) {  //根据客户端访问地址改变API请求地址
            if (window.location.href.indexOf('localhost') > -1) {
                state.apiUrl = 'http://127.0.0.1:8000'
            }
            else {
                if (window.location.href.indexOf('192.168.16.67') > -1) {
                    state.apiUrl = 'http://192.168.16.67:8000'
                }
                else {
                    state.apiUrl = 'http://wlon.vicp.net:7080'
                }
            }
        },
        refreshPhoto(state, payload) {  //更改"是否刷新照片列表"的值
            state.refreshPhoto = payload.show
        },
        refreshAlbum(state, payload) {  //更改"是否刷新影集列表"的值
            state.refreshAlbum = payload.show
        },
        refreshFace(state, payload) {  //更改"是否刷新面孔列表"的值
            state.refreshFace = payload.show
        },
        refreshPhotoStatistics(state, payload) {  //更改“是否刷新照片库统计信息”的值
            state.refreshPhotoStatistics = payload.show
        },
        refreshUserInfo(state, payload) {  //更改“是否刷新用户基本信息”的值
            state.refreshUserInfo = payload.show
        },
        cancelSelectPhoto(state, payload) {  //更改“是否取消已选中的照片”的值
            state.cancelSelectPhoto = payload.action
        },
        setInfoSideStatus(state, payload) {  //更改“信息侧边栏的最后一次显示状态”的值
            state.infoSideStatus = payload.status
        },
        setPhotoCheckList(state, payload) {  //更改”选中的照片列表“的值
            state.photoCheckList = payload.checkList
        },
        setFaceCheckList(state, payload) {  //更改”选中的面孔列表“的值
            state.faceCheckList = payload.checkList
        },
        cancelSelectFace(state, payload) {  //更改“是否取消已选中的面孔”的值
            state.cancelSelectFace = payload.action
        },
        showMenu(state, payload) {  //更改"小尺寸屏幕下是否显示菜单"的值
            state.showMenu = payload.show
        },
        pickPhotoMode(state, payload) {  //更改"移动设备下是否进入选择照片模式"的值
            state.pickPhotoMode = payload.show
        },
    }
})
store.commit('setApiUrl')

export default store