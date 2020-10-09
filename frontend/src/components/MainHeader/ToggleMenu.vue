<template>
    <div class="btn-menu hidden-sm-and-up">
        <i :class="{'el-icon-s-unfold':!showMenu, 'el-icon-s-fold':showMenu}" @click="toggleMenu"></i>
    </div>
</template>

<script>
    export default {
        name: "ToggleMenu",
        computed: {
            showMenu() {
                return this.$store.state.showMenu  //小尺寸屏幕下是否显示菜单
            },
        },
        methods: {
            toggleMenu() {
                //切换菜单
                this.$store.commit('showMenu', {show: !this.showMenu})
            },
        }
    }
</script>

<style scoped>
    .btn-menu {  /*小尺寸屏幕下的菜单切换按钮*/
        float: left;
        width: 25px;
        margin-top: 1px;
        margin-right: 10px;
        font-size: 24px;
    }
</style>