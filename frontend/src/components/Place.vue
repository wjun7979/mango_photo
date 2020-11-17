<template>
    <el-container>
        <el-header class="mp-page-header" height="64px">
            <el-col class="mp-page-header-title" :span="14">
                <div style="float: left;width: 40px"><i class="el-icon-back mp-page-header-back" @click="$router.back()"></i></div>
                <div class="place-title">
                    <span>{{placeProvince}}</span>
                    <span v-if="placeCity!=='none'">{{placeCity}}</span>
                    <span v-if="placeDistrict!=='none'">{{placeDistrict}}</span>
                </div>
            </el-col>
            <el-col :span="10" style="text-align: right">
                <SearchButton style="margin-right: 20px"></SearchButton>
                <MoreOption style="margin: 19px 20px 0 0"></MoreOption>
            </el-col>
        </el-header>
        <el-main class="mp-page-main">
            <PhotoList callMode="place" :placeProvince="placeProvince" :placeCity="placeCity"
                       :placeDistrict="placeDistrict"></PhotoList>
        </el-main>
    </el-container>
</template>

<script>
    import SearchButton from "./MainHeader/SearchButton";
    import MoreOption from "./MainHeader/MoreOption";
    import PhotoList from "./PhotoList";

    export default {
        name: "Place",
        components: {PhotoList, SearchButton, MoreOption},
        data() {
            return {
                placeProvince: decodeURIComponent(this.$route.params.province),  //省
                placeCity: decodeURIComponent(this.$route.params.city),  //市
                placeDistrict: decodeURIComponent(this.$route.params.district),  //县
            }
        },
    }
</script>

<style scoped>
    .place-title {
        float: left;
        width: calc(100% - 40px);
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
    }
    @media only screen and (max-width: 767px) {
        .place-title {
            width: calc(100% - 50px);
        }
    }
</style>