<template>
    <el-dropdown trigger="click" @command="handCommand" placement="bottom-end" class="btn-pick hidden-pc-only">
        <i class="el-icon-more" title="更多选项" style="transform: rotate(90deg);"></i>
        <el-dropdown-menu slot="dropdown">
            <el-dropdown-item icon="el-icon-circle-check" command="pick">选择照片</el-dropdown-item>
        </el-dropdown-menu>
    </el-dropdown>
</template>

<script>
    export default {
        name: "PickPhotoButton",
        methods: {
            handCommand(command) {
                //更多选项
                switch (command) {
                    case 'pick':  // 选择照片
                        this.$store.commit('pickPhotoMode', {show: true})
                        break
                }
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