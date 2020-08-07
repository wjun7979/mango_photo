<template>
    <div>
        <div v-if="isShowTips" style="text-align: center;">
            <img src="../assets/images/upload-bg.png"/>
            <div style="font-size: 32px; line-height: 50px; font-weight: 400; color: #202124">准备好添加一些照片了吗？</div>
            <div style="font-size: 16px; line-height: 40px; font-weight: 400; color: #3c4043">点击右上角的【上传】按钮上传照片</div>
        </div>
        <div class="div-images">
            <el-image v-for="(img, index) in waterfallList"
                      :key="img.uuid"
                      :src="img.src"
                      :lazy="true"
                      class="v-waterfall-item"
                      :style="{top:img.top+'px',left:img.left+'px',width:ImgWidth+'px',height:img.height}"
                      :preview-src-list="getSrcList(index)">
                <div slot="error">
                    <div class="image-slot">
                        <i class="el-icon-picture-outline"></i>
                    </div>
                </div>
            </el-image>
        </div>
    </div>
</template>

<script>
    export default {
        name: "Browse",
        data() {
            return {
                api_url: this.$store.state.api_url,  //从全局状态管理器中获取数据
                photo_list: [],  //照片列表
                preview_list: [],  //照片预览列表
                isShowTips: false,  //是否显示上传提示
                waterfallList: [],  //瀑布流照片列表
                ImgWidth: '',  //照片的宽度，calculationWidth()计算得到
                ImgCol: 4,  //每行显示多少张照片
                ImgRight: 5,  //照片的右边距
                ImgBottom: 5,  //照片的下边距
                deviationHeight: [],  //偏移高度数组
                screenWidth: document.body.clientWidth - 296,  //照片列表区宽度
            }
        },
        computed: {
            //重要：vuex中定义的数据一定要在这里绑定，放在data()里视图不会更新
            refresh_photo() {
                return this.$store.state.refresh_photo  //是否刷新照片列表
            }
        },
        mounted() {
            this.showPhotos()  //获取并显示照片列表
            //window窗口大小改变时重新计算照片列表区宽度
            window.addEventListener('resize', this.listenResize)
        },
        beforeDestroy() {
            window.removeEventListener('resize', this.listenResize)
        },
        watch: {
            refresh_photo() {  //有其它组件发出刷新照片的指令
                if (this.refresh_photo) {
                    this.showPhotos()
                }
            },
            screenWidth(){  //window窗口大小改变时重新计算照片列表区宽度
                // 为了避免频繁触发resize函数导致页面卡顿，使用定时器
                if(!this.timer){
                    // 一旦监听到的screenWidth值改变，就将其重新赋给data里的screenWidth
                    this.timer = true
                    let that = this
                    setTimeout(function(){
                        that.calculationWidth();  //重新计算图片宽度
                        that.timer = false
                    },400)
                }
            },
        },
        methods: {
            showPhotos() {  //获取并显示照片列表
                this.$http.get(this.api_url + '/api/photo_list').then(response => {
                    const res = JSON.parse(response.bodyText)
                    if (res.msg == 'success') {
                        this.photo_list = res.list
                        // 生成大图预览列表
                        this.preview_list = []
                        for (let i in this.photo_list) {
                            this.preview_list.push(this.api_url + '/' + this.photo_list[i].path + '/' + this.photo_list[i].name)
                        }
                        //以瀑布流方式显示图片
                        if (this.photo_list.length > 0) {
                            this.calculationWidth()
                        }
                        this.isShowTips = this.photo_list.length == 0
                    } else {
                        this.$notify.error({
                            title: '提示',
                            message: '获取照片失败:' + res.msg,
                            position: 'top-right'
                        })
                    }
                    this.$store.commit('refreshPhoto', {show: false})
                })
            },
            getSrcList(index) {  //获取大图预览对象
                //改变数组顺序，从当前索引截取到最后，再加上从第一个到当前索引
                return this.preview_list.slice(index).concat(this.preview_list.slice(0, index))
            },
            listenResize() {  //window窗口大小改变时重新计算照片列表区宽度
                this.screenWidth = document.body.clientWidth - 296
            },
            calculationWidth() {  //计算每个图片的宽度
                this.ImgWidth = (this.screenWidth - this.ImgRight * this.ImgCol) / this.ImgCol;
                //初始化偏移高度数组
                this.deviationHeight = new Array(this.ImgCol);
                for (let i = 0; i < this.deviationHeight.length; i++) {
                    this.deviationHeight[i] = 0;
                }
                this.imgPreloading()
            },
            imgPreloading() {  //图片预加载
                this.waterfallList = []
                for (let i = 0; i < this.photo_list.length; i++) {
                    let imgData = {}
                    imgData.height = this.ImgWidth / this.photo_list[i].width * this.photo_list[i].height  //按比例计算图片高度
                    imgData.src = this.api_url + '/' + this.photo_list[i].thumbnail_path + '/' + this.photo_list[i].name
                    imgData.uuid = this.photo_list[i].uuid
                    this.waterfallList.push(imgData)
                    this.rankImg(imgData) //渲染页面
                }
            },
            rankImg(imgData) {  //瀑布流布局
                let {ImgWidth, ImgRight, ImgBottom, deviationHeight} = this
                let minIndex = this.filterMin()  //获得高度最小的一列的下标
                imgData.top = deviationHeight[minIndex]  //插入图片的top值
                imgData.left = minIndex * (ImgRight + ImgWidth)  //插入图片的left值
                deviationHeight[minIndex] += imgData.height + ImgBottom  //更新当前列的高度
            },
            filterMin() {  //找到最短的列并返回下标
                const min = Math.min.apply(null, this.deviationHeight)
                return this.deviationHeight.indexOf(min)
            },
        }
    }
</script>

<style scoped>
    .image-slot {
        margin-right: 5px;
        width: 200px;
        height: 200px;
        line-height: 200px;
        background: #f5f7fa;
        color: #909399;
        text-align: center;
    }

    .div-images {
        width: 100%;
        height: 100%;
        position: relative;
    }

    .div-images >>> .el-image-viewer__wrapper {
        padding: 20px;  /*大图预览初始内边距*/
    }

    .div-images >>> .el-image-viewer__mask {
        opacity: 0.9;  /*大图预览遮罩透明度*/
    }

    .div-images >>> .el-image-viewer__close {
        color: #fff;  /*大图预览关闭按钮颜色*/
    }

    .v-waterfall-item{
        position: absolute;
    }
    .v-waterfall-item img{
        width: 100%;
        height: 100%;
    }
</style>