import Vue from "vue";
import Vuex from 'vuex'

Vue.use(Vuex)  //全局状态管理

const store = new Vuex.Store({
    state: {
        apiUrl: 'http://127.0.0.1:8000',  //后台api调用地址
        refreshPhoto: false,  //是否刷新照片列表
        refreshAlbum: false,  //是否刷新影集列表
        refreshPhotoStatistics: false,  //是否刷新照片库统计信息
        cancelSelectPhoto: false,  //是否取消已选中的照片
        infoSideStatus: true,  //信息侧边栏的最后一次显示状态
    },
    mutations: {
        setApiUrl(state) {  //根据客户端访问地址改变API请求地址
            if (window.location.href.indexOf('localhost') > -1) {
                state.apiUrl = 'http://127.0.0.1:8000'
            }
            else {
                state.apiUrl = 'http://wlon.vicp.net:7080'
            }
        },
        refreshPhoto(state, payload) {  //更改"是否刷新照片列表"的值
            state.refreshPhoto = payload.show
        },
        refreshAlbum(state, payload) {  //更改"是否刷新影集列表"的值
            state.refreshAlbum = payload.show
        },
        refreshPhotoStatistics(state, payload) {  //更改“是否刷新照片库统计信息”的值
            state.refreshPhotoStatistics = payload.show
        },
        cancelSelectPhoto(state, payload) {  //更改“是否取消已选中的照片”的值
            state.cancelSelectPhoto = payload.action
        },
        setInfoSideStatus(state, payload) {  //更改“信息侧边栏的最后一次显示状态”的值
            state.infoSideStatus = payload.status
        }
    }
})
store.commit('setApiUrl')

export default store