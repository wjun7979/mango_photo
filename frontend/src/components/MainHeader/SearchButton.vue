<template>
    <div class="hidden-sm-and-up" style="display: inline-block">
        <i class="el-icon-search icon-button" @click="search"></i>
    </div>
</template>

<script>
    export default {
        name: "SearchButton",
        methods: {
            search() {
                this.$prompt('', {
                    inputPlaceholder: '请输入搜索关键字',
                    inputValue: this.$store.state.searchKeyword,
                    closeOnClickModal: false,
                    callback: ((action, instance) => {
                        if (action === 'confirm') {
                            this.$store.commit('searchKeyword', {keyword: instance.inputValue})
                        }
                    })
                })
            },
        }
    }
</script>

<style scoped>
</style>