<template>
    <el-dropdown trigger="click" @command="handCommand" placement="bottom-end" class="btn-pick hidden-pc-only">
        <i class="el-icon-more" title="更多选项" style="transform: rotate(90deg);"></i>
        <el-dropdown-menu slot="dropdown">
            <el-dropdown-item icon="el-icon-circle-check" command="pick">选择照片</el-dropdown-item>
            <el-dropdown-item v-if="showSearch" icon="el-icon-search" command="search">搜索</el-dropdown-item>
        </el-dropdown-menu>
    </el-dropdown>
</template>

<script>
    export default {
        name: "MoreOption",
        props: {
            showSearch: {  //是否显示搜索菜单
                type: Boolean,
                default: false
            },
        },
        methods: {
            handCommand(command) {
                //更多选项
                switch (command) {
                    case 'pick':  // 选择照片
                        this.$store.commit('pickPhotoMode', {show: true})
                        break
                    case 'search':  //搜索
                        this.search()
                        break
                }
            },
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
    .btn-pick {
        display: inline-block;
    }
    .btn-pick i {
        font-size: 24px;
    }
</style>