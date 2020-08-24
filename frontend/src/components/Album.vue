<template>
    <PhotoList :title="'影集 - ' + albumName" callMode="album" :albumUUID="albumUUID"></PhotoList>
</template>

<script>
    import PhotoList from "./PhotoList"

    export default {
        name: "Album",
        components: {PhotoList},
        data() {
            return {
                albumUUID: this.$route.params.uuid,  //影集uuid
                albumName: '',  //影集标题
            }
        },
        computed: {
            apiUrl() {
                return this.$store.state.apiUrl  //后台api调用地址
            },
        },
        mounted() {
            this.getAlbum()
        },
        methods: {
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
        }
    }
</script>

<style scoped>

</style>