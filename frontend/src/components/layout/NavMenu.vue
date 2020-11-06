<template>
    <div class="div-container">
        <div class="hidden-sm-and-up" style="border-bottom: 1px solid #dadce0;">
            <span class="span-title">芒果相册</span>
            <UserCard style="margin-top: 10px"></UserCard>
        </div>
        <el-menu :default-active="$route.path" router @select="selectMenu">
            <el-menu-item index="/photos">
                <i class="el-icon-picture-outline"></i>
                <span>照片</span>
            </el-menu-item>
            <el-menu-item-group title="照片库">
                <el-menu-item index="/albums">
                    <i class="el-icon-collection"></i>
                    <span>影集</span>
                </el-menu-item>
                <el-menu-item index="/peoples">
                    <i class="el-icon-user"></i>
                    <span>人物</span>
                </el-menu-item>
                <el-menu-item index="/favorites">
                    <i class="el-icon-star-off"></i>
                    <span>收藏夹</span>
                </el-menu-item>
                <el-menu-item index="/trash">
                    <i class="el-icon-delete"></i>
                    <span>回收站</span>
                </el-menu-item>
            </el-menu-item-group>
        </el-menu>
    </div>
</template>

<script>
    import UserCard from "../UserCard";

    export default {
        name: "NavMenu",
        components: {UserCard},
        methods: {
            selectMenu() {
                this.$store.commit('showMenu', {show: false})
            },
        }
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

    .div-container >>> .el-menu-item-group__title {
        margin: 10px 0;
    }
    .span-title {  /*logo标题*/
        display: inline-block;
        margin: 10px 0 10px 20px;
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
</style>