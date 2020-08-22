<template>
    <div>
        <el-button icon="el-icon-upload2" @click="show_upload_dialog = true">上 传</el-button>
        <el-dialog title="上传"
                   :visible.sync="show_upload_dialog"
                   :close-on-click-modal="false"
                   width="840px"
                   style="text-align: left">
            <div class="div-el-dialog">
                <el-upload :action="api_url + '/api/upload_photo'"
                           ref="upload"
                           :multiple="true"
                           list-type="picture-card"
                           :show-file-list="true"
                           accept="image/*"
                           :headers="headers"
                           :data="upload_data"
                           :auto-upload="false"
                           :on-change="handleChange"
                           :before-upload="beforeUpload"
                           :on-success="handleSuccess"
                           :on-error="handleError">
                    <i class="el-icon-plus"></i>
                </el-upload>
            </div>
            <span slot="footer" class="dialog-footer">
                <el-button @click="clearFiles">清 空</el-button>
                <el-button @click="submitUpload">提 交</el-button>
                <el-button @click="show_upload_dialog = false">关 闭</el-button>
            </span>
        </el-dialog>

    </div>
</template>

<script>
    export default {
        name: "UploadFile",
        data() {
            return {
                headers: {userid: localStorage.getItem('userid'), token: localStorage.getItem('token')},
                upload_data: {
                    userid: localStorage.getItem('userid'),  //当前用户id
                    dt: ''  //上传时附带的参数，文件的最后修改时间
                },
                show_upload_dialog: false,  //是否显示上传对话框
                fileList: [],
            }
        },
        computed: {
            api_url() {
                return this.$store.state.api_url  //从全局状态管理器中获取数据
            },
        },
        methods: {
            beforeUpload(file) {
                //将文件的最后修改时间附加到上传参数中
                let fileDate = this.$common.date_format(file.lastModifiedDate, 'yyyy-MM-dd hh:mm:ss')
                this.upload_data.dt = fileDate
            },
            submitUpload(){
                //提交
                this.$refs.upload.submit()
            },
            handleSuccess(response, file) {
                //文件上传成功时
                let newDate = new Date()
                let msg = file.name + '上传成功'
                this.$store.commit('showLog', {type: 'success', msg: msg, time: newDate.toLocaleTimeString()})
            },
            handleChange(file, fileList) {
                //文件状态改变时
                this.fileList = fileList
                let newDate = new Date()
                if (file.status === 'ready') {  // 文件添加之后
                    //检查文件类型
                    //上传文件的扩展名
                    const extension_name = file.name.substring(file.name.lastIndexOf('.') + 1).toLowerCase()
                    const accept_list = ['jpg', 'jpeg', 'png', 'bmp']  //允许上传的文件类型列表
                    const isImage = accept_list.indexOf(extension_name) !== -1
                    if (!isImage) {
                        let msg = '不支持 ' + file.name + ' 的文件格式'
                        this.$store.commit('showLog', {type: 'error', msg: msg, time: newDate.toLocaleTimeString()})
                        fileList.pop()
                    }
                    //检查文件大小
                    const isOverSize = file.size / 1024 / 1024 <= 20
                    if (!isOverSize) {
                        let msg = file.name + ' 文件大小超过了20MB'
                        this.$store.commit('showLog', {type: 'error', msg: msg, time: newDate.toLocaleTimeString()})
                        fileList.pop()
                    }
                    //检查是否重复添加
                    let existFile = fileList.slice(0, fileList.length - 1).find(f => f.name === file.name)
                    if (existFile) {
                        fileList.pop()
                    }
                }
                //检查是否全部上传完毕
                let readyList = this.fileList.filter(t => t.status === 'ready')
                if (readyList.length === 0) {
                    this.$store.commit('refreshPhoto', {show: true})  //刷新图片列表
                    this.clearFiles()
                    this.show_upload_dialog = false  //关闭上传对话框
                }
            },
            handleError(err, file) {
                //文件上传失败时
                const result =  JSON.parse(err.message)  //关键点，得用JSON.parse来解析err里面的内容
                let newDate = new Date()
                let msg = file.name + '上传失败: ' + result.msg
                this.$store.commit('showLog', {type: 'error', msg: msg, time: newDate.toLocaleTimeString()})
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
    .div-el-dialog {
        height: 400px;
        overflow: auto;
    }
</style>