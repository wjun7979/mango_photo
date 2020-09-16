<template>
    <el-container>
        <el-header class="mp-page-header" height="56px" style="padding: 4px 0 0 0">
            <el-col class="mp-page-header-title" :span="8">
                <i class="el-icon-close pick-close" @click="$router.back()"></i>
                <span v-if="addList.length===0 && removeList.length===0">添加到影集：{{albumName}}</span>
                <span v-if="addList.length>0" style="padding-left: 7px;">添加了 {{addList.length}} 张照片</span>
                <span v-if="addList.length>0 && removeList.length>0" style="padding-left: 7px;">，</span>
                <span v-if="removeList.length>0" style="padding-left: 7px;">移除了 {{removeList.length}} 张照片</span>
            </el-col>
            <el-col :span="16" style="text-align: right">
                <el-form :inline="true" style="margin-top: 2px;">
                    <el-form-item>
                        <UploadFile callMode="album" :albumUUID="albumUUID" button-text="从计算机中选择"
                                    :on-completed="onClose"></UploadFile>
                    </el-form-item>
                    <el-form-item style="padding-right: 10px">
                        <el-button type="primary" size="small" @click="finishPick">完成</el-button>
                    </el-form-item>
                </el-form>
            </el-col>
        </el-header>
        <el-main style="padding-top: 56px">
            <PhotoList callMode="pick" :albumUUID="albumUUID" :albumPhotoList="albumPhotoList"
                       :on-pick="onPick"></PhotoList>
        </el-main>
    </el-container>
</template>

<script>
    import PhotoList from "./PhotoList";
    import UploadFile from "./UploadFile";

    export default {
        name: "Pick",
        data() {
            return {
                albumUUID: this.$route.params.albumUUID,
                albumName: '',
                albumPhotoList: [],  //影集中的照片列表
                addList: [],  //添加的照片列表
                removeList: [],  //移除的照片列表
            }
        },
        components: {PhotoList, UploadFile},
        computed: {
            apiUrl() {
                return this.$store.state.apiUrl  //后台api调用地址
            },
        },
        mounted() {
            this.getAlbum()
            this.getAlbumPhotoList()
        },
        created() {
            //防抖
            this._pickToAlbum = this.$lodash.debounce(this.pickToAlbum, this.$common.DEBOUNCE_TIMEOUT, {
                leading: true,
                trailing: false
            })
        },
        methods: {
            onClose() {
                this.$router.back()
            },
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
            getAlbumPhotoList() {
                //获取当前影集中的照片，进行初始选中
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
                })
            },
            onPick(removeList, addList) {
                //当选中列表值改变时的回调
                this.addList = addList
                this.removeList = removeList
            },
            finishPick() {
                //完成选择
                if (this.removeList.length > 0) {
                    this.$confirm('您仍然可以在相册中找到该内容', '要移除此内容吗？', {
                        confirmButtonText: '移除',
                        cancelButtonText: '取消',
                        type: 'warning'
                    }).then(() => {
                        this._pickToAlbum()
                    }).catch(() => {
                    });
                } else {
                    if (this.addList.length > 0) {
                        this._pickToAlbum()
                    }
                    else {
                        this.$router.back()
                    }
                }
            },
            pickToAlbum() {
                //选择照片到影集，包括添加和移除
                this.$axios({
                    method: 'post',
                    url: this.apiUrl + '/api/album_pick_photo',
                    data: {
                        album_uuid: this.albumUUID,
                        add_list: this.addList,
                        remove_list: this.removeList,
                    }
                }).then(() => {
                    let msg = ''
                    if (this.addList.length > 0) {
                        msg = '成功将 ' + this.addList.length + ' 张照片添加到影集 [' + this.albumName + '] 中'
                    }
                    if (this.removeList.length > 0) {
                        if (msg !== '') msg += '； 同时 '
                        msg += this.removeList.length + ' 张照片已从影集 [' + this.albumName + '] 中移除'
                    }
                    this.$message({
                        message: msg,
                        type: 'success',
                    })
                    this.onClose()
                })
            },
        }
    }
</script>

<style scoped>
    .pick-close { /*影集页头的返回按钮*/
        padding: 8px;
        margin-right: 10px;
        color: #5f6368;
        font-weight: bold;
        cursor: pointer;
    }

    .pick-close:hover {
        background-color: #e5e5e5;
        border-radius: 50%;
    }
</style>