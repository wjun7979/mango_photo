<template>
    <el-container>
        <el-header class="mp-page-header" height="56px">
            <el-col class="mp-page-header-title" :span="8">
                <span>回收站</span>
            </el-col>
            <el-col :span="16" style="text-align: right; padding: 8px 20px 0 0">
                <el-button icon="el-icon-delete" size="small" @click="emptyTrash">清空回收站</el-button>
            </el-col>
        </el-header>
        <el-main :style="{height: mainHeight, overflow: 'auto', padding: 0}">
            <PhotoList title="回收站" callMode="trash"></PhotoList>
        </el-main>
    </el-container>
</template>

<script>
    import PhotoList from "./PhotoList"

    export default {
        name: 'Trash',
        components: {PhotoList},
        computed: {
            apiUrl() {
                return this.$store.state.apiUrl  //后台api调用地址
            },
            mainHeight() {
                return this.$store.state.mainHeight  //主内容区的高度
            },
        },
        methods: {
            emptyTrash() {
                //清空回收站
                this.$confirm('所有内容将被永久删除，且此操作无法撤消', '要清空回收站吗？', {
                    confirmButtonText: '清空回收站',
                    cancelButtonText: '取消',
                    type: 'warning'
                }).then(() => {
                    this.$axios({
                        method: 'post',
                        url: this.apiUrl + '/api/photo_empty_trash',
                        data: {
                            userid: localStorage.getItem('userid'),
                        }
                    }).then(() => {
                        let msg = '回收站已清空'
                        this.unselectPhoto()
                        this.$notify({
                            type: 'success',
                            title: '成功',
                            message: msg,
                            position: 'top-right'
                        })
                        this.$store.commit('showLog', {
                            type: 'success',
                            msg: msg,
                            time: new Date().toLocaleTimeString()
                        })
                        this.$store.commit('refreshPhoto', {show: true})  //刷新图片列表
                    })
                }).catch(() => {
                });
            },
        }
    }
</script>

<style scoped>

</style>
