<template>
    <div class="footer">
        <el-row>
            <el-col :span="12" class="status">
                <div v-if="photoCount.nums>0">照片库中共有 {{photoCount.nums}} 张照片，占用空间 {{photoCount.size}}</div>
            </el-col>
            <el-popover @show="openLogBox">
                <el-card class="log-box" id="logBox" :body-style="{padding: '0'}">
                    <div slot="header">
                        <el-row>
                            <el-col :span="12" style="line-height: 28px;">日志</el-col>
                            <el-col :span="12" style="text-align: right">
                                <el-button icon="el-icon-delete" type="text" size="mini" @click="clearLogBox"
                                           title="清空日志"></el-button>
                            </el-col>
                        </el-row>
                    </div>
                    <div id="card-contend">
                        <p v-for="(log, index) in logs" v-bind:key="index">
                            <span>{{ log.time }} : </span>
                            <span :class="log.type">{{ log.msg }}</span>
                        </p>
                    </div>
                </el-card>
                <el-col slot="reference" :span="12" class="output">
                    <i class="el-icon-chat-line-square" style="margin-right: 5px;"></i>
                    <span v-if="currLog.time">{{ currLog.time }} : </span>
                    <span :class="currLog.type">{{ currLog.msg }}</span>
                </el-col>
            </el-popover>
        </el-row>
    </div>
</template>

<script>
    export default {
        name: "Footer",
        data() {
            return {
                photoCount: {
                    nums: 0,
                    size: '',
                }
            }
        },
        computed: {
            apiUrl() {
                return this.$store.state.apiUrl  //后台api调用地址
            },
            currLog() {
                return this.$store.state.currLog  //当前日志信息
            },
            logs() {
                return this.$store.state.logs  //日志列表
            },
            refreshPhotoStatistics() {  //是否刷新照片库统计信息
                return this.$store.state.refreshPhotoStatistics
            },
        },
        watch: {
            'logs': 'scrollToBottom',  //监视日志列表的变化
            refreshPhotoStatistics() {
                //有其它组件发出刷新照片库统计信息的指令
                if (this.refreshPhotoStatistics) {
                    this.getPhotoStatistics()
                }
            }
        },
        mounted() {
            this.getPhotoStatistics()
        },
        methods: {
            getPhotoStatistics() {
                //统计照片数量和占用空间等信息
                this.$axios({
                    method: 'get',
                    url: this.apiUrl + '/api/photo_statistics',
                    params: {
                        userid: localStorage.getItem('userid')
                    }
                }).then(response => {
                    this.photoCount = response.data
                    this.photoCount.size = this.$common.bytesToSize(this.photoCount.size)
                    this.$store.commit('refreshPhotoStatistics', {show: false})  //重置“是否刷新照片库统计信息”标志
                })
            },
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
                this.scrollToBottom()
            },
            clearLogBox: function () {
                //清空日志
                this.$store.commit('clearLog')
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