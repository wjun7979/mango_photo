<template>
    <div>
        <div v-if="isShowTips" style="text-align: center;">
            <img src="../assets/images/upload-bg.png"/>
            <div style="font-size: 32px; line-height: 50px; font-weight: 400; color: #202124">准备好添加一些照片了吗？</div>
            <div style="font-size: 16px; line-height: 40px; font-weight: 400; color: #3c4043">点击右上角的【上传】按钮上传照片</div>
        </div>
        <div class="div-images">
            <el-image v-for="(photo, index) in photo_list" v-bind:key="photo.uuid"
                      :src="api_url + '/' + photo.thumbnail_path + '/' + photo.name"
                      :lazy="true"
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
            }
        },
        computed: {
            //重要：vuex中定义的数据一定要在这里绑定，放在data()里视图不会更新
            refresh_photo(){
                return this.$store.state.refresh_photo  //是否刷新照片列表
            }
        },
        mounted: function () {
            this.showPhotos()
        },
        watch: {
            'refresh_photo': function () {
                if (this.refresh_photo) {
                    this.showPhotos()
                }
            }
        },
        methods: {
            showPhotos() {  //显示照片列表
                this.$http.get(this.api_url + '/api/photo_list').then(response => {
                    const res = JSON.parse(response.bodyText)
                    if (res.msg == 'success') {
                        this.photo_list = res.list
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
            }
        }
    }
</script>

<style scoped>
    .div-images >>> .el-image__inner {
        display: block;
        width: auto;
        height: 200px;
        margin-right: 5px;
    }

    .image-slot {
        margin-right: 5px;
        width: 200px;
        height: 200px;
        line-height: 200px;
        background: #f5f7fa;
        color: #909399;
        text-align: center;
    }
</style>