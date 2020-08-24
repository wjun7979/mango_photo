<template>
    <el-container>
        <el-header class="mp-page-header" height="48px">
            <el-col class="mp-page-header-title" :span="8">影集</el-col>
            <el-col :span="16" style="text-align: right; padding: 8px 20px 0 0">
                <el-button icon="el-icon-circle-plus-outline" size="small" @click="newAlbum">创建影集</el-button>
            </el-col>
        </el-header>
        <el-main :style="{height: mainHeight, overflow: 'auto'}">
            <AlbumList></AlbumList>
        </el-main>
    </el-container>
</template>

<script>
    import AlbumList from "./AlbumList";

    export default {
        name: "Albums",
        components: {AlbumList},
        computed: {
            apiUrl() {
                return this.$store.state.apiUrl  //后台api调用地址
            },
            mainHeight() {
                return this.$store.state.mainHeight  //主内容区的高度
            },
        },
        methods: {
            newAlbum() {
                //创建影集
                this.$prompt('请输入影集标题', {
                    inputValidator: (value => {
                        if (value.trim().length === 0)
                            return false
                    }),
                    inputErrorMessage: '影集标题不能为空'
                }).then(({value}) => {
                    this.$axios({
                        method: 'post',
                        url: this.apiUrl + '/api/album_new',
                        data: {
                            name: value,
                            userid: localStorage.getItem('userid')
                        }
                    }).then(() => {
                        this.$store.commit('refreshAlbum', {show: true})
                        this.$store.commit('showLog', {
                            type: 'success',
                            msg: '影集 [' + value + '] 创建成功',
                            time: new Date().toLocaleTimeString()
                        })
                    })
                }).catch(() => {
                });
            },
        }
    }
</script>

<style scoped>

</style>