<template>
    <div class="footer">
        <el-row>
            <el-col :span="12" class="status">0</el-col>
            <el-col :span="12" class="output" @click.native="openLogBox">
                <i class="el-icon-chat-line-square" style="margin-right: 5px;"></i>
                <span :class="curr_log.type">{{ curr_log.msg }}</span>
            </el-col>
        </el-row>
        <!--日志面板-->
        <el-collapse-transition>
            <el-card v-show="isShowLogBox" class="log-box" id="logBox"
                     :body-style="{padding: '0'}">
                <div slot="header">
                    <el-row>
                        <el-col :span="12" style="line-height: 28px;">日志</el-col>
                        <el-col :span="12" style="text-align: right">
                            <el-button icon="el-icon-delete" type="text" size="mini" @click="clearLogBox"
                                       title="清空日志"></el-button>
                            <el-button icon="el-icon-close" type="text" size="mini" @click="closeLogBox"
                                       title="关闭日志面板"></el-button>
                        </el-col>
                    </el-row>
                </div>
                <div id="card-contend">
                    <p v-for="(log, index) in logs" v-bind:key="index">
                        <span>{{ log.time }} :</span>
                        <span :class="log.type">{{ log.msg }}</span>
                    </p>
                </div>
            </el-card>
        </el-collapse-transition>
    </div>
</template>

<script>
    export default {
        name: "Footer",
        data() {
            return {
                curr_log: this.$store.state.curr_log,  //当前日志信息
                logs: this.$store.state.logs,  //日志列表
                isShowLogBox: false,  //是否显示日志面板
                logBoxWidth: 400,
            }
        },
        watch: {
            'logs': 'scrollToBottom'  //监视日志列表的变化
        },
        methods: {
            scrollToBottom: function () {
                //日志更新后，将日志面板滚动到最底部
                //$nextTick 是在下次 DOM 更新循环结束之后执行延迟回调，在修改数据之后使用
                this.$nextTick(() => {
                    let cardContend = document.getElementById('card-contend');
                    cardContend.scrollTop = cardContend.scrollHeight;
                })
            },
            openLogBox: function () {
                //打开日志面板
                this.isShowLogBox = !this.isShowLogBox
                this.scrollToBottom()
            },
            closeLogBox: function () {
                //关闭日志面板
                this.isShowLogBox = false
            },
            clearLogBox: function () {
                //清空日志
                this.logs = []
            }
        }
    }
</script>

<style scoped>
    .footer {
        margin-top: 8px;
        height: 40px;
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
        width: 33%;
        height: 300px;
        overflow: auto;
        font-size: 12px;
        overflow: visible;
    }

    .log-box >>> .el-card__header {
        padding: 8px 20px;
    }

    #card-contend {
        height: 253px;
        overflow: auto;
        padding: 10px 20px;
    }

    .success {
        color: #67c23a;
    }

    .error {
        color: #f56c6c;
    }
</style>