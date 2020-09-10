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
        <el-main class="mp-page-main">
            <PhotoList callMode="trash"></PhotoList>
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
        },
        methods: {
            emptyTrash() {
                //清空回收站
                this.$store.commit('cancelSelectPhoto', {action: true})  //取消已选中的照片
                this.$confirm('所有内容将被永久删除，且此操作无法撤消', '要清空回收站吗？', {
                    confirmButtonText: '清空回收站',
                    cancelButtonText: '取消',
                    type: 'warning',
                    closeOnClickModal: false,
                }).then(() => {
                    this.$axios({
                        method: 'post',
                        url: this.apiUrl + '/api/photo_empty_trash',
                        data: {
                            userid: localStorage.getItem('userid'),
                        }
                    }).then(() => {
                        this.$message({
                            message: '回收站已清空',
                            type: 'success',
                        })
                        this.$store.commit('refreshPhoto', {show: true})  //刷新图片列表
                        this.$store.commit('refreshPhotoStatistics', {show: true})  //刷新照片库统计信息
                    })
                }).catch(() => {
                });
            },
        }
    }
</script>

<style scoped>

</style>
