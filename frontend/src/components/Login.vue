<template>
    <div style="display: flex; align-items: center; height: 100%;">
        <el-form ref="loginForm" :model="form" :rules="rules" label-width="80px" style="width: 460px; margin: 0 auto;">
            <el-form-item label="用户名" prop="userid">
                <el-input v-model="form.userid" name="userid" placeholder="请输入用户名"
                          prefix-icon="el-icon-user" :clearable="true" :autofocus="true"
                          @keypress.enter.native="nextInput($event)"></el-input>
            </el-form-item>
            <el-form-item label="密码" prop="password">
                <el-input type="password" ref="password" v-model="form.password" name="password" placeholder="请输入密码"
                          prefix-icon="el-icon-lock" :clearable="true" :show-password="true"
                          @keypress.enter.native="login"></el-input>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" @click="login">登录</el-button>
                <el-button @click="resetForm">重置</el-button>
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
                    userid: '',  //用户名
                    password: '',  //登录密码
                },
                rules: {
                    userid: [
                        {required: true, message: '请输入用户名', trigger: 'blur'}
                    ],
                    password: [
                        {required: true, message: '请输入登录密码', trigger: 'blur'}
                    ],
                }
            }
        },
        computed: {
            api_url() {
                return this.$store.state.api_url  //从全局状态管理器中获取数据
            },
        },
        methods: {
            login() {
                //验证登录
                this.$refs['loginForm'].validate((valid) => {
                        if (!valid)  //首先做表单前台检验
                            return false
                        this.$axios({
                            method: 'post',
                            url: this.api_url + '/api/login',
                            data: this.form
                        }).then(response => {
                            const res = response.data
                            localStorage.userid = res.userid  //存储token
                            localStorage.token = res.token
                            this.$router.push('/photos')
                        })
                    }
                )
            },
            resetForm() {
                //重置表单
                this.$refs['loginForm'].resetFields()
            },
            nextInput(event) {
                //密码框获得焦点
                if (event) {
                    event.target.blur()
                    this.$refs.password.focus()
                }
            },
        }
    }
</script>

<style scoped>

</style>