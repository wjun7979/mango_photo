<template>
    <el-container>
        <el-header class="mp-page-header" height="56px">
            <el-col class="mp-page-header-title" :span="12">
                <div style="float: left;width: 40px"><i class="el-icon-back mp-page-header-back" @click="$router.back()"></i></div>
                <span>人物</span>
            </el-col>
            <el-col :span="12" style="text-align: right">
                <SearchButton style="margin-right: 20px"></SearchButton>
            </el-col>
        </el-header>
        <el-main class="mp-page-main">
            <!--当人物列表为空时显示一些提示信息-->
            <div v-if="isShowEmptyTips" style="text-align: center; padding-top: 80px">
                <div style="font-size: 18px; font-weight: 400; color: #202124; margin-bottom: 20px">空空如也，没有任何内容。</div>
                <img src="../assets/images/empty.png" alt=""/>
            </div>
            <el-row :gutter="10" style="margin: 0">
                <el-col :xs="{span:8}" :sm="{span:6}" :lg="{span:4}" :xl="{span:3}" v-for="people of peopleList"
                        :key="people.uuid" style="position: relative">
                    <div class="people-wrap" @click="showPeople(people.uuid)">
                        <div class="people-cover"
                             :style="{'background-image':'url('+apiUrl+'/'+people.cover_path+'/'+people.cover_name+')'}"></div>
                        <p class="people-name" :title="people.name+'('+people.faces+')'">
                            <span>{{people.name}}</span>
                            <span class="people-peoples">（{{people.faces}}）</span>
                        </p>
                        <p class="people-peoples">
                            <span style="margin-right: 10px">特征照片: {{people.features}}</span>
                            <el-tooltip v-if="people.features===0" class="item" effect="dark" placement="bottom-start">
                                <span slot="content">该人物没有特征照片，将无法进行智能匹配！</span>
                                <i class="el-icon-info" style="color: #F56C6C;"></i>
                            </el-tooltip>
                        </p>
                    </div>
                    <!--下拉菜单-->
                    <el-dropdown class="btn-dropdown" trigger="click" placement="bottom-start"
                                 @command="handCommand">
                        <i class="el-icon-more btn-menu"></i>
                        <el-dropdown-menu slot="dropdown">
                            <el-dropdown-item icon="el-icon-edit"
                                              :command="beforeHandleCommand(people.uuid, people.name, 'rename')">
                                重命名人物
                            </el-dropdown-item>
                            <el-dropdown-item icon="el-icon-user-solid"
                                              :command="beforeHandleCommand(people.uuid, people.name, 'feature')">
                                选择特征照片
                            </el-dropdown-item>
                            <el-dropdown-item icon="el-icon-delete"
                                              :command="beforeHandleCommand(people.uuid, people.name, 'remove')">
                                删除人物
                            </el-dropdown-item>
                        </el-dropdown-menu>
                    </el-dropdown>
                </el-col>
            </el-row>
        </el-main>
    </el-container>
</template>

<script>
    import SearchButton from "./MainHeader/SearchButton";

    export default {
        name: "Peoples",
        components: {SearchButton},
        data() {
            return {
                peopleList: [],  //人物列表
                isShowEmptyTips: false,  //是否显示空列表提示
            }
        },
        computed: {
            apiUrl() {
                return this.$store.state.apiUrl  //后台api调用地址
            },
        },
        mounted() {
            this.showPeoples()
        },
        methods: {
            showPeoples() {
                //获取人物列表
                this.$axios({
                    method: 'get',
                    url: this.apiUrl + '/api/people_list',
                    params: {
                        userid: localStorage.getItem('userid'),
                    }
                }).then(response => {
                    this.peopleList = response.data
                    if (this.peopleList.length === 0) {  //显示空列表提示
                        this.isShowEmptyTips = true
                    }
                })
            },
            showPeople(uuid) {
                //跳转到指定的人物
                this.$router.push({
                    name: 'people',
                    params: {uuid: uuid, type: 'photo'}
                })
            },
            beforeHandleCommand(uuid, name, command) {
                return {
                    'uuid': uuid,
                    'name': name,
                    'command': command
                }
            },
            handCommand(command) {
                switch (command.command) {
                    case 'rename':  //重命名人物
                        this.renamePeople(command.uuid, command.name)
                        break
                    case 'feature':
                        this.openPickFeature(command.uuid)
                        break
                    case 'remove':  //删除人物
                        this.removePeople(command.uuid, command.name)
                        break
                }
            },
            renamePeople(uuid, name) {
                //重命名人物
                this.$prompt('请输入人物姓名：', {
                    inputValue: name,
                    closeOnClickModal: false,
                    inputValidator: (value => {
                        if (value.trim().length === 0)
                            return false
                    }),
                    inputErrorMessage: '人物姓名不能为空'
                }).then(({value}) => {
                    this.$axios({
                        method: 'post',
                        url: this.apiUrl + '/api/people_rename',
                        data: {
                            uuid: uuid,
                            name: value
                        }
                    }).then(() => {
                        this.showPeoples()
                        this.$message({
                            message: '人物 [' + name + '] 成功重命名为 [' + value + ']',
                            type: 'success',
                        })
                    })
                }).catch(() => {
                });
            },
            removePeople(uuid, name) {
                //删除人物
                this.$confirm('人物一经删除便无法恢复。不过，已删除人物中的照片仍会保留在您的相册中。', '要删除人物吗？', {
                    confirmButtonText: '删除',
                    cancelButtonText: '保留人物',
                    closeOnClickModal: false,
                    type: 'warning'
                }).then(() => {
                    this.$axios({
                        method: 'post',
                        url: this.apiUrl + '/api/people_remove',
                        data: {
                            userid: localStorage.getItem('userid'),
                            uuid: uuid,
                        }
                    }).then(() => {
                        this.showPeoples()  //刷新人物列表
                        this.$message({
                            message: '人物 [' + name + '] 删除成功',
                            type: 'success',
                        })
                    })
                }).catch(() => {
                });
            },
            openPickFeature(uuid) {
                //选择人物特征照片
                this.$router.push({
                    name: 'pick_feature',
                    params: {peopleUUID: uuid}
                })
            },
        }
    }
</script>

<style scoped>
    .people-wrap { /*人物容器*/
        cursor: pointer;
        margin-bottom: 15px;
    }

    .people-cover { /*人物封面*/
        position: relative;
        padding-top: 100%;
        background-color: #80868b;
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        border-radius: 8px;
    }

    .people-name { /*人物姓名*/
        width: 100%;
        padding-top: 8px;
        font-size: 14px;
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
    }

    .people-peoples { /*人物中人脸的数量*/
        font-size: 12px;
        color: #5f6368;
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
    }

    .btn-dropdown { /*操作弹出菜单*/
        position: absolute;
        top: 5px;
        right: 15px;
    }

    .btn-menu { /*操作按钮*/
        padding: 5px;
        color: rgba(255, 255, 255, .7);
        background-color: rgba(0, 0, 0, .2);
        border-radius: 50%;
        cursor: pointer;
        transform: rotate(90deg);
    }

    .btn-menu:hover {
        color: #fff;
    }
</style>