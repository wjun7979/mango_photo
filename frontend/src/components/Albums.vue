<template>
    <el-container>
        <el-header class="mp-page-header" height="56px">
            <el-col class="mp-page-header-title" :span="8">影集</el-col>
            <el-col :span="16" style="text-align: right; padding: 8px 20px 0 0">
                <CreateAlbum></CreateAlbum>
            </el-col>
        </el-header>
        <el-main :style="{height: mainHeight, overflow: 'auto', padding: 0}">
            <AlbumList></AlbumList>
        </el-main>
    </el-container>
</template>

<script>
    import AlbumList from "./AlbumList";
    import CreateAlbum from "./CreateAlbum";

    export default {
        name: "Albums",
        components: {AlbumList, CreateAlbum},
        computed: {
            mainHeight() {
                return this.$store.state.mainHeight  //主内容区的高度
            },
        },
    }
</script>

<style scoped>

</style>