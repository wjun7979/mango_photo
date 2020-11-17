<template>
    <div>
        <div ref="viewer-wrapper" class="viewer-wrapper"
             :style="{'margin-right': viewerWrapperMargin}">
            <div class="viewer-mask"></div>
            <!-- 关闭按钮 -->
            <span class="viewer-btn viewer-close" @click="close">
                <i class="el-icon-back"></i>
            </span>
            <span v-show="currentImg.comments" class="viewer-comments"
                  @click="setPhotoComments">{{currentImg.comments}}</span>
            <!--工具栏-->
            <div class="viewer-toolbar">
                <div v-if="['photo','favorites','people','place'].indexOf(callMode)>-1">
                    <i class="el-icon-s-operation hidden-mobile-only" title="修改" @click="showModify"></i>
                    <i class="el-icon-warning-outline" title="信息" @click="showInfo"></i>
                    <i v-if="currentImg.is_favorited" class="el-icon-star-on" title="收藏" @click="removeFromFavorites"></i>
                    <i v-if="!currentImg.is_favorited" class="el-icon-star-off" title="收藏" @click="addToFavorites"></i>
                    <el-dropdown trigger="click" @command="handCommand" placement="bottom-end">
                        <i class="el-icon-more" title="更多选项" style="transform: rotate(90deg);"></i>
                        <el-dropdown-menu slot="dropdown">
                            <el-dropdown-item icon="el-icon-download" command="download">下载</el-dropdown-item>
                            <el-dropdown-item icon="el-icon-folder-add" command="add_to_album">添加到影集</el-dropdown-item>
                            <el-dropdown-item icon="el-icon-delete" command="trash">移到回收站</el-dropdown-item>
                        </el-dropdown-menu>
                    </el-dropdown>
                </div>
                <div v-if="callMode === 'album'">
                    <i class="el-icon-s-operation hidden-mobile-only" title="修改" @click="showModify"></i>
                    <i class="el-icon-warning-outline" title="信息" @click="showInfo"></i>
                    <i v-if="currentImg.is_favorited" class="el-icon-star-on" title="收藏" @click="removeFromFavorites"></i>
                    <i v-if="!currentImg.is_favorited" class="el-icon-star-off" title="收藏" @click="addToFavorites"></i>
                    <el-dropdown trigger="click" @command="handCommand" placement="bottom-end">
                        <i class="el-icon-more" title="更多选项" style="transform: rotate(90deg);"></i>
                        <el-dropdown-menu slot="dropdown">
                            <el-dropdown-item icon="el-icon-download" command="download">下载</el-dropdown-item>
                            <el-dropdown-item icon="el-icon-plus" command="add_to_album">添加到影集</el-dropdown-item>
                            <el-dropdown-item icon="el-icon-folder-delete" command="remove_from_album">从影集中移除</el-dropdown-item>
                            <el-dropdown-item icon="el-icon-notebook-1" command="set_album_cover">设为影集封面</el-dropdown-item>
                            <el-dropdown-item icon="el-icon-delete" command="trash">移到回收站</el-dropdown-item>
                        </el-dropdown-menu>
                    </el-dropdown>
                </div>
                <div v-if="callMode === 'trash'">
                    <i class="el-icon-warning-outline" title="信息" @click="showInfo"></i>
                    <i class="el-icon-delete" title="永久删除" @click="removePhoto"></i>
                    <i class="el-icon-time" title="恢复" @click="restorePhoto"></i>
                </div>
                <div v-if="['pick','cover','feature','pick_face'].indexOf(callMode)>-1">
                    <i class="el-icon-warning-outline" title="信息" @click="showInfo"></i>
                </div>
            </div>
            <!-- 上一张、下一张 -->
            <template v-if="!isSingle">
                <span class="viewer-btn viewer-prev hidden-mobile-only"
                      @click="prev">
                    <i class="el-icon-arrow-left"/>
                </span>
                <span class="viewer-btn viewer-next hidden-mobile-only"
                      @click="next">
                    <i class="el-icon-arrow-right"/>
                </span>
            </template>
            <!-- 动作按钮 -->
            <div class="viewer-btn viewer-actions">
                <div class="viewer-actions-inner">
                    <i class="el-icon-zoom-out" @click="handleActions('zoomOut')"></i>
                    <i class="el-icon-zoom-in" @click="handleActions('zoomIn')"></i>
                    <i class="el-image-viewer__actions__divider"></i>
                    <i :class="mode.icon" @click="toggleMode"></i>
                    <i class="el-image-viewer__actions__divider"></i>
                    <i class="el-icon-refresh-left" @click="handleActions('anticlocelise')"></i>
                    <i class="el-icon-refresh-right" @click="handleActions('clocelise')"></i>
                </div>
            </div>
            <!--大图显示-->
            <div class="viewer-canvas">
                <img class="viewer-img" ref="img" :src="currentImg.url" alt="" :style="imgStyle"
                     @load="handleImgLoad" @error="handleImgError" @mousedown="handleMouseDown"
                     @touchstart="handleTouchStart" @touchmove="handleTouchMove"
                     @touchend="handleTouchEnd" @doubleTap="handleDblclick" @dblclick="handleDblclick"/>
            </div>
        </div>
        <!--修改侧边栏-->
        <div class="viewer-side" v-show="isShowModifySide">
            <el-row>
                <i class="el-icon-close side-btn-close" @click="closeModify"/>
            </el-row>
        </div>
        <!--信息侧边栏-->
        <div class="viewer-side" v-show="isShowInfoSide">
            <el-row class="side-close">
                <i class="el-icon-close side-btn-close" @click="closeInfo"/>
                <span style="font-size: 20px">信息</span>
            </el-row>
            <div style="padding-top: 70px">
                <!--照片说明-->
                <el-row v-if="['photo','album','favorites','people','place'].indexOf(callMode)>-1" class="side-href"
                        @click.native="setPhotoComments">
                    <el-col :span="24" style="border-bottom: solid 1px #8c939d">
                        <span v-if="photoInfo.comments">{{photoInfo.comments}}</span>
                        <span v-else>添加说明</span>
                    </el-col>
                </el-row>
                <el-row v-if="['trash','pick','cover'].indexOf(callMode)>-1 && photoInfo.comments">
                    <el-col :span="24">
                        <span>{{photoInfo.comments}}</span>
                    </el-col>
                </el-row>
                <el-row v-show="photoFaces.length>0" style="font-size: 12px">人物</el-row>
                <el-row v-show="photoFaces.length>0" :gutter="15" style="padding: 15px 30px 0 30px">
                    <el-col v-for="(face, index) of this.photoFaces" :key="index" :span="6" style="margin-bottom: 15px">
                        <div style="position:relative; padding-top: 100%">
                            <img :src="apiUrl+'/'+face.path_thumbnail+'/'+face.name" alt=""
                                 :class="{'face-img':true, 'face-img-unknow':!face.people_uuid}"/>
                            <!--叠加特征标志-->
                            <i v-if="face.feature_token" class="el-icon-user-solid face-feature"></i>
                        </div>
                        <el-dropdown v-if="['photo','album','favorites','people','pick','pick_face','place'].indexOf(callMode)>-1"
                                     trigger="click"
                                     placement="bottom-start" @command="faceCommand" style="cursor: pointer">
                            <span class="face-name" v-if="face.people_name">
                                {{face.people_name}}<i class="el-icon-arrow-down el-icon--right"></i>
                            </span>
                            <span class="face-name" v-else>Ta是谁<i class="el-icon-arrow-down el-icon--right"></i>
                            </span>
                            <el-dropdown-menu slot="dropdown">
                                <el-dropdown-item v-if="!face.people_name"
                                                  :command="beforeFaceCommand(face.uuid, face.people_uuid, 'setName')">
                                    添加姓名
                                </el-dropdown-item>
                                <el-dropdown-item v-if="face.people_name"
                                                  :command="beforeFaceCommand(face.uuid, face.people_uuid, 'removeName')">
                                    Ta不是{{face.people_name}}
                                </el-dropdown-item>
                                <el-dropdown-item v-if="photoFaces.length===1 && face.people_name && face.feature_token===null"
                                                  :command="beforeFaceCommand(face.uuid, face.people_uuid, 'addFeature')">
                                    将Ta作为人物特征
                                </el-dropdown-item>
                                <el-dropdown-item v-if="photoFaces.length===1 && face.people_name && face.feature_token"
                                                  :command="beforeFaceCommand(face.uuid, face.people_uuid, 'removeFeature')">
                                    取消作为人物特征
                                </el-dropdown-item>
                                <el-dropdown-item v-if="face.people_name"
                                                  :command="beforeFaceCommand(face.uuid, face.people_uuid, 'setCover')">
                                    设为人物封面
                                </el-dropdown-item>
                                <el-dropdown-item :command="beforeFaceCommand(face.uuid, face.people_uuid, 'removeFace')">
                                    删除该面孔
                                </el-dropdown-item>
                            </el-dropdown-menu>
                        </el-dropdown>
                        <div v-if="['trash','cover','feature'].indexOf(callMode)>-1">
                            <span class="face-name" v-if="face.people_name">{{face.people_name}}</span>
                            <span class="face-name" v-else>Ta是谁</span>
                        </div>
                    </el-col>
                </el-row>
                <el-row v-show="photoAlbums.length>0" style="font-size: 12px">影集</el-row>
                <el-row v-for="(album, index) of this.photoAlbums" :key="index">
                    <el-col :span="4">
                        <div class="side-album-cover"
                             :style="{'background-image':'url('+apiUrl+'/'+album.cover_path+'/'+album.cover_name+')'}"></div>
                    </el-col>
                    <el-col :span="20">
                        <p>{{album.name}}</p>
                        <p style="font-size: 14px; color: #8c939d" v-if="album.photos === 0">没有内容</p>
                        <p class="album-tree-photos" v-else>
                            <span>{{$common.dateFormat(album.min_time,'yyyy年MM月dd日')}}至{{$common.dateFormat(album.max_time,'yyyy年MM月dd日')}}</span>
                            <span style="margin-left: 10px">{{album.photos}}项</span>
                        </p>
                    </el-col>
                </el-row>
                <el-row style="font-size: 12px">详情</el-row>
                <el-row :class="{'side-href':['photo','album','favorites','people','place'].indexOf(callMode)>-1}" v-if="photoInfo.exif_datetime"
                        @click.native="showModifyDateTime">
                    <el-col :span="3">
                        <i class="el-icon-date" style="font-size: 24px; line-height: 44px"></i>
                    </el-col>
                    <el-col :span="18">
                        <p>{{$common.dateFormat(photoInfo.exif_datetime, 'yyyy年M月d日')}}</p>
                        <p style="font-size: 14px; color: #8c939d">
                            <span>{{$common.dateFormat(photoInfo.exif_datetime, '周w')}}，</span>
                            <span>{{$common.dateFormat(photoInfo.exif_datetime, 'hh:mm')}}</span>
                        </p>
                    </el-col>
                    <el-col :span="3" style="text-align: right">
                        <i v-show="['photo','album'].indexOf(callMode)>-1" class="el-icon-edit" style="font-size: 16px; line-height: 44px; color: #8c939d"></i>
                    </el-col>
                </el-row>
                <el-row v-show="photoInfo.name">
                    <el-col :span="3">
                        <i class="el-icon-picture" style="font-size: 24px; line-height: 44px"></i>
                    </el-col>
                    <el-col :span="21">
                        <p :title="photoInfo.name" class="side-title">{{photoInfo.name_original}}</p>
                        <p style="font-size: 14px; color: #8c939d">
                            <span style="margin-right: 10px;">{{photoInfo.width}} × {{photoInfo.height}}</span>
                            <span>{{$common.bytesToSize(photoInfo.size)}}</span>
                        </p>
                    </el-col>
                </el-row>
                <el-row v-show="photoInfo.exif_make">
                    <el-col :span="3">
                        <i class="el-icon-camera-solid" style="font-size: 24px; line-height: 44px"></i>
                    </el-col>
                    <el-col :span="21">
                        <p class="side-title">{{photoInfo.exif_make}} {{photoInfo.exif_model}}</p>
                        <p style="font-size: 14px; color: #8c939d">
                            <span style="margin-right: 10px;">ƒ/{{photoInfo.exif_fnumber}}</span>
                            <span style="margin-right: 10px;">{{photoInfo.exif_exposuretime}}</span>
                            <span style="margin-right: 10px;">{{photoInfo.exif_focallength}}mm</span>
                            <span>ISO{{photoInfo.exif_isospeedratings}}</span>
                        </p>
                    </el-col>
                </el-row>
                <!--位置信息-->
                <el-row :class="{'side-href':['photo','album','favorites','people','place'].indexOf(callMode)>-1}"
                        @click.native="showModifyLocation">
                    <el-col :span="3">
                        <i class="el-icon-location" style="font-size: 24px;"></i>
                    </el-col>
                    <el-col :span="18">
                        <p v-if="photoInfo.photo_address">
                            <span v-if="photoInfo.photo_poi_name">{{photoInfo.photo_poi_name}} - </span>
                            <span>{{photoInfo.photo_address}}</span>
                        </p>
                        <p v-else>这张照片是在哪里拍摄的？</p>
                    </el-col>
                    <el-col :span="3" style="text-align: right">
                        <i v-show="['photo','album'].indexOf(callMode)>-1" class="el-icon-edit" style="font-size: 16px; color: #8c939d"></i>
                    </el-col>
                </el-row>
                <el-row style="padding: 0" v-show="photoInfo.photo_address">
                    <div id="map-core" style="height: 360px"></div>
                    <a :href="'http://api.map.baidu.com/marker?location='+photoInfo.photo_lat+','+photoInfo.photo_lng+'&output=html&src=wjun.mango_photo'"
                       target="_blank" title="在百度地图上显示照片位置信息">
                        <img src="../assets/images/bmap_copyright_logo.png" alt=""
                             style="position: absolute; left: 5px; bottom: 10px;"/>
                    </a>
                </el-row>
            </div>
        </div>
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
            <p v-if="photoInfo.photo_address" style="margin-bottom: 20px">
                <span v-if="photoInfo.photo_poi_name">{{photoInfo.photo_poi_name}} - </span>
                <span>{{photoInfo.photo_address}}</span>
            </p>
            <el-autocomplete v-model="photoLocationName" placeholder="输入地理位置" :fetch-suggestions="getLocationList"
                             value-key="name" :clearable="true" :trigger-on-focus="true" @select="selectLocation"
                             @clear="photoLocationValue=''" style="width: 280px"></el-autocomplete>
            <span slot="footer">
            <el-button v-if="photoInfo.photo_address" type="danger" size="small"
                       @click="modifyLocation">清除位置信息</el-button>
            <el-button size="small" @click="isShowModifyLocationDialog=false">取消</el-button>
            <el-button type="primary" size="small" @click="checkLocation">确定</el-button>
        </span>
        </el-dialog>
        <!--指定人物对话框-->
        <el-dialog title="Ta是谁" :visible.sync="isShowPeopleDialog" width="320px"
                   :close-on-click-modal="false" @closed="deviceSupportInstall">
            <el-autocomplete v-model="currFace.name" placeholder="请输入人物姓名" :fetch-suggestions="getPeopleList"
                             value-key="name" :clearable="true" :trigger-on-focus="true"
                             style="width: 280px"></el-autocomplete>
            <el-checkbox v-if="photoFaces.length===1" v-model="setPeopleFeature" style="margin-top: 20px">
                <span>同时设为该人物的特征</span>
                <el-tooltip effect="light" placement="bottom-start" style="margin-left: 10px;">
                    <div slot="content" style="font-size: 14px; line-height: 22px">
                        人物有了特征照片之后，系统就能自动查找与之匹配的其他照片。<br/>
                        为了提高识别率，建议您选取清晰的正面照作为特征。<br/>
                    </div>
                    <i class="el-icon-info" style="font-size: 16px"></i>
                </el-tooltip>
            </el-checkbox>
            <span slot="footer">
                <el-button size="small" @click="isShowPeopleDialog=false">取消</el-button>
                <el-button type="primary" size="small" @click="setPeopleName">确定</el-button>
            </span>
        </el-dialog>
    </div>
</template>

<script>
    import {on, off} from 'element-ui/src/utils/dom';
    import {rafThrottle, isFirefox} from 'element-ui/src/utils/util';
    import BMap from 'BMap'
    const Mode = {
        CONTAIN: {
            name: 'contain',
            icon: 'el-icon-full-screen'
        },
        ORIGINAL: {
            name: 'original',
            icon: 'el-icon-c-scale-to-original'
        }
    };
    const mousewheelEventName = isFirefox() ? 'DOMMouseScroll' : 'mousewheel';
    export default {
        name: "Photo",
        data() {
            return {
                albumName: '',  //影集标题
                previewListOrder: [],  //大图预览列表
                index: 0,  //当前预览图编号
                currentImg: {},  //当前预览图
                loading: false,  //当前是否于图片加载状态
                mode: Mode.CONTAIN,  //显示模式 CONTAIN:适应窗口,ORIGINAL:原始
                transform: {
                    scale: 1,
                    deg: 0,
                    offsetX: 0,
                    offsetY: 0,
                    enableTransition: false
                },
                isShowInfoSide: false,  //是否显示信息侧边栏
                isShowModifySide: false,  //是否显示修改侧边栏
                viewerWrapperMargin: '0px',  //最外层容器右边距
                photoInfo: {},  //当前照片的详细信息
                photoAlbums: [],  //当前照片所属的影集列表
                photoFaces: [],  //当前照片中的人脸列表
                baiduMap: null,  //百度地图对象
                isShowAddToAlbumDialog: false,  //是否显示添加到影集对话框
                isShowModifyDateTimeDialog: false,  //是否显示修改日期时间对话框
                photoDateTime: null,  //照片的拍摄时间
                isShowModifyLocationDialog: false,  //是否显示修改位置信息对话框
                photoLocationName: '', //照片的拍摄地点（输入框中显示的内容）
                photoLocationValue: '', //照片的拍摄地点（提交给后台的内容）
                locationLoading: false,  //位置选择框是否正在从远程获取数据
                locationOptions: [],  //地点的检索结果
                isShowPeopleDialog: false,  //是否显示指定人物对话框
                currFace: {  //当前操作的人脸对象
                    face_uuid: '',
                    name: ''
                },
                setPeopleFeature: false,  //是否同时设为该人物的特征
                peopleOptions: [],  //人物的检索结果
                touchStart: {  //手指在屏幕滑动时记录一些坐标
                    offsetX: 0,
                    offsetY: 0,
                    startX: 0,  //单点触摸的起始坐标
                    startY: 0,
                    startTouches: [],  //双指触摸时的起始坐标
                    touchTime: 0,  //点击时的时间
                },
            }
        },
        props: {
            uuid: {
                type: String
            },
            callMode: {  //调用模式
                type: String,
                default: 'photo'
            },
            photoList: {  //照片列表
                type: Array,
                default: () => []
            },
            albumUUID: {  //当调用模式为album时，必须指定影集uuid
                type: String,
                default: 'none'
            },
            peopleUUID: {  //当调用模式为people和feature时，必须指定人物uuid
                type: String,
                default: 'none'
            },
            onClose: {
                type: Function,
                default: () => {}
            },
        },
        watch: {
            index: {
                handler: function () {
                    this.currentImg = this.previewListOrder[this.index]
                    this.reset();
                    if (this.isShowInfoSide) {
                        this.getPhotoInfo()  //重新获取照片详细信息
                        this.getPhotoAlbums()  //重新获取照片所属的影集列表
                        this.getPhotoFaces()  //重新获取照片中的人物
                    }
                }
            },
            currentImg() {
                this.$nextTick(() => {
                    const $img = this.$refs.img;
                    if (!$img.complete) {
                        this.loading = true;
                    }
                });
            }
        },
        computed: {
            apiUrl() {
                return this.$store.state.apiUrl  //后台api调用地址
            },
            isSingle() {  //是否只有一张图片
                return this.previewListOrder.length <= 1
            },
            imgStyle() {
                const {scale, deg, offsetX, offsetY, enableTransition} = this.transform
                const style = {
                    transform: `scale(${scale}) rotate(${deg}deg)`,
                    transition: enableTransition ? 'transform .3s' : '',
                    'margin-left': `${offsetX}px`,
                    'margin-top': `${offsetY}px`
                };
                if (this.mode === Mode.CONTAIN) {
                    style.maxWidth = style.maxHeight = '100%'
                }
                return style;
            },
            infoSideStatus() {
                return this.$store.state.infoSideStatus  //信息侧边栏的最后一次显示状态
            },
        },
        mounted() {
            if (this.callMode === 'album') {
                this.getAlbum()
            }
            this.getPreviewList()  //获取预览列表
            this.deviceSupportInstall()
            this.$refs['viewer-wrapper'].focus()
        },
        beforeDestroy() {
            this.onClose()
            this.deviceSupportUninstall()  //卸载键盘按键支持
        },
        methods: {
            deviceSupportInstall() {
                //注册键盘按键、鼠标滚动、多点触摸支持
                //键盘按键
                this._keyDownHandler = rafThrottle(e => {
                    const keyCode = e.keyCode
                    switch (keyCode) {
                        case 27:  //ESC退出
                            this.close()
                            break
                        case 32:  //SPACE切换显示模式:1:1或合适缩放
                            this.toggleMode()
                            break
                        case 37:  //LEFT_ARROW上一张
                            this.prev()
                            break
                        case 38:  //UP_ARROW放大
                            this.handleActions('zoomIn')
                            break
                        case 39:  //RIGHT_ARROW 下一张
                            this.next()
                            break
                        case 40:  //DOWN_ARROW缩小
                            this.handleActions('zoomOut')
                            break
                    }
                })
                //鼠标滚动
                this._mouseWheelHandler = rafThrottle(e => {
                    const delta = e.wheelDelta ? e.wheelDelta : -e.detail
                    if (delta > 0) {
                        this.handleActions('zoomIn', {
                            zoomRate: 0.2,
                            enableTransition: false
                        })
                    } else {
                        this.handleActions('zoomOut', {
                            zoomRate: 0.2,
                            enableTransition: false
                        })
                    }
                })
                on(document, 'keydown', this._keyDownHandler)
                on(this.$refs.img, mousewheelEventName, this._mouseWheelHandler)
            },
            deviceSupportUninstall() {
                //卸载键盘按键和鼠标滚动支持
                off(document, 'keydown', this._keyDownHandler)
                off(this.$refs.img, mousewheelEventName, this._mouseWheelHandler)
                this._keyDownHandler = null
                this._mouseWheelHandler = null
            },
            handleImgLoad() {
                //图片加载完毕时
                this.loading = false;
            },
            handleImgError(e) {
                //图片加载失败时
                this.loading = false;
                e.target.alt = '加载失败';
            },
            handleDblclick() {
                //双击照片
                this.reset()
                this.mode = Mode.CONTAIN
            },
            handleMouseDown(e) {
                //鼠标左键按下时，拖动图片
                if (this.loading || e.button !== 0) return

                const {offsetX, offsetY} = this.transform
                const startX = e.pageX
                const startY = e.pageY
                this._dragHandler = rafThrottle(ev => {
                    if (this.checkPhotoSize()) return  //照片比屏幕小时不允许拖动
                    this.transform.offsetX = offsetX + ev.pageX - startX
                    this.transform.offsetY = offsetY + ev.pageY - startY
                });
                on(document, 'mousemove', this._dragHandler)
                on(document, 'mouseup', () => {
                    off(document, 'mousemove', this._dragHandler)
                })

                e.preventDefault()
            },
            handleTouchStart(e) {
                //手指触摸屏幕时触发，即使已经有手指在屏幕上也会触发
                this.touchStart.startTouches = e.touches  //记录触摸点的数量和坐标
                if (e.touches && e.touches.length === 1) {  //单点触摸时记录相关坐标
                    this.touchStart.offsetX = this.transform.offsetX
                    this.touchStart.offsetY = this.transform.offsetY
                    this.touchStart.startX = e.touches[0].pageX
                    this.touchStart.startY = e.touches[0].pageY
                }
            },
            handleTouchMove(e) {
                //单指滑动
                if (this.touchStart.startTouches.length === 1 && e.touches && e.touches.length === 1) {
                    if (!this.checkPhotoSize()) {  //照片比屏幕大时，判断为拖动操作
                        this.transform.offsetX = this.touchStart.offsetX + (e.touches[0].pageX - this.touchStart.startX) * 2
                        this.transform.offsetY = this.touchStart.offsetY + (e.touches[0].pageY - this.touchStart.startY) * 2
                    }
                    else {  //当照片比屏幕小时，禁止系统事件，防止在浏览大图时手指滑动操作会带动列表滚动
                        e.preventDefault()
                    }
                }
                //双指缩放
                if (e.touches && e.touches.length >= 2) {
                    e.preventDefault()  //禁止系统事件，防止双指缩放时会同时移动照片
                    //得到缩放比例
                    let now = e.touches
                    let scale = this.$common.getDistance(now[0], now[1]) / this.$common.getDistance(this.touchStart.startTouches[0], this.touchStart.startTouches[1])
                    if (scale > 1) {
                        this.handleActions('zoomIn', {
                            zoomRate: 0.1,
                            enableTransition: false
                        })
                    } else {
                        this.handleActions('zoomOut', {
                            zoomRate: 0.1,
                            enableTransition: false
                        })
                    }
                }
            },
            handleTouchEnd(e) {
                if (this.touchStart.startTouches.length === 1) {  //单点触摸
                    if (this.checkPhotoSize()) {  //照片比屏幕小时，判断为滑动操作
                        let endX = e.changedTouches[0].pageX;
                        let endY = e.changedTouches[0].pageY;
                        let direction = this.$common.getDirection(this.touchStart.startX, this.touchStart.startY, endX, endY)
                        switch (direction) {
                            case 2:
                                this.close()
                                break;
                            case 3:
                                this.next()
                                break;
                            case 4:
                                this.prev()
                                break;
                        }
                    }
                    else {  //照片比屏幕大时，判断是否为双击操作
                        let nowTime = new Date()
                        if (nowTime.getTime() - this.touchStart.touchTime <= 300) {
                            this.handleDblclick()
                        }
                        this.touchStart.touchTime = nowTime.getTime()
                    }
                }
                if (this.touchStart.startTouches.length >= 2) {  //多点触摸
                    e.preventDefault()
                }
            },
            checkPhotoSize() {
                //检查照片实际大小是否小于屏幕尺寸
                let realWidth = this.$refs.img.getBoundingClientRect().width
                let realHeight = this.$refs.img.getBoundingClientRect().height
                let screenWidth = document.documentElement.clientWidth
                let screenHeight = document.documentElement.clientHeight
                if (realWidth <= screenWidth && realHeight <= screenHeight)
                    return true
                else
                    return false
            },
            reset() {
                //重置图片缩放比例和方向
                this.transform = {
                    scale: 1,
                    deg: 0,
                    offsetX: 0,
                    offsetY: 0,
                    enableTransition: false
                }
            },
            toggleMode() {
                if (this.loading) return;
                const modeNames = Object.keys(Mode);
                const modeValues = Object.values(Mode);
                const index = modeValues.indexOf(this.mode);
                const nextIndex = (index + 1) % modeNames.length;
                this.mode = Mode[modeNames[nextIndex]];
                this.reset();
            },
            close() {
                this.$router.back()
            },
            prev() {  //上一张
                const len = this.previewListOrder.length
                this.index = (this.index - 1 + len) % len
                this.$router.replace({
                    name: this.$route.name,
                    params: {photo_uuid: this.previewListOrder[this.index].uuid}
                })
            },
            next() {  //下一张
                const len = this.previewListOrder.length
                this.index = (this.index + 1) % len
                this.$router.replace({
                    name: this.$route.name,
                    params: {photo_uuid: this.previewListOrder[this.index].uuid}
                })
            },
            handleActions(action, options = {}) {  //对图片进行缩放和旋转操作
                if (this.loading) return;
                const {zoomRate, enableTransition} = {
                    zoomRate: 0.2,
                    enableTransition: true,
                    ...options
                };
                const {transform} = this;
                switch (action) {
                    case 'zoomOut':
                        if (!this.checkPhotoSize()) {  //照片比屏幕小时不允许缩小
                            transform.scale = parseFloat((transform.scale - zoomRate).toFixed(3))
                        }
                        else {
                            this.reset()
                            this.mode = Mode.CONTAIN
                        }
                        break;
                    case 'zoomIn':
                        if (transform.scale < 5) {  //控制最大缩放比例
                            transform.scale = parseFloat((transform.scale + zoomRate).toFixed(3))
                        }
                        break
                    case 'anticlocelise':  //左旋转
                        // transform.deg -= rotateDeg
                        this.$axios({
                            method: 'post',
                            url: this.apiUrl + '/api/photo_rotate',
                            data: {
                                photo_uuid: this.currentImg.uuid,
                                angle: 90
                            }
                        }).then(response => {
                            let res = response.data
                            this.previewListOrder[this.index].name = res.file_name
                            this.previewListOrder[this.index].url = this.apiUrl + '/' + res.path_thumbnail_l + '/' + res.file_name
                            this.reset()
                            //更新前端列表
                            let photo = this.photoList.find(t => t.uuid === this.currentImg.uuid)
                            photo.name = res.file_name
                            photo.width = res.width
                            photo.height = res.height
                            this.$store.commit('refreshPhoto', {action: 'update', list: photo, refreshPhotoGroup: false})
                        })
                        break;
                    case 'clocelise':  //右旋转
                        // transform.deg += rotateDeg
                        this.$axios({
                            method: 'post',
                            url: this.apiUrl + '/api/photo_rotate',
                            data: {
                                photo_uuid: this.currentImg.uuid,
                                angle: 270
                            }
                        }).then(response => {
                            let res = response.data
                            this.previewListOrder[this.index].name = res.file_name
                            this.previewListOrder[this.index].url = this.apiUrl + '/' + res.path_thumbnail_l + '/' + res.file_name
                            this.reset()
                            //更新前端列表
                            let photo = this.photoList.find(t => t.uuid === this.currentImg.uuid)
                            photo.name = res.file_name
                            photo.width = res.width
                            photo.height = res.height
                            this.$store.commit('refreshPhoto', {action: 'update', list: photo, refreshPhotoGroup: false})
                        })
                        break;
                }
                transform.enableTransition = enableTransition;
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
            getPreviewList() {
                // 生成大图预览列表
                let previewList = []
                for (let item of this.photoList) {
                    previewList.push({
                        'uuid': item.uuid,
                        'name': item.name,
                        'url': this.apiUrl + '/' + item.path_thumbnail_l + '/' + item.name,
                        'comments': item.comments,
                        'is_favorited': item.is_favorited,
                    })
                }
                let index = previewList.findIndex(t => t.uuid === this.uuid)  //获取即将预览的照片索引
                //根据索引对预览数组重新排序
                this.previewListOrder = previewList.slice(index).concat(previewList.slice(0, index))
                this.currentImg = this.previewListOrder[0]
                //如果用户上一次操作时，信息侧边栏是打开状态的，则恢复它
                if (this.infoSideStatus) {
                    this.showInfo()
                }
            },
            showModify() {  //显示修改侧边栏
                this.isShowInfoSide = false
                this.isShowModifySide = !this.isShowModifySide
                this.viewerWrapperMargin = this.isShowModifySide ? '360px' : '0px'
            },
            closeModify() {  //关闭修改侧边栏
                this.isShowModifySide = false
                this.viewerWrapperMargin = '0px'
            },
            showInfo() {  //显示信息侧边栏
                this.isShowModifySide = false
                this.isShowInfoSide = !this.isShowInfoSide
                //保存信息侧边栏当前的打开状态，便于下次进入页面时恢复
                this.$store.commit('setInfoSideStatus',{status: this.isShowInfoSide})
                this.viewerWrapperMargin = this.isShowInfoSide ? '360px' : '0px'
                if (this.isShowInfoSide) {
                    this.getPhotoInfo()  //获取照片详细信息
                    this.getPhotoAlbums()  //获取照片所属的影集列表
                    this.getPhotoFaces()  //获取照片中的人脸列表
                }
            },
            closeInfo() {  //关闭信息侧边栏
                this.isShowInfoSide = false
                this.$store.commit('setInfoSideStatus',{status: false})
                this.viewerWrapperMargin = '0px'
                // 将照片信息和所属影集列表恢复到初始值，便于信息侧边栏恢复到初始状态，避免打开侧边栏时会闪现上一张照片信息的问题
                this.photoInfo = {}
                this.photoAlbums = []
            },
            getPhotoInfo() {
                //获取当前照片的详细信息
                this.$axios({
                    method: 'get',
                    url: this.apiUrl + '/api/photo_get_info',
                    params: {
                        photo_uuid: this.currentImg.uuid
                    }
                }).then(response => {
                    const res = response.data
                    this.photoInfo = res
                    //将当前位置定位到地图
                    this.$nextTick(function () {
                        if (res.photo_lng && res.photo_lat) {
                            this.baiduMap = new BMap.Map("map-core", {enableMapClick:false})
                            // let top_left_navigation = new BMap.NavigationControl()  //左上角，添加默认缩放平移控件
                            this.baiduMap.addControl(new BMap.NavigationControl())  //左上角，添加默认缩放平移控件
                            //this.baiduMap.enableScrollWheelZoom(true)
                            // this.baiduMap.centerAndZoom(new BMap.Point(116.331398, 39.897445), 15)
                            this.baiduMap.clearOverlays()  //清除标注
                            let new_point = new BMap.Point(res.photo_lng, res.photo_lat)
                            this.baiduMap.centerAndZoom(new_point, 15)
                            let marker = new BMap.Marker(new_point)  // 创建标注
                            this.baiduMap.addOverlay(marker)  // 将标注添加到地图中
                            this.baiduMap.panTo(new_point)  //定位到标注点
                        }
                    })
                })
            },
            getPhotoAlbums() {
                //获取指定照片所属的影集列表
                this.$axios({
                    method: 'get',
                    url: this.apiUrl + '/api/photo_get_albums',
                    params: {
                        photo_uuid: this.currentImg.uuid
                    }
                }).then(response => {
                    this.photoAlbums = response.data
                })
            },
            getPhotoFaces() {
                //获取指定照片中的人脸列表
                this.$axios({
                    method: 'get',
                    url: this.apiUrl + '/api/photo_get_faces',
                    params: {
                        photo_uuid: this.currentImg.uuid
                    }
                }).then(response => {
                    this.photoFaces = response.data
                })
            },
            addToFavorites() {
                //收藏
                this.$axios({
                    method: 'post',
                    url: this.apiUrl + '/api/photo_favorites',
                    data: {
                        photo_list: [this.currentImg.uuid]
                    }
                }).then(() => {
                    this.$message({
                        message: '已将照片添加到收藏夹',
                        type: 'success',
                    })
                    this.currentImg.is_favorited = true
                    //更新前端列表
                    let photo = this.photoList.find(t => t.uuid === this.currentImg.uuid)
                    photo.is_favorited = true
                    this.$store.commit('refreshPhoto', {action: 'update', list: photo, refreshPhotoGroup: false})
                })
            },
            removeFromFavorites() {
                //取消收藏
                this.$axios({
                    method: 'post',
                    url: this.apiUrl + '/api/photo_unfavorites',
                    data: {
                        photo_list: [this.currentImg.uuid]
                    }
                }).then(() => {
                    this.$message({
                        message: '已将照片从收藏夹中移除',
                        type: 'success',
                    })
                    this.currentImg.is_favorited = false
                    if (this.callMode === 'favorites') {
                        let photo_uuid = this.currentImg.uuid
                        this.$store.commit('refreshPhoto', {action: 'delete', list: [photo_uuid]})
                        //从当前预览列表中移除当前照片
                        this.previewListOrder.splice(this.index, 1)
                        if (this.previewListOrder.length > 0) {
                            if (this.index > this.previewListOrder.length - 1)
                                this.index = 0
                            this.currentImg = this.previewListOrder[this.index]
                            if (this.isShowInfoSide) {
                                this.getPhotoInfo()  //重新获取照片详细信息
                                this.getPhotoAlbums()  //重新获取照片所属的影集列表
                                this.getPhotoFaces()  //重新获取照片中的人物
                            }
                        }
                        else
                            this.close()  //否则关闭预览
                    }
                    else {
                        //更新前端列表
                        let photo = this.photoList.find(t => t.uuid === this.currentImg.uuid)
                        photo.is_favorited = false
                        this.$store.commit('refreshPhoto', {action: 'update', list: photo, refreshPhotoGroup: false})
                    }
                })
            },
            handCommand(command) {
                //更多选项
                switch (command) {
                    case 'download':
                        this.downloadPhoto()
                        break
                    case 'add_to_album':
                        this.deviceSupportUninstall()
                        this.isShowAddToAlbumDialog = true
                        break
                    case 'remove_from_album':
                        this.removeFromAlbum()
                        break
                    case 'set_album_cover':
                        this.setAlbumCover()
                        break
                    case 'trash':
                        this.trashPhoto()
                        break
                }
            },
            downloadPhoto() {
                //下载
                this.$message('下载功能还没做好呢:-)')
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
                        photo_list: [this.currentImg.uuid]
                    }
                }).then(() => {
                    let msg = '成功将照片添加到影集 [' + album_name + '] 中'
                    this.$message({
                        message: msg,
                        type: 'success',
                    })
                    //如果信息侧边栏处于打开状态，则刷新该图片所属的影集列表
                    if (this.isShowInfoSide) {
                        this.getPhotoAlbums()
                    }
                })
            },
            removeFromAlbum() {
                //从影集中移除照片
                this.deviceSupportUninstall()
                this.$confirm('您仍然可以在相册中找到该内容', '要移除此内容吗？', {
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
                            photo_list: [this.currentImg.uuid]
                        }
                    }).then(() => {
                        let msg = '照片已从影集 [' + this.albumName + '] 中移除'
                        this.$message({
                            message: msg,
                            type: 'success',
                        })
                        let photo_uuid = this.currentImg.uuid
                        this.$store.commit('refreshPhoto', {action: 'delete', list: [photo_uuid]})
                        //从当前预览列表中移除当前照片
                        this.previewListOrder.splice(this.index, 1)
                        if (this.previewListOrder.length > 0) {
                            if (this.index > this.previewListOrder.length - 1)
                                this.index = 0
                            this.currentImg = this.previewListOrder[this.index]
                            if (this.isShowInfoSide) {
                                this.getPhotoInfo()  //重新获取照片详细信息
                                this.getPhotoAlbums()  //重新获取照片所属的影集列表
                                this.getPhotoFaces()  //重新获取照片中的人物
                            }
                        }
                        else
                            this.close()  //否则关闭预览
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
                            photo_list: [this.currentImg.uuid]
                        }
                    }).then(() => {
                        let msg = '已将照片移到回收站'
                        this.$message({
                            message: msg,
                            type: 'success',
                        })
                        let photo_uuid = this.currentImg.uuid
                        this.$store.commit('refreshPhoto', {action: 'delete', list: [photo_uuid]})
                        //从当前预览列表中移除当前照片
                        this.previewListOrder.splice(this.index, 1)
                        if (this.previewListOrder.length > 0) {
                            if (this.index > this.previewListOrder.length - 1)
                                this.index = 0
                            this.currentImg = this.previewListOrder[this.index]
                            if (this.isShowInfoSide) {
                                this.getPhotoInfo()  //重新获取照片详细信息
                                this.getPhotoAlbums()  //重新获取照片所属的影集列表
                                this.getPhotoFaces()  //重新获取照片中的人物
                            }
                        }
                        else
                            this.close()  //否则关闭预览
                    })
                }).catch(() => {
                    this.deviceSupportInstall()
                });
            },
            setAlbumCover() {
                //设为影集封面
                this.$axios({
                    method: 'post',
                    url: this.apiUrl + '/api/album_set_cover',
                    data: {
                        album_uuid: this.albumUUID,
                        photo_uuid: this.currentImg.uuid
                    }
                }).then(() => {
                    let msg = '影集 [' + this.albumName + '] 的封面设置成功'
                    this.$message({
                        message: msg,
                        type: 'success',
                    })
                    //如果信息侧边栏处于打开状态，则刷新该图片所属的影集列表
                    if (this.isShowInfoSide) {
                        this.getPhotoAlbums()
                    }
                })
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
                            photo_list: [this.currentImg.uuid]
                        }
                    }).then(() => {
                        let msg = '照片已被成功删除'
                        this.$message({
                            message: msg,
                            type: 'success',
                        })
                        let photo_uuid = this.currentImg.uuid
                        this.$store.commit('refreshPhoto', {action: 'delete', list: [photo_uuid]})
                        //从当前预览列表中移除当前照片
                        this.previewListOrder.splice(this.index, 1)
                        if (this.previewListOrder.length > 0) {
                            if (this.index > this.previewListOrder.length - 1)
                                this.index = 0
                            this.currentImg = this.previewListOrder[this.index]
                            if (this.isShowInfoSide) {
                                this.getPhotoInfo()  //重新获取照片详细信息
                                this.getPhotoAlbums()  //重新获取照片所属的影集列表
                                this.getPhotoFaces()  //重新获取照片中的人物
                            }
                        }
                        else
                            this.close()  //否则关闭预览
                    })
                }).catch(() => {
                    this.deviceSupportInstall()
                });
            },
            restorePhoto() {
                //将照片从回收站恢复
                this.$axios({
                    method: 'post',
                    url: this.apiUrl + '/api/photo_restore',
                    data: {
                        photo_list: [this.currentImg.uuid]
                    }
                }).then(() => {
                    let msg = '照片已成功恢复'
                    this.$message({
                        message: msg,
                        type: 'success',
                    })
                    let photo_uuid = this.currentImg.uuid
                    this.$store.commit('refreshPhoto', {action: 'delete', list: [photo_uuid]})
                    //从当前预览列表中移除当前照片
                    this.previewListOrder.splice(this.index, 1)
                    if (this.previewListOrder.length > 0) {
                        if (this.index > this.previewListOrder.length - 1)
                            this.index = 0
                        this.currentImg = this.previewListOrder[this.index]
                        if (this.isShowInfoSide) {
                            this.getPhotoInfo()  //重新获取照片详细信息
                            this.getPhotoAlbums()  //重新获取照片所属的影集列表
                            this.getPhotoFaces()  //重新获取照片中的人物
                        }
                    } else
                        this.close()  //否则关闭预览
                })
            },
            setPhotoComments() {
                //为照片添加说明文字
                this.deviceSupportUninstall()  //卸载键盘按键支持
                this.$prompt('请输入照片说明：', {
                    inputValue: this.currentImg.comments,
                    closeOnClickModal: false,
                    callback: ((action, instance) => {
                        if (action === 'confirm') {
                            this.$axios({
                                method: 'post',
                                url: this.apiUrl + '/api/photo_set_comments',
                                data: {
                                    photo_uuid: this.currentImg.uuid,
                                    comments: instance.inputValue,
                                }
                            }).then(() => {
                                this.currentImg.comments = instance.inputValue
                                this.previewListOrder[this.index].comments = instance.inputValue
                                if (instance.inputValue) {
                                    this.$message({
                                        message: '成功为照片添加了说明 [' + instance.inputValue + ']',
                                        type: 'success',
                                    })
                                }
                                else {
                                    this.$message({
                                        message: '成功清除了照片的说明',
                                        type: 'success',
                                    })
                                }
                                this.photoInfo.comments = instance.inputValue
                                //更新前端列表
                                let photo = this.photoList.find(t => t.uuid === this.currentImg.uuid)
                                photo.comments = instance.inputValue
                                this.$store.commit('refreshPhoto', {action: 'update', list: photo, refreshPhotoGroup: false})
                            })
                        }
                        this.deviceSupportInstall()  //恢复键盘按键支持
                    })
                })
            },
            showModifyDateTime() {
                //显示修改日期和时间对话框
                if (['photo','album','favorites','people','place'].indexOf(this.callMode) === -1)
                    return false
                this.deviceSupportUninstall()  //卸载键盘按键支持，避免与dialog的esc关闭冲突
                this.photoDateTime = this.photoInfo.exif_datetime
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
                        photo_list: [this.photoInfo.uuid],
                        photo_datetime: this.photoDateTime,
                    }
                }).then(() => {
                    this.getPhotoInfo()  //刷新当前图片信息
                    let msg = '成功将照片的拍摄时间修改为 ' + this.photoDateTime
                    this.$message({
                        message: msg,
                        type: 'success',
                    })
                    //更新前端列表
                    let photo = this.photoList.find(t => t.uuid === this.currentImg.uuid)
                    photo.exif_datetime = this.photoDateTime
                    this.$store.commit('refreshPhoto', {action: 'update', list: photo, refreshPhotoGroup: true})
                })
            },
            showModifyLocation(){
                //显示修改位置信息对话框
                if (['photo','album','favorites','people','place'].indexOf(this.callMode) === -1)
                    return false
                this.deviceSupportUninstall()
                this.photoLocationName = ''
                this.photoLocationValue = ''
                this.locationOptions = []
                this.isShowModifyLocationDialog = true
            },
            getLocationList(query, cb) {
                //根据用户输入的关键字返回位置列表
                this.photoLocationValue = ''
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
                        //查询类似于“湖北省”这样的地点时，返回结果中没有经纬度信息，过滤掉
                        this.locationOptions = []
                        for (let item of response.data) {
                            if (item.location) {
                                item.name = item.name + '(' + item.province + item.city + item.district + ')'
                                this.locationOptions.push(item)
                            }
                        }
                        cb(this.locationOptions)
                    })
                }
                else {
                    cb([])
                }
            },
            selectLocation(item) {
                //选择位置
                this.photoLocationValue = item.location.lat+','+item.location.lng+','+item.name
            },
            checkLocation() {
                //检查输入的位置信息
                if (this.photoLocationName === '' || this.photoLocationValue === '') {
                    this.$message({
                        message: '请输入并选择正确的地理位置',
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
                        photo_list: [this.photoInfo.uuid],
                        location: this.photoLocationValue,
                    }
                }).then(response => {
                    this.getPhotoInfo()  //刷新当前图片信息
                    let res = response.data
                    let msg
                    if (res.address) {
                        msg = '成功将照片的位置信息修改为 ' + res.address
                    }
                    else {
                        msg = '成功删除了照片的位置信息'
                    }
                    this.$message({
                        message: msg,
                        type: 'success',
                    })
                    //更新前端列表
                    let photo = this.photoList.find(t => t.uuid === this.currentImg.uuid)
                    photo.address__poi_name = res.poi_name
                    photo.address__address = res.address
                    this.$store.commit('refreshPhoto', {action: 'update', list: photo, refreshPhotoGroup: false})
                    //在地点调用时，修改位置信息后重新检查是否仍然属于当前地点
                    if (this.callMode === 'place') {
                        if (photo.city !== '') {  //有市级信息时，判断省和市是否发生了改变
                            if (photo.address__province !== res.province || photo.address__city !== res.city) {
                                this.$store.commit('refreshPhoto', {action: 'delete', list: [photo.uuid]})
                            }
                        }
                        else {  //没有有市级信息时，判断省、市、县是否发生了改变
                            if (photo.address__province !== res.province || photo.address__city !== res.city || photo.address__district !== res.district) {
                                this.$store.commit('refreshPhoto', {action: 'delete', list: [photo.uuid]})
                            }
                        }
                    }
                })
            },
            beforeFaceCommand(uuid, people_uuid, command) {
                return {
                    'uuid': uuid,
                    'people_uuid': people_uuid,
                    'command': command
                }
            },
            faceCommand(command) {
                switch (command.command) {
                    case 'setName':  //设置人物姓名
                        this.currFace = {
                            face_uuid: command.uuid,
                            name: '',
                        }
                        this.setPeopleFeature = false
                        this.deviceSupportUninstall()  //卸载键盘按键支持
                        this.isShowPeopleDialog = true
                        break
                    case 'removeName':  //清除人物姓名
                        this.removePeopleName(command.uuid, command.people_uuid)
                        break
                    case 'addFeature':  //添加特征
                        this.addPeopleFeature(command.uuid)
                        break
                    case 'removeFeature':  //删除特征
                        this.removePeopleFeature(command.uuid)
                        break
                    case 'setCover':  //设为人物封面
                        this.setPeopleCover(command.uuid, command.people_uuid)
                        break
                    case 'removeFace':  //删除面孔
                        this.removeFace(command.uuid, command.people_uuid)
                        break
                }
            },
            getPeopleList(query, cb) {
                //获取人物列表
                this.$axios({
                    method: 'get',
                    url: this.apiUrl + '/api/photo_query_peoples',
                    params: {
                        userid: localStorage.getItem('userid'),
                        query: query,  //查询的关键字
                    }
                }).then(response => {
                    this.peopleOptions = response.data
                    cb(this.peopleOptions)
                })
            },
            setPeopleName() {
                // 设置人物姓名
                if (this.currFace.name === '') {
                    this.$message({
                        message: '请输入人物姓名',
                        type: 'error',
                    })
                    return false
                }
                this.isShowPeopleDialog = false  //关闭对话框
                this.$axios({
                    method: 'post',
                    url: this.apiUrl + '/api/people_add_face',
                    data: {
                        userid: localStorage.getItem('userid'),
                        face_uuid: this.currFace.face_uuid,
                        name: this.currFace.name,
                        is_feature: this.setPeopleFeature,  //是否设为特征
                    }
                }).then(() => {
                    this.getPhotoFaces()  //刷新人脸列表
                    this.$message({
                        message: '成功为人物命名为 [' + this.currFace.name + ']',
                        type: 'success',
                    })
                })
            },
            removePeopleName(uuid, people_uuid) {
                // 清除人物姓名
                this.$axios({
                    method: 'post',
                    url: this.apiUrl + '/api/people_remove_name',
                    data: {
                        filter_type: 'face',
                        people_uuid: people_uuid,
                        face_list: [uuid],
                    }
                }).then(() => {
                    this.$message({
                        message: '成功清除了人物姓名',
                        type: 'success',
                    })
                    //在人物影集下，清除当前人物的姓名就是删除照片，但前提条件是该人物在当前照片中没有其它的面孔了
                    if (this.callMode === 'people') {
                        let hasMoreFace = false
                        for (let face of this.photoFaces) {
                            if (face.uuid !== uuid && face.people_uuid === this.peopleUUID) {
                                hasMoreFace = true
                            }
                        }
                        if (!hasMoreFace) {
                            let photo_uuid = this.currentImg.uuid
                            this.$store.commit('refreshPhoto', {action: 'delete', list: [photo_uuid]})
                            //从当前预览列表中移除当前照片
                            this.previewListOrder.splice(this.index, 1)
                            if (this.previewListOrder.length > 0) {
                                if (this.index > this.previewListOrder.length - 1)
                                    this.index = 0
                                this.currentImg = this.previewListOrder[this.index]
                                if (this.isShowInfoSide) {
                                    this.getPhotoInfo()  //重新获取照片详细信息
                                    this.getPhotoAlbums()  //重新获取照片所属的影集列表
                                    this.getPhotoFaces()  //重新获取照片中的人物
                                }
                            } else
                                this.close()  //否则关闭预览
                        }
                        this.$store.commit('refreshFace', {action: 'delete', list: [uuid]})
                    }
                    this.getPhotoFaces()
                })
            },
            addPeopleFeature(uuid) {
                //添加特征
                this.$axios({
                    method: 'post',
                    url: this.apiUrl + '/api/people_add_feature',
                    data: {
                        face_uuid: uuid,
                    }
                }).then(() => {
                    this.getPhotoFaces()
                    this.$message({
                        message: '成功添加了人物特征',
                        type: 'success',
                    })
                    //更新前端列表
                    if (this.callMode === 'people') {
                        let face = this.photoFaces.find(t => t.uuid === uuid)
                        face.feature_token = 'feature'  //这里填一个占位符即可，不用等待后台返回真实的token
                        this.$store.commit('refreshFace', {action: 'update', list: face})
                    }
                })
            },
            removePeopleFeature(uuid) {
                //删除特征
                this.$axios({
                    method: 'post',
                    url: this.apiUrl + '/api/people_remove_feature',
                    data: {
                        face_uuid: uuid,
                    }
                }).then(() => {
                    this.getPhotoFaces()
                    this.$message({
                        message: '成功删除了人物特征',
                        type: 'success',
                    })
                    //更新前端列表
                    if (this.callMode === 'people') {
                        let face = this.photoFaces.find(t => t.uuid === uuid)
                        face.feature_token = ''
                        this.$store.commit('refreshFace', {action: 'update', list: face})
                    }
                })
            },
            setPeopleCover(uuid, people_uuid) {
                // 设为人物封面
                this.$axios({
                    method: 'post',
                    url: this.apiUrl + '/api/people_set_cover',
                    data: {
                        people_uuid: people_uuid,
                        face_uuid: uuid,
                    }
                }).then(() => {
                    this.$message({
                        message: '人物封面设置成功',
                        type: 'success',
                    })
                })
            },
            removeFace(uuid, people_uuid) {
                this.$confirm('面孔一旦删除将无法恢复', '要删除选中的面孔吗？', {
                    confirmButtonText: '删除',
                    cancelButtonText: '取消',
                    type: 'warning',
                    closeOnClickModal: false,
                }).then(() => {
                    this.$axios({
                        method: 'post',
                        url: this.apiUrl + '/api/people_remove_face',
                        data: {
                            face_list: [uuid],
                        }
                    }).then(() => {
                        this.$message({
                            message: '面孔已删除',
                            type: 'success',
                        })
                        //在人物影集下，删除当前人物的面孔就是删除照片，但前提条件是该人物在当前照片中没有其它的面孔了
                        if (this.callMode === 'people') {
                            let hasMoreFace = false
                            for (let face of this.photoFaces) {
                                console.log(face.uuid)
                                console.log(uuid)
                                console.log(face.people_uuid)
                                console.log(people_uuid)
                                if (face.uuid !== uuid && face.people_uuid === this.peopleUUID) {
                                    hasMoreFace = true
                                    break
                                }
                            }
                            if (!hasMoreFace) {
                                let photo_uuid = this.currentImg.uuid
                                this.$store.commit('refreshPhoto', {action: 'delete', list: [photo_uuid]})
                                //从当前预览列表中移除当前照片
                                this.previewListOrder.splice(this.index, 1)
                                if (this.previewListOrder.length > 0) {
                                    if (this.index > this.previewListOrder.length - 1)
                                        this.index = 0
                                    this.currentImg = this.previewListOrder[this.index]
                                    if (this.isShowInfoSide) {
                                        this.getPhotoInfo()  //重新获取照片详细信息
                                        this.getPhotoAlbums()  //重新获取照片所属的影集列表
                                        this.getPhotoFaces()  //重新获取照片中的人物
                                    }
                                } else
                                    this.close()  //否则关闭预览
                            }
                        }
                        this.$store.commit('refreshFace', {action: 'delete', list: [uuid]})
                        this.getPhotoFaces()  //刷新人脸列表
                    })
                }).catch(() => {
                });
            },
        }
    }
</script>

<style scoped>
    /*最外层容器*/
    .viewer-wrapper {
        position: fixed;
        top: 0;
        right: 0;
        bottom: 0;
        left: 0;
        z-index: 10;
    }
    /*遮罩*/
    .viewer-mask {
        position: absolute;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
        background: #000;
    }
    /*大图画布*/
    .viewer-canvas {
        width: 100%;
        height: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    /*按钮*/
    .viewer-btn {
        position: absolute;
        z-index: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        cursor: pointer;
        box-sizing: border-box;
        user-select: none;
    }
    @media (any-hover: hover) {
        .viewer-btn:hover {
            background-color: #454749;
        }
    }
    /*关闭按钮*/
    .viewer-close {
        top: 10px;
        left: 10px;
        width: 40px;
        height: 40px;
        font-size: 23px;
        background-color: rgba(0, 0, 0, 0.1);
        color: #fff;
    }
    /*照片的说明文字*/
    .viewer-comments {
        position: absolute;
        top: 12px;
        left: 50px;
        padding: 8px;
        max-width: 500px;
        color: #fff;
        background-color: rgba(0, 0, 0, 0.1);
        border-radius: 8px;
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
        cursor: pointer;
        z-index: 1;
    }
    @media (any-hover: hover) {
        .viewer-comments:hover {
            background-color: #454749;
        }
    }
    @media (any-hover: none) {
        .viewer-comments {
            max-width: 100%;
            top: unset;
            left: 5px;
            bottom: 2px;
            background: none;
            font-size: 12px;
        }
    }
    /*上一张按钮*/
    .viewer-prev, .viewer-next {
        top: 50%;
        transform: translateY(-50%);
        width: 44px;
        height: 44px;
        font-size: 23px;
        color: #fff;
        background-color: rgba(0, 0, 0, 0.1);
        border-color: #fff;
    }
    .viewer-prev {
        left: 40px;
    }
    .viewer-next {
        right: 40px;
    }
    /*动作按钮*/
    .viewer-actions {
        left: 50%;
        bottom: 30px;
        transform: translateX(-50%);
        width: 282px;
        height: 44px;
        padding: 0 23px;
        background-color: rgba(0, 0, 0, 0.3);
        border-color: #fff;
        border-radius: 22px;
    }
    .viewer-actions-inner {
        width: 100%;
        height: 100%;
        text-align: justify;
        cursor: default;
        font-size: 23px;
        color: #bbbbbb;
        display: flex;
        align-items: center;
        justify-content: space-around;
    }
    .viewer-actions-inner i {
        cursor: pointer;
    }
    @media (any-hover: hover) {
        .viewer-actions-inner i:hover {
            color: #fff;
        }
    }
    /*工具栏*/
    .viewer-toolbar {
        position: absolute;
        z-index: 1;
        height: 44px;
        top: 10px;
        right: 5px;
    }
    .viewer-toolbar i {
        margin-right: 10px;
        width: 44px;
        height: 44px;
        color: #fff;
        font-size: 24px;
        line-height: 44px;
        text-align: center;
        background-color: rgba(0, 0, 0, 0.1);
        border-radius: 50%;
        cursor: pointer;
    }
    @media (any-hover: hover) {
        .viewer-toolbar i:hover {
            background-color: #454749;
            border-radius: 50%;
        }
    }
    /*侧边栏*/
    .viewer-side {
        position: fixed;
        top: 0;
        right: 0;
        z-index: 10;
        width: 360px;
        height: 100%;
        overflow-x: hidden;
        overflow-y: auto;
        background-color: #202124;
        color: #d9d9d9;
    }
    @media only screen and (max-width: 420px) {
        .viewer-side {
            left: 0;
            width: 100%;
        }
    }
    .viewer-side >>> .el-row {
        padding: 15px 30px;
    }
    .viewer-side::-webkit-scrollbar {
        display: none;
    }
    .side-close { /*侧边栏的关闭栏*/
        position: fixed;
        width: 360px;
        background-color: #202124;
        z-index: 1
    }
    /*侧边栏的关闭按钮*/
    .side-btn-close {
        width: 40px;
        height: 40px;
        line-height: 40px;
        text-align: center;
        margin-right: 5px;
        color: #fff;
        font-size: 23px;
        cursor: pointer;
    }
    @media (any-hover: hover) {
        .side-btn-close:hover {
            background-color: #454749;
            border-radius: 50%;
        }
    }
    .side-album-cover { /*侧边栏影集封面*/
        width: 44px;
        height: 44px;
        background-color: #80868b;
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        border-radius: 5px;
    }
    .side-href { /*侧边栏照片拍摄时间*/
        cursor: pointer;
    }
    @media (any-hover: hover) {
        .side-href:hover {
            background-color: #454545;
        }
    }
    .side-title { /*侧边栏中超长的文字*/
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
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

    .face-img {  /*人脸图像*/
        position: absolute;
        top: 0;
        width: 100%;
        height: 100%;
        border-radius: 8px;
    }
    .face-img-unknow {  /*未知的人脸图像*/
        filter: sepia(1);
        transition: 0.5s filter;
    }
    .face-img-unknow:hover {
        filter: none;
    }
    .face-name {  /*人物姓名*/
        color: #d9d9d9;
        font-size: 12px;
    }
    .face-feature {  /*面孔右上角的特征标志*/
        position: absolute;
        left: 3px;
        bottom: 3px;
        z-index: 1;
        color: #fff;
        font-size: 18px;
        -webkit-text-stroke: 1px rgba(0, 0, 0, .1);
    }
</style>