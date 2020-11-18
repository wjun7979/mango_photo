<template>
    <el-container style="height: 100%;">
        <el-header height="72px" class="div-header hidden-xs-only">
            <Header></Header>
        </el-header>
        <el-container class="div-body">
            <el-aside width="256px" :class="{'hidden-xs-only': !showMenu}" class="div-aside">
                <NavMenu class="div-menu"></NavMenu>
                <Statistics></Statistics>
            </el-aside>
            <el-main class="div-main">
                <transition name="fade" :duration="{ enter: 1000, leave: 0 }">
                    <router-view></router-view>
                </transition>
            </el-main>
        </el-container>
    </el-container>
</template>

<script>
    import Header from "./Header";
    import NavMenu from "./NavMenu";
    import Statistics from "./Statistics";

    export default {
        name: 'Main',
        components: {
            Header, NavMenu, Statistics
        },
        computed: {
            showMenu() {
                return this.$store.state.showMenu  //小尺寸屏幕下是否显示菜单
            },
        },
    }
</script>

<style scoped>
    .div-header { /*顶部*/
        position: fixed;
        width: 100%;
        min-width: 320px;
        padding: 0;
        background-color: #fff;
        z-index: 2;
    }

    .div-body { /*中部*/
        padding-top: 64px;
    }
    @media only screen and (max-width: 767px) {
        .div-body {
            padding-top: 0;
        }
    }

    .div-aside { /*侧边栏*/
        position: fixed;
        top: 64px;
        z-index: 2;
        height: calc(100% - 64px);
        overflow: hidden;
        background-color: #fff;
        border-right: 1px solid #dadce0;
    }

    .div-menu {  /*菜单*/
        height: calc(100% - 56px);
    }

    .div-main {  /*主内容区*/
        padding: 0 0 0 256px;
    }
    @media only screen and (max-width: 767px) {
        .div-main {
            padding: 0;
        }
    }

    /*路由切换过渡动画*/
    .fade-enter-active, .fade-leave-active {
        transition: opacity .5s;
    }

    .fade-enter, .fade-leave-to {
        opacity: 0;
    }
</style>
