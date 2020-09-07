<template>
    <el-container>
        <el-header class="mp-page-header" height="56px">
            <el-col class="mp-page-header-title" :span="8">
                <i class="el-icon-back alumb-back" @click="$router.back()"></i>
                <span>{{albumName}}</span>
            </el-col>
            <el-col :span="16" style="text-align: right">
                <el-form :inline="true" style="margin-top: 2px;">
                    <el-form-item>
                        <CreateAlbum buttonText="创建子影集" :parentUUID="albumUUID"></CreateAlbum>
                    </el-form-item>
                    <el-form-item>
                        <el-button icon="el-icon-document-add" size="small" @click="openPick">添加照片
                        </el-button>
                    </el-form-item>
                </el-form>
            </el-col>
        </el-header>
        <el-main class="mp-page-main">
            <PhotoList callMode="album" :albumUUID="albumUUID"></PhotoList>
        </el-main>
    </el-container>
</template>

<script>
    import PhotoList from "./PhotoList"
    import CreateAlbum from "./CreateAlbum";

    export default {
        name: "Album",
        components: {PhotoList, CreateAlbum},
        data() {
            return {
                albumUUID: this.$route.params.uuid,  //影集uuid
                albumName: '',  //影集标题
            }
        },
        props: [
            'onClose',
        ],
        computed: {
            apiUrl() {
                return this.$store.state.apiUrl  //后台api调用地址
            },
        },
        mounted() {
            this.getAlbum()
        },
        methods: {
            getAlbum() {
                //获取指定的影集信息
                this.$axios({
                    method: 'get',
                    url: this.apiUrl + '/api/album_get',
                    params: {
                        uuid: this.albumUUID
                    }
                }).then(response => {
                    const result = response.data
                    this.albumName = result.name
                })
            },
            openPick() {
                this.$router.push({
                    name: 'pick',
                    params: {albumUUID: this.albumUUID}
                })
            },
        }
    }
</script>

<style scoped>
    .alumb-back { /*影集页头的返回按钮*/
        padding: 8px;
        margin-right: 10px;
        color: #5f6368;
        font-weight: bold;
        cursor: pointer;
    }

    .alumb-back:hover {
        background-color: #e5e5e5;
        border-radius: 50%;
    }
</style>