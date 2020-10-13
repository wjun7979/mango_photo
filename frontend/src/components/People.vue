<template>
    <el-container>
        <el-header class="mp-page-header" height="64px">
            <el-col class="mp-page-header-title" :span="14">
                <div style="float: left;width: 40px"><i class="el-icon-back mp-page-header-back" @click="$router.back()"></i></div>
                <div class="people-cover hidden-xs-only" :style="{'background-image':'url('+apiUrl+'/'+people.cover_path+'/'+people.cover_name+')'}"></div>
                <div class="people-title">{{people.name}}
                    <span v-if="showType==='photo'">({{people.photos}})</span>
                    <span v-if="showType==='face'">({{people.faces}})</span>
                </div>
            </el-col>
            <el-col :span="10" style="text-align: right; padding-right: 20px">
                <el-button v-if="showType==='face'" icon="el-icon-user-solid" size="small" type="success"
                           @click="openPick" style="margin: 15px 20px 0 0" class="hidden-mobile-only">确认其他面孔
                </el-button>
                <i v-if="showType==='face'" class="iconfont iconzengjiarenwu icon-button hidden-pc-only"
                   @click="openPick" style="font-size: 32px; margin-top: 15px;"></i>
                <el-radio-group v-model="showType" size="small" @change="changeShowType" class="hidden-mobile-only"
                                style="float:right; margin-top: 15px">
                    <el-radio-button label="photo">显示照片</el-radio-button>
                    <el-radio-button label="face">显示面孔</el-radio-button>
                </el-radio-group>
                <el-dropdown trigger="click" @command="handCommand" placement="bottom-end"
                             class="btn-pick hidden-pc-only">
                    <i class="el-icon-more" title="更多选项" style="transform: rotate(90deg);"></i>
                    <el-dropdown-menu slot="dropdown">
                        <el-dropdown-item v-show="showType==='face'" icon="el-icon-picture" command="show-photo">显示照片</el-dropdown-item>
                        <el-dropdown-item v-show="showType==='photo'" icon="el-icon-user-solid" command="show-face">显示面孔</el-dropdown-item>
                        <el-dropdown-item v-show="showType==='photo'" icon="el-icon-circle-check" command="pick-photo">选择照片</el-dropdown-item>
                        <el-dropdown-item v-show="showType==='face'" icon="el-icon-circle-check" command="pick-face">选择面孔</el-dropdown-item>
                    </el-dropdown-menu>
                </el-dropdown>
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
            handCommand(command) {
                //更多选项
                switch (command) {
                    case 'pick-photo':  // 选择照片
                        this.$store.commit('pickPhotoMode', {show: true})
                        break
                    case 'pick-face':  // 选择面孔
                        this.$store.commit('pickFaceMode', {show: true})
                        break
                    case 'show-photo':  //显示照片
                        this.$router.replace({
                            name: 'people',
                            params: {uuid: this.peopleUUID, type: 'photo'}
                        })
                        break
                    case 'show-face':  //显示面孔
                        this.$router.replace({
                            name: 'people',
                            params: {uuid: this.peopleUUID, type: 'face'}
                        })
                        break
                }
            },
        }
    }
</script>

<style scoped>
    .people-cover {  /*人物封面*/
        float: left;
        margin-top: 17px;
        margin-right: 10px;
        width: 30px;
        height: 30px;
        background-color: #80868b;
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        border-radius: 5px;
    }

    .people-title {
        float: left;
        width: calc(100% - 80px);
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
    }
    @media only screen and (max-width: 767px) {
        .people-title {
            width: calc(100% - 50px);
        }
    }

    .no-feature {  /*人物没有特征时的警告信息*/
        padding: 10px;
        margin: 10px 10px;
        color: #F56C6C;
        background-color: #fde2e2;
        border-radius: 8px;
    }

    .btn-pick {
        display: inline-block;
        float: right;
        margin-top: 20px;
        margin-left: 20px;
    }
    .btn-pick i {
        font-size: 24px;
    }
</style>