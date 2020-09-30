<template>
    <el-container>
        <el-header class="mp-page-header" height="56px">
            <el-col class="mp-page-header-title" :span="8">
                <div style="float: left;width: 40px"><i class="el-icon-back alumb-back" @click="$router.back()"></i></div>
                <div class="album-cover" :style="{'background-image':'url('+apiUrl+'/'+album.cover_path+'/'+album.cover_name+')'}"></div>
                <div style="float: left">{{album.name}}
                    <span v-if="album.photos>0">({{album.photos}} 张照片)</span>
                </div>
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
                album: {  //影集信息
                    name: '',
                    cover_path: '',
                    cover_name: '',
                    photos: 0,
                },
            }
        },
        props: [
            'onClose',
        ],
        computed: {
            apiUrl() {
                return this.$store.state.apiUrl  //后台api调用地址
            },
            refreshPhoto() {
                return this.$store.state.refreshPhoto  //是否刷新照片列表
            },
        },
        watch: {
            refreshPhoto() {
                //有其它组件发出刷新照片的指令
                if (this.refreshPhoto) {
                    this.getAlbum()
                }
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
                    this.album = result
                })
            },
            openPick() {
                this.$router.push({
                    name: 'pick_photo',
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

    .album-cover {  /*影集封面*/
        float: left;
        margin-top: 9px;
        margin-right: 10px;
        width: 30px;
        height: 30px;
        background-color: #80868b;
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        border-radius: 5px;
    }
</style>