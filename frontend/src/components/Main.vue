<template>
    <el-container style="height: 100%;">
        <el-header height="72px" style="padding: 0">
            <Header></Header>
        </el-header>
        <el-container>
            <el-aside width="256px">
                <NavMenu></NavMenu>
            </el-aside>
            <el-main :style="{height: main_height}">
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
        data() {
            return {
                main_height: document.documentElement.clientHeight - 72 - 48 + 'px',
            }
        },
        components: {
            Footer, Header, NavMenu
        },
        created() {
            this.$store.commit('setApiUrl')  //根据客户端访问地址改变API请求地址
        },
        mounted() {
            window.addEventListener('resize', this.listenResize)
        },
        beforeDestroy() {
            window.removeEventListener('resize', this.listenResize)
        },
        methods: {
            listenResize: function () {
                this.main_height = document.documentElement.clientHeight - 72 - 48 + 'px'
            }
        }
    }
</script>

<style scoped>

</style>
