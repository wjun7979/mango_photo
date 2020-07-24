module.exports = {
    assetsDir: 'static',  //指定`build`时,在静态文件上一层添加static目录
}

module.exports = {
    chainWebpack: config => {
        config
            .plugin('html')
            .tap(args => {
                args[0].title = '芒果相册2'
                return args
            })
    }
}