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
            <el-popover placement="bottom-end" class="hidden-xs-only">
                <label>尺寸：</label>
                <el-slider v-model="imgHeight" :min="110" :max="300" :show-tooltip="false" style="width: 200px"></el-slider>
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
        <el-checkbox-group v-model="checkGroupList" class="images-wrap"
                           :class="{'show-checkbox': checkList.length > 0}">
            <el-row v-for="(photoGroup, index) of photoListGroup" :key="index" style="margin-right: 5px">
                <el-checkbox v-if="multiple" class="chk-group" :label="photoGroup.timestamp"
                             @change="selectPhotoGroup(photoGroup.timestamp)">
                </el-checkbox>
                <span v-if="!multiple" class="chk-group-label">{{photoGroup.timestamp}}</span>
                <el-checkbox-group v-model="checkList">
                    <!--瀑布流样式的照片列表-->
                    <div class="div-images">
                        <div v-for="img of photoGroup.list"
                             :key="img.uuid"
                             class="div-img"
                             :class="{'chk-checked': checkList.indexOf(img.uuid) !== -1,
                                      'chk-last-checked': lastSelectedUUID === img.uuid}"
                             :style="{'width': img.width * imgHeight / img.height + 'px',
                                      'flex-grow':img.width * imgHeight / img.height}">
                            <i :style="{'padding-bottom': img.height / img.width * 100 + '%', 'display':'block'}"></i>
                            <!--叠加选择框-->
                            <el-checkbox v-if="multiple" :label="img.uuid"
                                         @change="selectPhoto(img.uuid, photoGroup.timestamp)"
                                         @click.native.shift.exact="multiSelectPhotos($event, img.uuid, photoGroup.timestamp)"
                                         class="btn-checkbox"
                                         :class="{'show-always':showChkToolBar}">
                            </el-checkbox>
                            <!--叠加预览按钮-->
                            <i class="el-icon-zoom-in btn-preview" @click="showPreview(img.uuid)"
                               :class="{'show-always':showChkToolBar}"></i>
                            <el-image :src="apiUrl + '/' + img.path_thumbnail_s + '/' + img.name"
                                      lazy
                                      :alt="img.name"
                                      @click.exact="clickImage(img.uuid, photoGroup.timestamp)"
                                      @click.shift.exact="multiSelectPhotos($event, img.uuid, photoGroup.timestamp)"
                                      style="cursor: pointer;">
                                <div slot="error">
                                    <div class="image-slot">
                                        <i class="el-icon-picture-outline"></i>
                                    </div>
                                </div>
                            </el-image>
                            <!--叠加显示位置信息和照片说明-->
                            <div v-if="img.comments||img.address__address" class="div-img-comments"
                                 @click="clickImage(img.uuid, photoGroup.timestamp)">
                                <el-tooltip placement="bottom-start" :content="img.address__address">
                                    <div slot="content">
                                        <span v-show="img.address__poi_name">{{img.address__poi_name}} - </span>
                                        <span>{{img.address__address}}</span>
                                    </div>
                                    <i v-if="img.address__address" class="el-icon-location-outline btn-location"></i>
                                </el-tooltip>
                                <el-tooltip placement="bottom-start" :content="img.comments">
                                    <span>{{img.comments}}</span>
                                </el-tooltip>
                            </div>
                            <!--叠加收藏标志-->
                            <div v-if="img.is_favorited" class="btn-flag">
                                <i v-if="img.is_favorited" class="el-icon-star-on"></i>
                            </div>
                        </div>
                    </div>
                </el-checkbox-group>
            </el-row>
        </el-checkbox-group>
        <!--选中照片后的工具栏-->
        <el-row class="chk-toolbar" v-show="showChkToolBar">
            <el-col :span="12">
                <i class="el-icon-close" style="color: #202124;" @click="unselectPhoto"></i>
                <span v-show="checkList.length>0" class="chk-title">
                    <span class="hidden-xs-only">选择了 {{checkList.length}} 张照片</span>
                    <span class="hidden-sm-and-up">{{checkList.length}} 张</span>
                </span>
                <span v-show="checkList.length===0" class="chk-title">选择照片</span>
            </el-col>
            <el-col v-show="checkList.length>0" :span="12" style="text-align: right">
                <div v-if="['photo','favorites'].indexOf(callMode)>-1">
                    <i class="el-icon-folder-add" title="添加到影集" @click="showAlbumTree"></i>
                    <i class="el-icon-delete" title="删除" @click="trashPhoto"></i>
                    <el-dropdown trigger="click" @command="handCommand" placement="bottom-end">
                        <i class="el-icon-more" title="更多选项" style="transform: rotate(90deg);"></i>
                        <el-dropdown-menu slot="dropdown">
                            <el-dropdown-item icon="el-icon-download" command="download">下载</el-dropdown-item>
                            <el-dropdown-item v-if="noFavorited" icon="el-icon-star-on" command="favorites">收藏</el-dropdown-item>
                            <el-dropdown-item v-if="!noFavorited" icon="el-icon-star-off" command="unfavorites">从收藏夹中移除</el-dropdown-item>
                            <el-dropdown-item icon="el-icon-date" command="modify_datetime">修改日期和时间</el-dropdown-item>
                            <el-dropdown-item icon="el-icon-location-outline" command="modify_location">修改位置信息
                            </el-dropdown-item>
                        </el-dropdown-menu>
                    </el-dropdown>
                </div>
                <div v-if="callMode==='album'">
                    <i class="el-icon-folder-delete" title="从影集中移除" @click="removeFromAlbum"></i>
                    <i class="el-icon-delete" title="删除" @click="trashPhoto"></i>
                    <el-dropdown trigger="click" @command="handCommand" placement="bottom-end">
                        <i class="el-icon-more" title="更多选项" style="transform: rotate(90deg);"></i>
                        <el-dropdown-menu slot="dropdown">
                            <el-dropdown-item icon="el-icon-download" command="download">下载</el-dropdown-item>
                            <el-dropdown-item v-if="noFavorited" icon="el-icon-star-on" command="favorites">收藏</el-dropdown-item>
                            <el-dropdown-item v-if="!noFavorited" icon="el-icon-star-off" command="unfavorites">从收藏夹中移除</el-dropdown-item>
                            <el-dropdown-item icon="el-icon-date" command="modify_datetime">修改日期和时间</el-dropdown-item>
                            <el-dropdown-item icon="el-icon-location-outline" command="modify_location">修改位置信息
                            </el-dropdown-item>
                        </el-dropdown-menu>
                    </el-dropdown>
                </div>
                <div v-if="callMode==='people'">
                    <i class="el-icon-document-remove" title="从人物中移除" @click="removeFromPeople"></i>
                    <i class="el-icon-delete" title="删除" @click="trashPhoto"></i>
                    <el-dropdown trigger="click" @command="handCommand" placement="bottom-end">
                        <i class="el-icon-more" title="更多选项" style="transform: rotate(90deg);"></i>
                        <el-dropdown-menu slot="dropdown">
                            <el-dropdown-item icon="el-icon-download" command="download">下载</el-dropdown-item>
                            <el-dropdown-item v-if="noFavorited" icon="el-icon-star-on" command="favorites">收藏</el-dropdown-item>
                            <el-dropdown-item v-if="!noFavorited" icon="el-icon-star-off" command="unfavorites">从收藏夹中移除</el-dropdown-item>
                            <el-dropdown-item icon="el-icon-folder-add" command="add_to_album">添加到影集</el-dropdown-item>
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
                   width="340px"
                   :close-on-click-modal="false"
                   :destroy-on-close="true"
                   @closed="deviceSupportInstall">
            <el-tree class="album-tree" ref="albumTree" :lazy="true" :load="loadAlbumTree" node-key="uuid"
                     :props="{label:'name'}"
                     :default-expand-all="false"
                     :expand-on-click-node="true"
                     :highlight-current="true">
                <div slot-scope="{ data }">
                    <div class="album-tree-cover" :style="{'background-image':'url('+apiUrl+'/'+data.cover_path+'/'+data.cover_name+')'}"></div>
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
                <el-button @click="isShowAddToAlbumDialog = false" size="small">取消</el-button>
                <el-button type="primary" size="small" @click="addToAlbum">确定</el-button>
            </span>
        </el-dialog>
        <!--修改日期和时间对话框-->
        <el-dialog title="修改日期和时间" :visible.sync="isShowModifyDateTimeDialog" width="320px"
                   :close-on-click-modal="false" @closed="deviceSupportInstall">
            <el-date-picker type="datetime" v-model="photoDateTime" default-time="8:00:00"
                            placeholder="选择日期时间" format="yyyy-MM-dd HH:mm"
                            value-format="yyyy-MM-dd HH:mm:ss" style="width: 280px"></el-date-picker>
            <span slot="footer">
                <el-button size="small" @click="isShowModifyDateTimeDialog=false">取消</el-button>
                <el-button type="primary" size="small" @click="modifyDateTime">确定</el-button>
            </span>
        </el-dialog>
        <!--修改位置信息对话框-->
        <el-dialog title="修改位置信息" :visible.sync="isShowModifyLocationDialog" width="320px" top="80px"
                   :close-on-click-modal="false" @closed="deviceSupportInstall">
            <p v-if="photoLocationList.length>0" style="font-weight: 600; margin-bottom: 10px">选中的照片中包含以下位置信息：</p>
            <div v-if="photoLocationList.length>0" class="location-list">
                <p v-for="(address,index) of photoLocationList" :key="index" style="margin-bottom: 5px">
                    <span>{{address}}</span>
                </p>
            </div>
            <el-select v-model="photoLocation" :remote="true" :filterable="true" placeholder="输入地理位置"
                       :remote-method="getLocationList" :loading="locationLoading" :clearable="true"
                       @clear="locationOptions=[]"
                       style="width: 280px">
                <el-option v-for="item in locationOptions" :key="item.uid"
                           :label="item.name"
                           :value="item.location.lat+','+item.location.lng+','+item.name">
                    <span style="float: left">{{ item.name }}</span>
                    <span style="float: right; color: #8492a6; font-size: 13px">{{ item.province + item.city + item.district }}</span>
                </el-option>
            </el-select>
            <span slot="footer">
                <el-button v-if="photoLocationList.length>0" type="danger" size="small" @click="modifyLocation">清除位置信息</el-button>
                <el-button size="small" @click="isShowModifyLocationDialog=false">取消</el-button>
                <el-button type="primary" size="small" @click="checkLocation">确定</el-button>
            </span>
        </el-dialog>
    </div>
</template>

<script>
    import AlbumList from "./AlbumList";
    import UploadFile from "./MainHeader/UploadFile";
    import {rafThrottle} from "element-ui/src/utils/util";
    import {off, on} from "element-ui/src/utils/dom";
    export default {
        name: "PhotoList",
        components: {AlbumList, UploadFile},
        data() {
            return {
                imgHeight: 200,  //照片的高度
                albumName: '',  //当callMode为album时，影集的名称
                photoList: [],  //照片列表
                checkList: [],  //选中的照片列表
                photoListGroup: [],  //分组后的照片列表
                isShowTips: false,  //是否显示上传提示
                groupType: 'day',  //分组类型 day, month, year
                checkGroupList: [],  //选中的分组列表
                multiple: true,  //是否允许多选
                lastSelectedUUID: null,  //最后一次选中的照片uuid
                noFavorited: false,  //选中列表中是否含有未收藏的内容，用于切换工具栏菜单
                isShowAddToAlbumDialog: false,  //是否显示添加到影集对话框
                isShowModifyDateTimeDialog: false,  //是否显示修改日期时间对话框
                photoDateTime: null,  //照片的拍摄时间
                isShowModifyLocationDialog: false,  //是否显示修改位置信息对话框
                photoLocation: '',  //照片的拍摄地点
                photoLocationList: [],  //选中照片中包含的位置列表
                locationLoading: false,  //位置选择框是否正在从远程获取数据
                locationOptions: [],  //地点检索的结果
            }
        },
        props: {
            callMode: {  //调用模式
                type: String,
                //photo:照片; album:影集; trash:回收站; pick:挑选照片到影集; favorites:收藏夹; cover:设置影集封面
                //people:人物; feature:挑选人物特征
                default: 'photo'
            },
            albumUUID: {  //当调用模式为album时，必须指定影集uuid
                type: String,
                default: 'none'
            },
            albumPhotoList: {  //影集中的照片列表
                type: Array,
                default: () => []
            },
            peopleUUID: {  //当调用模式为people和feature时，必须指定人物uuid
                type: String,
                default: 'none'
            },
            onPick: {
                type: Function,
                default: () => {}
            },
        },
        computed: {
            //重要：vuex中定义的数据一定要在这里绑定，放在data()里视图不会更新
            apiUrl() {
                return this.$store.state.apiUrl  //后台api调用地址
            },
            refreshPhoto() {
                return this.$store.state.refreshPhoto  //是否刷新照片列表
            },
            cancelSelectPhoto() {
                return this.$store.state.cancelSelectPhoto  //是否取消已选中的照片
            },
            pickPhotoMode() {
                return this.$store.state.pickPhotoMode  //移动设备下是否进入选择照片模式
            },
            showChkToolBar() {  //是否显示选择工具栏
                if (['pick', 'cover', 'feature'].indexOf(this.callMode) === -1 && this.checkList.length > 0) {
                    return true
                } else {
                    if (this.pickPhotoMode) {
                        return true
                    } else {
                        return false
                    }
                }
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
                if (['cover','feature'].indexOf(this.callMode) > -1) {
                    this.onPick(this.checkList)
                }
                //返回选中列表中是否包含未收藏的照片
                if (['photo','album','favorites','people'].indexOf(this.callMode) > -1) {
                    this.noFavorited = false
                    for (let item of val) {
                        let photo = this.photoList.find(t => t.uuid === item)
                        if (!photo.is_favorited) {
                            this.noFavorited = true
                            break
                        }
                    }
                }
            },
            groupType() {
                //分组类型改变时重新载入照片
                this.creatPhotoGroup()
            },
            albumPhotoList(val) {
                //AddPhotoToAlbum组件载入时会异步获取影集照片列表并传入，所以这里要监视该属性的变化
                if (this.callMode === 'pick') {
                    for (let item of val) {
                        this.checkList.push(item)  //将当前影集中的照片默认选中
                    }
                }
            },
        },
        mounted() {
            if (this.callMode === 'album') {
                this.getAlbum()
            }
            this.showPhotos()  //获取并显示照片列表
            if (['pick','cover','feature'].indexOf(this.callMode) === -1)
                this.deviceSupportInstall()  //注册键盘按键支持
            if (['cover','feature'].indexOf(this.callMode) > -1)  //设置影集封面、选择人物特征模式下，只允许单选
                this.multiple = false
            this.setImgHeight()
            window.addEventListener('resize', this.listenResize)
        },
        beforeDestroy() {
            if (['pick','cover','feature'].indexOf(this.callMode) === -1) {
                this.deviceSupportUninstall()  //卸载键盘按键支持
            }
            window.removeEventListener('resize', this.listenResize)
            this.$store.commit('pickPhotoMode', {show: false})  //重置移动设备下是否进入选择照片模式
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
            getAlbum() {
                //获取指定的影集信息
                this.$axios({
                    method: 'get',
                    url: this.apiUrl + '/api/album_get',
                    params: {
                        uuid: this.albumUUID
                    }
                }).then(response => {
                    const result = response.data
                    this.albumName = result.name
                })
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
                        people_uuid: this.peopleUUID,
                    }
                }).then(response => {
                    this.photoList = response.data
                    //为照片列表增加分组信息
                    for (let index in this.photoList) {
                        this.photoList[index]['timestamp'] = this.getGroupLabel(this.photoList[index]['exif_datetime'])
                    }
                    this.creatPhotoGroup()  //创建照片分组
                    //从vuex中读取上次选中的照片列表
                    let lastCheckList = this.$store.state.photoCheckList
                    if (lastCheckList.length > 0) {
                        this.checkList = lastCheckList
                        this.$store.commit('setPhotoCheckList', {'checkList': []})
                    }
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
                //记录当前选中的列表，便于从预览页面返回时重新将其选中
                this.$store.commit('setPhotoCheckList', {'checkList': this.checkList})
                this.$router.push({
                    name: 'photo',
                    params: {
                        uuid: uuid,
                        callMode: this.callMode,
                        albumUUID: this.albumUUID,
                        peopleUUID: this.peopleUUID,
                    }
                })
            },
            clickImage(uuid, timestamp) {
                //点击照片时发生，按下shift等修饰键时不会触发单击事件
                if (this.showChkToolBar) {  //当前有照片被选中了
                    let idx = this.checkList.indexOf(uuid)
                    if (idx === -1) {
                        if (!this.multiple)  //单选模式下先清空已选择的照片
                            this.checkList = []
                        this.checkList.push(uuid)
                    } else {
                        this.checkList.splice(idx, 1)
                    }
                    this.selectPhoto(uuid, timestamp)  //触发照片选择事件
                } else {
                    switch (this.callMode) {
                        case 'pick':  //添加照片到影集、设置影集封面、选择人物特征模式下，点击照片不是预览，而是选中
                        case 'cover':
                        case 'feature':
                            this.checkList.push(uuid)
                            this.selectPhoto(uuid, timestamp)  //触发照片选择事件
                            break
                        default:
                            this.showPreview(uuid)  //没有照片被选中时，点击照片就是预览
                    }
                }
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
                this.$store.commit('pickPhotoMode', {show: false})  //重置移动设备下是否进入选择照片模式
            },
            multiSelectPhotos(e, uuid, timestamp) {
                if (!this.multiple) return false
                //连续选择照片，当按下shift时才触发该事件
                if (e.target.tagName === 'SPAN') return  //因为原生click事件会执行两次，第一次在label标签上，第二次在input标签上，故此处理
                //当起始照片uuid不存在时，不执行连续选择操作
                if (this.lastSelectedUUID != null) {
                    let startIdx = this.photoList.findIndex(t => t.uuid === this.lastSelectedUUID)
                    let endIdx = this.photoList.findIndex(t => t.uuid === uuid)
                    let startIndex = endIdx > startIdx ? startIdx : endIdx
                    let endIndex = endIdx > startIdx ? endIdx : startIdx
                    if (this.checkList.indexOf(uuid) === -1) {  //当前照片处于未选中状态，执行连续选中操作
                        for (let i = startIndex; i <= endIndex; i++) {
                            if (this.checkList.indexOf(this.photoList[i].uuid) === -1) {
                                this.checkList.push(this.photoList[i].uuid)
                                this.selectPhoto(this.photoList[i].uuid, this.photoList[i].timestamp)  //触发照片选择事件
                            }
                        }
                    } else {  //当前照片处于选中状态，执行连续取消选中操作
                        for (let i = startIndex; i <= endIndex; i++) {
                            let idx = this.checkList.indexOf(this.photoList[i].uuid)
                            if (idx !== -1) {
                                this.checkList.splice(idx, 1)
                                this.selectPhoto(this.photoList[i].uuid, this.photoList[i].timestamp)  //触发照片选择事件
                            }
                        }
                    }
                } else {  //当用户在照片上按住shift键单击时，映射到点击照片的动作
                    if (e.target.tagName === 'IMG')
                        this.clickImage(uuid, timestamp)
                }
            },
            showAlbumTree() {
                //打开影集树形列表对话框
                this.deviceSupportUninstall()  //卸载键盘支持，避免与dialog的esc关闭冲突
                this.isShowAddToAlbumDialog = true
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
                let album_name = ''
                if (album_uuid)  //如果有节点被选中，获取节点名称
                    album_name = this.$refs.albumTree.getCurrentNode().name
                if (!album_uuid) {
                    this.$message({
                        message: '请选择要添加照片的影集',
                        type: 'error',
                    })
                    return false
                }
                this.isShowAddToAlbumDialog = false
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
                    this.$message({
                        message: msg,
                        type: 'success',
                    })
                })
            },
            removeFromAlbum() {
                //从影集中移除照片
                this.deviceSupportUninstall()
                this.$confirm('从影集中移除并不会删除照片，您仍然可以在相册中找到该内容', '要移除此内容吗？', {
                    confirmButtonText: '移除',
                    cancelButtonText: '取消',
                    type: 'warning',
                    closeOnClickModal: false,
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
                        this.$message({
                            message: msg,
                            type: 'success',
                        })
                        this.$store.commit('refreshPhoto', {show: true})  //刷新图片列表
                    })
                }).catch(() => {
                    this.deviceSupportInstall()
                });
            },
            trashPhoto() {
                //将照片移到回收站
                this.deviceSupportUninstall()
                this.$confirm('当需要的时候可以在回收站中恢复。', '确定要删除照片吗？', {
                    confirmButtonText: '移到回收站',
                    cancelButtonText: '取消',
                    type: 'warning',
                    closeOnClickModal: false,
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
                        this.$message({
                            message: msg,
                            type: 'success',
                        })
                        this.$store.commit('refreshPhoto', {show: true})  //刷新图片列表
                        this.$store.commit('refreshPhotoStatistics', {show: true})  //刷新照片库统计信息
                    })
                }).catch(() => {
                    this.deviceSupportInstall()
                });
            },
            restorePhoto() {
                //将照片从回收站恢复
                this.deviceSupportUninstall()
                this.$confirm('要恢复选中的内容吗？', {
                    confirmButtonText: '恢复',
                    cancelButtonText: '取消',
                    type: 'info',
                    closeOnClickModal: false,
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
                        this.$message({
                            message: msg,
                            type: 'success',
                        })
                        this.$store.commit('refreshPhoto', {show: true})  //刷新图片列表
                        this.$store.commit('refreshPhotoStatistics', {show: true})  //刷新照片库统计信息
                    })
                }).catch(() => {
                    this.deviceSupportInstall()
                });
            },
            removePhoto() {
                //永久删除照片
                this.deviceSupportUninstall()
                this.$confirm('内容一旦永久删除将无法恢复', '要永久删除选中的内容吗？', {
                    confirmButtonText: '删除',
                    cancelButtonText: '取消',
                    type: 'warning',
                    closeOnClickModal: false,
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
                        this.$message({
                            message: msg,
                            type: 'success',
                        })
                        this.$store.commit('refreshPhoto', {show: true})  //刷新图片列表
                    })
                }).catch(() => {
                    this.deviceSupportInstall()
                });
            },
            handCommand(command) {
                //更多选项
                switch (command) {
                    case 'download':
                        this.downloadPhoto()
                        break
                    case 'favorites':
                        this.addToFavorites()
                        break
                    case 'unfavorites':
                        this.removeFromFavorites()
                        break
                    case 'add_to_album':
                        this.showAlbumTree()
                        break
                    case 'modify_datetime':
                        this.showModifyDateTime()
                        break
                    case 'modify_location':
                        this.deviceSupportUninstall()  //卸载键盘按键支持，避免与dialog的esc关闭冲突
                        this.photoLocation = ''
                        this.locationOptions = []
                        this.isShowModifyLocationDialog = true
                        //获取选中照片中包含的位置列表
                        this.photoLocationList = []
                        for (let uuid of this.checkList) {
                            let photo = this.photoList.find(t => t.uuid === uuid)
                            if (photo && photo.address__address) {
                                let address = photo.address__address
                                if (photo.address__poi_name) {
                                    address = photo.address__poi_name + ' - ' + address
                                }
                                this.photoLocationList.push(address)
                            }
                        }
                        this.photoLocationList = Array.from(new Set(this.photoLocationList))  //数组去重复
                        break
                }
            },
            downloadPhoto() {
                //下载
                this.$message('下载功能还没做好呢:-)')
            },
            addToFavorites() {
                //收藏
                this.$axios({
                    method: 'post',
                    url: this.apiUrl + '/api/photo_favorites',
                    data: {
                        photo_list: this.checkList
                    }
                }).then(() => {
                    let msg = '已将' + this.checkList.length + ' 张照片添加到收藏夹'
                    this.unselectPhoto()
                    this.$message({
                        message: msg,
                        type: 'success',
                    })
                    this.$store.commit('refreshPhoto', {show: true})  //刷新图片列表
                })
            },
            removeFromFavorites() {
                //从收藏夹中移除
                this.$axios({
                    method: 'post',
                    url: this.apiUrl + '/api/photo_unfavorites',
                    data: {
                        photo_list: this.checkList
                    }
                }).then(() => {
                    let msg = '已将' + this.checkList.length + ' 张照片从收藏夹中移除'
                    this.unselectPhoto()
                    this.$message({
                        message: msg,
                        type: 'success',
                    })
                    this.$store.commit('refreshPhoto', {show: true})  //刷新图片列表
                })
            },
            showModifyDateTime() {
                //显示修改日期和时间对话框
                this.deviceSupportUninstall()  //卸载键盘按键支持，避免与dialog的esc关闭冲突
                if (this.checkList.length > 0) {
                    let uuid = this.checkList[0]
                    let photo = this.photoList.find(t => t.uuid === uuid)
                    this.photoDateTime = photo.exif_datetime
                }
                this.isShowModifyDateTimeDialog = true
            },
            modifyDateTime() {
                //修改日期和时间
                if (this.photoDateTime === null) {
                    this.$message({
                        message: '请输入正确的拍摄时间',
                        type: 'error',
                    })
                    return false
                }
                this.isShowModifyDateTimeDialog = false
                this.$axios({
                    method: 'post',
                    url: this.apiUrl + '/api/photo_set_datetime',
                    data: {
                        photo_list: this.checkList,
                        photo_datetime: this.photoDateTime,
                    }
                }).then(() => {
                    let msg = '成功将 ' + this.checkList.length + ' 张照片的拍摄时间修改为 ' + this.photoDateTime
                    this.unselectPhoto()
                    this.$message({
                        message: msg,
                        type: 'success',
                    })
                    this.$store.commit('refreshPhoto', {show: true})  //刷新图片列表
                })
            },
            getLocationList(query) {
                //根据用户输入的关键字返回位置列表
                if (query !== '') {
                    this.locationLoading = true
                    this.$axios({
                        method: 'get',
                        url: this.apiUrl + '/api/photo_query_location',
                        params: {
                            query: query,  //查询的关键字
                        }
                    }).then(response => {
                        this.locationLoading = false
                        this.locationOptions = response.data
                    })
                }
            },
            checkLocation() {
                //检查输入的位置信息
                if (this.photoLocation === '') {
                    this.$message({
                        message: '请输入正确的地理位置',
                        type: 'error',
                    })
                    return false
                }
                this.modifyLocation()
            },
            modifyLocation() {
                //修改照片的位置信息
                this.isShowModifyLocationDialog = false
                this.$axios({
                    method: 'post',
                    url: this.apiUrl + '/api/photo_set_location',
                    data: {
                        photo_list: this.checkList,
                        location: this.photoLocation,
                    }
                }).then(response => {
                    let res = response.data
                    let msg
                    if (res.address) {
                        msg = '成功将 ' + this.checkList.length + ' 张照片的位置信息修改为 ' + res.address
                    }
                    else {
                        msg = '成功删除了 ' + this.checkList.length + ' 张照片的位置信息'
                    }
                    this.unselectPhoto()
                    this.$message({
                        message: msg,
                        type: 'success',
                    })
                    this.$store.commit('refreshPhoto', {show: true})  //刷新图片列表
                })
            },
            removeFromPeople() {
                // 从人物中移除
                this.deviceSupportUninstall()
                this.$confirm('从人物中移除并不会删除照片，您仍然可以在相册中找到该内容', '要移除此内容吗？', {
                    confirmButtonText: '移除',
                    cancelButtonText: '取消',
                    type: 'warning',
                    closeOnClickModal: false,
                }).then(() => {
                    this.$axios({
                        method: 'post',
                        url: this.apiUrl + '/api/people_remove_face',
                        data: {
                            filter_type: 'photo',
                            people_uuid: this.peopleUUID,
                            photo_list: this.checkList,
                        }
                    }).then(() => {
                        let msg = '已将' + this.checkList.length + ' 张照片从人物中移除'
                        this.unselectPhoto()
                        this.$message({
                            message: msg,
                            type: 'success',
                        })
                        this.$store.commit('refreshPhoto', {show: true})  //刷新图片列表
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
        width: 200px;
        height: 200px;
        line-height: 200px;
        background: #f5f7fa;
        color: #909399;
        font-size: 22px;
        text-align: center;
    }
    .images-wrap, .div-images { /*瀑布流照片*/
        display: flex;
        flex-wrap: wrap;
    }
    .images-wrap {
        padding-left: 10px;
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
    .chk-group >>> .el-checkbox__input { /*分组标签的复选框默认隐藏*/
        margin-top: -2px;  /*修正分组选择勾选框的位置偏移*/
        margin-left: -10px;
        width: 0;
        visibility: hidden;
        transition: width 0.2s;
    }
    .chk-group:hover >>> .el-checkbox__input {  /*鼠标移到分组标签上时，显示复选框*/
        margin-left: 0;
        width: 20px;
        visibility: visible;
    }
    .show-checkbox >>> .el-checkbox__input {  /*当选择了照片时，所有的勾选控件都显示出来*/
        margin-left: 0;
        width: 20px;
        visibility: visible;
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

    .chk-group-label {  /*单选模式下的分组标签*/
        display: inline-block;
        font-size: 14px;
        margin-top: 15px;
        margin-bottom: 10px
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
    .div-img-comments {  /*照片的说明文字*/
        position: absolute;
        bottom: 0;
        padding: 5px;
        width: 100%;
        font-size: 12px;
        color: #fff;
        background: linear-gradient(rgba(0,0,0,0),rgba(0,0,0,.1),rgba(0,0,0,.5)); /*渐变色背景*/
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
        cursor: pointer;
    }
    @media (hover: none) {
        .div-img-comments {
            visibility: hidden;
        }
    }
    @media (hover: hover) {
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
    .btn-flag {  /*照片右上角的收藏和人物特征标志*/
        position: absolute;
        top: 0;
        right: 0;
        width: 100%;
        height: 33px;
        line-height: 33px;
        padding-right: 5px;
        text-align: right;
        color: #fff;
        background: linear-gradient(rgba(0,0,0,.5),rgba(0,0,0,.1)); /*渐变色背景*/
        font-size: 22px;
    }
    .btn-location {  /*照片的位置信息*/
        margin-right: 5px;
        color: #fff;
        font-size: 14px;
        cursor: pointer;
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
        z-index: 4;
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
    .btn-toolbar {
        margin-top: 12px;
        margin-right: 15px;
    }
    .div-group-size {
        position: fixed;
        right: 20px;
        z-index: 1;
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

    .location-list {  /*已存在的位置列表*/
        padding: 0 10px;
        margin-bottom: 20px;
        max-height: 150px;
        overflow: auto;
    }
    .location-list::-webkit-scrollbar {
        width: 6px;
    }
    .location-list::-webkit-scrollbar-track {
        background-color: #fff;
    }
    .location-list::-webkit-scrollbar-thumb {
        border-radius:5px;
        background-color: #cdcdcd;
    }
    .location-list p {
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
    }
    /*移动端进入选择模式后显示某些控件*/
    .show-always {
        visibility: visible;
    }
</style>