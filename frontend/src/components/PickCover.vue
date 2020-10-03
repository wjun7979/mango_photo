<template>
    <el-container>
        <el-header class="mp-page-header" height="56px" style="padding: 4px 0 0 0">
            <el-col class="mp-page-header-title" :span="8">
                <i class="el-icon-close pick-close" @click="$router.back()"></i>
                <span>选择影集封面：{{albumName}}</span>
            </el-col>
            <el-col :span="16" style="text-align: right">
                <el-form :inline="true" style="margin-top: 2px;">
                    <el-form-item style="padding-right: 10px">
                        <el-button type="primary" size="small" @click="_setCover">完成</el-button>
                    </el-form-item>
                </el-form>
            </el-col>
        </el-header>
        <el-main style="padding-top: 56px">
            <PhotoList callMode="cover" :albumUUID="albumUUID" :on-pick="onPick"></PhotoList>
        </el-main>
    </el-container>
</template>

<script>
    import PhotoList from "./PhotoList";

    export default {
        name: "PickCover",
        data() {
            return {
                albumUUID: this.$route.params.albumUUID,
                albumName: '',
                photo_uuid: ''  //选中的封面照片
            }
        },
        components: {PhotoList},
        computed: {
            apiUrl() {
                return this.$store.state.apiUrl  //后台api调用地址
            },
        },
        mounted() {
            this.getAlbum()
        },
        created() {
            //防抖
            this._setCover = this.$lodash.debounce(this.setCover, this.$common.DEBOUNCE_TIMEOUT, {
                leading: true,
                trailing: false
            })
        },
        methods: {
            onClose() {
                this.$router.back()
            },
            getAlbum() {
                //获取指定的影集信息
                this.$axios({
                    method: 'get',
                    url: this.apiUrl + '/api/album_get',
                    params: {
                        uuid: this.albumUUID
                    }
                }).then(response => {
                    const result = response.data
                    this.albumName = result.name
                })
            },
            onPick(checkList) {
                //当选中列表值改变时的回调
                this.photo_uuid = checkList[0]
            },
            setCover() {
                //设置影集封面
                if (!this.photo_uuid) {
                    this.$message({
                        message: '请选择要作为影集封面的照片',
                        type: 'error',
                    })
                    return false
                }
                this.$axios({
                    method: 'post',
                    url: this.apiUrl + '/api/album_set_cover',
                    data: {
                        album_uuid: this.albumUUID,
                        photo_uuid: this.photo_uuid
                    }
                }).then(() => {
                    let msg = '成功为影集 [' + this.albumName + '] 设置了封面'
                    this.$message({
                        message: msg,
                        type: 'success',
                    })
                    this.onClose()
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