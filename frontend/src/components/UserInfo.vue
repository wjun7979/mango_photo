<template>
    <div>
        <el-container>
            <el-header class="mp-page-header" height="56px">
                <el-col class="mp-page-header-title" :span="8">管理用户账号</el-col>
                <el-col :span="16" style="text-align: right; padding: 8px 20px 0 0">
                    <el-button icon="el-icon-lock" size="small" @click="showModifyPwdDialog">修改登录密码</el-button>
                </el-col>
            </el-header>
            <el-main class="mp-page-main">
                <el-form ref="form-userinfo" class="form-userinfo" :model="userInfo" :rules="rules" label-width="100px">
                    <el-form-item label="用户ID:">
                        {{userInfo.userid}}
                    </el-form-item>
                    <el-form-item>
                        <UserAvatar></UserAvatar>
                        <el-button v-if="userInfo.avatar" type="text" @click="_removeAvatar">不使用头像</el-button>
                    </el-form-item>
                    <el-form-item label="姓:">
                        <el-col :span="8">
                            <el-form-item prop="first_name">
                                <el-input v-model="userInfo.first_name" :clearable="true" maxlength="10"></el-input>
                            </el-form-item>
                        </el-col>
                        <el-col :span="4" style="text-align: right; padding-right: 12px">名:</el-col>
                        <el-col :span="12">
                            <el-form-item prop="last_name">
                                <el-input v-model="userInfo.last_name" :clearable="true" maxlength="30"></el-input>
                            </el-form-item>
                        </el-col>
                    </el-form-item>
                    <el-form-item label="手机:" prop="mobile_number">
                        <el-input v-model="userInfo.mobile_number" placeholder="请输入手机号码" :clearable="true"
                                  maxlength="20"></el-input>
                    </el-form-item>
                    <el-form-item label="邮箱:" prop="email">
                        <el-input v-model="userInfo.email" placeholder="请输入邮箱地址" :clearable="true"
                                  maxlength="50"></el-input>
                    </el-form-item>
                    <el-form-item>
                        <el-button type="primary" @click="_saveInfo">提 交</el-button>
                        <el-button @click="resetForm">重 置</el-button>
                    </el-form-item>
                </el-form>
            </el-main>
        </el-container>
        <!--修改登录密码对话框-->
        <el-dialog title="修改登录密码" :visible.sync="isShowModifyPwdDialog" width="400px"
                   :close-on-click-modal="false" @closed="$refs['form-userpwd'].resetFields()">
            <el-form ref="form-userpwd" :model="userPwd" :rules="rules" label-width="80px">
                <el-form-item prop="old_pwd" label="原密码">
                    <el-input type="password" v-model="userPwd.old_pwd" placeholder="请输入原密码"
                              :clearable="true" :show-password="true" maxlength="50"></el-input>
                </el-form-item>
                <el-form-item prop="new_pwd" label="新密码">
                    <el-input type="password" v-model="userPwd.new_pwd" placeholder="请输入新密码"
                              :clearable="true" :show-password="true" maxlength="50"></el-input>
                </el-form-item>
                <el-form-item prop="confirm_pwd" label="确认密码" style="margin-bottom: 0">
                    <el-input type="password" v-model="userPwd.confirm_pwd" placeholder="请再次输入新密码"
                              :clearable="true" :show-password="true" maxlength="50"></el-input>
                </el-form-item>
            </el-form>
            <span slot="footer">
                <el-button @click="isShowModifyPwdDialog=false">取消</el-button>
                <el-button type="primary" @click="savePwd">确定</el-button>
            </span>
        </el-dialog>
    </div>
</template>

<script>
    import UserAvatar from "./UserAvatar";

    export default {
        name: "UserInfo",
        components: {UserAvatar},
        data() {
            //手机号码检验规则
            let validatePhoto = (rule, value, callback) => {
                if (value === '') {
                    callback(new Error('请输入手机号码'));
                } else {
                    const reg = /^1[3|4|5|7|8][0-9]\d{8}$/
                    if (reg.test(value)) {
                        callback();
                    } else {
                        return callback(new Error('请输入正确的手机号'));
                    }
                }
            };
            //确认密码校验规则
            let validatePass = (rule, value, callback) => {
                if (value === '') {
                    callback(new Error('请再次输入新密码'));
                } else if (value !== this.userPwd.new_pwd) {
                    callback(new Error('两次输入的密码不一致'));
                } else {
                    callback();
                }
            };
            return {
                userInfo: {
                    userid: '',  //用户id
                    first_name: '',  //姓
                    last_name: '',  //名
                    mobile_number: '',  //移动电话
                    email: '',  //邮箱
                },
                userPwd: {
                    userid: localStorage.getItem('userid'),
                    old_pwd: '',  //原密码
                    new_pwd: '',  //新密码
                    confirm_pwd: '',  //确认密码
                },
                rules: {
                    first_name: [
                        {required: true, message: '请输入姓氏', trigger: 'blur'}
                    ],
                    last_name: [
                        {required: true, message: '请输入名字', trigger: 'blur'}
                    ],
                    mobile_number: [
                        {validator: validatePhoto, trigger: 'blur'}
                    ],
                    email: [
                        {required: true, message: '请输入邮箱地址', trigger: 'blur'},
                        {type: 'email', message: '请输入正确的邮箱地址', trigger: ['blur', 'change']}
                    ],
                    old_pwd: [
                        {required: true, message: '请输入原密码', trigger: 'blur'}
                    ],
                    new_pwd: [
                        {required: true, message: '请输入新密码', trigger: 'blur'},
                        {min: 6, message: '密码长度不得少于6个字符', trigger: 'blur' }
                    ],
                    confirm_pwd: [
                        {validator: validatePass, trigger: 'blur'}
                    ],
                },
                isShowModifyPwdDialog: false,  //是否显示修改登录密码对话框
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
        created() {
            //防抖
            this._saveInfo = this.$lodash.debounce(this.saveInfo, this.$common.DEBOUNCE_TIMEOUT, {
                leading: true,
                trailing: false
            })
            this._removeAvatar = this.$lodash.debounce(this.removeAvatar, this.$common.DEBOUNCE_TIMEOUT, {
                leading: true,
                trailing: false
            })
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
                    this.$store.commit('refreshUserInfo', {show: false})
                })
            },
            saveInfo() {
                //保存账号信息
                this.$refs['form-userinfo'].validate((valid) => {
                    if (!valid)  //首先做表单前台检验
                        return false
                    this.$axios({
                        method: 'post',
                        url: this.apiUrl + '/api/user_save_info',
                        data: this.userInfo
                    }).then(() => {
                        this.$message({
                            message: '用户账号信息保存成功',
                            type: 'success',
                        })
                        this.$store.commit('refreshUserInfo', {show: true})
                    })
                })
            },
            resetForm() {
                //重置用户基本信息表单
                this.$refs['form-userinfo'].resetFields()
                this.getUser()
            },
            showModifyPwdDialog() {
                //显示修改密码对话框
                this.isShowModifyPwdDialog = true
            },
            savePwd() {
                //保存登录密码
                this.$refs['form-userpwd'].validate((valid) => {
                    if (!valid)  //首先做表单前台检验
                        return false
                    this.$axios({
                        method: 'post',
                        url: this.apiUrl + '/api/user_save_pwd',
                        data: this.userPwd
                    }).then(() => {
                        this.$message({
                            message: '登录密码修改成功，下次登录请使用新密码',
                            type: 'success',
                        })
                        this.isShowModifyPwdDialog = false
                    })
                })
            },
            removeAvatar() {
                //清除用户头像
                this.$confirm('用户头像一旦清除将无法恢复', '要清除用户头像吗？', {
                    confirmButtonText: '清除',
                    cancelButtonText: '取消',
                    type: 'warning',
                    closeOnClickModal: false,
                }).then(() => {
                    this.$axios({
                        method: 'get',
                        url: this.apiUrl + '/api/user_remove_avatar',
                        params: {
                            userid: localStorage.getItem('userid')
                        }
                    }).then(() => {
                        this.$message({
                            message: '已删除用户头像',
                            type: 'success',
                        })
                        this.$store.commit('refreshUserInfo', {show: true})
                    })
                }).catch(() => {
                });
            },
        }
    }
</script>

<style scoped>
    .form-userinfo { /*修改密码表单*/
        margin: 20px 0 0 50px;
        width: 400px;
    }
</style>