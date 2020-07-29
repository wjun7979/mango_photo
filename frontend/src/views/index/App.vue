<template>
    <div class="index-wrap">
        <el-container style="height: 100%;">
            <el-header height="72px" style="padding: 0">
                <Header></Header>
            </el-header>
            <el-container>
                <el-aside width="256px">
                    <NavMenu></NavMenu>
                </el-aside>
                <el-main>
                    <router-view></router-view>
                </el-main>
            </el-container>
            <el-footer>Footer</el-footer>
        </el-container>
    </div>
</template>

<script>
    import Header from "../../components/Header";
    import NavMenu from "../../components/NavMenu";

    export default {
        name: 'Index',
        components: {
            Header, NavMenu
        }
    }
</script>

<style scoped>

</style>
