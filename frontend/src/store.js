import Vue from "vue";
import Vuex from 'vuex'

Vue.use(Vuex)  //全局状态管理

const store = new Vuex.Store({
    state: {
        apiUrl: 'http://127.0.0.1:8000',  //后台api调用地址
        currLog: {
            type: '',
            msg: '欢迎使用芒果相册!',
            time: '',
        },  //当前日志信息
        logs: [],  //日志列表
        mainHeight: document.documentElement.clientHeight - 72 - 56 - 48 + 'px',  //主内容区的高度
        refreshPhoto: false,  //是否刷新照片列表
        refreshAlbum: false,  //是否刷新影集列表
        refreshPhotoStatistics: false,  //是否刷新照片库统计信息
        cancelSelectPhoto: false,  //是否取消已选中的照片
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
        showLog(state, payload) {  //更新当前日志
            state.currLog.type = payload.type
            state.currLog.msg = payload.msg
            state.currLog.time = payload.time
            //加入日志面板
            state.logs.push({'type': payload.type, 'msg': payload.msg, 'time': payload.time})
            // 只保留最新的10000条日志信息
            if (state.logs.length > 10000) {
                state.logs.splice(0, 1)
            }
        },
        clearLog(state) {  //清空日志列表
            state.logs = []
        },
        setMainHeight(state) {  //设置主内容区的高度
            state.mainHeight = document.documentElement.clientHeight - 72 - 56 - 48 + 'px'
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
    }
})
store.commit('setApiUrl')

export default store