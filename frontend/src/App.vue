<template>
    <div class="mp-index-wrap">
        <transition name="fade" :duration="{ enter: 1000, leave: 0 }">
            <router-view></router-view>
        </transition>
    </div>
</template>

<script>
    export default {
        name: 'App'
    }
</script>

<style scoped>
    /*路由切换过渡动画*/
    .fade-enter-active, .fade-leave-active {
        transition: opacity .5s;
    }

    .fade-enter, .fade-leave-to {
        opacity: 0;
    }
</style>