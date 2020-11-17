<template>
    <el-container>
        <el-header class="mp-page-header" height="56px">
            <el-col class="mp-page-header-title" :span="12">
                <div style="float: left;width: 40px"><i class="el-icon-back mp-page-header-back" @click="$router.back()"></i></div>
                <span>地点</span>
            </el-col>
            <el-col :span="12" style="text-align: right">
                <SearchButton style="margin-right: 20px"></SearchButton>
            </el-col>
        </el-header>
        <el-main class="mp-page-main">
            <!--当地点列表为空时显示一些提示信息-->
            <div v-if="isShowEmptyTips" style="text-align: center; padding-top: 80px">
                <div style="font-size: 18px; font-weight: 400; color: #202124; margin-bottom: 20px">空空如也，没有任何内容。</div>
                <img src="../assets/images/empty.png" alt=""/>
            </div>
            <el-row :gutter="10" style="margin: 0">
                <el-col :xs="{span:8}" :sm="{span:6}" :lg="{span:4}" :xl="{span:3}" v-for="place of placeList"
                        :key="place.name" style="position: relative">
                    <div class="place-wrap" @click="showPlace(place.province, place.name)">
                        <div class="place-cover" :style="{'background-image':'url('+apiUrl+'/'+place.cover+')'}"></div>
                        <p class="place-name">{{place.name}}</p>
                        <p class="place-photos">{{place.photos}}项</p>
                    </div>
                </el-col>
            </el-row>
        </el-main>
    </el-container>
</template>

<script>
    import SearchButton from "./MainHeader/SearchButton";

    export default {
        name: "Places",
        components: {SearchButton},
        data() {
            return {
                placeList: [],  //地点列表
                isShowEmptyTips: false,  //是否显示空列表提示
            }
        },
        computed: {
            apiUrl() {
                return this.$store.state.apiUrl  //后台api调用地址
            },
        },
        mounted() {
            this.showPlaces()
        },
        methods: {
            showPlaces() {
                //获取地点列表
                this.$axios({
                    method: 'get',
                    url: this.apiUrl + '/api/place_list',
                    params: {
                        userid: localStorage.getItem('userid'),
                    }
                }).then(response => {
                    this.placeList = response.data
                    if (this.placeList.length === 0) {  //显示空列表提示
                        this.isShowEmptyTips = true
                    }
                })
            },
            showPlace(province, name) {
                //跳转到指定的地点
                this.$axios({
                    method: 'get',
                    url: this.apiUrl + '/api/place_show',
                    params: {
                        userid: localStorage.getItem('userid'),
                        province: province,
                        name: name
                    }
                }).then(response => {
                    let res = response.data
                    this.$router.push({
                        name: 'place',
                        params: {
                            province: encodeURIComponent(res.province),
                            city: encodeURIComponent(res.city),
                            district: encodeURIComponent(res.district)
                        }
                    })
                })
            },
        }
    }
</script>

<style scoped>
    .place-wrap { /*地点容器*/
        cursor: pointer;
        margin-bottom: 15px;
    }

    .place-cover { /*地点封面*/
        position: relative;
        padding-top: 100%;
        background-color: #80868b;
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        border-radius: 8px;
    }

    .place-name { /*地点名称*/
        width: 100%;
        padding-top: 8px;
        font-size: 14px;
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
    }

    .place-photos { /*地点中照片的数量*/
        font-size: 12px;
        color: #5f6368;
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
    }
</style>