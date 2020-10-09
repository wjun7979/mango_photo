<template>
    <el-row class="div-login">
        <el-carousel ref="carousel" class="bg-carousel" height="100%" indicator-position="none" :autoplay="false"
                     arrow="never">
            <el-carousel-item class="bg-item" v-for="(img, index) of bgList" :key="index"
                              :style="{'background-image': 'url(https://www.bing.com'+img.url+')'}">
            </el-carousel-item>
        </el-carousel>

        <el-col class="div-form"
                :xs="{span: 20, offset: 2}"
                :sm="{span: 12, offset: 6}"
                :lg="{span: 6, offset: 9}">
            <el-form class="login-form" ref="loginForm" :model="form" :rules="rules">
                <p class="login-title">芒果相册</p>
                <div class="div-input">
                    <el-form-item prop="userid">
                        <el-input v-model="form.userid" name="userid" placeholder="请输入用户名"
                                  prefix-icon="el-icon-user" :clearable="true" :autofocus="true"
                                  @keypress.enter.native="nextInput($event)"></el-input>
                    </el-form-item>
                    <el-form-item prop="password" style="margin-bottom: 0">
                        <el-input type="password" ref="password" v-model="form.password" name="password" placeholder="请输入密码"
                                  prefix-icon="el-icon-lock" :clearable="true" :show-password="true"
                                  @keypress.enter.native="_login"></el-input>
                    </el-form-item>
                </div>
                <div class="div-btn">
                    <el-button @click="resetForm">重置</el-button>
                    <el-button type="primary" @click="_login">登录</el-button>
                </div>
            </el-form>
        </el-col>
        <div class="bgimg-tools">
            <el-button class="btn-prev" icon="el-icon-arrow-left" title="上一张" circle @click="prevBackImg"></el-button>
            <el-button class="btn-next" icon="el-icon-arrow-right" title="下一张" circle @click="nextBackImg"></el-button>
        </div>
    </el-row>
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
                },
                bgList: [],  //背景图片列表
            }
        },
        computed: {
            apiUrl() {
                return this.$store.state.apiUrl  //从全局状态管理器中获取数据
            },
        },
        mounted() {
            this.getBackImg()
        },
        created() {
            //防抖
            this._login = this.$lodash.debounce(this.login, this.$common.DEBOUNCE_TIMEOUT, {
                leading: true,
                trailing: false
            })
        },
        methods: {
            login() {
                //验证登录
                this.$refs['loginForm'].validate((valid) => {
                    if (!valid)  //首先做表单前台检验
                        return false
                    this.$axios({
                        method: 'post',
                        url: this.apiUrl + '/api/login',
                        data: this.form
                    }).then(response => {
                        const res = response.data
                        localStorage.userid = res.userid  //存储token
                        localStorage.token = res.token
                        this.$router.push('/photos')
                    })
                })
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
            getBackImg() {
                //获取背景图片
                this.$axios({
                    method: 'get',
                    url: this.apiUrl + '/api/login_get_bgimg',
                }).then(response => {
                    const res = response.data.images
                    this.bgList = res
                })
            },
            prevBackImg() {
                //选择上一张背景图片
                this.$refs.carousel.next()
            },
            nextBackImg() {
                //选择下一张背景图片
                this.$refs.carousel.prev()
            },
        }
    }
</script>

<style scoped>
    .div-login { /*最外层容器*/
        position: fixed;
        top: 0;
        right: 0;
        bottom: 0;
        left: 0;
    }

    .div-form {
        height: 100%;
        display: flex;
        align-items: center;
    }

    .login-form { /*登录表单*/
        width: 100%;
        background-color: rgba(255, 255, 255, 0.9);
        border: 1px solid #e4e4e4;
        border-radius: 20px;
        box-shadow: 0 1px 2px 0 rgba(60, 64, 67, .30), 0 2px 6px 2px rgba(60, 64, 67, .15);
    }

    .login-title { /*网站标题*/
        padding-left: 45px;
        margin: 20px 0 0 30px;
        background-image: url("../assets/images/mango.png");
        background-repeat: no-repeat;
        background-position-y: 2px;
        background-size: 36px;
        line-height: 40px;
        color: #3a8ee6;
        font-size: 22px;
        font-weight: 500;
    }

    .div-input { /*文本框区域*/
        padding: 30px;
    }

    .div-btn { /*按钮区域*/
        padding: 20px 30px;
        text-align: right;
        border-top: 1px solid #e4e4e4;
        background-color: rgba(200, 200, 200, 0.6);
        border-bottom-left-radius: 20px;
        border-bottom-right-radius: 20px;
    }

    .bg-carousel { /*走马灯*/
        position: fixed;
        z-index: -1;
        width: 100%;
        height: 100%;
    }

    .bg-item { /*走马灯成员*/
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }

    .bgimg-tools >>> .el-button {
        position: absolute;
        bottom: 20px;
        padding: 8px;
        background: transparent;
        color: #fff;
        font-size: 20px;
    }

    .btn-prev {
        right: 100px;
    }

    .btn-next {
        right: 40px;
    }
</style>