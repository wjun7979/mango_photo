<template>
    <div class="div-container">
        <el-row type="flex">
            <el-col :span="4">
                <span class="span-title">芒果相册</span>
            </el-col>
            <el-col :span="10">
                <el-input class="input-search" placeholder="搜索你的照片" prefix-icon="el-icon-search"></el-input>
            </el-col>
            <el-col :span="10" style="text-align: right">
                <UploadFile></UploadFile>
            </el-col>
        </el-row>
    </div>
</template>

<script>
    import UploadFile from "./UploadFile";
    export default {
        name: "Header",
        components: {UploadFile}
    }
</script>

<style scoped>
    .div-container {
        height: 64px;
        padding: 12px;
        border-bottom: 1px solid #dadce0;
    }
    .span-title {
        padding-left: 35px;
        background-image: url("../assets/images/mango.png");
        background-size: 29px;
        background-repeat: no-repeat;
        line-height: 40px;
        color: #5f6368;
        font-size: 20px;
        vertical-align: middle;
    }
    /* >>> 是深度作用选择器，它可以让scoped样式中的一个选择器作用得“更深”，例如影响子组件*/
    .input-search >>> .el-input__inner {
        background-color: #F1F3F4;
    }
</style>