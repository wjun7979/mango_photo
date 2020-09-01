<template>
    <el-container class="pick-wrapper">
        <el-header class="mp-page-header" height="56px">
            <el-col class="mp-page-header-title" :span="8">
                <i class="el-icon-close pick-close" @click="onClose"></i>
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
                    <el-form-item style="padding-right: 20px">
                        <el-button type="primary" size="small" @click="finishPick">完成</el-button>
                    </el-form-item>
                </el-form>
            </el-col>
        </el-header>
        <el-main :style="{height: mainHeight, overflow: 'auto', padding: '20px'}">
            <PhotoList callMode="pick" :albumUUID="albumUUID" :albumName="albumName" :albumPhotoList="albumPhotoList"
                       :on-pick="onPick"></PhotoList>
        </el-main>
    </el-container>
</template>

<script>
    import PhotoList from "./PhotoList";
    import UploadFile from "./UploadFile";
    import {rafThrottle} from "element-ui/src/utils/util";
    import {off, on} from "element-ui/src/utils/dom";

    export default {
        name: "AddPhotoToAlbum",
        data() {
            return {
                addList: [],  //添加的照片列表
                removeList: [],  //移除的照片列表
            }
        },
        components: {PhotoList, UploadFile},
        props: {
            albumUUID: {  //影集uuid
                type: String,
                default: ''
            },
            albumName: {  //影集标题
                type: String,
                default: ''
            },
            albumPhotoList: {  //影集中的照片列表
                type: Array,
                default: () => []
            },
            onClose: {  //关闭照片选择界面时的回调函数
                type: Function,
                default: () => {
                }
            }
        },
        computed: {
            apiUrl() {
                return this.$store.state.apiUrl  //后台api调用地址
            },
            mainHeight() {
                return this.$store.state.mainHeight  //主内容区的高度
            },
        },
        mounted() {
            this.deviceSupportInstall()  //注册键盘按键支持
        },
        beforeDestroy() {
            this.deviceSupportUninstall()  //卸载键盘按键支持
        },
        methods: {
            deviceSupportInstall() {
                //注册键盘按键支持
                this._keyDownHandler = rafThrottle(e => {
                    const keyCode = e.keyCode
                    switch (keyCode) {
                        case 27:  //ESC取消选择
                            this.onClose()
                            break
                    }
                })
                on(document, 'keydown', this._keyDownHandler)
            },
            deviceSupportUninstall() {
                //卸载键盘按键支持
                off(document, 'keydown', this._keyDownHandler)
                this._keyDownHandler = null
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
                        this.pickToAlbum()
                    }).catch(() => {
                    });
                } else {
                    if (this.addList.length > 0) {
                        this.pickToAlbum()
                    }
                    else {
                        this.onClose()
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
                    this.onClose()
                })
            },
        }
    }
</script>

<style scoped>
    .pick-wrapper {
        position: fixed;
        top: 0;
        right: 0;
        bottom: 0;
        left: 0;
        padding-top: 8px;
        text-align: left;
        background-color: #fff;
        z-index: 1100;
    }

    .pick-close { /*影集页头的返回按钮*/
        padding: 8px;
        margin-right: 10px;
        color: #5f6368;
        cursor: pointer;
    }

    .pick-close:hover {
        background-color: #e5e5e5;
        border-radius: 50%;
    }
</style>