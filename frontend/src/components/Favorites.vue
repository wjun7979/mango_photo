<template>
    <el-container>
        <el-header class="mp-page-header" height="64px">
            <el-col class="mp-page-header-title" :span="14">
                <ToggleMenu></ToggleMenu>
                <span>收藏夹</span>
            </el-col>
            <el-col :span=10 style="text-align: right">
                <PickPhotoButton style="margin: 19px 20px 0 0"></PickPhotoButton>
            </el-col>
        </el-header>
        <el-main class="mp-page-main">
            <PhotoList callMode="favorites"></PhotoList>
        </el-main>
    </el-container>
</template>

<script>
    import PhotoList from "./PhotoList";
    import ToggleMenu from "./MainHeader/ToggleMenu";
    import PickPhotoButton from "./MainHeader/PickPhotoButton";

    export default {
        name: "Favorites",
        components: {PickPhotoButton, ToggleMenu, PhotoList},
    }
</script>

<style scoped>

</style>