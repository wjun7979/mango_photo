<template>
    <div>
        <el-upload class="upload-wrap" action="" :drag="true" :multiple="true">
            <img src="../assets/images/upload-bg.png" />
            <div style="font-size: 32px; line-height: 50px; font-weight: 400; color: #202124">准备好添加一些照片了吗？</div>
            <div style="font-size: 16px; line-height: 40px; font-weight: 400; color: #3c4043">将照片和视频拖放至任意位置即可上传</div>
        </el-upload>
    </div>
</template>

<script>
    export default {
        name: "Browse"
    }
</script>

<style scoped>
    .upload-wrap {
        text-align: center;
    }
    .upload-wrap >>> .el-upload-dragger {
        width: 729px;
        height: 459px;
        padding: 20px;
    }
</style>