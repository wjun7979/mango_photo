export default {
    date_format: function (dt, fmt) {
        //将datetime对象格式化成指定格式的字符串
        let o = {
            "y+": dt.getFullYear(),
            "M+": dt.getMonth() + 1,                 //月份
            "d+": dt.getDate(),                    //日
            "h+": dt.getHours(),                   //小时
            "m+": dt.getMinutes(),                 //分
            "s+": dt.getSeconds(),                 //秒
            "q+": Math.floor((dt.getMonth() + 3) / 3), //季度
            "S+": dt.getMilliseconds()             //毫秒
        };
        for (let k in o) {
            if (new RegExp("(" + k + ")").test(fmt)) {
                if (k == "y+") {
                    fmt = fmt.replace(RegExp.$1, ("" + o[k]).substr(4 - RegExp.$1.length));
                } else if (k == "S+") {
                    let lens = RegExp.$1.length;
                    lens = lens == 1 ? 3 : lens;
                    fmt = fmt.replace(RegExp.$1, ("00" + o[k]).substr(("" + o[k]).length - 1, lens));
                } else {
                    fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
                }
            }
        }
        return fmt;
    }
}