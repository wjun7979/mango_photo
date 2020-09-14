<template>
    <el-container style="height: 100%;">
        <el-header height="72px" class="div-header">
            <Header></Header>
        </el-header>
        <el-container class="div-body">
            <el-aside width="256px" class="div-menu">
                <NavMenu></NavMenu>
            </el-aside>
            <el-main class="div-main">
                <transition name="fade" :duration="{ enter: 1000, leave: 0 }">
                    <router-view :key="$route.fullPath"></router-view>
                </transition>
            </el-main>
        </el-container>
        <el-footer height="48px" class="div-footer">
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
    .div-header { /*顶部*/
        position: fixed;
        width: 100%;
        min-width: 1280px;
        padding: 0;
        background-color: #fff;
        z-index: 2;
    }

    .div-body { /*中部*/
        padding-top: 72px;
        padding-bottom: 48px;
    }

    .div-footer { /*底部*/
        position: fixed;
        bottom: 0;
        width: 100%;
        min-width: 1280px;
        padding: 0;
        background-color: #fff;
        z-index: 1;
    }

    .div-menu {  /*菜单*/
        position: fixed;
    }

    .div-main {  /*主内容区*/
        padding: 0 0 0 266px
    }

    /*路由切换过渡动画*/
    .fade-enter-active, .fade-leave-active {
        transition: opacity .5s;
    }

    .fade-enter, .fade-leave-to {
        opacity: 0;
    }
</style>
