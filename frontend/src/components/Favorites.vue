<template>
    <el-container>
        <el-header class="mp-page-header" height="64px">
            <el-col class="mp-page-header-title" :span="14">
                <div style="float: left;width: 40px"><i class="el-icon-back mp-page-header-back" @click="$router.back()"></i></div>
                <span>收藏夹</span>
            </el-col>
            <el-col :span=10 style="text-align: right">
                <SearchButton style="margin-right: 20px"></SearchButton>
                <MoreOption style="margin: 19px 20px 0 0"></MoreOption>
            </el-col>
        </el-header>
        <el-main class="mp-page-main">
            <PhotoList callMode="favorites"></PhotoList>
        </el-main>
    </el-container>
</template>

<script>
    import PhotoList from "./PhotoList";
    import MoreOption from "./MainHeader/MoreOption";
    import SearchButton from "./MainHeader/SearchButton";

    export default {
        name: "Favorites",
        components: {MoreOption, PhotoList, SearchButton},
    }
</script>

<style scoped>

</style>