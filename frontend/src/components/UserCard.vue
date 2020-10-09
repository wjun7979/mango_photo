<template>
    <div style="float:right; width: 50px;">
        <el-popover ref="popover" placement="bottom-end" width="350" :visible-arrow="true">
            <div style="text-align: center">
                <el-row style="padding-left: 122px">
                    <UserAvatar></UserAvatar>
                </el-row>
                <el-row>
                    <span class="user-name">{{userInfo.first_name + userInfo.last_name}}</span>
                </el-row>
                <el-row>
                    <span class="user-email">{{userInfo.email}}</span>
                </el-row>
                <el-row style="margin: 20px 0;">
                    <el-button round @click="showUserInfo">管理您的账号信息</el-button>
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
    import UserAvatar from "./UserAvatar";
    export default {
        name: "UserCard",
        components: {UserAvatar},
        data() {
            return {
                userInfo: {  //用户信息
                    first_name: '',
                    last_name: '',
                    email: '',
                    avatar: '',
                },
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
                    //用户基本信息读取完成后，将store.js中的refreshUserInfo值重置为false
                    this.$store.commit('refreshUserInfo', {show: false})
                })
            },
            logout() {
                //退出登录
                if (localStorage.getItem('userid')) {
                    localStorage.removeItem('userid')  //清除本地token
                    localStorage.removeItem('token')
                }
                this.$router.push('/login')  //路由跳转到登录页面
            },
            showUserInfo() {
                //跳转到修改用户账号组件
                this.$store.commit('showMenu', {show: false})  //隐藏菜单
                this.$refs['popover'].doClose()
                this.$router.push({
                    name: 'user_info'
                })
            },
        }
    }
</script>

<style scoped>
    .user-avatar-small-one, .user-avatar-small-two { /*用户头像*/
        background-color: #33691E;
    }

    .user-avatar-small-one, .user-avatar-small-two {
        cursor: pointer;
    }

    .user-avatar-small-one {
        font-size: 20px;
    }

    .user-avatar-small-two {
        font-size: 14px;
    }

    .user-name { /*用户名*/
        display: block;
        margin: 10px 0;
        font-size: 20px;
        font-weight: 600;
    }

    .user-email { /*email*/
        font-size: 14px;
        color: #5f6368;
    }
</style>