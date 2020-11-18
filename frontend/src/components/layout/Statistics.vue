<template>
    <div class="statistics">
        共 {{photoCount.nums}} 张照片，占用空间 {{photoCount.size}}
    </div>
</template>

<script>
    export default {
        name: "Statistics",
        data() {
            return {
                photoCount: {
                    nums: 0,
                    size: '0 B',
                }
            }
        },
        computed: {
            apiUrl() {
                return this.$store.state.apiUrl  //后台api调用地址
            },
            refreshPhotoStatistics() {  //是否刷新照片库统计信息
                return this.$store.state.refreshPhotoStatistics
            },
        },
        watch: {
            refreshPhotoStatistics() {
                //有其它组件发出刷新照片库统计信息的指令
                if (this.refreshPhotoStatistics) {
                    this.getPhotoStatistics()
                }
            }
        },
        mounted() {
            this.getPhotoStatistics()
        },
        methods: {
            getPhotoStatistics() {
                //统计照片数量和占用空间等信息
                this.$axios({
                    method: 'get',
                    url: this.apiUrl + '/api/photo_statistics',
                    params: {
                        userid: localStorage.getItem('userid')
                    }
                }).then(response => {
                    let res = response.data
                    this.photoCount.nums = res.nums
                    this.photoCount.size = this.$common.bytesToSize(res.size)
                    this.$store.commit('refreshPhotoStatistics', {show: false})  //重置“是否刷新照片库统计信息”标志
                })
            },
        }
    }
</script>

<style scoped>
    .statistics {
        padding: 10px 20px;
        font-size: 12px;
        line-height: 22px;
        color: #5f6368;
    }
</style>