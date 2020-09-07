<template>
    <el-container>
        <el-header class="mp-page-header" height="56px">
            <el-col class="mp-page-header-title" :span="8">
                <span>照片</span>
            </el-col>
            <el-col :span="16" style="text-align: right; padding: 8px 20px 0 0">
                <UploadFile></UploadFile>
            </el-col>
        </el-header>
        <el-main class="mp-page-main">
            <PhotoList></PhotoList>
        </el-main>
    </el-container>
</template>

<script>
    import PhotoList from "./PhotoList";
    import UploadFile from "./UploadFile";

    export default {
        name: "Photos",
        components: {PhotoList, UploadFile},
    }
</script>

<style scoped>

</style>