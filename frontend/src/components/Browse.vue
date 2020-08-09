<template>
    <div>
        <div v-if="isShowTips" style="text-align: center;">
            <img src="../assets/images/upload-bg.png" style="width: 649px; height: 327px;"/>
            <div style="font-size: 32px; line-height: 50px; font-weight: 400; color: #202124">准备好添加一些照片了吗？</div>
            <div style="font-size: 16px; line-height: 40px; font-weight: 400; color: #3c4043">点击右上角的【上传】按钮上传照片</div>
        </div>

        <div class="div-images">
            <div v-for="(img, index) in photo_list"
                 :key="img.uuid"
                 class="div-img"
                 :style="{'width': img.width*220/img.height+'px','flex-grow':img.width*200/img.height}">
                <i :style="{'padding-bottom': img.height/img.width*100 + '%', 'display':'block'}"></i>
                <el-image :src="api_url + '/' + img.thumbnail_path + '/' + img.name" lazy
                          :alt="img.name" :title="img.name"
                          :preview-src-list="getSrcList(index)">
                    <div slot="error">
                        <div class="image-slot">
                            <i class="el-icon-picture-outline"></i>
                        </div>
                    </div>
                </el-image>
            </div>
        </div>
    </div>
</template>

<script>
    export default {
        name: "Browse",
        data() {
            return {
                photo_list: [],  //照片列表
                preview_list: [],  //照片预览列表
                isShowTips: false,  //是否显示上传提示
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
        mounted() {
            this.showPhotos()  //获取并显示照片列表
        },
        watch: {
            refresh_photo() {  //有其它组件发出刷新照片的指令
                if (this.refresh_photo) {
                    this.showPhotos()
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

    .div-images >>> .el-image-viewer__wrapper {
        padding: 20px; /*大图预览初始内边距*/
    }

    .div-images >>> .el-image-viewer__mask {
        opacity: 0.9; /*大图预览遮罩透明度*/
    }

    .div-images >>> .el-image-viewer__close {
        color: #fff; /*大图预览关闭按钮颜色*/
    }
</style>