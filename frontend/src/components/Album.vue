<template>
    <el-container>
        <el-header class="mp-page-header" height="64px">
            <el-col class="mp-page-header-title" :span="14">
                <div style="float: left;width: 40px"><i class="el-icon-back mp-page-header-back" @click="$router.back()"></i></div>
                <div class="album-cover hidden-xs-only" :style="{'background-image':'url('+apiUrl+'/'+album.cover_path+'/'+album.cover_name+')'}"></div>
                <div class="album-title">{{album.name}}</div>
            </el-col>
            <el-col :span=10 style="text-align: right">
                <CreateAlbum buttonText="创建子影集" :parentUUID="albumUUID"></CreateAlbum>
                <el-button class="hidden-mobile-only" icon="iconfont icontianjiatupian" size="middle" @click="openPick"
                           style="margin: 11px 20px 0 20px">添加照片
                </el-button>
                <i class="iconfont icontianjiatupian icon-button hidden-pc-only" @click="openPick"
                   style="margin-left: 20px; font-size: 22px"></i>
                <MoreOption style="margin: 0 20px"></MoreOption>
            </el-col>
        </el-header>
        <el-main class="mp-page-main">
            <PhotoList callMode="album" :albumUUID="albumUUID"></PhotoList>
        </el-main>
    </el-container>
</template>

<script>
    import PhotoList from "./PhotoList"
    import CreateAlbum from "./MainHeader/CreateAlbum";
    import MoreOption from "./MainHeader/MoreOption";

    export default {
        name: "Album",
        components: {MoreOption, PhotoList, CreateAlbum},
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
    .album-cover {  /*影集封面*/
        float: left;
        margin-top: 17px;
        margin-right: 10px;
        width: 30px;
        height: 30px;
        background-color: #80868b;
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        border-radius: 5px;
    }

    .album-title {
        float: left;
        width: calc(100% - 80px);
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
    }
    @media only screen and (max-width: 767px) {
        .album-title {
            width: calc(100% - 50px);
        }
    }
</style>