<template>
    <div>
        <el-popover placement="bottom-end" width="350">
            <div style="text-align: center">
                <el-row style="text-align: center;">
                    <el-avatar
                            :class="{
                                    'user-avatar-large-one': userInfo.last_name.length === 1,
                                    'user-avatar-large-two': userInfo.last_name.length > 1
                            }"
                            :src="userInfo.avatar"
                            :key="userInfo.avatar"
                            :size="80">
                        {{userInfo.last_name}}
                    </el-avatar>
                    <el-upload class="upload-avatar"
                               :action="api_url + '/api/upload_avatar'"
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
                </el-row>
                <el-row>
                    <span class="user-name">{{userInfo.first_name + userInfo.last_name}}</span>
                </el-row>
                <el-row>
                    <span class="user-email">{{userInfo.email}}</span>
                </el-row>
                <el-row style="margin: 20px 0;">
                    <el-button round>修改您的登录密码</el-button>
                </el-row>
                <el-divider></el-divider>
                <el-row>
                    <el-button @click="logout">退 出</el-button>
                </el-row>
            </div>
            <div slot="reference">
                <el-avatar slot="reference" :class="{
                                   'user-avatar-small-one': userInfo.last_name.length === 1,
                                   'user-avatar-small-two': userInfo.last_name.length > 1
                           }"
                           :src="userInfo.avatar"
                           :key="userInfo.avatar">{{userInfo.last_name}}
                </el-avatar>
            </div>
        </el-popover>
    </div>
</template>

<script>
    export default {
        name: "UserCard",
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
            api_url() {
                return this.$store.state.api_url  //从全局状态管理器中获取数据
            },
        },
        mounted() {
            this.getUser()
        },
        methods: {
            getUser() {
                //获取当前用户信息
                this.$axios({
                    method: 'get',
                    url: this.api_url + '/api/get_user',
                    params: {
                        userid: localStorage.getItem('userid')
                    }
                }).then(response => {
                    this.userInfo = response.data
                    this.userInfo.avatar = this.api_url + '/' + this.userInfo.avatar
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
                    this.$notify({
                        type: 'error',
                        title: '提示',
                        message: msg,
                        position: 'top-right'
                    })
                    let newDate = new Date()
                    this.$store.commit('showLog', {type: 'error', msg: msg, time: newDate.toLocaleTimeString()})
                    return false
                }
                //检查文件大小
                const isOverSize = file.size / 1024 / 1024 < 1
                if (!isOverSize) {
                    let msg = '不支持超过1MB的文件'
                    this.$notify({
                        type: 'error',
                        title: '提示',
                        message: msg,
                        position: 'top-right'
                    })
                    let newDate = new Date()
                    this.$store.commit('showLog', {type: 'error', msg: msg, time: newDate.toLocaleTimeString()})
                    return false
                }
            },
            handleSuccess(response) {
                //文件上传成功时
                this.userInfo.avatar = this.api_url + '/' + response.path
                let msg = '用户头像修改成功'
                let newDate = new Date()
                this.$store.commit('showLog', {type: 'success', msg: msg, time: newDate.toLocaleTimeString()})
            },
            handleError(err) {
                //头像文件上传失败时
                const result =  JSON.parse(err.message)  //关键点，得用JSON.parse来解析err里面的内容
                this.$notify({
                    type: 'error',
                    title: '提示',
                    message: result.msg,
                    position: 'top-right'
                })
                let newDate = new Date()
                let msg = '用户头像上传失败: ' + result.msg
                this.$store.commit('showLog', {type: 'error', msg: msg, time: newDate.toLocaleTimeString()})
            },
            logout() {
                //退出登录
                if (localStorage.getItem('userid')) {
                    localStorage.removeItem('userid')  //清除本地token
                    localStorage.removeItem('token')
                }
                this.$router.push('/login')  //路由跳转到登录页面
            }
        }
    }
</script>

<style scoped>
    .user-avatar-small-one, .user-avatar-small-two, .user-avatar-large-one, .user-avatar-large-two { /*用户头像*/
        background-color: #33691E;
    }

    .user-avatar-small-one, .user-avatar-small-two {
        cursor: pointer;
    }

    .user-avatar-small-one {
        font-size:20px;
    }

    .user-avatar-small-two {
        font-size: 14px;
    }

    .user-avatar-large-one {
        font-size: 42px;
    }

    .user-avatar-large-two {
        font-size: 30px;
    }

    .user-name { /*用户名*/
        display: block;
        margin: 10px 0;
        font-size: 20px;
        font-weight: 600;
    }

    .user-email {  /*email*/
        font-size: 14px;
        color: #5f6368;
    }

    .upload-avatar {  /*上传用户头像组件*/
        position: absolute;
        bottom: 0;
        left: 175px;
    }

    .btn-avatar {  /*上传用户头像按钮*/
        font-size: 18px;
    }
</style>