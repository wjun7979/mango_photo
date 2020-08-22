<template>
    <div class="div-container">
        <el-row type="flex">
            <el-col style="width: 256px;">
                <span class="span-title">芒果相册</span>
            </el-col>
            <el-col :span="10">
                <el-input class="input-search" placeholder="搜索你的照片" v-model="keyword" prefix-icon="el-icon-search"></el-input>
            </el-col>
            <el-col :span="10" style="text-align: right">
                <UploadFile></UploadFile>
            </el-col>
            <el-col style="width: 60px; text-align: center;">
                <UserCard></UserCard>
            </el-col>
        </el-row>

    </div>
</template>

<script>
    import UploadFile from "./UploadFile";
    import UserCard from "./UserCard";

    export default {
        name: "Header",
        components: {UserCard, UploadFile},
        data () {
            return {
                keyword: ''  //搜索关键字
            }
        }
    }
</script>

<style scoped>
    .div-container {  /*最外层容器*/
        height: 64px;
        padding: 12px;
        border-bottom: 1px solid #dadce0;
    }
    .span-title {  /*logo标题*/
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