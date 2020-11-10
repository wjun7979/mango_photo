<template>
    <el-container>
        <el-header class="mp-page-header" height="64px">
            <el-col class="mp-page-header-title" :span="14">
                <div style="float: left;width: 40px"><i class="el-icon-back mp-page-header-back" @click="$router.back()"></i></div>
                <div class="location-title">
                    <span>{{locationProvince}}</span>
                    <span v-if="locationCity!=='none'">{{locationCity}}</span>
                    <span v-if="locationDistrict!=='none'">{{locationDistrict}}</span>
                </div>
            </el-col>
            <el-col :span="10" style="text-align: right">
                <SearchButton style="margin-right: 20px"></SearchButton>
                <MoreOption style="margin: 19px 20px 0 0"></MoreOption>
            </el-col>
        </el-header>
        <el-main class="mp-page-main">
            <PhotoList callMode="location" :locationProvince="locationProvince" :locationCity="locationCity"
                       :locationDistrict="locationDistrict"></PhotoList>
        </el-main>
    </el-container>
</template>

<script>
    import SearchButton from "./MainHeader/SearchButton";
    import MoreOption from "./MainHeader/MoreOption";
    import PhotoList from "./PhotoList";

    export default {
        name: "Location",
        components: {PhotoList, SearchButton, MoreOption},
        data() {
            return {
                locationProvince: decodeURIComponent(this.$route.params.province),  //省
                locationCity: decodeURIComponent(this.$route.params.city),  //市
                locationDistrict: decodeURIComponent(this.$route.params.district),  //县
            }
        },
    }
</script>

<style scoped>
    .location-title {
        float: left;
        width: calc(100% - 40px);
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
    }
    @media only screen and (max-width: 767px) {
        .location-title {
            width: calc(100% - 50px);
        }
    }
</style>