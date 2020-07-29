module.exports = {
    assetsDir: 'static',  //指定`build`时,在静态文件上一层添加static目录
    pages: {
        index: {
            entry: "src/views/index/main.js",  //配置入口js文件
            template: "public/index.html",  //主页面
            filename: "index.html",  //打包后的html文件的名称
            title: "芒果相册"  //打包后的html中<title>标签的文本内容
        }
    }
}