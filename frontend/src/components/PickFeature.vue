<template>
    <el-container>
        <el-header class="mp-page-header" height="64px" style="padding: 0">
            <el-col class="mp-page-header-title" :span="14">
                <i class="el-icon-close pick-close" @click="$router.back()"></i>
                <span>选择特征照片</span>
                <span class="hidden-xs-only">：{{peopleName}}</span>
            </el-col>
            <el-col :span="10" style="text-align: right">
                <el-button type="primary" @click="_setFeature" style="margin: 11px 10px 0 0">完成</el-button>
            </el-col>
        </el-header>
        <el-main class="mp-page-main">
            <PhotoList callMode="feature" :peopleUUID="peopleUUID" :on-pick="onPick"></PhotoList>
        </el-main>
    </el-container>
</template>

<script>
    import PhotoList from "./PhotoList";

    export default {
        name: "PickFeature",
        data() {
            return {
                peopleUUID: this.$route.params.peopleUUID,
                peopleName: '',
                photo_uuid: ''  //选中的人物特征照片
            }
        },
        components: {PhotoList},
        computed: {
            apiUrl() {
                return this.$store.state.apiUrl  //后台api调用地址
            },
        },
        mounted() {
            this.getPeople()
        },
        created() {
            //防抖
            this._setFeature = this.$lodash.debounce(this.setFeature, this.$common.DEBOUNCE_TIMEOUT, {
                leading: true,
                trailing: false
            })
        },
        methods: {
            onClose() {
                this.$router.back()
            },
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
                    this.peopleName = result.name
                })
            },
            onPick(checkList) {
                //当选中列表值改变时的回调
                this.photo_uuid = checkList[0]
            },
            setFeature() {
                //设置影集封面
                if (!this.photo_uuid) {
                    this.$message({
                        message: '请选择要作为人物特征的照片',
                        type: 'error',
                    })
                    return false
                }
                //获取指定照片中的人脸列表
                this.$axios({
                    method: 'get',
                    url: this.apiUrl + '/api/photo_get_faces',
                    params: {
                        photo_uuid: this.photo_uuid
                    }
                }).then(response => {
                    let faces = response.data
                    this.$axios({
                        method: 'post',
                        url: this.apiUrl + '/api/people_add_feature',
                        data: {
                            face_uuid: faces[0].uuid,
                        }
                    }).then(() => {
                        this.$message({
                            message: '成功为人物 [' + this.peopleName + '] 选择了特征照片',
                            type: 'success',
                        })
                        this.onClose()
                    })
                })

            }
        }
    }
</script>

<style scoped>
    .pick-close { /*影集页头的返回按钮*/
        padding: 8px;
        margin-right: 10px;
        color: #5f6368;
        font-weight: bold;
        cursor: pointer;
    }

    .pick-close:hover {
        background-color: #e5e5e5;
        border-radius: 50%;
    }
</style>