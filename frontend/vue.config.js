module.exports = {
    assetsDir: 'static',  //指定`build`时,在静态文件上一层添加static目录
    devServer: {
        allowedHosts: [
            'wlon.vicp.net',
        ],
        port: 8001
    },
    configureWebpack: {
        externals: {
            "BMap": "BMap"
        }
    }
}