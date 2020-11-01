<template>
    <div style="padding-top: 10px">
        <el-row :gutter="20" style="margin: 0">
            <el-col :xs="{span:12}" :sm="{span:8}" :lg="{span:6}" :xl="{span:4}" v-for="album of albumList"
                    :key="album.uuid" style="position: relative">
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
                                          :command="beforeHandleCommand(album.uuid, album.name, album.parent_uuid, 'rename')">
                            重命名影集
                        </el-dropdown-item>
                        <el-dropdown-item icon="el-icon-delete"
                                          :command="beforeHandleCommand(album.uuid, album.name, album.parent_uuid, 'remove')">
                            删除影集
                        </el-dropdown-item>
                        <el-dropdown-item icon="el-icon-sort"
                                          :command="beforeHandleCommand(album.uuid, album.name, album.parent_uuid, 'move')">
                            移动影集
                        </el-dropdown-item>
                        <el-dropdown-item icon="el-icon-notebook-1"
                                          :command="beforeHandleCommand(album.uuid, album.name, album.parent_uuid, 'cover')">
                            选择影集封面
                        </el-dropdown-item>
                    </el-dropdown-menu>
                </el-dropdown>
            </el-col>
        </el-row>
        <el-divider id="album_divider" v-if="parentUUID!=='' && albumList.length>0"></el-divider>
        <!--移动影集对话框-->
        <el-dialog class="album-dialog" title="移动影集"
                   :visible.sync="isShowMoveAlbumDialog"
                   width="340px"
                   :close-on-click-modal="false">
            <el-tree class="album-tree" ref="albumTree" :lazy="true" :load="loadAlbumTree" node-key="uuid"
                     :props="{label:'name'}"
                     :default-expand-all="false"
                     :expand-on-click-node="true"
                     :highlight-current="true">
                <div slot-scope="{ data }">
                    <div class="album-tree-cover"
                         :style="{'background-image':'url('+apiUrl+'/'+data.cover_path+'/'+data.cover_name+')'}"></div>
                    <div style="float: left">
                        <p class="album-tree-title">{{data.name}}</p>
                        <p class="album-tree-photos" v-if="data.photos === 0">没有内容</p>
                        <p class="album-tree-photos" v-else>
                            <span>{{$common.dateFormat(data.min_time,'yyyy-MM-dd')}}至{{$common.dateFormat(data.max_time,'yyyy-MM-dd')}}</span>
                            <span style="margin-left: 10px">{{data.photos}}项</span>
                        </p>
                    </div>
                </div>
            </el-tree>
            <span slot="footer">
                <el-button type="primary" size="small" @click="moveAlbum('root')">移动到根节点</el-button>
                <el-button @click="isShowMoveAlbumDialog = false" size="small">取消</el-button>
                <el-button type="primary" size="small" @click="moveAlbum('node')">确定</el-button>
            </span>
        </el-dialog>
    </div>
</template>

<script>
    export default {
        name: "AlbumList",
        data() {
            return {
                albumList: [],  //影集列表
                isShowMoveAlbumDialog: false,  //是否显示移动影集对话框
                currAlbum: {  //将要被移动的影集对象
                    'uuid': '',
                    'name': '',
                    'parent_uuid': '',
                    'command': ''
                },
                node: null,
                resolve: null,
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
            parentUUID() {
                //当上级影集uuid变化时，重新载入影集列表
                this.showAlbums()
            }
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
            beforeHandleCommand(uuid, name, parent_uuid, command) {
                return {
                    'uuid': uuid,
                    'name': name,
                    'parent_uuid': parent_uuid,
                    'command': command
                }
            },
            handCommand(command) {
                this.$store.commit('cancelSelectPhoto', {action: true})  //取消已选中的照片
                switch (command.command) {
                    case 'rename':  //重命名
                        this.renameAlbum(command)
                        break
                    case 'remove':  //删除
                        this.removeAlbum(command)
                        break
                    case 'move':  //移动
                        this.showAlbumTree(command)
                        break
                    case 'cover':  //设置影集封面
                        this.setAlbumCover(command)
                        break
                }
            },
            renameAlbum(command) {
                //重命令影集
                this.$prompt('请输入影集标题：', {
                    inputValue: command.name,
                    closeOnClickModal: false,
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
                            name: value
                        }
                    }).then(() => {
                        this.showAlbums()  //刷新影集列表
                        this.$message({
                            message: '影集 [' + command.name + '] 成功重命名为 [' + value + ']',
                            type: 'success',
                        })
                    })
                }).catch(() => {
                });
            },
            showAlbumTree(command) {
                //打开影集树形列表对话框
                this.currAlbum = command
                if (this.node)
                    this.loadAlbumTree(this.node, this.resolve)
                this.isShowMoveAlbumDialog = true
                this.$store.commit('cancelSelectPhoto', {action: true})  //取消已选中的照片
            },
            loadAlbumTree(node, resolve) {
                //加载影集树
                if (node.level === 0) {  //修正el-tree懒加载的时候，只加载一次的问题
                    this.node = node  //这里是关键！在data里面定义一个变量，将node.level == 0的node存起来
                    this.resolve = resolve  //同上，把node.level == 0的resolve也存起来
                    // 把子节点清空，否则下次加载时会直接往里push子节点导致重复
                    this.node.childNodes = []
                }

                let parent_uuid = ''
                if (node.level !== 0) {
                    parent_uuid = node.data.uuid
                }
                this.$axios({
                    method: 'get',
                    url: this.apiUrl + '/api/album_target_list',
                    params: {
                        parent_uuid: parent_uuid,
                        curr_album_uuid: this.currAlbum.uuid,
                        userid: localStorage.getItem('userid'),
                    }
                }).then(response => {
                    const result = response.data
                    return resolve(result)
                })
            },
            moveAlbum(type) {
                //移动影集
                let target_album_uuid = ''  //目标影集uuid
                let target_album_name = ''  //目标影集名称
                if (type === 'node') {
                    target_album_uuid = this.$refs.albumTree.getCurrentKey()
                    if (!target_album_uuid) {
                        this.$message({
                            message: '请选择目标影集',
                            type: 'error',
                        })
                        return false
                    }
                    target_album_name = this.$refs.albumTree.getCurrentNode().name
                }
                if (type === 'root') {
                    target_album_uuid = ''  //移动到根节点
                    target_album_name = '根节点'
                }
                this.isShowMoveAlbumDialog = false
                this.$axios({
                    method: 'post',
                    url: this.apiUrl + '/api/album_move',
                    data: {
                        uuid: this.currAlbum.uuid,
                        parent_uuid: target_album_uuid
                    }
                }).then(() => {
                    this.$store.commit('refreshAlbum', {show: true})
                    this.$message({
                        message: '影集 [' + this.currAlbum.name + '] 成功移动到 [' + target_album_name + ']',
                        type: 'success',
                    })
                })
            },
            removeAlbum(command) {
                //删除影集
                this.$confirm('即将删除影集和所有的子影集。影集一经删除便无法恢复。不过，已删除影集中的照片仍会保留在您的相册中。', '要删除影集吗？', {
                    confirmButtonText: '删除',
                    cancelButtonText: '保留影集',
                    closeOnClickModal: false,
                    type: 'warning',
                }).then(() => {
                    this.$axios({
                        method: 'post',
                        url: this.apiUrl + '/api/album_remove',
                        data: {
                            uuid: command.uuid
                        }
                    }).then(() => {
                        this.showAlbums()  //刷新影集列表
                        this.$message({
                            message: '影集 [' + command.name + '] 删除成功',
                            type: 'success',
                        })
                    })
                }).catch(() => {
                });
            },
            setAlbumCover(command) {
                //选择影集封面
                this.$router.push({
                    name: 'pick_cover',
                    params: {albumUUID: command.uuid}
                })
            },
            showAlbum(uuid) {
                //跳转到指定的影集
                this.$router.push({
                    name: 'album',
                    params: {album_uuid: uuid}
                })
            },
        }
    }
</script>

<style scoped>
    .album-wrap { /*影集容器*/
        cursor: pointer;
        margin-bottom: 15px;
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

    .album-tree { /*影集树*/
        height: 300px;
        overflow: auto;
    }
    .album-dialog >>> .el-tree--highlight-current .el-tree-node.is-current > .el-tree-node__content {
        color: #f56c6c; /*影集树选中的节点*/
    }
    .album-tree >>> .el-tree-node__content {
        height: 50px;
        margin-bottom: 10px;
    }
    .album-tree-cover {
        float: left;
        margin-top: 2px;
        margin-right: 10px;
        width: 40px;
        height: 40px;
        background-color: #80868b;
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        border-radius: 5px;
    }
    .album-tree-title {
        font-size: 16px;
    }
    .album-tree-photos { /*影集中照片的数量*/
        margin-top: 5px;
        color: #909399;
        font-size: 12px;
    }
</style>