<template>
    <div style="margin: 0 auto; width: 500px; padding-top: 100px;">
        <div style="float: left; width: 300px">
            <el-button type="primary" icon="el-icon-arrow-left" @click="$router.back()">返回</el-button>
            <p style="font-size: 36px; font-weight: bold; margin: 80px 0 20px 0">404</p>
            <p style="font-size: 24px; font-weight: 500">请求的页面不存在！</p>
        </div>
        <div style="float: right; width: 200px">
            <img src="../assets/images/401.gif" alt=""/>
        </div>
    </div>
</template>

<script>
    export default {
        name: "NotFound"
    }
</script>

<style scoped>

</style>