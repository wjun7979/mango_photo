<template>
    <el-container style="height: 100%;">
        <el-header height="72px" style="padding: 0">
            <Header></Header>
        </el-header>
        <el-container>
            <el-aside width="256px">
                <NavMenu></NavMenu>
            </el-aside>
            <el-main style="padding: 0">
                <router-view></router-view>
            </el-main>
        </el-container>
        <el-footer height="48px" style="padding: 0">
            <Footer></Footer>
        </el-footer>
    </el-container>
</template>

<script>
    import Header from "./Header";
    import NavMenu from "./NavMenu";
    import Footer from "./Footer";

    export default {
        name: 'Main',
        components: {
            Footer, Header, NavMenu
        },
    }
</script>

<style scoped>

</style>
