<template>
    <div style="display: inline-block">
        <el-button icon="el-icon-upload2" size="middle" @click="showUpload" :type="buttonType" class="hidden-mobile-only"
                   style="margin-top: 11px">
            {{buttonText}}
        </el-button>
        <i class="el-icon-upload2 icon-button hidden-pc-only" @click="showUpload"></i>
        <el-dialog title="上传"
                   :visible.sync="showUploadDialog"
                   :close-on-click-modal="false"
                   :modal-append-to-body='false'
                   top="80px"
                   class="dialog-wrap"
                   style="text-align: left;">
            <div class="div-el-upload">
                <el-upload action=""
                           ref="upload"
                           :multiple="true"
                           :file-list="fileList"
                           list-type="picture-card"
                           :show-file-list="true"
                           accept="image/*"
                           :auto-upload="false"
                           :on-change="handleChange"
                           :on-remove="handleRemove">
                    <i class="el-icon-plus"></i>
                </el-upload>
            </div>
            <span slot="footer" class="dialog-footer">
                <el-button @click="clearFiles">清 空</el-button>
                <el-button @click="submitUpload">提 交</el-button>
                <el-button @click="showUploadDialog = false">关 闭</el-button>
            </span>
        </el-dialog>

        <!--进度条-->
        <el-card v-if="showUploadProgress" class="upload-progress">
            <p class="upload-progress-tips">正在上传 {{this.fileList.length}} 张照片...</p>
            <el-progress :percentage="progress" :text-inside="true" :stroke-width="20"></el-progress>
            <p class="upload-progress-warning">操作完成前请勿关闭或刷新本页面！</p>
        </el-card>
    </div>
</template>

<script>
    export default {
        name: "UploadFile",
        data() {
            return {
                showUploadDialog: false,  //是否显示上传对话框
                fileList: [],  //上传的文件列表
                showUploadProgress: false,  //是否显示上传进度
                progress: 0,  //已完成的上传进度
            }
        },
        props: {
            callMode: {  //调用模式
                type: String,
                default: 'photo'
            },
            albumUUID: {  //当调用模式为album时，必须指定影集uuid
                type: String,
                default: ''
            },
            buttonType: {  //上传按钮类型
                type: String,
                default: ''
            },
            buttonText: {  //上传按钮文本
                type: String,
                default: '上传'
            },
            onCompleted: {  //当上传完成时的回调
                type: Function,
                default: () => {
                }
            },
        },
        computed: {
            apiUrl() {
                return this.$store.state.apiUrl  //后台api调用地址
            },
        },
        methods: {
            showUpload() {
                this.showUploadDialog = true
                if (this.callMode === 'photo') {
                    this.$store.commit('cancelSelectPhoto', {action: true})  //取消已选中的照片
                }
            },
            submitUpload() {
                //提交
                if (this.fileList.length === 0) {
                    this.$message.warning('请选取照片')
                    return
                }

                this.showUploadDialog = false  //关闭上传对话框

                let formData = new FormData()
                // 因为要传一个文件数组过去，所以要循环append
                this.fileList.forEach((file) => {
                    let fileDate = this.$common.dateFormat(new Date(), 'yyyy-MM-dd hh:mm:ss')
                    if (file.raw.lastModifiedDate !== undefined) {
                        fileDate = this.$common.dateFormat(file.raw.lastModifiedDate, 'yyyy-MM-dd hh:mm:ss')
                    }
                    formData.append('file', file.raw)
                    formData.append(file.name, fileDate)
                })

                this.$axios({
                    method: 'post',
                    headers: {'Content-Type': 'multipart/form-data'},
                    url: this.apiUrl + '/api/upload_photo',
                    data: formData,
                    params: {
                        userid: localStorage.getItem('userid'),  //当前用户id
                        call_mode: this.callMode,  //调用模式
                        album_uuid: this.albumUUID  //影集uuid
                    },
                    onUploadProgress: (progressEvent) => {
                        this.showUploadProgress = true
                        let num = progressEvent.loaded / progressEvent.total * 100 | 0;  //百分比
                        this.progress = num
                    }
                }).then(response => {
                    this.showUploadProgress = false
                    let res = response.data
                    let msg = '本次共上传 ' + this.fileList.length + ' 张照片'
                    if (res.success.length > 0)
                        msg += '，成功 ' + res.success.length + ' 张'
                    if (res.error.length > 0)
                        msg += '，失败 ' + res.error.length + ' 张'
                    if (res.error.length === 0) {
                        this.$notify({
                            type: 'success',
                            title: '提示',
                            message: msg,
                            position: 'top-right'
                        })
                    }
                    else {
                        msg += '<div style="width: 250px; max-height: 250px; overflow: auto">'
                        for (let error of res.error) {
                            msg += '<br/>' + error.name + '上传失败: ' + error.msg
                        }
                        msg += '</div>'
                        this.$notify({
                            type: 'error',
                            title: '提示',
                            message: msg,
                            customClass: 'err-notify',
                            dangerouslyUseHTMLString: true,
                            position: 'top-right',
                            duration: 0
                        })
                    }
                    this.$store.commit('refreshPhoto', {show: true})  //刷新图片列表
                    this.$store.commit('refreshPhotoStatistics', {show: true})  //刷新照片库统计信息
                    this.clearFiles()
                    this.onCompleted()  //上传完成后的回调
                }).catch(() => {
                    this.showUploadProgress = false
                    this.clearFiles()
                })
            },
            handleChange(file, fileList) {
                //文件状态改变时
                this.fileList = fileList
                if (file.status === 'ready') {  // 文件添加之后
                    //检查文件类型
                    //上传文件的扩展名
                    const extension_name = file.name.substring(file.name.lastIndexOf('.') + 1).toLowerCase()
                    const accept_list = ['jpg', 'jpeg', 'png', 'bmp']  //允许上传的文件类型列表
                    const isImage = accept_list.indexOf(extension_name) !== -1
                    if (!isImage) {
                        if (document.getElementsByClassName('el-message').length === 0) {
                            let msg = '不支持 ' + file.name + ' 的文件格式'
                            this.$message({
                                message: msg,
                                type: 'error',
                            })
                        }
                        fileList.pop()
                    }
                    //检查文件大小
                    const isOverSize = file.size / 1024 / 1024 <= 20
                    if (!isOverSize) {
                        if (document.getElementsByClassName('el-message').length === 0) {
                            let msg = file.name + ' 文件大小超过了20MB'
                            this.$message({
                                message: msg,
                                type: 'error',
                            })
                        }
                        fileList.pop()
                    }
                    //检查是否重复添加
                    let existFile = fileList.slice(0, fileList.length - 1).find(f => f.name === file.name)
                    if (existFile) {
                        fileList.pop()
                    }
                }
            },
            handleRemove(file, fileList) {
                //文件列表移除文件时的钩子
                this.fileList = fileList
            },
            clearFiles() {
                //清空已上传的文件列表
                if (this.fileList.length > 0) {
                    this.$refs.upload.clearFiles()
                    this.fileList = []
                }
            },
        }
    }
</script>

<style scoped>
    .dialog-wrap >>> .el-dialog {
        width: 840px;
    }

    @media only screen and (max-width: 767px) {
        .dialog-wrap >>> .el-dialog {
            width: 320px;
        }
    }

    .div-el-upload {  /*上传对话框*/
        height: 350px;
        overflow: auto;
    }

    @media only screen and (max-width: 767px) {
        .div-el-upload >>> .el-upload-list--picture-card .el-upload-list__item,
        .div-el-upload >>> .el-upload--picture-card {
            width: 130px;
            height: 130px;
        }
    }

    .upload-progress {  /*上传进度条*/
        position: fixed;
        left: 20px;
        bottom: 60px;
        width: 320px;
        z-index: 2;
    }
    .upload-progress-tips {
        text-align: left;
        padding: 0 0 10px 0;
    }
    .upload-progress-warning {
        text-align: left;
        font-size: 14px;
        color: #F56C6C;
        padding: 10px 0 0 0;
    }
</style>