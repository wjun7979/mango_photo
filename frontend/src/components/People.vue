<template>
    <el-container>
        <el-header class="mp-page-header" height="56px">
            <el-col class="mp-page-header-title" :span="12">
                <div style="float: left;width: 40px"><i class="el-icon-back people-back" @click="$router.back()"></i></div>
                <div class="people-cover" :style="{'background-image':'url('+apiUrl+'/'+people.cover_path+'/'+people.cover_name+')'}"></div>
                <div style="float: left">{{people.name}}
                    <span v-if="showType==='photo'">({{people.photos}}张照片)</span>
                    <span v-if="showType==='face'">({{people.faces}}个面孔)</span>
                </div>
            </el-col>
            <el-col :span="12" style="text-align: right; padding: 7px 20px 0 0">
                <el-button v-if="showType==='face'" icon="el-icon-user-solid" size="small" type="success"
                           @click="openPick" style="margin-right: 20px">确认其他面孔
                </el-button>
                <el-radio-group v-model="showType" size="small" @change="changeShowType">
                    <el-radio-button label="photo">显示照片</el-radio-button>
                    <el-radio-button label="face">显示面孔</el-radio-button>
                </el-radio-group>
            </el-col>
        </el-header>
        <el-main class="mp-page-main">
            <div v-if="people.features===0" class="no-feature">
                <i class="el-icon-info"></i>
                <span style="margin-left: 10px">注意：该人物没有特征照片，将无法进行智能匹配！请
                    <el-button type="text" style="font-size: 16px" @click="openPickFeature">点击这里</el-button> 选取清晰的正面照作为Ta的特征。</span>
            </div>
            <PhotoList v-if="showType==='photo'" callMode="people" :peopleUUID="peopleUUID"></PhotoList>
            <FaceList v-if="showType==='face'" callMode="people" :peopleUUID="peopleUUID"></FaceList>
        </el-main>
    </el-container>
</template>

<script>
    import PhotoList from "./PhotoList";
    import FaceList from "./FaceList";

    export default {
        name: "People",
        components: {PhotoList, FaceList},
        data() {
            return {
                peopleUUID: this.$route.params.uuid,  //人物uuid
                showType: this.$route.params.type,  //显示类型：photo:照片; face:面孔
                people: {  //人物信息
                    name: '',
                    cover_path: '',
                    cover_name: '',
                },
            }
        },
        computed: {
            apiUrl() {
                return this.$store.state.apiUrl  //后台api调用地址
            },
            refreshPhoto() {
                return this.$store.state.refreshPhoto  //是否刷新照片列表
            },
        },
        watch: {
            refreshPhoto() {
                //有其它组件发出刷新照片的指令
                if (this.refreshPhoto) {
                    this.getPeople()
                }
            },
        },
        mounted() {
            this.getPeople()
        },
        methods: {
            getPeople() {
                //获取指定的人物信息
                this.$axios({
                    method: 'get',
                    url: this.apiUrl + '/api/people_get',
                    params: {
                        uuid: this.peopleUUID
                    }
                }).then(response => {
                    const result = response.data
                    this.people = result
                })
            },
            changeShowType() {
                //改变显示类别，照片或面孔
                this.$router.replace({
                    name: 'people',
                    params: {uuid: this.peopleUUID, type: this.showType}
                })
            },
            openPick() {
                //添加面孔
                this.$router.push({
                    name: 'pick_face',
                    params: {peopleUUID: this.peopleUUID}
                })
            },
            openPickFeature() {
                //选择人物特征照片
                this.$router.push({
                    name: 'pick_feature',
                    params: {peopleUUID: this.peopleUUID}
                })
            },
        }
    }
</script>

<style scoped>
    .people-back { /*人物页头的返回按钮*/
        padding: 8px;
        margin-right: 10px;
        color: #5f6368;
        font-weight: bold;
        cursor: pointer;
    }

    .people-back:hover {
        background-color: #e5e5e5;
        border-radius: 50%;
    }

    .people-cover {  /*人物封面*/
        float: left;
        margin-top: 9px;
        margin-right: 10px;
        width: 30px;
        height: 30px;
        background-color: #80868b;
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        border-radius: 5px;
    }

    .no-feature {  /*人物没有特征时的警告信息*/
        padding: 10px;
        margin: 10px 20px;
        color: #F56C6C;
        background-color: #fde2e2;
        border-radius: 8px;
    }
</style>