<template>
    <el-container>
        <el-header class="mp-page-header" height="64px">
            <el-col class="mp-page-header-title" :span="12">
                <ToggleMenu></ToggleMenu>
                <span>影集</span>
            </el-col>
            <el-col :span="12" style="text-align: right">
                <SearchButton style="margin-right: 20px"></SearchButton>
                <CreateAlbum style="margin-right: 20px"></CreateAlbum>
            </el-col>
        </el-header>
        <el-main class="mp-page-main">
            <el-row :gutter="20" style="margin: 20px 0 30px 0">
                <el-col :xs="{span:8}" :sm="{span:6}" :lg="{span:4}" :xl="{span:3}">
                    <router-link to="/favorites">
                        <div class="group favorites"></div>
                    </router-link>
                    <div class="group-title">
                        <i class="el-icon-star-off" style="margin-right: 5px"></i>
                        <span>收藏夹</span>
                    </div>
                </el-col>
                <el-col :xs="{span:8}" :sm="{span:6}" :lg="{span:4}" :xl="{span:3}">
                    <router-link to="/peoples">
                        <div class="group people"></div>
                    </router-link>
                    <div class="group-title">
                        <span>人物</span>
                    </div>
                </el-col>
                <el-col :xs="{span:8}" :sm="{span:6}" :lg="{span:4}" :xl="{span:3}">
                    <router-link to="/locations">
                        <div class="group location"></div>
                    </router-link>
                    <div class="group-title">地点</div>
                </el-col>
            </el-row>
            <AlbumList></AlbumList>
        </el-main>
    </el-container>
</template>

<script>
    import AlbumList from "./AlbumList";
    import ToggleMenu from "./MainHeader/ToggleMenu";
    import CreateAlbum from "./MainHeader/CreateAlbum";
    import SearchButton from "./MainHeader/SearchButton";

    export default {
        name: "Albums",
        components: {SearchButton, ToggleMenu, AlbumList, CreateAlbum},
    }
</script>

<style scoped>
    .group {  /*系统分组*/
        background-color: #e8eaed;
        border-radius: 8px;
        cursor: pointer;
    }
    .group:before {  /*使分组容器宽和高保持一致*/
        content: " ";
        display: block;
        padding-top: 100%;
    }
    .group-title {  /*系统分组的标题*/
        margin: 8px 0 16px 0;
        font-size: 14px;
    }
    .favorites {
        background-image: url('../assets/images/sys-group/favorites.png');
        background-position: center;
        background-repeat: no-repeat;
        background-size: 50%;
    }
    .people {
        background-image: url('../assets/images/sys-group/people.png');
        background-position: center;
        background-repeat: no-repeat;
        background-size: 50%;
    }
    .location {
        background-image: url('../assets/images/sys-group/location.png');
        background-position: center;
        background-repeat: no-repeat;
        background-size: 50%;
    }
</style>