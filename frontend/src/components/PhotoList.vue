<template>
    <div>
        <!--照片分组尺寸快捷工具-->
        <div v-if="photoList.length>0" class="div-group-size">
            <el-popover placement="bottom-end">
                <label>分组：</label>
                <el-radio-group v-model="groupType" size="small">
                    <el-radio-button label="year">按年</el-radio-button>
                    <el-radio-button label="month">按月</el-radio-button>
                    <el-radio-button label="day">按天</el-radio-button>
                </el-radio-group>
                <i class="el-icon-menu btn-group-size" slot="reference"></i>
            </el-popover>
            <el-popover placement="bottom-end">
                <label>尺寸：</label>
                <el-slider v-model="imgHeight" :min="100" :max="200" style="width: 200px"></el-slider>
                <i class="el-icon-picture btn-group-size" slot="reference"></i>
            </el-popover>
        </div>
        <!--子影集列表-->
        <AlbumList v-if="callMode==='album'" :parentUUID="albumUUID"></AlbumList>
        <!--当照片列表为空时显示一些提示信息-->
        <div v-if="isShowTips" style="text-align: center; padding-top: 80px">
            <div style="font-size: 18px; font-weight: 400; color: #202124; margin-bottom: 20px">空空如也，没有任何内容。</div>
            <UploadFile v-if="callMode==='photo'" button-type="primary"></UploadFile>
            <img src="../assets/images/empty.png" alt=""/>
        </div>
        <!--照片列表-->
        <el-checkbox-group v-model="checkGroupList" class="images-wrap">
            <el-row v-for="(photo, index) of photoListGroup" :key="index" style="margin-right: 28px;">
                <el-checkbox class="chk-group" :label="photo.timestamp"
                             @change="selectPhotoGroup(photo.timestamp)">
                </el-checkbox>
                <el-checkbox-group v-model="checkList">
                    <!--瀑布流样式的照片列表-->
                    <div class="div-images">
                        <div v-for="img of photo.list"
                             :key="img.uuid"
                             class="div-img"
                             :class="{'chk-checked': checkList.indexOf(img.uuid) !== -1,
                                      'chk-last-checked': lastSelectedUUID === img.uuid,
                                      'show-checkbox': checkList.length > 0}"
                             :style="{'width': img.width * imgHeight / img.height + 'px',
                                      'flex-grow':img.width * imgHeight / img.height}">
                            <i :style="{'padding-bottom': img.height / img.width * 100 + '%', 'display':'block'}"></i>
                            <el-checkbox :label="img.uuid"
                                         @change="selectPhoto(img.uuid, photo.timestamp)"
                                         @click.native.shift.exact="multiSelectPhotos($event, img.uuid, photo.timestamp)">
                            </el-checkbox>
                            <i class="el-icon-zoom-in btn-preview" @click="showPreview(img.uuid)"></i>
                            <el-image :src="apiUrl + '/' + img.path_thumbnail + '/' + img.name"
                                      lazy
                                      :alt="img.name"
                                      :title="img.name"
                                      @click.exact="clickImage(img.uuid, photo.timestamp)"
                                      @click.shift.exact="multiSelectPhotos($event, img.uuid, photo.timestamp)"
                                      style="cursor: pointer;">
                                <div slot="error">
                                    <div class="image-slot">
                                        <i class="el-icon-picture-outline"></i>
                                    </div>
                                </div>
                            </el-image>
                        </div>
                    </div>
                </el-checkbox-group>
            </el-row>
        </el-checkbox-group>

        <!--大图预览-->
        <Preview v-if="isShowPreview" :url-list="previewListOrder" :callMode="callMode" :albumUUID="albumUUID"
                 :albumName="albumName" :on-close="closeViewer"></Preview>

        <!--选中照片后的工具栏-->
        <el-row class="chk-toolbar" v-show="callMode!=='pick' && checkList.length>0">
            <el-col :span="12">
                <i class="el-icon-close" style="color: #202124;" @click="unselectPhoto"></i>
                <span style="font-size: 1.125rem; padding-left: 7px;">选择了 {{checkList.length}} 张照片</span>
            </el-col>
            <el-col :span="12" style="text-align: right">
                <div v-if="callMode==='photo'">
                    <i class="el-icon-plus" title="添加到影集" @click="isShowAddToAlbumDialog = true"></i>
                    <i class="el-icon-star-off" title="收藏" @click="addToFavorites"></i>
                    <i class="el-icon-delete" title="删除" @click="trashPhoto"></i>
                    <el-dropdown trigger="click" @command="handCommand" placement="bottom-end">
                        <i class="el-icon-more" title="更多选项" style="transform: rotate(90deg);"></i>
                        <el-dropdown-menu slot="dropdown">
                            <el-dropdown-item icon="el-icon-download" command="download">下载</el-dropdown-item>
                            <el-dropdown-item icon="el-icon-date" command="modify_datetime">修改日期和时间</el-dropdown-item>
                            <el-dropdown-item icon="el-icon-location-outline" command="modify_location">修改位置信息
                            </el-dropdown-item>
                        </el-dropdown-menu>
                    </el-dropdown>
                </div>
                <div v-if="callMode==='album'">
                    <i class="el-icon-remove-outline" title="从影集中移除" @click="removeFromAlbum"></i>
                    <i class="el-icon-star-off" title="收藏" @click="addToFavorites"></i>
                    <i class="el-icon-delete" title="删除" @click="trashPhoto"></i>
                    <el-dropdown trigger="click" @command="handCommand" placement="bottom-end">
                        <i class="el-icon-more" title="更多选项" style="transform: rotate(90deg);"></i>
                        <el-dropdown-menu slot="dropdown">
                            <el-dropdown-item icon="el-icon-download" command="download">下载</el-dropdown-item>
                            <el-dropdown-item icon="el-icon-date" command="modify_datetime">修改日期和时间</el-dropdown-item>
                            <el-dropdown-item icon="el-icon-location-outline" command="modify_location">修改位置信息
                            </el-dropdown-item>
                        </el-dropdown-menu>
                    </el-dropdown>
                </div>
                <div v-if="callMode==='trash'">
                    <el-button class="btn-toolbar" v-if="callMode==='trash'" type="text" @click="restorePhoto">恢复
                    </el-button>
                    <el-button class="btn-toolbar" v-if="callMode==='trash'" type="text" @click="removePhoto">永久删除
                    </el-button>
                </div>
            </el-col>
        </el-row>

        <!--添加到影集对话框-->
        <el-dialog class="album-dialog" title="添加到影集"
                   :visible.sync="isShowAddToAlbumDialog"
                   width="400px"
                   :close-on-click-modal="false">
            <el-tree class="album-tree" ref="albumTree" :lazy="true" :load="loadAlbumTree" node-key="uuid"
                     :props="{label:'name'}"
                     :default-expand-all="false"
                     :expand-on-click-node="true"
                     :highlight-current="true"></el-tree>
            <span slot="footer">
                <el-button @click="isShowAddToAlbumDialog = false" size="small">取消</el-button>
                <el-button type="primary" size="small" @click="addToAlbum">确定</el-button>
            </span>
        </el-dialog>
    </div>
</template>

<script>
    import AlbumList from "./AlbumList";
    import UploadFile from "./UploadFile";
    import Preview from "./Preview";
    import {rafThrottle} from "element-ui/src/utils/util";
    import {off, on} from "element-ui/src/utils/dom";

    export default {
        name: "PhotoList",
        components: {Preview, AlbumList, UploadFile},
        data() {
            return {
                imgHeight: 200,  //照片的高度
                photoList: [],  //照片列表
                photoListGroup: [],  //分组后的照片列表
                isShowTips: false,  //是否显示上传提示
                isShowPreview: false,  //是否显示大图预览
                previewList: [],  //初始的照片预览列表
                previewListOrder: [],  //重新排序之后的照片预览列表
                groupType: 'day',  //分组类型 day, month, year
                checkGroupList: [],  //选中的分组列表
                checkList: [],  //选中的照片列表
                lastSelectedUUID: null,  //最后一次选中的照片uuid
                isShowAddToAlbumDialog: false,  //是否显示添加到影集对话框
            }
        },
        props: {
            callMode: {  //调用模式
                type: String,
                default: 'photo'  //photo:照片; album:影集; pick:挑选照片到影集
            },
            albumUUID: {  //当调用模式为album时，必须指定影集uuid
                type: String,
                default: ''
            },
            albumName: {  //影集标题
                type: String,
                default: ''
            },
            albumPhotoList: {  //影集中的照片列表
                type: Array,
                default: () => []
            },
            onPick: {
                type: Function,
                default: () => {}
            }
        },
        computed: {
            //重要：vuex中定义的数据一定要在这里绑定，放在data()里视图不会更新
            apiUrl() {
                return this.$store.state.apiUrl  //后台api调用地址
            },
            mainHeight() {
                if (this.callMode === 'pick')
                    return document.documentElement.clientHeight - 48 + 'px'
                else
                    return this.$store.state.mainHeight  //主内容区的高度
            },
            refreshPhoto() {
                return this.$store.state.refreshPhoto  //是否刷新照片列表
            },
            cancelSelectPhoto() {
                return this.$store.state.cancelSelectPhoto  //是否取消已选中的照片
            },
        },
        watch: {
            refreshPhoto() {
                //有其它组件发出刷新照片的指令
                if (this.refreshPhoto) {
                    this.showPhotos()
                }
            },
            cancelSelectPhoto() {
                //有其它组件发出取消已选中照片的指令
                if (this.cancelSelectPhoto) {
                    this.unselectPhoto()
                }
            },
            checkList(val) {
                //当选中的照片列表发生变化时，记录最后一次选中照片的uuid
                if (val.length === 0)
                    this.lastSelectedUUID = null
                else {
                    this.lastSelectedUUID = val[val.length - 1]
                }
                //将选中的照片列表传递给上级组件
                if (this.callMode === 'pick') {
                    let albumPhotoList = this.albumPhotoList
                    let removeList = albumPhotoList.filter(function(v){ return val.indexOf(v) === -1 })
                    let addList = val.filter(function(v){ return albumPhotoList.indexOf(v) === -1 })
                    this.onPick(removeList, addList)
                }
            },
            groupType() {
                //分组类型改变时重新载入照片
                this.creatPhotoGroup()
            }
        },
        mounted() {
            this.showPhotos()  //获取并显示照片列表
            if (this.callMode === 'pick') {
                for (let item of this.albumPhotoList) {
                    this.checkList.push(item)  //将当前影集中的照片默认选中
                }
            }
            if (this.callMode !== 'pick') {
                this.deviceSupportInstall()  //注册键盘按键支持
            }
            window.addEventListener('resize', this.listenResize)
            this.setImgHeight()
        },
        beforeDestroy() {
            if (this.callMode !== 'pick') {
                this.deviceSupportUninstall()  //卸载键盘按键支持
            }
            window.removeEventListener('resize', this.listenResize)
        },
        methods: {
            deviceSupportInstall() {
                //注册键盘按键支持
                this._keyDownHandler = rafThrottle(e => {
                    const keyCode = e.keyCode
                    switch (keyCode) {
                        case 27:  //ESC取消选择
                            this.unselectPhoto()
                            break
                    }
                })
                on(document, 'keydown', this._keyDownHandler)
            },
            deviceSupportUninstall() {
                //卸载键盘按键支持
                off(document, 'keydown', this._keyDownHandler)
                this._keyDownHandler = null
            },
            listenResize: function () {
                //监听浏览器窗口大小变化的事件
                this.setImgHeight()
            },
            setImgHeight() {
                //浏览器窗口大小变化时改变照片的大小
                this.imgHeight = parseInt((document.documentElement.clientWidth / 8).toString())
                this.imgHeight = this.imgHeight < 100 ? 100 : this.imgHeight
                this.imgHeight = this.imgHeight > 200 ? 200 : this.imgHeight
            },
            showPhotos() {
                //获取并显示照片列表
                this.$axios({
                    method: 'get',
                    url: this.apiUrl + '/api/photo_list',
                    params: {
                        userid: localStorage.getItem('userid'),
                        call_mode: this.callMode,
                        album_uuid: this.albumUUID,
                    }
                }).then(response => {
                    this.photoList = response.data
                    // 生成大图预览列表
                    this.previewList = []
                    for (let item of this.photoList) {
                        this.previewList.push({
                            'uuid': item.uuid,
                            'url': this.apiUrl + '/' + item.path + '/' + item.name,
                            'timestamp': this.getGroupLabel(item['exif_datetime'])
                        })
                    }
                    this.creatPhotoGroup()  //创建照片分组
                    // 当没有照片时显示上传提示
                    this.isShowTips = this.photoList.length === 0
                    //照片读取完成后，将store.js中的refreshPhoto值重置为false
                    this.$store.commit('refreshPhoto', {show: false})
                })
            },
            creatPhotoGroup() {
                //将照片列表转换成时间线要求的分组格式
                let dataMap = []
                for (let d of this.photoList) {
                    let findData = dataMap.find(t => t.timestamp === this.getGroupLabel(d['exif_datetime']))
                    if (!findData)
                        dataMap.push({'timestamp': this.getGroupLabel(d['exif_datetime']), 'list': [d]})
                    else
                        findData.list.push(d)
                }
                this.photoListGroup = dataMap
            },
            showPreview(uuid) {
                //显示大图预览
                let index = this.previewList.findIndex(t => t.uuid === uuid)  //获取即将预览的照片索引
                //根据索引对预览数组重新排序
                this.previewListOrder = this.previewList.slice(index).concat(this.previewList.slice(0, index))
                this.isShowPreview = true
                this.deviceSupportUninstall()  //卸载键盘按键支持，防止与大图预览中的快捷键冲突
            },
            clickImage(uuid, timestamp) {
                //点击照片时发生，按下shift等修饰键时不会触发单击事件
                if (this.checkList.length > 0) {  //当前有照片被选中了
                    let idx = this.checkList.indexOf(uuid)
                    if (idx === -1) {
                        this.checkList.push(uuid)
                    } else {
                        this.checkList.splice(idx, 1)
                    }
                    this.selectPhoto(uuid, timestamp)  //触发照片选择事件
                } else {
                    if (this.callMode === 'pick') {
                        this.checkList.push(uuid)
                        this.selectPhoto(uuid, timestamp)  //触发照片选择事件
                    }
                    else {  //没有照片被选中时，点击照片就是预览
                        this.showPreview(uuid)
                    }
                }
            },
            closeViewer() {
                //关闭大图预览
                this.isShowPreview = false
                this.deviceSupportInstall()  //恢复键盘按键支持
            },
            getGroupLabel(val) {
                //获取分组标签
                let groupLabel
                switch (this.groupType) {
                    case 'year':
                        groupLabel = this.$common.dateFormat(val, 'yyyy年')
                        break
                    case 'month':
                        groupLabel = this.$common.dateFormat(val, 'yyyy年M月')
                        break
                    case 'day':
                        groupLabel = this.$common.dateFormat(val, 'yyyy年M月d日 周w')
                        break
                    default:
                        groupLabel = val
                }
                return groupLabel
            },
            selectPhotoGroup(timestamp) {
                //按组选择照片时
                let photoGroup = this.photoListGroup.find(t => t.timestamp === timestamp)
                let timeStamp = photoGroup.timestamp
                let photos = photoGroup.list
                for (let item of photos) {
                    if (this.checkGroupList.indexOf(timeStamp) !== -1) {  //选中了该组
                        if (this.checkList.indexOf(item.uuid) === -1) {
                            this.checkList.push(item.uuid)
                        }
                    } else {
                        let idx = this.checkList.indexOf(item.uuid)
                        if (idx !== -1) {
                            this.checkList.splice(idx, 1)
                        }
                    }
                }
            },
            selectPhoto(uuid, timestamp) {
                //选择照片时，判断分组复选框是否勾选
                let photoGroup = this.photoListGroup.find(t => t.timestamp === timestamp)
                let timeStamp = photoGroup.timestamp
                let photos = photoGroup.list
                let tmpArr = []
                for (let item of photos) {  //将当前组内的照片uuid存入一个新的数组
                    tmpArr.push(item.uuid)
                }
                let idx = this.checkGroupList.indexOf(timeStamp)
                if (this.$common.isContain(this.checkList, tmpArr)) {  //判断当前组照片是否全被选中
                    if (idx === -1)
                        this.checkGroupList.push(timeStamp)
                } else {
                    if (idx !== -1)
                        this.checkGroupList.splice(idx, 1)
                }
            },
            unselectPhoto() {
                //放弃选择
                this.checkList = []
                this.checkGroupList = []
                this.$store.commit('cancelSelectPhoto', {action: false})  //重置vuex的值
            },
            multiSelectPhotos(e, uuid, timestamp) {
                //连续选择照片，当按下shift时才触发该事件
                if (e.target.tagName === 'SPAN') return  //因为原生click事件会执行两次，第一次在label标签上，第二次在input标签上，故此处理
                //当起始照片uuid不存在时，不执行连续选择操作
                if (this.lastSelectedUUID != null) {
                    let startIdx = this.previewList.findIndex(t => t.uuid === this.lastSelectedUUID)
                    let endIdx = this.previewList.findIndex(t => t.uuid === uuid)
                    let startIndex = endIdx > startIdx ? startIdx : endIdx
                    let endIndex = endIdx > startIdx ? endIdx : startIdx
                    if (this.checkList.indexOf(uuid) === -1) {  //当前照片处于未选中状态，执行连续选中操作
                        for (let i = startIndex; i <= endIndex; i++) {
                            if (this.checkList.indexOf(this.previewList[i].uuid) === -1) {
                                this.checkList.push(this.previewList[i].uuid)
                                this.selectPhoto(this.previewList[i].uuid, this.previewList[i].timestamp)  //触发照片选择事件
                            }
                        }
                    } else {  //当前照片处于选中状态，执行连续取消选中操作
                        for (let i = startIndex; i <= endIndex; i++) {
                            let idx = this.checkList.indexOf(this.previewList[i].uuid)
                            if (idx !== -1) {
                                this.checkList.splice(idx, 1)
                                this.selectPhoto(this.previewList[i].uuid, this.previewList[i].timestamp)  //触发照片选择事件
                            }
                        }
                    }
                } else {  //当用户在照片上按住shift键单击时，映射到点击照片的动作
                    if (e.target.tagName === 'IMG')
                        this.clickImage(uuid, timestamp)
                }
            },
            loadAlbumTree(node, resolve) {
                //加载影集树
                let parent_uuid = ''
                if (node.level !== 0) {
                    parent_uuid = node.data.uuid
                }
                this.$axios({
                    method: 'get',
                    url: this.apiUrl + '/api/album_list',
                    params: {
                        parent_uuid: parent_uuid,
                        userid: localStorage.getItem('userid'),
                    }
                }).then(response => {
                    const result = response.data
                    return resolve(result)
                })
            },
            addToAlbum() {
                //将照片添加到影集
                let album_uuid = this.$refs.albumTree.getCurrentKey()
                let album_name = this.$refs.albumTree.getCurrentNode().name
                if (!album_uuid) {
                    this.$notify({
                        type: 'error',
                        title: '提示',
                        message: '请选择要添加照片的影集',
                        position: 'top-right'
                    })
                    return false
                }
                this.$axios({
                    method: 'post',
                    url: this.apiUrl + '/api/album_add_photo',
                    data: {
                        album_uuid: album_uuid,
                        photo_list: this.checkList
                    }
                }).then(() => {
                    let msg = '成功将' + this.checkList.length + ' 张照片添加到影集 [' + album_name + '] 中'
                    this.unselectPhoto()
                    this.isShowAddToAlbumDialog = false
                    this.$notify({
                        type: 'success',
                        title: '成功',
                        message: msg,
                        position: 'top-right'
                    })
                    this.$store.commit('showLog', {
                        type: 'success',
                        msg: msg,
                        time: new Date().toLocaleTimeString()
                    })
                })
            },
            removeFromAlbum() {
                //从影集中移除照片
                this.$confirm('您仍然可以在相册中找到该内容', '要移除此内容吗？', {
                    confirmButtonText: '移除',
                    cancelButtonText: '取消',
                    type: 'warning'
                }).then(() => {
                    this.$axios({
                        method: 'post',
                        url: this.apiUrl + '/api/album_remove_photo',
                        data: {
                            album_uuid: this.albumUUID,
                            photo_list: this.checkList
                        }
                    }).then(() => {
                        let msg = this.checkList.length + ' 张照片已从影集 [' + this.albumName + '] 中移除'
                        this.unselectPhoto()
                        this.$notify({
                            type: 'success',
                            title: '成功',
                            message: msg,
                            position: 'top-right'
                        })
                        this.$store.commit('showLog', {
                            type: 'success',
                            msg: msg,
                            time: new Date().toLocaleTimeString()
                        })
                        this.$store.commit('refreshPhoto', {show: true})  //刷新图片列表
                    })
                }).catch(() => {
                });
            },
            addToFavorites() {
                //收藏
                this.$message('收藏功能还没做好呢:-)')
            },
            trashPhoto() {
                //将照片移到回收站
                this.$confirm('当需要的时候可以在回收站中恢复。', '确定要删除照片吗？', {
                    confirmButtonText: '移到回收站',
                    cancelButtonText: '取消',
                    type: 'warning'
                }).then(() => {
                    this.$axios({
                        method: 'post',
                        url: this.apiUrl + '/api/photo_trash',
                        data: {
                            photo_list: this.checkList
                        }
                    }).then(() => {
                        let msg = '已将' + this.checkList.length + ' 张照片移到回收站'
                        this.unselectPhoto()
                        this.$notify({
                            type: 'success',
                            title: '成功',
                            message: msg,
                            position: 'top-right'
                        })
                        this.$store.commit('showLog', {
                            type: 'success',
                            msg: msg,
                            time: new Date().toLocaleTimeString()
                        })
                        this.$store.commit('refreshPhoto', {show: true})  //刷新图片列表
                        this.$store.commit('refreshPhotoStatistics', {show: true})  //刷新照片库统计信息
                    })
                }).catch(() => {
                });
            },
            restorePhoto() {
                //将照片从回收站恢复
                this.$confirm('要恢复选中的内容吗？', {
                    confirmButtonText: '恢复',
                    cancelButtonText: '取消',
                    type: 'info'
                }).then(() => {
                    this.$axios({
                        method: 'post',
                        url: this.apiUrl + '/api/photo_restore',
                        data: {
                            photo_list: this.checkList
                        }
                    }).then(() => {
                        let msg = this.checkList.length + ' 张照片成功恢复'
                        this.unselectPhoto()
                        this.$notify({
                            type: 'success',
                            title: '成功',
                            message: msg,
                            position: 'top-right'
                        })
                        this.$store.commit('showLog', {
                            type: 'success',
                            msg: msg,
                            time: new Date().toLocaleTimeString()
                        })
                        this.$store.commit('refreshPhoto', {show: true})  //刷新图片列表
                        this.$store.commit('refreshPhotoStatistics', {show: true})  //刷新照片库统计信息
                    })
                }).catch(() => {
                });
            },
            removePhoto() {
                //永久删除照片
                this.$confirm('内容一旦永久删除将无法恢复', '要永久删除选中的内容吗？', {
                    confirmButtonText: '删除',
                    cancelButtonText: '取消',
                    type: 'warning'
                }).then(() => {
                    this.$axios({
                        method: 'post',
                        url: this.apiUrl + '/api/photo_remove',
                        data: {
                            photo_list: this.checkList
                        }
                    }).then(() => {
                        let msg = this.checkList.length + ' 张照片成功删除'
                        this.unselectPhoto()
                        this.$notify({
                            type: 'success',
                            title: '成功',
                            message: msg,
                            position: 'top-right'
                        })
                        this.$store.commit('showLog', {
                            type: 'success',
                            msg: msg,
                            time: new Date().toLocaleTimeString()
                        })
                        this.$store.commit('refreshPhoto', {show: true})  //刷新图片列表
                    })
                }).catch(() => {
                });
            },
            handCommand(command) {
                //更多选项
                switch (command) {
                    case 'download':
                        this.downloadPhoto()
                        break
                    case 'modify_datetime':
                        this.modifyDateTime()
                        break
                    case 'modify_location':
                        this.modifyLocation()
                        break
                }
            },
            downloadPhoto() {
                //下载
                this.$message('下载功能还没做好呢:-)')
            },
            modifyDateTime() {
                //修改日期和时间
                this.$message('修改日期和时间功能还没做好呢:-)')
            },
            modifyLocation() {
                //修改位置信息
                this.$message('修改位置功能还没做好呢:-)')
            },
        }
    }
</script>

<style scoped>
    .image-slot { /*图片加载失败时的插槽*/
        margin-right: 5px;
        width: 200px;
        height: 200px;
        line-height: 200px;
        background: #f5f7fa;
        color: #909399;
        text-align: center;
    }

    .images-wrap, .div-images { /*瀑布流照片*/
        display: flex;
        flex-wrap: wrap;
    }

    .div-images::after {
        content: '';
        flex-grow: 999999999;
    }

    .div-images .div-img {
        position: relative;
        margin: 0 5px 5px 0;
    }

    .div-img >>> .el-image {
        position: absolute;
        top: 0;
        width: 100%;
        vertical-align: bottom;
    }

    .chk-group { /*分组选择*/
        margin-top: 15px;
        margin-bottom: 10px;
    }

    .chk-group >>> .el-checkbox__input { /*修正分组选择勾选框的位置偏移*/
        margin-top: -2px;
    }

    .chk-group >>> .el-checkbox__inner { /*分组选择控件外观*/
        width: 20px;
        height: 20px;
        border-width: 2px;
        border-radius: 50%;
    }

    .chk-group >>> .el-checkbox__inner:after { /*分组选择控件内勾的外观*/
        top: 0;
        width: 5px;
        height: 11px;
        border: 2px solid #FFF;
        border-left: 0;
        border-top: 0;
    }

    .chk-group >>> .is-checked .el-checkbox__inner {
        background-color: #757575;
        border-color: #757575;
    }

    .chk-group >>> .is-checked + .el-checkbox__label {
        color: #606266;
    }

    .div-images >>> .el-checkbox { /*选择控件*/
        visibility: hidden; /*控件默认隐藏*/
        position: absolute;
        top: 8px;
        left: 8px;
    }

    .div-images >>> .el-checkbox__label { /*选择控件的文本*/
        display: none;
    }

    .div-images >>> .el-checkbox__inner { /*选择控件的外观*/
        width: 20px;
        height: 20px;
        border: 2px solid #FFF;
        border-radius: 50%;
        background-color: rgba(0, 0, 0, .1);
    }

    .div-images >>> .el-checkbox__inner:after { /*选择控件内勾的外观*/
        top: 0;
        width: 5px;
        height: 11px;
        border: 2px solid #FFF;
        border-left: 0;
        border-top: 0;
    }

    .div-images >>> .is-checked .el-checkbox__inner {
        background-color: #409eff;
        border-color: #409eff;
    }

    .div-img:hover >>> .el-checkbox,
    .div-img:hover .btn-preview { /*鼠标移上去时显示勾选控件和预览按钮*/
        visibility: visible;
    }

    .show-checkbox >>> .el-checkbox {
        visibility: visible; /*当选择了照片时，所有的勾选控件都显示出来*/
    }

    .chk-checked { /*选中之后的背景色*/
        background-color: #dbe9ff;
    }

    .chk-last-checked { /*最后一次选中的的背景色*/
        background-color: #ffd9e9;
    }

    .chk-checked >>> .el-image { /*选中之后改变照片大小*/
        top: 16px;
        left: 16px;
        width: calc(100% - 32px);
        height: calc(100% - 32px);
    }

    .chk-checked >>> .el-checkbox__inner {
        visibility: visible;
    }

    .btn-preview { /*照片上浮现的预览按钮*/
        visibility: hidden;
        position: absolute;
        right: 8px;
        bottom: 8px;
        padding: 5px;
        z-index: 1;
        color: rgba(255, 255, 255, .7);
        background-color: rgba(0, 0, 0, .2);
        font-size: 20px;
        font-weight: bold;
        border-radius: 50%;
        cursor: pointer;
    }

    .btn-preview:hover {
        color: #fff;
    }

    .chk-toolbar { /*选中照片后的工具栏*/
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 64px;
        padding: 0 14px;
        background-color: #fff;
        box-shadow: 0 1px 2px 0 rgba(60, 64, 67, .30), 0 2px 6px 2px rgba(60, 64, 67, .15);
        z-index: 1100;
    }

    .chk-toolbar i {
        margin-top: 12px;
        margin-right: 5px;
        width: 40px;
        height: 40px;
        color: #1a73e8;
        font-size: 1.125rem;
        font-weight: bold;
        line-height: 40px;
        text-align: center;
        border-radius: 50%;
        cursor: pointer;
    }

    .chk-toolbar i:hover {
        background-color: #e5e5e5;
        border-radius: 50%;
    }

    .btn-toolbar {
        margin-top: 12px;
        margin-right: 15px;
    }

    .div-group-size {
        position: fixed;
        right: 50px;
        z-index: 1100;
        padding-top: 10px;
    }

    .btn-group-size { /*照片分组和尺寸工具按钮*/
        margin-left: 10px;
        padding: 8px;
        color: #409EFF;
        background-color: #ecf5ff;
        border-radius: 50%;
        cursor: pointer;
    }

    .album-tree { /*影集树*/
        height: 300px;
    }

    .album-dialog >>> .el-tree--highlight-current .el-tree-node.is-current > .el-tree-node__content {
        color: #f56c6c; /*影集树选中的节点*/
    }
</style>