<template>
    <div>
        <el-upload action="http://127.0.0.1:8000/api/uploadfile"
                   :multiple="true"
                   :show-file-list="false"
                   accept="image/*"
                   :before-upload="beforeUpload"
                   :on-success="handleSuccess">
            <el-button icon="el-icon-upload2">上传</el-button>
        </el-upload>
    </div>
</template>

<script>
    export default {
        name: "UploadFile",
        data() {
            return {}
        },
        methods: {
            beforeUpload(file) {  //文件上传之前
                const extension_name = file.name.substring(file.name.lastIndexOf('.') + 1)
                const accept_list = ['jpg', 'jpeg', 'png', 'bmp']
                const isImage = accept_list.indexOf(extension_name) != -1
                if (!isImage) {
                    let newDate = new Date()
                    let msg = '不支持 ' + file.name + ' 的文件格式'
                    this.$root.eventBus.$emit('showLog', 'error', msg, newDate.toLocaleTimeString())
                }
                return isImage
            },
            handleSuccess(response, file) {  //文件上传成功之后
                let newDate = new Date()
                if (response.msg == 'success') {
                    let msg = file.name + '上传成功'
                    this.$root.eventBus.$emit('showLog', 'success', msg, newDate.toLocaleTimeString())
                }
                else {
                    let msg = file.name + '上传失败'
                    this.$root.eventBus.$emit('showLog', 'error', msg, newDate.toLocaleTimeString())
                }
            }
        }
    }
</script>

<style scoped>

</style>