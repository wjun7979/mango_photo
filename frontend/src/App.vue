<template>
    <div class="mp-index-wrap">
        <transition name="fade" :duration="{ enter: 1000, leave: 0 }">
            <router-view></router-view>
        </transition>

        <!--回到顶部-->
        <el-backtop :right="20" :bottom="50" style="z-index: 1"></el-backtop>

        <!--文件上传进度条-->
        <el-card v-if="showUploadProgress" class="upload-progress">
            <p class="upload-progress-tips">正在上传 {{fileTotal}} 张照片...</p>
            <el-progress :percentage="percentage" :text-inside="true" :stroke-width="20"></el-progress>
            <p class="upload-progress-warning">上传完成前请勿刷新浏览器！</p>
        </el-card>
    </div>
</template>

<script>
    export default {
        name: 'App',
        computed: {
            showUploadProgress() {
                return this.$store.state.progress.show  //是否显示进度条
            },
            fileTotal() {
                return this.$store.state.progress.total  //上传文件的数量
            },
            percentage() {
                return this.$store.state.progress.percentage  //当前进度百分比
            }
        },
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

    .upload-progress {  /*上传进度条*/
        position: fixed;
        left: 20px;
        bottom: 50px;
        width: 320px;
        z-index: 2;
    }
    .upload-progress-tips {
        text-align: left;
        padding: 0 0 10px 0;
    }
    .upload-progress-warning {
        text-align: left;
        font-size: 14px;
        color: #F56C6C;
        padding: 10px 0 0 0;
    }
</style>