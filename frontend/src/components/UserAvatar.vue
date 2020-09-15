<template>
    <div style="width:80px; position: relative">
        <el-avatar
                :class="{'user-avatar-large-one': userInfo.last_name.length === 1,
                         'user-avatar-large-two': userInfo.last_name.length > 1}"
                :src="userInfo.avatar"
                :key="userInfo.avatar"
                :size="80">
            {{userInfo.last_name}}
        </el-avatar>
        <el-upload class="upload-avatar"
                   :action="apiUrl + '/api/user_upload_avatar'"
                   accept="image/*"
                   :show-file-list="false"
                   :headers="headers"
                   :data="upload_data"
                   :before-upload="beforeUpload"
                   :on-success="handleSuccess"
                   :on-error="handleError">
            <el-button class="btn-avatar" icon="el-icon-camera-solid" circle size="mini"
                       title="修改用户头像"></el-button>
        </el-upload>
    </div>
</template>

<script>
    export default {
        name: "UserAvatar",
        data() {
            return {
                headers: {userid: localStorage.getItem('userid'), token: localStorage.getItem('token')},
                upload_data: {
                    userid: localStorage.getItem('userid'),  //当前用户id
                },
                userInfo: {  //用户信息
                    first_name: '',
                    last_name: '',
                    email: '',
                    avatar: '',
                },
                avatar: '',
            }
        },
        computed: {
            //重要：vuex中定义的数据一定要在这里绑定，放在data()里视图不会更新
            apiUrl() {
                return this.$store.state.apiUrl  //后台api调用地址
            },
            refreshUserInfo() {
                return this.$store.state.refreshUserInfo  //是否刷新照片列表
            },
        },
        watch: {
            refreshUserInfo() {
                //有其它组件发出刷新用户基本信息的指令
                if (this.refreshUserInfo) {
                    this.getUser()
                }
            }
        },
        mounted() {
            this.getUser()
        },
        methods: {
            getUser() {
                //获取当前用户信息
                this.$axios({
                    method: 'get',
                    url: this.apiUrl + '/api/user_get_info',
                    params: {
                        userid: localStorage.getItem('userid')
                    }
                }).then(response => {
                    this.userInfo = response.data
                    if (this.userInfo.avatar) {
                        this.userInfo.avatar = this.apiUrl + '/' + this.userInfo.avatar
                    }
                    this.$store.commit('refreshUserInfo', {show: false})
                })
            },
            beforeUpload(file) {
                //文件上传之前进行文件类型和大小检查
                //上传文件的扩展名
                const extension_name = file.name.substring(file.name.lastIndexOf('.') + 1).toLowerCase()
                const accept_list = ['jpg', 'jpeg', 'png', 'bmp']  //允许上传的文件类型列表
                const isImage = accept_list.indexOf(extension_name) !== -1
                if (!isImage) {
                    let msg = '不支持 ' + extension_name + ' 的文件格式'
                    this.$message({
                        message: msg,
                        type: 'success',
                    })
                    return false
                }
                //检查文件大小
                const isOverSize = file.size / 1024 / 1024 < 10
                if (!isOverSize) {
                    let msg = '不支持超过10MB的文件'
                    this.$message({
                        message: msg,
                        type: 'success',
                    })
                    return false
                }
            },
            handleSuccess() {
                //文件上传成功时
                this.$message({
                    message: '用户头像修改成功',
                    type: 'success',
                })
                this.$store.commit('refreshUserInfo', {show: true})
            },
            handleError(err) {
                //头像文件上传失败时
                const result = JSON.parse(err.message)  //关键点，得用JSON.parse来解析err里面的内容
                this.$message({
                    message: result.msg,
                    type: 'error',
                })
            },
        }
    }
</script>

<style scoped>
    .user-avatar-large-one, .user-avatar-large-two { /*用户头像*/
        background-color: #33691E;
    }

    .user-avatar-large-one {
        font-size: 42px;
    }

    .user-avatar-large-two {
        font-size: 30px;
    }

    .upload-avatar { /*上传用户头像组件*/
        position: absolute;
        bottom: 0;
        right: 0;
    }

    .btn-avatar { /*上传用户头像按钮*/
        font-size: 18px;
    }
</style>