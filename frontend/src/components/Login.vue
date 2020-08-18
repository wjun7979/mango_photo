<template>
    <div style="display: flex; align-items: center; height: 100%;">
        <el-form :model="form" label-width="80px" style="width: 460px; margin: 0 auto;">
            <el-form-item label="用户名">
                <el-input v-model="form.username" placeholder="请输入用户名"
                          prefix-icon="el-icon-user"></el-input>
            </el-form-item>
            <el-form-item label="密码">
                <el-input type="password" v-model="form.password" placeholder="请输入密码"
                          prefix-icon="el-icon-lock"></el-input>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" @click="login">登录</el-button>
                <el-button>重置</el-button>
            </el-form-item>
        </el-form>
    </div>
</template>

<script>
    export default {
        name: "Login",
        data() {
            return {
                form: {
                    username: '',  //用户名
                    password: '',  //登录密码
                }
            }
        },
        methods: {
            login() {
                this.$router.push('/photo')
            }
        }
    }
</script>

<style scoped>

</style>