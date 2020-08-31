<template>
    <div class="mp-index-wrap">
        <router-view></router-view>
    </div>
</template>

<script>
    export default {
        name: 'App',
        mounted() {
            window.addEventListener('resize', this.listenResize)
        },
        beforeDestroy() {
            window.removeEventListener('resize', this.listenResize)
        },
        methods: {
            listenResize: function () {
                //监听浏览器窗口大小变化的事件
                this.$store.commit('setMainHeight')  //重新设置主内容区的高度
            },
        }
    }
</script>

<style scoped>

</style>