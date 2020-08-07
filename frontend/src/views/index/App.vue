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
                <el-main :style="{height: main_height}">
                    <router-view></router-view>
                </el-main>
            </el-container>
            <el-footer height="48px" style="padding: 0">
                <Footer></Footer>
            </el-footer>
        </el-container>
    </div>
</template>

<script>
    import Header from "../../components/Header";
    import NavMenu from "../../components/NavMenu";
    import Footer from "../../components/Footer";

    export default {
        name: 'Index',
        data() {
            return {
                main_height: this.listenResize(),
            }
        },
        components: {
            Footer, Header, NavMenu
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
