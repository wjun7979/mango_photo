<template>
    <transition name="el-fade-in-linear">
        <div>
            <div ref="viewer-wrapper" class="viewer-wrapper"
                 :style="{'margin-right': viewerWrapperMargin,'z-index': 2000}">
                <div class="viewer-mask"></div>
                <!-- 关闭按钮 -->
                <span class="viewer-btn viewer-close" @click="close">
                    <i class="el-icon-back"></i>
                </span>
                <!--工具栏-->
                <div class="viewer-toolbar">
                    <i class="el-icon-s-operation" title="修改" @click="showModify"></i>
                    <i class="el-icon-warning-outline" title="信息" @click="showInfo"></i>
                    <i class="el-icon-star-off" title="收藏"></i>
                    <i class="el-icon-delete" title="删除"></i>
                    <i class="el-icon-plus" title="添加到影集"></i>
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
                    <img class="viewer-img" ref="img" :src="currentImg" :style="imgStyle" @load="handleImgLoad"
                         @error="handleImgError" @mousedown="handleMouseDown"/>
                </div>
            </div>
            <!--修改侧边栏-->
            <div class="viewer-side" v-if="isShowModifySide">
                <el-row>
                    <i class="el-icon-close viewer-side-btn-close" @click="closeModify"/>
                </el-row>
            </div>
            <!--信息侧边栏-->
            <div class="viewer-side" v-if="isShowInfoSide">
                <el-row>
                    <i class="el-icon-close viewer-side-btn-close" @click="closeInfo"/>
                </el-row>
            </div>
        </div>
    </transition>
</template>

<script>
    import { on, off } from 'element-ui/src/utils/dom';
    import { rafThrottle, isFirefox } from 'element-ui/src/utils/util';

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
                index: 0,  //当前预览图编号
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
            }
        },
        props: [
            'urlList',
            'onClose',
        ],
        watch: {
            index: {
                handler: function () {
                    this.reset();
                }
            },
            currentImg() {
                // eslint-disable-next-line no-unused-vars
                this.$nextTick(_ => {
                    const $img = this.$refs.img;
                    if (!$img.complete) {
                        this.loading = true;
                    }
                });
            }
        },
        mounted() {
            this.deviceSupportInstall();
            this.$refs['viewer-wrapper'].focus();
        },
        computed: {
            isSingle() {  //是否只有一张图片
                return this.urlList.length <= 1;
            },
            currentImg() {  //当前图片默认是传入数组urlList的第一个元素
                return this.urlList[this.index].url;
            },
            imgStyle() {
                const {scale, deg, offsetX, offsetY, enableTransition} = this.transform;
                const style = {
                    transform: `scale(${scale}) rotate(${deg}deg)`,
                    transition: enableTransition ? 'transform .3s' : '',
                    'margin-left': `${offsetX}px`,
                    'margin-top': `${offsetY}px`
                };
                if (this.mode === Mode.CONTAIN) {
                    style.maxWidth = style.maxHeight = '100%';
                }
                return style;
            }
        },
        methods: {
            close() {  //关闭大图预览
                this.deviceSupportUninstall();
                this.onClose();
            },
            deviceSupportInstall() {  //注册键盘按键和鼠标滚动支持
                this._keyDownHandler = rafThrottle(e => {
                    const keyCode = e.keyCode;
                    switch (keyCode) {
                        case 27:  //ESC退出
                            this.close();
                            break;
                        case 32:  //SPACE切换显示模式:1:1或合适缩放
                            this.toggleMode();
                            break;
                        case 37:  //LEFT_ARROW上一张
                            this.prev();
                            break;
                        case 38:  //UP_ARROW放大
                            this.handleActions('zoomIn');
                            break;
                        case 39:  //RIGHT_ARROW 下一张
                            this.next();
                            break;
                        case 40:  //DOWN_ARROW缩小
                            this.handleActions('zoomOut');
                            break;
                    }
                });
                this._mouseWheelHandler = rafThrottle(e => {
                    const delta = e.wheelDelta ? e.wheelDelta : -e.detail;
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
                on(document, mousewheelEventName, this._mouseWheelHandler);
            },
            deviceSupportUninstall() {  //卸载键盘按键和鼠标滚动支持
                off(document, 'keydown', this._keyDownHandler);
                off(document, mousewheelEventName, this._mouseWheelHandler);
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
                const len = this.urlList.length;
                this.index = (this.index - 1 + len) % len;
            },
            next() {  //下一张
                const len = this.urlList.length;
                this.index = (this.index + 1) % len;
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
            showModify() {  //显示修改侧边栏
                this.isShowInfoSide = false
                this.isShowModifySide = ! this.isShowModifySide
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
            },
            closeInfo() {  //关闭信息侧边栏
                this.isShowInfoSide = false
                this.viewerWrapperMargin = '0px'
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
        background-color: rgba(0,0,0,0.1);
        color: #fff;
    }

    /*上一张按钮*/
    .viewer-prev, .viewer-next {
        top: 50%;
        transform: translateY(-50%);
        width: 44px;
        height: 44px;
        font-size: 23px;
        color: #fff;
        background-color: rgba(0,0,0,0.1);
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
        background-color: rgba(0,0,0,0.3);
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
        background-color: rgba(0,0,0,0.1);
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
        padding: 20px;
        width: 360px;
        height: 100%;
        background-color: #202124;
    }
    /*侧边栏的关闭按钮*/
    .viewer-side-btn-close {
        width: 44px;
        height: 44px;
        line-height: 44px;
        text-align: center;
        color: #fff;
        font-size: 23px;
        cursor: pointer;
    }
    .viewer-side-btn-close:hover {
        background-color: #454749;
        border-radius: 50%;
    }
</style>