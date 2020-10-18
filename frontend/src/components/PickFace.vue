<template>
    <el-container>
        <el-header class="mp-page-header" height="64px" style="padding: 0">
            <el-col class="mp-page-header-title" :span="14">
                <i class="el-icon-close pick-close" @click="$router.back()"></i>
                <span v-if="addList.length===0">添加到：{{peopleName}}</span>
                <span v-if="addList.length>0" style="padding-left: 7px;">选择了 {{addList.length}} 张</span>
            </el-col>
            <el-col :span="10" style="text-align: right">
                <el-form :inline="true" style="margin-top: 12px;">
                    <el-form-item v-show="addList.length>0">
                        <el-button size="small" type="danger" @click="removeFace">删除</el-button>
                        <el-button type="primary" size="small" @click="_finishPick">添加</el-button>
                    </el-form-item>
                </el-form>
            </el-col>
        </el-header>
        <el-main class="mp-page-main">
            <FaceList callMode="pick_face" :on-pick="onPick"></FaceList>
        </el-main>
    </el-container>
</template>

<script>
    import FaceList from "./FaceList";
    export default {
        name: "PickFace",
        components: {FaceList},
        data() {
            return {
                peopleUUID: this.$route.params.peopleUUID,
                peopleName: '',  //人物姓名
                addList: [],  //添加的面孔列表
            }
        },
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
            this._finishPick = this.$lodash.debounce(this.finishPick, this.$common.DEBOUNCE_TIMEOUT, {
                leading: true,
                trailing: false
            })
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
                    this.peopleName = result.name
                })
            },
            onPick(addList) {
                //当选中列表值改变时的回调
                this.addList = addList
            },
            finishPick() {
                //完成选择
                this.$axios({
                    method: 'post',
                    url: this.apiUrl + '/api/people_add_faces',
                    data: {
                        people_uuid: this.peopleUUID,
                        face_list: this.addList,
                    }
                }).then(() => {
                    let msg = '成功将 ' + this.addList.length + ' 个面孔添加到人物 [' + this.peopleName + '] 中'
                    this.$message({
                        message: msg,
                        type: 'success',
                    })
                    this.$router.back()
                })
            },
            removeFace() {
                this.$confirm('面孔一旦删除将无法恢复', '要删除选中的面孔吗？', {
                    confirmButtonText: '删除',
                    cancelButtonText: '取消',
                    type: 'warning',
                    closeOnClickModal: false,
                }).then(() => {
                    this.$axios({
                        method: 'post',
                        url: this.apiUrl + '/api/people_remove_face',
                        data: {
                            face_list: this.addList,
                        }
                    }).then(() => {
                        let msg = this.addList.length + ' 张面孔成功删除'
                        this.$message({
                            message: msg,
                            type: 'success',
                        })
                        this.$store.commit('refreshFace', {action: 'delete', list: this.addList})
                        this.addList = []
                        this.$store.commit('cancelSelectFace', {action: true})  //取消已选中的面孔
                    })
                }).catch(() => {
                });
            },
        },
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