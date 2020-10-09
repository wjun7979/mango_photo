<template>
    <el-container>
        <el-header class="mp-page-header" height="64px">
            <el-col class="mp-page-header-title" :span="24">
                <ToggleMenu></ToggleMenu>
                <span>收藏夹</span>
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

    export default {
        name: "Favorites",
        components: {ToggleMenu, PhotoList},
    }
</script>

<style scoped>

</style>