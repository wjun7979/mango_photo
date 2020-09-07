<template>
    <transition name="el-fade-in-linear">
        <div>
            <div ref="viewer-wrapper" class="viewer-wrapper"
                 :style="{'margin-right': viewerWrapperMargin,'z-index': 2000}">
                <div class="viewer-mask"></div>
                <!-- 关闭按钮 -->
                <span class="viewer-btn viewer-close" @click="$router.back()">
                    <i class="el-icon-back"></i>
                </span>
                <span class="viewer-comments" @click="setPhotoComments">{{currentImg.comments}}</span>
                <!--工具栏-->
                <div class="viewer-toolbar">
                    <div v-if="callMode === 'photo'">
                        <i class="el-icon-s-operation" title="修改" @click="showModify"></i>
                        <i class="el-icon-warning-outline" title="信息" @click="showInfo"></i>
                        <i class="el-icon-star-off" title="收藏" @click="addToFavorites"></i>
                        <el-dropdown trigger="click" @command="handCommand" placement="bottom-end">
                            <i class="el-icon-more" title="更多选项" style="transform: rotate(90deg);"></i>
                            <el-dropdown-menu slot="dropdown">
                                <el-dropdown-item icon="el-icon-download" command="download">下载</el-dropdown-item>
                                <el-dropdown-item icon="el-icon-plus" command="add_to_album">添加到影集</el-dropdown-item>
                                <el-dropdown-item icon="el-icon-delete" command="trash_photo">移到回收站</el-dropdown-item>
                            </el-dropdown-menu>
                        </el-dropdown>
                    </div>
                    <div v-if="callMode === 'album'">
                        <i class="el-icon-s-operation" title="修改" @click="showModify"></i>
                        <i class="el-icon-warning-outline" title="信息" @click="showInfo"></i>
                        <i class="el-icon-star-off" title="收藏" @click="addToFavorites"></i>
                        <el-dropdown trigger="click" @command="handCommand" placement="bottom-end">
                            <i class="el-icon-more" title="更多选项" style="transform: rotate(90deg);"></i>
                            <el-dropdown-menu slot="dropdown">
                                <el-dropdown-item icon="el-icon-download" command="download">下载</el-dropdown-item>
                                <el-dropdown-item icon="el-icon-plus" command="add_to_album">添加到影集</el-dropdown-item>
                                <el-dropdown-item icon="el-icon-remove-outline" command="remove_from_album">从影集中移除
                                </el-dropdown-item>
                                <el-dropdown-item icon="el-icon-notebook-1" command="set_album_cover">设为影集封面
                                </el-dropdown-item>
                                <el-dropdown-item icon="el-icon-delete" command="trash_photo">移到回收站</el-dropdown-item>
                            </el-dropdown-menu>
                        </el-dropdown>
                    </div>
                    <div v-if="callMode === 'trash'">
                        <i class="el-icon-warning-outline" title="信息" @click="showInfo"></i>
                        <i class="el-icon-delete" title="永久删除" @click="removePhoto"></i>
                        <i class="el-icon-time" title="恢复" @click="restorePhoto"></i>
                    </div>
                </div>
                <!-- 上一张、下一张 -->
                <template v-if="!isSingle">
                    <span class="viewer-btn viewer-prev"
                          @click="prev">
                        <i class="el-icon-arrow-left"/>
                    </span>
                    <span class="viewer-btn viewer-next"
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
                    <img class="viewer-img" ref="img" :src="currentImg.url" :style="imgStyle" @load="handleImgLoad"
                         @error="handleImgError" @mousedown="handleMouseDown"/>
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
                    <el-row class="side-href" @click.native="setPhotoComments">
                        <el-col :span="24" style="border-bottom: solid 1px #8c939d">
                            <span v-if="photoInfo.comments===null">添加说明</span>
                            <span v-else>{{photoInfo.comments}}</span>
                        </el-col>
                    </el-row>
                    <el-row style="font-size: 12px" v-show="photoAlbums.length>0">影集</el-row>
                    <el-row v-for="(album, index) of this.photoAlbums" :key="index">
                        <el-col :span="4">
                            <div class="side-album-cover"
                                 :style="{'background-image':'url('+apiUrl+'/'+album.cover_path+'/'+album.cover_name+')'}"></div>
                        </el-col>
                        <el-col :span="20">
                            <p>{{album.name}}</p>
                            <p style="font-size: 14px; color: #8c939d" v-if="album.photos === 0">没有内容</p>
                            <p style="font-size: 14px; color: #8c939d" v-else>{{album.photos}}项</p>
                        </el-col>
                    </el-row>
                    <el-row style="font-size: 12px">详情</el-row>
                    <el-row class="side-href" v-if="photoInfo.exif_datetime">
                        <el-col :span="3">
                            <i class="el-icon-date" style="font-size: 24px; line-height: 44px"></i>
                        </el-col>
                        <el-col :span="18">
                            <p>{{$common.dateFormat(photoInfo.exif_datetime, 'yyyy年M月d日')}}</p>
                            <p style="font-size: 14px; color: #8c939d">
                                <span>{{$common.dateFormat(photoInfo.exif_datetime, '周w')}}，</span>
                                <span>{{$common.dateFormat(photoInfo.exif_datetime, 'hh:mm:ss')}}</span>
                            </p>
                        </el-col>
                        <el-col :span="3" style="text-align: right">
                            <i class="el-icon-edit" style="font-size: 16px; line-height: 44px; color: #8c939d"></i>
                        </el-col>
                    </el-row>
                    <el-row v-show="photoInfo.name">
                        <el-col :span="3">
                            <i class="el-icon-picture" style="font-size: 24px; line-height: 44px"></i>
                        </el-col>
                        <el-col :span="21">
                            <p :title="photoInfo.name" class="side-title">{{photoInfo.name}}</p>
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
                    <el-row class="side-href">
                        <el-col :span="3">
                            <i class="el-icon-location" style="font-size: 24px;"></i>
                        </el-col>
                        <el-col :span="18">
                            <p v-if="photoInfo.photo_address">{{photoInfo.photo_address}}</p>
                            <p v-else>这张照片是在哪里拍摄的？</p>
                        </el-col>
                        <el-col :span="3" style="text-align: right">
                            <i class="el-icon-edit" style="font-size: 16px; color: #8c939d"></i>
                        </el-col>
                    </el-row>
                    <el-row style="padding: 15px 0" v-show="photoInfo.photo_address">
                        <div id="map-core" style="height: 360px"></div>
                    </el-row>
                </div>
            </div>
            <!--添加到影集对话框-->
            <el-dialog class="album-dialog" title="添加到影集"
                       :visible.sync="isShowAddToAlbumDialog"
                       width="400px"
                       :close-on-click-modal="false"
                       :destroy-on-close="true">
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
                            <p class="album-tree-photos" v-else>{{data.photos}}项</p>
                        </div>
                    </div>
                </el-tree>
                <span slot="footer">
                <el-button @click="isShowAddToAlbumDialog = false" size="small">取消</el-button>
                <el-button type="primary" size="small" @click="addToAlbum">确定</el-button>
            </span>
            </el-dialog>
        </div>
    </transition>
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
        name: "Preview",
        data() {
            return {
                uuid: this.$route.params.uuid,  //当前点击的照片uuid
                callMode: this.$route.params.callMode,  //调用模式
                albumUUID: this.$route.params.albumUUID,  //当调用模式为album时，必须指定影集uuid
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
                isShowModifySide: false,  //是否显示修改侧边栏
                isShowInfoSide: false,  //是否显示信息侧边栏
                viewerWrapperMargin: '0px',  //最外层容器右边距
                photoInfo: {},  //当前照片的详细信息
                photoAlbums: [],  //当前照片所属的影集列表
                baiduMap: null,  //百度地图对象
                isShowAddToAlbumDialog: false,  //是否显示添加到影集对话框
            }
        },
        watch: {
            index: {
                handler: function () {
                    this.currentImg = this.previewListOrder[this.index]
                    this.reset();
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
            }
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
            this.deviceSupportUninstall()  //卸载键盘按键支持
        },
        methods: {
            deviceSupportInstall() {  //注册键盘按键和鼠标滚动支持
                this._keyDownHandler = rafThrottle(e => {
                    const keyCode = e.keyCode
                    switch (keyCode) {
                        case 27:  //ESC退出
                            this.$router.back()
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
                });
                this._mouseWheelHandler = rafThrottle(e => {
                    const delta = e.wheelDelta ? e.wheelDelta : -e.detail
                    if (delta > 0) {
                        this.handleActions('zoomIn', {
                            zoomRate: 0.2,
                            enableTransition: false
                        });
                    } else {
                        this.handleActions('zoomOut', {
                            zoomRate: 0.2,
                            enableTransition: false
                        });
                    }
                });
                on(document, 'keydown', this._keyDownHandler);
                on(this.$refs.img, mousewheelEventName, this._mouseWheelHandler)
            },
            deviceSupportUninstall() {  //卸载键盘按键和鼠标滚动支持
                off(document, 'keydown', this._keyDownHandler);
                off(this.$refs.img, mousewheelEventName, this._mouseWheelHandler);
                this._keyDownHandler = null;
                this._mouseWheelHandler = null;
            },
            handleImgLoad() {  //图片加载完毕时
                this.loading = false;
            },
            handleImgError(e) {  //图片加载失败时
                this.loading = false;
                e.target.alt = '加载失败';
            },
            handleMouseDown(e) {
                //鼠标左键按下时，拖动图片
                if (this.loading || e.button !== 0) return;
                const {offsetX, offsetY} = this.transform;
                const startX = e.pageX;
                const startY = e.pageY;
                this._dragHandler = rafThrottle(ev => {
                    this.transform.offsetX = offsetX + ev.pageX - startX;
                    this.transform.offsetY = offsetY + ev.pageY - startY;
                });
                on(document, 'mousemove', this._dragHandler);
                on(document, 'mouseup', () => {
                    off(document, 'mousemove', this._dragHandler);
                });
                e.preventDefault();
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
            prev() {  //上一张
                const len = this.previewListOrder.length;
                this.index = (this.index - 1 + len) % len;
                this.$router.replace({
                    name: 'photo',
                    params: {
                        uuid: this.previewListOrder[this.index].uuid,
                        callMode: this.callMode,
                        albumUUID: this.albumUUID
                    }
                })
                if (this.isShowInfoSide) {
                    this.getPhotoInfo()  //重新获取照片详细信息
                    this.getPhotoAlbums()  //重新获取照片所属的影集列表
                }
            },
            next() {  //下一张
                const len = this.previewListOrder.length;
                this.index = (this.index + 1) % len;
                this.$router.replace({
                    name: 'photo',
                    params: {
                        uuid: this.previewListOrder[this.index].uuid,
                        callMode: this.callMode,
                        albumUUID: this.albumUUID
                    }
                })
                if (this.isShowInfoSide) {
                    this.getPhotoInfo()  //重新获取照片详细信息
                    this.getPhotoAlbums()  //重新获取照片所属的影集列表
                }
            },
            handleActions(action, options = {}) {  //对图片进行缩放和旋转操作
                if (this.loading) return;
                const {zoomRate, rotateDeg, enableTransition} = {
                    zoomRate: 0.2,
                    rotateDeg: 90,
                    enableTransition: true,
                    ...options
                };
                const {transform} = this;
                switch (action) {
                    case 'zoomOut':
                        if (transform.scale > 0.2) {  //控制最小缩放比例
                            transform.scale = parseFloat((transform.scale - zoomRate).toFixed(3));
                        }
                        break;
                    case 'zoomIn':
                        transform.scale = parseFloat((transform.scale + zoomRate).toFixed(3));
                        break;
                    case 'clocelise':  //左旋转
                        transform.deg += rotateDeg;
                        break;
                    case 'anticlocelise':  //右旋转
                        transform.deg -= rotateDeg;
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
                //获取预览列表
                this.$axios({
                    method: 'get',
                    url: this.apiUrl + '/api/photo_list',
                    params: {
                        userid: localStorage.getItem('userid'),
                        call_mode: this.callMode,
                        album_uuid: this.albumUUID,
                    }
                }).then(response => {
                    let photoList = response.data
                    // 生成大图预览列表
                    let previewList = []
                    for (let item of photoList) {
                        previewList.push({
                            'uuid': item.uuid,
                            'name': item.name,
                            'url': this.apiUrl + '/' + item.path + '/' + item.name,
                            'comments': item.comments
                        })
                    }
                    let index = previewList.findIndex(t => t.uuid === this.uuid)  //获取即将预览的照片索引
                    //根据索引对预览数组重新排序
                    this.previewListOrder = previewList.slice(index).concat(previewList.slice(0, index))
                    this.currentImg = this.previewListOrder[0]
                })
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
                this.viewerWrapperMargin = this.isShowInfoSide ? '360px' : '0px'
                if (this.isShowInfoSide) {
                    this.getPhotoInfo()  //获取照片详细信息
                    this.getPhotoAlbums()  //获取照片所属的影集列表
                }
            },
            closeInfo() {  //关闭信息侧边栏
                this.isShowInfoSide = false
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
                        photo_uuid: this.previewListOrder[this.index].uuid
                    }
                }).then(response => {
                    const res = response.data
                    console.log(res)
                    this.photoInfo = res
                    //将当前位置定位到地图
                    this.$nextTick(function () {
                        if (res.photo_lng && res.photo_lat) {
                            this.baiduMap = new BMap.Map("map-core")
                            this.baiduMap.enableScrollWheelZoom(true)
                            // this.baiduMap.centerAndZoom(new BMap.Point(116.331398, 39.897445), 15)
                            this.baiduMap.clearOverlays()  //清除标注
                            let new_point = new BMap.Point(res.photo_lng, res.photo_lat)
                            let marker = new BMap.Marker(new_point)  // 创建标注
                            this.baiduMap.addOverlay(marker)  // 将标注添加到地图中
                            this.baiduMap.panTo(new_point)  //定位到标注点
                            this.baiduMap.centerAndZoom(new_point, 15)
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
                        photo_uuid: this.previewListOrder[this.index].uuid
                    }
                }).then(response => {
                    const res = response.data
                    this.photoAlbums = res
                })
            },
            addToFavorites() {
                //收藏
                this.$message('收藏功能还没做好呢:-)')
            },
            handCommand(command) {
                //更多选项
                switch (command) {
                    case 'download':
                        this.downloadPhoto()
                        break
                    case 'add_to_album':
                        this.isShowAddToAlbumDialog = true
                        break
                    case 'remove_from_album':
                        this.removeFromAlbum()
                        break
                    case 'trash_photo':
                        this.trashPhoto()
                        break
                    case 'set_album_cover':
                        this.setAlbumCover()
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
                this.$axios({
                    method: 'post',
                    url: this.apiUrl + '/api/album_add_photo',
                    data: {
                        album_uuid: album_uuid,
                        photo_list: [this.currentImg.uuid]
                    }
                }).then(() => {
                    let msg = '成功将照片' + this.currentImg.name + '添加到影集 [' + album_name + '] 中'
                    this.$message({
                        message: msg,
                        type: 'success',
                    })
                    this.isShowAddToAlbumDialog = false
                    //如果信息侧边栏处于打开状态，则刷新该图片所属的影集列表
                    if (this.isShowInfoSide) {
                        this.getPhotoAlbums()
                    }
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
                            photo_list: [this.currentImg.uuid]
                        }
                    }).then(() => {
                        let msg = '照片' + this.currentImg.name + '已从影集 [' + this.albumName + '] 中移除'
                        this.$message({
                            message: msg,
                            type: 'success',
                        })
                        this.$store.commit('refreshPhoto', {show: true})  //刷新图片列表
                        //从当前预览列表中移除当前照片
                        this.previewListOrder.splice(this.index, 1)
                        if (this.previewListOrder.length > 0)
                            this.next()  //如果列表中还有照片，则显示下一张
                        else
                            this.close()  //否则关闭预览
                    })
                }).catch(() => {
                });
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
                            photo_list: [this.currentImg.uuid]
                        }
                    }).then(() => {
                        let msg = '已将照片' + this.currentImg.name + '移到回收站'
                        this.$message({
                            message: msg,
                            type: 'success',
                        })
                        this.$store.commit('refreshPhoto', {show: true})  //刷新图片列表
                        this.$store.commit('refreshPhotoStatistics', {show: true})  //刷新照片库统计信息
                        //从当前预览列表中移除当前照片
                        this.previewListOrder.splice(this.index, 1)
                        if (this.previewListOrder.length > 0)
                            this.next()  //如果列表中还有照片，则显示下一张
                        else
                            this.close()  //否则关闭预览
                    })
                }).catch(() => {
                });
            },
            setAlbumCover() {
                //设为影集封面
                this.$message('设为影集封面功能还没做好呢:-)')
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
                            photo_list: [this.currentImg.uuid]
                        }
                    }).then(() => {
                        let msg = '照片' + this.currentImg.name + '成功删除'
                        this.$message({
                            message: msg,
                            type: 'success',
                        })
                        this.$store.commit('refreshPhoto', {show: true})  //刷新图片列表
                        //从当前预览列表中移除当前照片
                        this.previewListOrder.splice(this.index, 1)
                        if (this.previewListOrder.length > 0)
                            this.next()  //如果列表中还有照片，则显示下一张
                        else
                            this.close()  //否则关闭预览
                    })
                }).catch(() => {
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
                    let msg = '照片' + this.currentImg.name + '成功恢复'
                    this.$message({
                        message: msg,
                        type: 'success',
                    })
                    this.$store.commit('refreshPhoto', {show: true})  //刷新图片列表
                    this.$store.commit('refreshPhotoStatistics', {show: true})  //刷新照片库统计信息
                    //从当前预览列表中移除当前照片
                    this.previewListOrder.splice(this.index, 1)
                    if (this.previewListOrder.length > 0)
                        this.next()  //如果列表中还有照片，则显示下一张
                    else
                        this.close()  //否则关闭预览
                })
            },
            setPhotoComments() {
                //为照片添加说明文字
                this.deviceSupportUninstall()  //卸载键盘按键支持
                this.$prompt('请输入照片说明：', {
                    inputValue: this.currentImg.comments,
                    inputValidator: (value => {
                        if (value.trim().length === 0)
                            return false
                    }),
                    inputErrorMessage: '照片说明不能为空',
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
                                this.photoInfo.comments = instance.inputValue
                                this.$message({
                                    message: '成功为照片添加了说明 [' + instance.inputValue + ']',
                                    type: 'success',
                                })
                                this.$store.commit('refreshPhoto', {show: true})  //刷新图片列表
                            })
                        }
                        this.deviceSupportInstall()  //恢复键盘按键支持
                    })
                })
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
    .viewer-btn:hover {
        background-color: #454749;
    }
    /*关闭按钮*/
    .viewer-close {
        top: 20px;
        left: 20px;
        width: 40px;
        height: 40px;
        font-size: 23px;
        background-color: rgba(0, 0, 0, 0.1);
        color: #fff;
    }
    /*照片的说明文字*/
    .viewer-comments {
        position: absolute;
        top: 20px;
        left: 70px;
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
    .viewer-comments:hover {
        background-color: #454749;
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
        color: #fff;
        display: flex;
        align-items: center;
        justify-content: space-around;
    }
    /*工具栏*/
    .viewer-toolbar {
        position: absolute;
        z-index: 1;
        height: 44px;
        top: 20px;
        right: 30px;
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
    .viewer-toolbar i:hover {
        background-color: #454749;
        border-radius: 50%;
    }
    /*侧边栏*/
    .viewer-side {
        position: fixed;
        top: 0;
        right: 0;
        z-index: 2000;
        width: 360px;
        height: 100%;
        overflow: auto;
        background-color: #202124;
        color: #d9d9d9;
    }
    .viewer-side >>> .el-row {
        padding: 15px 30px;
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
    .side-btn-close:hover {
        background-color: #454749;
        border-radius: 50%;
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
    .side-href:hover {
        background-color: #454545;
    }
    .side-title { /*侧边栏中超长的文字*/
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
    }

    .album-tree { /*影集树*/
        height: 300px;
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
        font-size: 12px;
    }
</style>