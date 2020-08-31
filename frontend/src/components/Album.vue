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
        <el-main :style="{height: mainHeight, overflow: 'auto', padding: 0}">
            <PhotoList callMode="album" :albumUUID="albumUUID" :albumName="albumName"></PhotoList>
        </el-main>

        <AddPhotoToAlbum v-if="isShowAddPhotoToAlbum" :albumUUID="albumUUID" :albumName="albumName"
                         :albumPhotoList="albumPhotoList"
                         :on-close="closePick"></AddPhotoToAlbum>
    </el-container>
</template>

<script>
    import PhotoList from "./PhotoList"
    import CreateAlbum from "./CreateAlbum";
    import AddPhotoToAlbum from "./AddPhotoToAlbum";

    export default {
        name: "Album",
        components: {AddPhotoToAlbum, PhotoList, CreateAlbum},
        data() {
            return {
                albumUUID: this.$route.params.uuid,  //影集uuid
                albumName: '',  //影集标题
                isShowAddPhotoToAlbum: false,  //是否显示添加照片到影集的选择界面
                albumPhotoList: [],  //影集中的照片列表
            }
        },
        props: [
            'onClose',
        ],
        computed: {
            apiUrl() {
                return this.$store.state.apiUrl  //后台api调用地址
            },
            mainHeight() {
                return this.$store.state.mainHeight  //主内容区的高度
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
                this.$store.commit('cancelSelectPhoto', {action: true})  //取消已选中的照片
                //打开照片选择界面，将当前影集中的照片传入组件进行初始选中
                this.$axios({
                    method: 'get',
                    url: this.apiUrl + '/api/photo_list',
                    params: {
                        userid: localStorage.getItem('userid'),
                        call_mode: 'album',
                        album_uuid: this.albumUUID,
                    }
                }).then(response => {
                    this.albumPhotoList = []
                    for (let item of response.data) {
                        this.albumPhotoList.push(item.uuid)
                    }
                    this.isShowAddPhotoToAlbum = true
                })
            },
            closePick() {
                //关闭照片选择界面
                this.isShowAddPhotoToAlbum = false
            },
        }
    }
</script>

<style scoped>
    .alumb-back { /*影集页头的返回按钮*/
        padding: 8px;
        margin-right: 10px;
        color: #5f6368;
        cursor: pointer;
    }

    .alumb-back:hover {
        background-color: #e5e5e5;
        border-radius: 50%;
    }
</style>