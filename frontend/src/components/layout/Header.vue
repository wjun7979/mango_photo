<template>
    <el-container class="div-container">
        <el-aside width="256px" style="overflow:hidden">
            <span class="span-title">芒果相册</span>
        </el-aside>
        <el-main style="overflow:hidden; padding: 12px 20px 12px 0">
            <el-row>
                <el-col :span="14">
                    <el-input class="input-search hidden-xs-only" placeholder="搜索你的照片" v-model="keyword"
                              prefix-icon="el-icon-search" :clearable="true" @clear="clearKeyword"
                              @keypress.native="search($event)"></el-input>
                </el-col>
                <el-col :span="10" style="text-align: right">
                    <UserCard></UserCard>
                </el-col>
            </el-row>
        </el-main>
    </el-container>
</template>

<script>
    import UserCard from "../UserCard";

    export default {
        name: "Header",
        data () {
            return {
                keyword: ''  //搜索关键字
            }
        },
        components: {UserCard},
        computed: {
            showMenu() {
                return this.$store.state.showMenu  //小尺寸屏幕下是否显示菜单
            },
            searchKeyword() {  //全局搜索关键字
                return this.$store.state.searchKeyword
            },
        },
        watch: {
            searchKeyword(val) {
                this.keyword = val
            }
        },
        methods: {
            toggleMenu() {
                //切换菜单
                this.$store.commit('showMenu', {show: !this.showMenu})
            },
            search(e) {
                //搜索
                if (e.keyCode === 13) {
                    this.$root.searchPhoto(this.keyword)
                }
            },
            clearKeyword() {
                //清除搜索关键字
                this.$store.commit('searchKeyword', {keyword: ''})
            },
        }
    }
</script>

<style scoped>
    .div-container {  /*最外层容器*/
        height: 64px;
        padding: 0;
        border-bottom: 1px solid #dadce0;
        margin-bottom: 8px;
    }
    .span-title {  /*logo标题*/
        display: block;
        margin-left: 20px;
        margin-top: 11px;
        padding-left: 35px;
        background-image: url("../../assets/images/mango.png");
        background-size: 29px;
        background-repeat: no-repeat;
        background-position-y: 5px;
        line-height: 40px;
        color: #5f6368;
        font-size: 20px;
        vertical-align: middle;
    }
    /* >>> 是深度作用选择器，它可以让scoped样式中的一个选择器作用得“更深”，例如影响子组件*/
    .input-search >>> .el-input__inner {
        background-color: #F1F3F4;
    }
</style>