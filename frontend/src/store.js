import Vue from "vue";
import Vuex from 'vuex'

Vue.use(Vuex)  //全局状态管理

const store = new Vuex.Store({
    state: {
        apiUrl: 'http://127.0.0.1:8000',  //后台api调用地址
        progress: {  //全局文件上传进度条
            show: false,  //是否显示
            total: 0,  //上传文件数量
            percentage: 0,  //当前进度百分比
        },
        refreshPhoto: {  //刷新照片列表
            action: 'none',  //none:不执行任何操作 reload:重新载入第1页 delete:删除成员 update:更新成员
            list: [],
            refreshPhotoGroup: false,  //action=update时指定是否需要重新分组
        },
        refreshAlbum: false,  //是否刷新影集列表
        refreshFace: {  //是否刷新面孔列表
            action: 'none',  //none:不执行任何操作 reload:重新载入第1页 delete:删除成员 update:更新成员
            list: [],
        },
        refreshPhotoStatistics: false,  //是否刷新照片库统计信息
        refreshUserInfo: false,  //是否刷新用户基本信息
        cancelSelectPhoto: false,  //是否取消已选中的照片
        infoSideStatus: false,  //信息侧边栏的最后一次显示状态
        cancelSelectFace: false,  //是否取消已选中的面孔
        showMenu: false,  //小尺寸屏幕下是否显示菜单
        pickPhotoMode: false,  //移动设备下是否进入选择照片模式
        pickFaceMode: false,  //移动设备下是否进入选择面孔模式
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
                    state.apiUrl = 'http://58.51.106.134:8000'
                }
            }
        },
        setProgress(state, payload) {  //设置进度条
            if (payload.show !== undefined)
                state.progress.show = payload.show
            if (payload.total !== undefined)
                state.progress.total = payload.total
            if (payload.percentage !== undefined)
                state.progress.percentage = payload.percentage
        },
        refreshPhoto(state, payload) {  //更改"是否刷新照片列表"的值
            state.refreshPhoto.action = payload.action
            if (payload.list !== undefined)
                state.refreshPhoto.list = payload.list
            if (payload.refreshPhotoGroup !== undefined)
                state.refreshPhoto.refreshPhotoGroup = payload.refreshPhotoGroup
        },
        refreshAlbum(state, payload) {  //更改"是否刷新影集列表"的值
            state.refreshAlbum = payload.show
        },
        refreshFace(state, payload) {  //更改"是否刷新面孔列表"的值
            state.refreshFace.action = payload.action
            if (payload.list !== undefined) {
                state.refreshFace.list = payload.list
            }
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
        cancelSelectFace(state, payload) {  //更改“是否取消已选中的面孔”的值
            state.cancelSelectFace = payload.action
        },
        showMenu(state, payload) {  //更改"小尺寸屏幕下是否显示菜单"的值
            state.showMenu = payload.show
        },
        pickPhotoMode(state, payload) {  //更改"移动设备下是否进入选择照片模式"的值
            state.pickPhotoMode = payload.show
        },
        pickFaceMode(state, payload) {  //更改"移动设备下是否进入选择面孔模式"的值
            state.pickFaceMode = payload.show
        },
    }
})
store.commit('setApiUrl')

export default store