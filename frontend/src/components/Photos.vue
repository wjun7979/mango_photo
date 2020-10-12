<template>
    <el-container>
        <el-header class="mp-page-header" height="64px">
            <el-col class="mp-page-header-title" :span="12">
                <ToggleMenu></ToggleMenu>
                <span>照片</span>
            </el-col>
            <el-col :span="12" style="text-align: right; padding-right: 10px">
                <SearchButton></SearchButton>
                <UploadFile style="margin-left: 20px"></UploadFile>
                <PickPhotoButton style="margin-left: 20px"></PickPhotoButton>
            </el-col>
        </el-header>
        <el-main class="mp-page-main">
            <PhotoList></PhotoList>
        </el-main>
    </el-container>
</template>

<script>
    import PhotoList from "./PhotoList";
    import UploadFile from "./MainHeader/UploadFile";
    import ToggleMenu from "./MainHeader/ToggleMenu";
    import SearchButton from "./MainHeader/SearchButton";
    import PickPhotoButton from "./MainHeader/PickPhotoButton";

    export default {
        name: "Photos",
        components: {PickPhotoButton, SearchButton, ToggleMenu, PhotoList, UploadFile},
    }
</script>

<style scoped>

</style>