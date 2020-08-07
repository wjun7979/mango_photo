import Vue from "vue";
import Vuex from 'vuex'

Vue.use(Vuex)  //全局状态管理

const store = new Vuex.Store({
    state: {
        api_url: 'http://127.0.0.1:8000',  //后台api调用地址
        curr_log: {
            type: '',
            msg: '',
            time: '',
        },  //当前日志信息
        logs: [],  //日志列表
        refresh_photo: false,  //是否刷新照片列表
    },
    mutations: {
        showLog(state, payload) {  // 更新当前日志
            state.curr_log.type = payload.type
            state.curr_log.msg = payload.msg
            state.curr_log.time = payload.time
            //加入日志面板
            state.logs.push({'type': payload.type, 'msg': payload.msg, 'time': payload.time})
            // 只保留最新的10000条日志信息
            if (state.logs.length > 10000) {
                state.logs.splice(0, 1)
            }
        },
        refreshPhoto(state, payload) {  //更改"是否刷新照片列表"的值
            state.refresh_photo = payload.show
        },
    }
})

export default store