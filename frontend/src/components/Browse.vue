<template>
    <div>
        <!--当照片列表为空时显示一些提示信息-->
        <div v-if="isShowTips" style="text-align: center;">
            <img src="../assets/images/upload-bg.png" style="width: 649px; height: 327px;"/>
            <div style="font-size: 32px; line-height: 50px; font-weight: 400; color: #202124">准备好添加一些照片了吗？</div>
            <div style="font-size: 16px; line-height: 40px; font-weight: 400; color: #3c4043">点击右上角的【上传】按钮上传照片</div>
        </div>

        <el-checkbox-group v-model="checkGroupList">
            <el-row v-for="(photo, index) in photo_list" :key="index">
                <el-checkbox class="chk-group" :label="photo.timestamp" @change="selectPhotoGroup">
                    {{common.date_format(photo.timestamp,'yyyy年M月d日 周w')}}
                </el-checkbox>
                <el-checkbox-group v-model="checkList">
                    <!--瀑布流样式的照片列表-->
                    <div class="div-images">
                        <div v-for="img in photo.list"
                             :key="img.uuid"
                             class="div-img"
                             :class="{'chk-checked': checkList.indexOf(img.uuid) != -1,
                                      'show-checkbox': checkList.length > 0}"
                             :style="{'width': img.width*220/img.height+'px','flex-grow':img.width*220/img.height}">
                            <i :style="{'padding-bottom': img.height/img.width*100 + '%', 'display':'block'}"></i>
                            <el-checkbox :label="img.uuid" @change="selectPhoto"></el-checkbox>
                            <el-image :src="api_url + '/' + img.path_thumbnail + '/' + img.name" lazy
                                      :alt="img.name"
                                      :title="img.name"
                                      @click="showPreview(img.uuid)"
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
    </div>
</template>

<script>
    import Preview from "./Preview";
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
                checkGroupList: [],
                checkList: [],
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
                        let result = res.list
                        // 生成大图预览列表
                        this.preview_list = []
                        for (let i in result) {
                            this.preview_list.push({
                                'uuid': result[i].uuid,
                                'url': this.api_url + '/' + result[i].path + '/' + result[i].name
                            })
                        }
                        // 将照片列表转换成时间线要求的格式
                        let dataMap = []
                        for (let d of result) {
                            let findData = dataMap.find(t=> t.timestamp == d['exif_datetime'].substring(0,10))
                            if (!findData)
                                dataMap.push({'timestamp': d['exif_datetime'].substring(0, 10), 'list': [d]})
                            else
                                findData.list.push(d)
                        }
                        this.photo_list = dataMap
                        // 当没有照片时显示提示
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
            showPreview(uuid) {  //显示大图预览
                if (this.checkList.length > 0) {  //当前有照片被选中了
                    let index = this.checkList.indexOf(uuid)
                    if (index == -1)
                        this.checkList.push(uuid)
                    else
                        this.checkList.splice(index, 1)
                    this.selectPhoto()  //触发照片选择事件
                }
                else {
                    let index = this.preview_list.findIndex(t => t.uuid == uuid)  //获取即将预览的照片索引
                    //根据索引对预览数组重新排序
                    this.preview_list_order = this.preview_list.slice(index).concat(this.preview_list.slice(0, index))
                    this.isShowPreview = true
                }
            },
            closeViewer() {  //关闭大图预览
                this.isShowPreview = false
            },
            selectPhotoGroup() {  //按组选择照片时
                for (let i in this.photo_list) {  //对所有照片进行分组循环
                    let timestamp = this.photo_list[i].timestamp
                    let photos = this.photo_list[i].list
                    for (let j in photos) {
                        if (this.checkGroupList.indexOf(timestamp) != -1) {  //选中了该组
                            if (this.checkList.indexOf(photos[j].uuid) == -1) {
                                this.checkList.push(photos[j].uuid)
                            }
                        }
                        else {
                            let index = this.checkList.indexOf(photos[j].uuid)
                            if (index != -1) {
                                this.checkList.splice(index, 1)
                            }
                        }
                    }
                }
            },
            selectPhoto() {  //选择照片时
                for (let i in this.photo_list) {  //对所有照片进行分组循环
                    let timestamp = this.photo_list[i].timestamp
                    let photos = this.photo_list[i].list
                    let tmpArr = []
                    for (let j in photos) {  //将当前组内的照片uuid存入一个新的数组
                        tmpArr.push(photos[j].uuid)
                    }
                    let index = this.checkGroupList.indexOf(timestamp)
                    if (this.common.isContain(this.checkList, tmpArr)) {  //判断当前组照片是否全被选中
                        if (index == -1)
                            this.checkGroupList.push(timestamp)
                    }
                    else {
                        if (index != -1)
                            this.checkGroupList.splice(index, 1)
                    }
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

    .div-images {  /*瀑布流照片*/
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

    .div-img:hover >>> .el-checkbox {  /*鼠标移上去时显示勾选控件*/
        visibility: visible;
    }

    .show-checkbox >>> .el-checkbox {
        visibility: visible;  /*当选择了照片时，所有的勾选控件都显示出来*/
    }

    .chk-checked {  /*选中之后的背景色*/
        background-color: #e8f0fe;
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

</style>