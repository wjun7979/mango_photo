<template>
    <el-button icon="el-icon-circle-plus-outline" size="small" @click="newAlbum">{{title}}</el-button>
</template>

<script>
    export default {
        name: "CreateAlbum",
        props: {
            title: {  //按钮标题
                type: String,
                default: '创建影集'
            },
            parentUUID: {  //上级影集uuid
                type: String,
                default: ''
            },
        },
        computed: {
            apiUrl() {
                return this.$store.state.apiUrl  //后台api调用地址
            },
        },
        methods: {
            newAlbum() {
                this.$store.commit('cancelSelectPhoto', {action: true})  //取消已选中的照片
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
                            parent_uuid: this.parentUUID,
                            userid: localStorage.getItem('userid')
                        }
                    }).then(response => {
                        const result = response.data
                        const uuid = result.uuid
                        this.$router.push({
                            name: 'album',
                            params: {uuid: uuid}
                        })
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