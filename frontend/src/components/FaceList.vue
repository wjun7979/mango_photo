<template>
    <div>
        <!--当面孔列表为空时显示一些提示信息-->
        <div v-if="isShowTips" style="text-align: center; padding-top: 80px">
            <div style="font-size: 18px; font-weight: 400; color: #202124; margin-bottom: 20px">空空如也，没有任何内容。</div>
            <img src="../assets/images/empty.png" alt=""/>
        </div>
        <!--选中照片后的工具栏-->
        <el-row class="chk-toolbar" v-show="showChkToolBar">
            <el-col :span="12">
                <i class="el-icon-close" style="color: #202124;" @click="unselectFace"></i>
                <span v-show="checkList.length>0" class="chk-title">
                    <span class="hidden-xs-only">选择了 {{checkList.length}} 张面孔</span>
                    <span class="hidden-sm-and-up">{{checkList.length}} 张</span>
                </span>
            </el-col>
            <el-col :span="12" style="text-align: right">
                <div v-if="callMode==='people'">
                    <el-button v-show="checkList.length>0" type="primary" class="btn-toolbar" @click="removeFromPeople">Ta<span
                            v-show="checkList.length>1">们</span>不是{{people.name}}
                    </el-button>
                </div>
            </el-col>
        </el-row>
        <!--瀑布流样式的面孔列表-->
        <el-checkbox-group v-model="checkList">
            <div class="div-images">
                <div v-for="face of faces.faceList" :key="face.uuid" class="div-img"
                     :class="{'chk-checked': checkList.indexOf(face.uuid) !== -1,
                              'chk-last-checked': lastSelectedUUID === face.uuid}">
                    <!--叠加选择框-->
                    <el-checkbox :label="face.uuid"
                                 @click.native.shift.exact="multiSelectFaces($event, face.uuid, face.photo_uuid)"
                                 class="btn-checkbox"
                                 :class="{'show-always':showPhotoTools}">
                    </el-checkbox>
                    <!--叠加预览按钮-->
                    <i class="el-icon-zoom-in btn-preview" :class="{'show-always':showPhotoTools}"
                       @click="showPreview(face.photo_uuid)"></i>
                    <!--叠加特征标志-->
                    <i v-if="face.feature_token" class="el-icon-user-solid btn-feature"></i>
                    <el-image class="img-face" :src="apiUrl + '/' + face.path_thumbnail + '/' + face.name" lazy
                              scroll-container="body"
                              @click.exact="clickImage(face.uuid, face.photo_uuid)"
                              @click.shift.exact="multiSelectFaces($event, face.uuid, face.photo_uuid)">
                        <div slot="error">
                            <div class="image-slot">
                                <i class="el-icon-picture-outline"></i>
                            </div>
                        </div>
                    </el-image>
                </div>
            </div>
        </el-checkbox-group>
        <!--大图预览-->
        <Photo v-if="isShowPreview" :callMode="callMode" :uuid="previewPhotoUUID" :photoList="photos.photoList"
               :peopleUUID="peopleUUID" :on-close="closePreview"></Photo>
    </div>
</template>

<script>
    import {rafThrottle} from "element-ui/src/utils/util";
    import {off, on} from "element-ui/src/utils/dom";
    import Photo from "./Photo";

    export default {
        name: "FaceList",
        components: {Photo},
        data() {
            return {
                faces: {
                    faceList: [],  //面孔列表
                    total: 0,  //照片总数
                    page: 1,  //当前页号
                    pages: 1,  //总页数
                    pageSize: 100,  //每页的数量
                    isLoading: false,  //当前是否为加载状态
                },
                photos: {
                    photoList: [],  //照片列表
                    total: 0,  //照片总数
                    page: 1,  //当前页号
                    pages: 1,  //总页数
                    pageSize: 100,  //每页的数量
                    isLoading: false,  //当前是否为加载状态
                },
                checkList: [],  //选中的照片列表
                isShowTips: false,  //是否显示上传提示
                lastSelectedUUID: null,  //最后一次选中的面孔uuid
                people: {  //人物信息
                    name: '',
                    cover_path: '',
                    cover_name: '',
                },
                isShowPreview: false,  //是否显示大图预览
            }
        },
        props: {
            callMode: {  //调用模式
                type: String,
                //people:人物；pick_face:添加面孔到人物
                default: 'people'
            },
            peopleUUID: {  //当调用模式为people时，必须指定人物uuid
                type: String,
                default: undefined
            },
            onPick: {
                type: Function,
                default: () => {}
            },
        },
        computed: {
            apiUrl() {
                return this.$store.state.apiUrl  //后台api调用地址
            },
            refreshFace() {
                return this.$store.state.refreshFace.action  //是否刷新照片列表
            },
            cancelSelectFace() {
                return this.$store.state.cancelSelectFace  //是否取消已选中的面孔
            },
            pickFaceMode() {
                return this.$store.state.pickFaceMode  //移动设备下是否进入选择面孔模式
            },
            showChkToolBar() {  //是否显示选择工具栏
                if (['pick_face'].indexOf(this.callMode) === -1 && this.checkList.length > 0) {
                    return true
                } else {
                    if (this.pickFaceMode) {
                        return true
                    } else {
                        return false
                    }
                }
            },
            showPhotoTools() {  //是否始终显示照片上的浮动选择框预览按钮
                return ['pick_face'].indexOf(this.callMode) > -1 || this.pickFaceMode
            },
            previewPhotoUUID() {
                return this.$route.params.photo_uuid  //当前预览的照片
            },
        },
        watch: {
            refreshFace() {
                //有其它组件发出刷新照片的指令
                let refreshFace = this.$store.state.refreshFace
                if (refreshFace.action === 'reload') {  //刷新
                    this.faces.isLoading = true  //当前正处于加载状态
                    this.faces.faceList = []
                    this.faces.page = 1
                    this.showFaces()
                    this.photos.isLoading = true  //当前正处于加载状态
                    this.photos.photoList = []
                    this.photos.page = 1
                    this.showPhotos()
                }
                if (refreshFace.action === 'delete') {  //删除
                    this.faces.isLoading = true  //当前正处于加载状态
                    for (let item of refreshFace.list) {
                        let index = this.faces.faceList.findIndex(t => t.uuid === item)
                        this.faces.faceList.splice(index, 1)
                    }
                    this.faces.isLoading = false  //重置加载状态
                }
                if (refreshFace.action === 'update') {  //更新
                    let face = refreshFace.list
                    let index = this.faces.faceList.findIndex(t => t.uuid === face.uuid)
                    this.faces.faceList.splice(index, 1, face)
                }
                //操作完成后，将store.js中的refreshFace值重置为false
                this.$store.commit('refreshFace', {action: 'none', list: []})
            },
            cancelSelectFace() {
                //有其它组件发出取消已选中照片的指令
                if (this.cancelSelectFace) {
                    this.unselectFace()
                }
            },
            checkList(val) {
                //当选中的照片列表发生变化时，记录最后一次选中照片的uuid
                if (val.length === 0)
                    this.lastSelectedUUID = null
                else {
                    this.lastSelectedUUID = val[val.length - 1]
                }
                //将选中的面孔列表传递给上级组件
                if (this.callMode === 'pick_face') {
                    this.onPick(this.checkList)
                }
            },
            previewPhotoUUID(val) {
                //当照片uuid变化时，判断是否需要显示大图预览
                if (val === undefined) {
                    this.isShowPreview = false
                }
                else {
                    this.isShowPreview = true
                }
            },
        },
        mounted() {
            this.showFaces()  //获取并显示面孔列表
            this.showPhotos()  //获取照片列表
            if (this.callMode === 'people') {
                this.getPeople()
            }
            this.deviceSupportInstall()  //注册键盘按键支持
            window.addEventListener('scroll', this.listenScroll)
        },
        beforeDestroy() {
            this.deviceSupportUninstall()  //卸载键盘按键支持
            window.removeEventListener('scroll', this.listenScroll)
            this.$store.commit('pickFaceMode', {show: false})  //重置移动设备下是否进入选择面孔模式
        },
        methods: {
            deviceSupportInstall() {
                //注册键盘按键支持
                this._keyDownHandler = rafThrottle(e => {
                    const keyCode = e.keyCode
                    switch (keyCode) {
                        case 27:  //ESC取消选择
                            this.unselectFace()
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
            listenScroll() {
                //监听滚动事件，实现滚动加载
                let bottomOfWindow = document.documentElement.offsetHeight - document.documentElement.scrollTop - window.innerHeight <= 20
                if (bottomOfWindow && this.faces.isLoading === false) {
                    this.faces.isLoading = true  //当前正处于加载状态
                    if (this.faces.page < this.faces.pages) {
                        this.faces.page ++
                        this.showFaces()
                    }
                }
                if (bottomOfWindow && this.photos.isLoading === false) {
                    this.photos.isLoading = true  //当前正处于加载状态
                    if (this.photos.page < this.photos.pages) {
                        this.photos.page ++
                        this.showPhotos()
                    }
                }
            },
            showFaces() {
                //获取并显示面孔列表
                this.$axios({
                    method: 'get',
                    url: this.apiUrl + '/api/people_get_faces',
                    params: {
                        call_mode: this.callMode,
                        people_uuid: this.peopleUUID,
                        page: this.faces.page,
                        pagesize: this.faces.pageSize,
                    }
                }).then(response => {
                    this.faces.total = response.data.total  //总照片数
                    this.faces.pages = Math.ceil(this.faces.total / this.faces.pageSize)  //总页数
                    this.faces.faceList.push.apply(this.faces.faceList, response.data.list)

                    // 当没有照片时显示上传提示
                    this.isShowTips = this.faces.faceList.length === 0
                    this.faces.isLoading = false  //重置加载状态
                })
            },
            showPhotos() {
                //获取照片列表
                this.$axios({
                    method: 'get',
                    url: this.apiUrl + '/api/photo_list',
                    params: {
                        userid: localStorage.getItem('userid'),
                        call_mode: this.callMode,
                        album_uuid: this.albumUUID,
                        people_uuid: this.peopleUUID,
                        page: this.photos.page,
                        pagesize: this.photos.pageSize,
                    }
                }).then(response => {
                    this.photos.total = response.data.total  //总照片数
                    this.photos.pages = Math.ceil(this.photos.total / this.photos.pageSize)  //总页数
                    this.photos.photoList.push.apply(this.photos.photoList, response.data.list)
                    this.photos.isLoading = false  //重置加载状态
                })
            },
            showPreview(photo_uuid) {
                //显示大图预览
                this.deviceSupportUninstall()  //卸载键盘按键支持
                // 隐藏滚动条
                document.getElementsByTagName('body')[0].classList.add("el-popup-parent--hidden")
                this.$router.push({
                    name: this.$route.name,
                    params: {photo_uuid: photo_uuid}
                })
            },
            closePreview() {
                //关闭大图预览
                this.deviceSupportInstall()  //注册键盘按键支持
                document.getElementsByTagName('body')[0].classList.remove("el-popup-parent--hidden")
            },
            clickImage(face_uuid, photo_uuid) {
                //点击照片时发生，按下shift等修饰键时不会触发单击事件
                if (this.showChkToolBar || this.checkList.length > 0) {  //当前有照片被选中了
                    let idx = this.checkList.indexOf(face_uuid)
                    if (idx === -1) {
                        this.checkList.push(face_uuid)
                    } else {
                        this.checkList.splice(idx, 1)
                    }
                } else {
                    //在pick模式下，面孔不是预览，而是选中
                    if (this.callMode === 'pick_face') {
                        this.checkList.push(face_uuid)
                    }
                    else {
                        this.showPreview(photo_uuid)  //没有照片被选中时，点击照片就是预览
                    }
                }
            },
            multiSelectFaces(e, face_uuid, photo_uuid) {
                //连续选择照片，当按下shift时才触发该事件
                if (e.target.tagName === 'SPAN') return  //因为原生click事件会执行两次，第一次在label标签上，第二次在input标签上，故此处理
                //当起始照片uuid不存在时，不执行连续选择操作
                if (this.lastSelectedUUID != null) {
                    let startIdx = this.faces.faceList.findIndex(t => t.uuid === this.lastSelectedUUID)
                    let endIdx = this.faces.faceList.findIndex(t => t.uuid === face_uuid)
                    let startIndex = endIdx > startIdx ? startIdx : endIdx
                    let endIndex = endIdx > startIdx ? endIdx : startIdx
                    if (this.checkList.indexOf(face_uuid) === -1) {  //当前照片处于未选中状态，执行连续选中操作
                        for (let i = startIndex; i <= endIndex; i++) {
                            if (this.checkList.indexOf(this.faces.faceList[i].uuid) === -1) {
                                this.checkList.push(this.faces.faceList[i].uuid)
                            }
                        }
                    } else {  //当前照片处于选中状态，执行连续取消选中操作
                        for (let i = startIndex; i <= endIndex; i++) {
                            let idx = this.checkList.indexOf(this.faces.faceList[i].uuid)
                            if (idx !== -1) {
                                this.checkList.splice(idx, 1)
                            }
                        }
                    }
                } else {  //当用户在照片上按住shift键单击时，映射到点击照片的动作
                    if (e.target.tagName === 'IMG')
                        this.clickImage(face_uuid, photo_uuid)
                }
            },
            unselectFace() {
                //放弃选择
                this.checkList = []
                this.$store.commit('cancelSelectFace', {action: false})  //重置vuex的值
                this.$store.commit('pickFaceMode', {show: false})  //重置移动设备下是否进入选择面孔模式
            },
            getPeople() {
                //获取指定的人物信息
                this.$axios({
                    method: 'get',
                    url: this.apiUrl + '/api/people_get',
                    params: {
                        uuid: this.peopleUUID
                    }
                }).then(response => {
                    const result = response.data
                    this.people = result
                })
            },
            removeFromPeople() {
                // 从人物中移除
                this.deviceSupportUninstall()
                this.$confirm('从人物中移除并不会删除照片，您仍然可以在相册中找到该内容', '要移除这些面孔吗？', {
                    confirmButtonText: '移除',
                    cancelButtonText: '取消',
                    type: 'warning',
                    closeOnClickModal: false,
                }).then(() => {
                    this.$axios({
                        method: 'post',
                        url: this.apiUrl + '/api/people_remove_name',
                        data: {
                            filter_type: 'face',
                            people_uuid: this.peopleUUID,
                            face_list: this.checkList,
                        }
                    }).then(() => {
                        let msg = '已将' + this.checkList.length + ' 个面孔从人物中移除'
                        this.$message({
                            message: msg,
                            type: 'success',
                        })
                        this.$store.commit('refreshFace', {action: 'delete', list: this.checkList})
                        this.unselectFace()
                    })
                }).catch(() => {
                    this.deviceSupportInstall()
                });
            },
        }
    }
</script>

<style scoped>
    .image-slot { /*图片加载失败时的插槽*/
        margin-right: 5px;
        width: 100%;
        padding-top: 50%;
        padding-bottom: 50%;
        line-height: 100%;
        background: #f5f7fa;
        color: #909399;
        font-size: 22px;
        text-align: center;
    }

    .div-images { /*瀑布流照片*/
        display: flex;
        flex-wrap: wrap;
        padding: 10px 0 10px 10px;
    }

    .div-images::after {
        content: '';
        flex-grow: 999999999;
    }

    .div-img {  /*面孔容器*/
        position: relative;
        width: 160px;
        height: 160px;
        flex-grow: 160;
        margin: 0 10px 10px 0;
    }
    @media only screen and (max-width: 767px) {
        .div-img {
            width: 110px;
            height: 110px;
            flex-grow: 110;
        }
    }

    .img-face {  /*面孔*/
        display: block;
        width: 100%;
        height: 100%;
        border-radius: 8px;
        cursor: pointer;
    }
    .btn-checkbox { /*选择控件*/
        visibility: hidden; /*控件默认隐藏*/
        position: absolute;
        top: 8px;
        left: 8px;
    }
    .btn-checkbox >>> .el-checkbox__label { /*选择控件的文本*/
        display: none;
    }
    .btn-checkbox >>> .el-checkbox__inner { /*选择控件的外观*/
        width: 20px;
        height: 20px;
        border: 2px solid #FFF;
        border-radius: 50%;
        background-color: rgba(0, 0, 0, .1);
    }
    .btn-checkbox >>> .el-checkbox__inner:after { /*选择控件内勾的外观*/
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
    @media (any-hover: hover) {
        .div-img:hover >>> .el-checkbox,
        .div-img:hover .btn-preview { /*鼠标移上去时显示勾选控件和预览按钮*/
            visibility: visible;
        }
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
    .btn-feature {  /*面孔右上角的特征标志*/
        position: absolute;
        left: 8px;
        bottom: 8px;
        z-index: 1;
        color: #fff;
        font-size: 24px;
        -webkit-text-stroke: 1px rgba(0, 0, 0, .1);
    }
    .chk-toolbar { /*选中照片后的工具栏*/
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 64px;
        padding: 0 14px;
        background-color: #fff;
        box-shadow: 0 1px 2px 0 rgba(60, 64, 67, .30), 0 2px 6px 2px rgba(60, 64, 67, .15);
        z-index: 2;
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
    .chk-title {  /*选择工具栏标题*/
        font-size: 1.125rem;
        padding-left: 7px;
    }
    .btn-toolbar {  /*选中工具栏上的文字按钮*/
        margin-top: 12px;
    }
    /*移动端进入选择模式后显示某些控件*/
    @media (any-hover: none) {
        .show-always {
            visibility: visible;
        }
    }
</style>