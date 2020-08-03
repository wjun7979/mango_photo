<template>
    <div class="footer">
        <el-row>
            <el-col :span="12" class="status">0</el-col>
            <el-col :span="12" class="output" @click.native="openLogBox">
                <i class="el-icon-chat-line-square"></i>
                {{ curr_log.msg }}
            </el-col>
        </el-row>
        <el-card v-show="isShowLogBox" class="log-box" id="logBox"
                 :body-style="{height: '253px', overflow: 'auto', padding: '10px 20px'}">
            <div slot="header">
                <el-row>
                    <el-col :span="12" style="line-height: 28px;">日志</el-col>
                    <el-col :span="12" style="text-align: right">
                        <el-button icon="el-icon-edit" size="mini"></el-button>
                    </el-col>
                </el-row>
            </div>
            <p v-for="(log, index) in logs" v-bind:key="index">
                <span>{{ log.time }} :</span>
                <span :class="log.type">{{ log.msg }}</span>
            </p>
        </el-card>
    </div>
</template>

<script>
    export default {
        name: "Footer",
        data() {
            return {
                logs: [],  //日志列表
                curr_log: {},  //当前日志信息
                isShowLogBox: true,  //是否显示日志面板
                logBoxWidth: 400,
            }
        },
        created: function () {
            this.showLog();
        },
        watch: {
            'logs': 'scrollToBottom'  //监视日志列表的变化
        },
        methods: {
            showLog: function () {
                //在状态栏中显示日志信息
                this.$root.eventBus.$on('showLog', (type, msg, time) => {
                    this.logs.push({'type': type, 'msg': msg, 'time': time})
                    this.curr_log.type = type
                    this.curr_log.msg = msg
                    this.curr_log.time = time
                    // 只保留最新的10000条日志信息
                    //if (this.logs.length > 1000) {
                    //    this.logs.splice(1000, 1)
                    //}

                })
            },
            scrollToBottom: function () {
                //日志更新后，将日志面板滚动到最底部
                //$nextTick 是在下次 DOM 更新循环结束之后执行延迟回调，在修改数据之后使用
                this.$nextTick(() => {
                    let logBox = document.getElementById('logBox');
                    logBox.scrollTop = logBox.scrollHeight;
                })
            },
            openLogBox: function (event) {
                //打开日志面板
                console.log(event.target.tagName)
                this.isShowLogBox = true
            }
        }
    }
</script>

<style scoped>
    .footer {
        border-top: 1px solid #dadce0;
    }

    .status, .output {
        padding: 0 20px;
        font-size: 12px;
        line-height: 39px;
    }

    .output {
        cursor: pointer;
    }

    .log-box {
        position: fixed;
        right: 5px;
        bottom: 45px;
        width: 50%;
        height: 300px;
        overflow: auto;
        font-size: 12px;
        overflow: visible;
    }

    .log-box >>> .el-card__header {
        padding: 8px 20px;
    }

    .success {
        color: #67c23a;
    }

    .error {
        color: #f56c6c;
    }
</style>