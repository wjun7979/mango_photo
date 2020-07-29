<template>
    <div class="div-container">
        <el-menu :default-active="$route.path" router>
            <el-menu-item index="/">
                <i class="el-icon-picture-outline"></i>
                <span>照片</span>
            </el-menu-item>
            <el-menu-item index="2">
                <i class="el-icon-collection"></i>
                <span>影集</span>
            </el-menu-item>
            <el-menu-item index="/trash">
                <i class="el-icon-delete"></i>
                <span>回收站</span>
            </el-menu-item>
        </el-menu>
    </div>
</template>

<script>
    export default {
        name: "NavMenu"
    }
</script>

<style scoped>
    .div-container >>> .el-menu {
        border: none;
    }

    .div-container >>> .el-menu-item {
        height: 40px;
        line-height: 40px;
    }

    .div-container >>> .el-menu-item:hover {
        background-color: #f1f3f4;
    }

    .div-container >>> .el-menu-item.is-active {
        background-color: #ecf5ff;
        font-weight: 500; /*当前激活菜单加粗*/
    }
</style>