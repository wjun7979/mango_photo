<template>
    <div>
        <!--当照片列表为空时显示一些提示信息-->
        <div v-if="isShowTips" style="text-align: center;">
            <img src="../assets/images/upload-bg.png" alt="tips" />
            <div style="font-size: 32px; line-height: 50px; font-weight: 400; color: #202124">准备好添加一些照片了吗？</div>
            <div style="font-size: 16px; line-height: 40px; font-weight: 400; color: #3c4043">点击右上角的【上传】按钮上传照片</div>
        </div>

        <!--照片列表-->
        <el-checkbox-group v-model="checkGroupList" class="images-wrap">
            <el-row v-for="(photo, index) of photo_list" :key="index" style="margin-right: 28px;">
                <el-checkbox class="chk-group" :label="photo.timestamp" @change="selectPhotoGroup(photo.timestamp)">
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
                            <el-image :src="api_url + '/' + img.path_thumbnail + '/' + img.name"
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
        <Preview v-if="isShowPreview" :url-list="preview_list_order" :on-close="closeViewer"></Preview>

        <!--选中照片后的工具栏-->
        <el-row class="chk-toolbar" v-show="checkList.length > 0">
            <el-col :span="12">
                <i class="el-icon-close" style="color: #202124;" @click="unselectPhoto"></i>
                <span style="font-size: 1.125rem; padding-left: 7px;">选择了 {{checkList.length}} 张照片</span>
            </el-col>
            <el-col :span="12" style="text-align: right">
                <i class="el-icon-plus" title="添加到影集"></i>
                <i class="el-icon-star-off" title="收藏"></i>
                <i class="el-icon-delete" title="删除"></i>
                <i class="el-icon-more" title="更多选项" style="transform: rotate(90deg);"></i>
            </el-col>
        </el-row>
    </div>
</template>

<script>
    import Preview from "./Preview";
    import {rafThrottle} from "element-ui/src/utils/util";
    import {off, on} from "element-ui/src/utils/dom";
    export default {
        name: "Browse",
        components: {Preview},
        data() {
            return {
                photo_list: [],  //照片列表
                isShowTips: false,  //是否显示上传提示
                isShowPreview: false,  //是否显示大图预览
                preview_list: [],  //初始的照片预览列表
                preview_list_order: [],  //重新排序之后的照片预览列表
                groupType: 'day',  //分组类型 day, month, year
                checkGroupList: [],  //选中的分组列表
                checkList: [],  //选中的照片列表
                imgHeight: 200,  //照片的高度
                lastSelectedUUID: null,  //最后一次选中的照片uuid
            }
        },
        computed: {
            //重要：vuex中定义的数据一定要在这里绑定，放在data()里视图不会更新
            api_url() {
                return this.$store.state.api_url  //从全局状态管理器中获取数据
            },
            refresh_photo() {
                return this.$store.state.refresh_photo  //是否刷新照片列表
            }
        },
        watch: {
            refresh_photo() {
                //有其它组件发出刷新照片的指令
                if (this.refresh_photo) {
                    this.showPhotos()
                }
            },
            checkList(val) {
                //当选中的照片列表发生变化时，记录最后一次选中照片的uuid
                if (val.length === 0)
                    this.lastSelectedUUID = null
                else {
                    this.lastSelectedUUID = val[val.length - 1]
                }
            },
            groupType() {
                //分组类型改变时重新载入照片
                this.showPhotos()
            }
        },
        mounted() {
            this.showPhotos()  //获取并显示照片列表
            this.deviceSupportInstall()  //注册键盘按键支持
            window.addEventListener('resize', this.listenResize)
            this.setImgHeight()
        },
        beforeDestroy() {
            this.deviceSupportUninstall()  //卸载键盘按键支持
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
                this.imgHeight = document.documentElement.clientWidth / 8
                this.imgHeight = this.imgHeight < 100 ? 100 : this.imgHeight
                this.imgHeight = this.imgHeight > 200 ? 200 : this.imgHeight
            },
            showPhotos() {
                //获取并显示照片列表
                this.$http.get(this.api_url + '/api/photo_list').then(response => {
                    const res = JSON.parse(response.bodyText)
                    if (res.msg === 'success') {
                        let result = res.list
                        // 生成大图预览列表
                        this.preview_list = []
                        for (let item of result) {
                            this.preview_list.push({
                                'uuid': item.uuid,
                                'url': this.api_url + '/' + item.path + '/' + item.name,
                                'timestamp': this.getGroupLabel(item['exif_datetime'])
                            })
                        }
                        // 将照片列表转换成时间线要求的格式
                        let dataMap = []
                        for (let d of result) {
                            let findData = dataMap.find(t=> t.timestamp === this.getGroupLabel(d['exif_datetime']))
                            if (!findData)
                                dataMap.push({'timestamp': this.getGroupLabel(d['exif_datetime']), 'list': [d]})
                            else
                                findData.list.push(d)
                        }
                        this.photo_list = dataMap
                        // 当没有照片时显示上传提示
                        this.isShowTips = this.photo_list.length === 0
                    } else {
                        this.$notify.error({
                            title: '提示',
                            message: '获取照片失败:' + res.msg,
                            position: 'top-right'
                        })
                    }
                    //照片读取完成后，将store.js中的refreshPhoto值重置为false
                    this.$store.commit('refreshPhoto', {show: false})
                })
            },
            showPreview(uuid) {
                //显示大图预览
                let index = this.preview_list.findIndex(t => t.uuid === uuid)  //获取即将预览的照片索引
                //根据索引对预览数组重新排序
                this.preview_list_order = this.preview_list.slice(index).concat(this.preview_list.slice(0, index))
                this.isShowPreview = true
                this.deviceSupportUninstall()  //卸载键盘按键支持，防止与大图预览中的快捷键冲突
            },
            clickImage(uuid, timestamp) {
                //点击照片时发生，按下shift等修饰键时不会触发单击事件
                if (this.checkList.length > 0) {  //当前有照片被选中了
                    let idx = this.checkList.indexOf(uuid)
                    if (idx === -1) {
                        this.checkList.push(uuid)
                    }
                    else {
                        this.checkList.splice(idx, 1)
                    }
                    this.selectPhoto(uuid, timestamp)  //触发照片选择事件
                }
                else {  //没有照片被选中时，点击照片就是预览
                    this.showPreview(uuid)
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
                        groupLabel = this.$common.date_format(val,'yyyy年')
                        break
                    case 'month':
                        groupLabel =  this.$common.date_format(val,'yyyy年M月')
                        break
                    case 'day':
                        groupLabel = this.$common.date_format(val,'yyyy年M月d日 周w')
                        break
                    default:
                        groupLabel = val
                }
                return groupLabel
            },
            selectPhotoGroup(timestamp) {
                //按组选择照片时
                let photoGroup = this.photo_list.find(t=> t.timestamp === timestamp)
                let timeStamp = photoGroup.timestamp
                let photos = photoGroup.list
                for (let item of photos) {
                    if (this.checkGroupList.indexOf(timeStamp) !== -1) {  //选中了该组
                        if (this.checkList.indexOf(item.uuid) === -1) {
                            this.checkList.push(item.uuid)
                        }
                    }
                    else {
                        let idx = this.checkList.indexOf(item.uuid)
                        if (idx !== -1) {
                            this.checkList.splice(idx, 1)
                        }
                    }
                }
            },
            selectPhoto(uuid, timestamp) {
                //选择照片时，判断分组复选框是否勾选
                let photoGroup = this.photo_list.find(t=> t.timestamp === timestamp)
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
                }
                else {
                    if (idx !== -1)
                        this.checkGroupList.splice(idx, 1)
                }
            },
            unselectPhoto() {
                //放弃选择
                this.checkList = []
                this.checkGroupList = []
            },
            multiSelectPhotos(e, uuid, timestamp) {
                //连续选择照片，当按下shift时才触发该事件
                if (e.target.tagName === 'SPAN') return  //因为原生click事件会执行两次，第一次在label标签上，第二次在input标签上，故此处理
                //当起始照片uuid不存在时，不执行连续选择操作
                if (this.lastSelectedUUID != null) {
                    let startIdx = this.preview_list.findIndex(t=> t.uuid === this.lastSelectedUUID)
                    let endIdx = this.preview_list.findIndex(t=> t.uuid === uuid)
                    let startIndex = endIdx > startIdx ? startIdx: endIdx
                    let endIndex = endIdx > startIdx ? endIdx : startIdx
                    if (this.checkList.indexOf(uuid) === -1) {  //当前照片处于未选中状态，执行连续选中操作
                        for (let i = startIndex;i <= endIndex; i++) {
                            if (this.checkList.indexOf(this.preview_list[i].uuid) === -1) {
                                this.checkList.push(this.preview_list[i].uuid)
                                this.selectPhoto(this.preview_list[i].uuid, this.preview_list[i].timestamp)  //触发照片选择事件
                            }
                        }
                    }
                    else {  //当前照片处于选中状态，执行连续取消选中操作
                        for (let i = startIndex;i <= endIndex; i++) {
                            let idx = this.checkList.indexOf(this.preview_list[i].uuid)
                            if (idx !== -1) {
                                this.checkList.splice(idx, 1)
                                this.selectPhoto(this.preview_list[i].uuid, this.preview_list[i].timestamp)  //触发照片选择事件
                            }
                        }
                    }
                }
                else {  //当用户在照片上按住shift键单击时，映射到点击照片的动作
                    if (e.target.tagName === 'IMG')
                        this.clickImage(uuid, timestamp)
                }
            },
        }
    }
</script>

<style scoped>
    .image-slot {  /*图片加载失败时的插槽*/
        margin-right: 5px;
        width: 200px;
        height: 200px;
        line-height: 200px;
        background: #f5f7fa;
        color: #909399;
        text-align: center;
    }

    .images-wrap, .div-images {  /*瀑布流照片*/
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

    .chk-group {  /*分组选择*/
        margin-top: 15px;
        margin-bottom: 10px;
    }

    .chk-group >>> .el-checkbox__input {  /*修正分组选择勾选框的位置偏移*/
        margin-top: -2px;
    }

    .chk-group >>> .el-checkbox__inner {  /*分组选择控件外观*/
        width: 20px;
        height: 20px;
        border-width: 2px;
        border-radius: 50%;
    }

    .chk-group >>> .el-checkbox__inner:after {  /*分组选择控件内勾的外观*/
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

    .chk-group >>> .is-checked+.el-checkbox__label {
        color: #606266;
    }

    .div-images >>> .el-checkbox {  /*选择控件*/
        visibility: hidden;  /*控件默认隐藏*/
        position: absolute;
        top: 8px;
        left: 8px;
    }

    .div-images >>> .el-checkbox__label {  /*选择控件的文本*/
        display: none;
    }

    .div-images >>> .el-checkbox__inner {  /*选择控件的外观*/
        width: 20px;
        height: 20px;
        border: 2px solid #FFF;
        border-radius: 50%;
        background-color: rgba(0,0,0,.1);
    }

    .div-images >>> .el-checkbox__inner:after {  /*选择控件内勾的外观*/
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
    .div-img:hover .btn-preview {  /*鼠标移上去时显示勾选控件和预览按钮*/
        visibility: visible;
    }

    .show-checkbox >>> .el-checkbox {
        visibility: visible;  /*当选择了照片时，所有的勾选控件都显示出来*/
    }

    .chk-checked {  /*选中之后的背景色*/
        background-color: #dbe9ff;
    }

    .chk-last-checked {  /*最后一次选中的的背景色*/
        background-color: #ffd9e9;
    }

    .chk-checked >>> .el-image {  /*选中之后改变照片大小*/
        top: 16px;
        left: 16px;
        width: calc(100% - 32px);
        height: calc(100% - 32px);
    }

    .chk-checked >>> .el-checkbox__inner {
        visibility: visible;
    }

    .btn-preview {  /*照片上浮现的预览按钮*/
        visibility: hidden;
        position: absolute;
        right: 8px;
        bottom: 8px;
        padding: 5px;
        z-index: 1;
        color: rgba(255,255,255,.7);
        background-color: rgba(0,0,0,.2);
        font-size: 20px;
        font-weight: bold;
        border-radius: 50%;
        cursor: pointer;
    }

    .btn-preview:hover {
        color: #fff;
    }

    .chk-toolbar {  /*选中照片后的工具栏*/
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 64px;
        padding: 0 14px;
        background-color: #fff;
        box-shadow: 0 1px 2px 0 rgba(60,64,67,.30), 0 2px 6px 2px rgba(60,64,67,.15);
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
</style>