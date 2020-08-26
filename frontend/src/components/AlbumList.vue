<template>
    <div>
        <el-row :gutter="20">
            <el-col :span="4" v-for="album of albumList" :key="album.uuid" style="position: relative">
                <div class="album-wrap" @click="showAlbum(album.uuid)">
                    <div class="album-cover"
                         :style="{'background-image':'url('+apiUrl+'/'+album.cover_path+'/'+album.cover_name+')'}"></div>
                    <p class="album-name">{{album.name}}</p>
                    <p class="album-photos" v-if="album.photos === 0">没有内容</p>
                    <p class="album-photos" v-else>{{album.photos}}项</p>
                </div>
                <!--下拉菜单-->
                <el-dropdown class="btn-dropdown" trigger="click" placement="bottom-start"
                             @command="handCommand">
                    <i class="el-icon-more btn-menu"></i>
                    <el-dropdown-menu slot="dropdown">
                        <el-dropdown-item icon="el-icon-edit"
                                          :command="beforeHandleCommand(album.uuid, album.name, 'rename')">重命名影集
                        </el-dropdown-item>
                        <el-dropdown-item icon="el-icon-delete"
                                          :command="beforeHandleCommand(album.uuid, album.name, 'remove')">删除影集
                        </el-dropdown-item>
                    </el-dropdown-menu>
                </el-dropdown>
            </el-col>
        </el-row>
        <el-divider v-if="parentUUID!=='' && albumList.length>0"></el-divider>
    </div>
</template>

<script>
    export default {
        name: "AlbumList",
        data() {
            return {
                albumList: [],  //影集列表
            }
        },
        props: {
            parentUUID: {  //上级影集uuid
                type: String,
                default: ''
            },
        },
        computed: {
            apiUrl() {
                return this.$store.state.apiUrl  //后台api调用地址
            },
            refreshAlbum() {
                return this.$store.state.refreshAlbum  //是否刷新影集列表
            },
        },
        watch: {
            refreshAlbum() {
                //有其它组件发出刷新影集的指令
                if (this.refreshAlbum) {
                    this.showAlbums()
                }
            },
        },
        mounted() {
            this.showAlbums()
        },
        methods: {
            showAlbums() {
                //获取并显示影集列表
                this.$axios({
                    method: 'get',
                    url: this.apiUrl + '/api/album_list',
                    params: {
                        parent_uuid: this.parentUUID,
                        userid: localStorage.getItem('userid'),
                    }
                }).then(response => {
                    const result = response.data
                    this.albumList = result
                    this.$store.commit('refreshAlbum', {show: false})
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
                    case 'rename':  //重命名
                        this.$prompt('请输入影集标题', {
                            inputValue: command.name,
                            inputValidator: (value => {
                                if (value.trim().length === 0)
                                    return false
                            }),
                            inputErrorMessage: '影集标题不能为空'
                        }).then(({value}) => {
                            this.$axios({
                                method: 'post',
                                url: this.apiUrl + '/api/album_rename',
                                data: {
                                    uuid: command.uuid,
                                    name: value,
                                    userid: localStorage.getItem('userid')
                                }
                            }).then(() => {
                                this.$store.commit('refreshAlbum', {show: true})
                                this.$store.commit('showLog', {
                                    type: 'success',
                                    msg: '影集 [' + command.name + '] 成功重命名为 [' + value + ']',
                                    time: new Date().toLocaleTimeString()
                                })
                            })
                        }).catch(() => {
                        });
                        break
                    case 'remove':  //删除
                        this.$confirm('即将删除影集和所有的子影集。影集一经删除便无法恢复。不过，已删除影集中的照片仍会保留在您的相册中。', '要删除影集吗？', {
                            confirmButtonText: '删除',
                            cancelButtonText: '保留影集',
                            type: 'warning'
                        }).then(() => {
                            this.$axios({
                                method: 'post',
                                url: this.apiUrl + '/api/album_remove',
                                data: {
                                    uuid: command.uuid
                                }
                            }).then(() => {
                                this.showAlbums()  //刷新影集列表
                                this.$store.commit('refreshPhoto', {show: true})  //刷新图片列表
                                this.$store.commit('showLog', {
                                    type: 'success',
                                    msg: '影集 [' + command.name + '] 删除成功',
                                    time: new Date().toLocaleTimeString()
                                })
                            })
                        }).catch(() => {
                        });
                        break
                }
            },
            showAlbum(uuid) {
                //跳转到指定的影集
                this.$router.push({
                    name: 'album',
                    params: {uuid: uuid}
                })
            },
        }
    }
</script>

<style scoped>
    .album-wrap { /*影集容器*/
        cursor: pointer;
    }

    .album-cover { /*影集封面*/
        position: relative;
        padding-top: 100%;
        background-color: #80868b;
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        border-radius: 8px;
    }

    .album-name { /*影集标题*/
        width: 100%;
        padding-top: 8px;
        font-size: 14px;
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
    }

    .album-photos { /*影集中照片的数量*/
        font-size: 12px;
        color: #5f6368;
    }

    .btn-dropdown { /*操作弹出菜单*/
        position: absolute;
        top: 10px;
        right: 20px;
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