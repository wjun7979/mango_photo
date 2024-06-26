export default {
    DEBOUNCE_TIMEOUT: 2000,  //防抖函数延迟时间
    dateFormat(dt, fmt) {
        //将datetime对象格式化成指定格式的字符串
        if (typeof dt == 'string') {
            dt = new Date(Date.parse(dt.replace(/-/g, "/")))
        }
        let o = {
            "y+": dt.getFullYear(),
            "M+": dt.getMonth() + 1,                 //月份
            "d+": dt.getDate(),                    //日
            "h+": dt.getHours(),                   //小时
            "m+": dt.getMinutes(),                 //分
            "s+": dt.getSeconds(),                 //秒
            "q+": Math.floor((dt.getMonth() + 3) / 3), //季度
            "S+": dt.getMilliseconds(),             //毫秒
            "w+": dt.getDay(),  //星期
        };
        for (let k in o) {
            if (new RegExp("(" + k + ")").test(fmt)) {
                if (k == "y+") {
                    fmt = fmt.replace(RegExp.$1, ("" + o[k]).substr(4 - RegExp.$1.length));
                } else if (k == "S+") {
                    let lens = RegExp.$1.length;
                    lens = lens == 1 ? 3 : lens;
                    fmt = fmt.replace(RegExp.$1, ("00" + o[k]).substr(("" + o[k]).length - 1, lens));
                } else if (k == "w+") {
                    fmt = fmt.replace(RegExp.$1, '日一二三四五六'.charAt(o[k]))
                } else {
                    fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
                }
            }
        }
        return fmt;
    },
    isContain(arr1, arr2) {
        //判断arr2是否是arr1的子集
        for (let i = arr2.length - 1; i >= 0; i--) {
            if (!arr1.includes(arr2[i])) {
                return false;
            }
        }
        return true;
    },
    bytesToSize(bytes) {
        //将字节转换为合适的容量单位
        if (bytes === null || bytes === 0) return '0 B'
        let k = 1024, sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'],
            i = Math.floor(Math.log(bytes) / Math.log(k))
        return (bytes / Math.pow(k, i)).toPrecision(3) + ' ' + sizes[i]
    },
    getDistance(p1, p2) {
        //勾股定理计算两点的距离
        let x = p2.pageX - p1.pageX,
            y = p2.pageY - p1.pageY
        return Math.sqrt((x * x) + (y * y))
    },
    getDirection(startx, starty, endx, endy) {
        //根据起点终点返回方向 1向上 2向下 3向左 4向右 0未滑动
        let angx = endx - startx
        let angy = endy - starty
        let result = 0

        //如果滑动距离太短
        if (Math.abs(angx) < 2 && Math.abs(angy) < 2) {
            return result
        }

        let angle = this.getAngle(angx, angy)
        if (angle >= -135 && angle <= -45) {
            result = 1  //向上
        } else if (angle > 45 && angle < 135) {
            result = 2  //向下
        } else if ((angle >= 135 && angle <= 180) || (angle >= -180 && angle < -135)) {
            result = 3  //向左
        } else if (angle >= -45 && angle <= 45) {
            result = 4  //向右
        }

        return result
    },
    getAngle(angx, angy) {
        //获得角度
        return Math.atan2(angy, angx) * 180 / Math.PI;
    },
}