<template>
    <el-container>
        <el-header class="mp-page-header" height="56px" style="padding: 4px 0 0 0">
            <el-col class="mp-page-header-title" :span="8">
                <i class="el-icon-close pick-close" @click="$router.back()"></i>
                <span v-if="addList.length===0">添加到人物：{{peopleName}}</span>
                <span v-if="addList.length>0" style="padding-left: 7px;">添加了 {{addList.length}} 张照片</span>
            </el-col>
            <el-col :span="16" style="text-align: right">
                <el-form :inline="true" style="margin-top: 2px;">
                    <el-form-item v-show="addList.length>0" style="padding-right: 10px">
                        <el-button size="small" @click="cancelPick">取消选择</el-button>
                        <el-button type="primary" size="small" @click="_finishPick">完成</el-button>
                    </el-form-item>
                </el-form>
            </el-col>
        </el-header>
        <el-main style="padding-top: 56px">
            <FaceList callMode="pick" :peopleUUID="peopleUUID" :on-pick="onPick"></FaceList>
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
            cancelPick() {
                this.addList = []
                this.$store.commit('cancelSelectFace', {action: true})
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
            }
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