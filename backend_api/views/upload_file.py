import os
import hashlib  # md5
import traceback  # 输出更详细的错误信息
import uuid
import re  # 正则
# import pprint  # 格式化打印
import requests  # 调用api
from datetime import datetime
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from PIL import Image  # 图像处理
import exifread  # 读取exif信息
from backend_api.models import Photo, Address


@require_http_methods(['POST'])  # django内置的视力装饰器，这行表示只能通过POST方法访问
@transaction.atomic  # 数据库事务处理
def upload_photo(request):
    """上传文件"""
    save_tag = transaction.savepoint()  # 设置保存点，用于数据库事务回滚
    response = {}
    photo_fullpath = ''  # 照片的完整路径
    thumbnail_fullpath = ''  # 缩略图的完整路径
    try:
        userid = request.POST['userid']  # 当前登录的用户id
        now = datetime.now()  # 当前时间，用于创建目录
        file = request.FILES['file']  # 前端上传的文件对象

        # 获取文件md5值，然后检查是否已经存在，如果存在就跳过
        file_md5 = __get_file_md5(file)
        photo = Photo.objects.filter(md5=file_md5)  # 表过滤
        if len(photo) > 0:
            response['msg'] = '照片已存在，跳过'
            return JsonResponse(response, status=500)

        # 根据当前日期创建文件夹 /photos/current/{userid}/年/月/日
        file_path = os.path.join('photos', 'current', userid, now.strftime('%Y'), now.strftime('%m'),
                                 now.strftime('%d'))  # 相对路径
        real_path = os.path.join(settings.BASE_DIR, file_path)  # 物理路径
        if not os.path.exists(real_path):  # 如果目标文件夹不存在则创建
            os.makedirs(real_path, exist_ok=True)

        # 检查当前目录下是否有同名文件，如果存在则重命名
        file_name = file.name  # 原始文件名
        photo_fullpath = os.path.join(real_path, file_name)  # 包含路径的完整文件名
        if os.path.exists(photo_fullpath):
            splitext = os.path.splitext(photo_fullpath)
            photo_fullpath = splitext[0] + '_' + str(uuid.uuid1()).replace('-', '') + splitext[1]

        # 写入文件
        file.seek(0)  # 因为之前获取md5时读取过文件，所以这里要将指针定位到文件头
        __write_file(photo_fullpath, file)

        # 创建缩略图
        thumbnail = __create_thumbnail(userid, photo_fullpath)
        thumbnail_fullpath = thumbnail[1]

        # 获取照片的尺寸
        im = Image.open(photo_fullpath)  # 打开原始照片文件
        im_width = im.width
        im_height = im.height

        # 获取照片的Exif信息
        exif = __get_exif(photo_fullpath, request.POST['dt'])
        # pprint.pprint(exif)

        # 写入照片数据库
        photo_uuid = str(uuid.uuid1()).replace('-', '')  # 生成照片唯一序列号
        photo = Photo()
        photo.uuid = photo_uuid
        photo.userid = userid
        photo.path = file_path
        photo.path_thumbnail = thumbnail[0]
        photo.name = os.path.split(photo_fullpath)[1]
        photo.md5 = file_md5
        photo.size = file.size
        photo.width = im_width
        photo.height = im_height
        photo.exif_datetime = exif['DateTime']
        photo.exif_make = exif['Make']
        photo.exif_model = exif['Model']
        photo.exif_lensmodel = exif['LensModel']
        photo.exif_fnumber = exif['FNumber']
        photo.exif_exposuretime = exif['ExposureTime']
        photo.exif_isospeedratings = exif['ISOSpeedRatings']
        photo.exif_focallength = exif['FocalLength']
        photo.exif_gpslatitude = exif['GPSLatitude']
        photo.exif_gpslatituderef = exif['GPSLatitudeRef']
        photo.exif_gpslongitude = exif['GPSLongitude']
        photo.exif_gpslongituderef = exif['GPSLongitudeRef']
        photo.save()

        # 获取并写入照片的位置信息
        if exif['GPSLatitude'] and exif['GPSLongitude']:
            location = __get_address_from_gps(exif['GPSLatitude'], exif['GPSLatitudeRef'], exif['GPSLongitude'],
                                              exif['GPSLongitudeRef'])
            Address.objects.filter(uuid=photo_uuid).delete()  # 先删除再插入
            address = Address()
            address.uuid = photo_uuid
            address.lat = location['lat']
            address.lng = location['lng']
            address.address = location['formatted_address']
            address.country = location['country']
            address.province = location['province']
            address.city = location['city']
            address.district = location['district']
            address.town = location['town']
            address.save()

        return JsonResponse(response, status=200)
    except Exception as e:
        traceback.print_exc()  # 输出详细的错误信息
        transaction.savepoint_rollback(save_tag)  # 回滚数据库事务
        if photo_fullpath and os.path.exists(photo_fullpath):  # 出错时删除可能已经上传的文件
            os.remove(photo_fullpath)
        if thumbnail_fullpath and os.path.exists(thumbnail_fullpath):  # 出错时删除可能已经生成的缩略图
            os.remove(thumbnail_fullpath)
        response['msg'] = str(e)
        return JsonResponse(response, status=500)


def __write_file(full_path, file):
    """写入文件"""
    with open(full_path, 'wb') as f:  # wb表示写二进制文件
        if file.multiple_chunks():  # 判断文件是否足够大，一般为2.5M
            for content in file.chunks():  # 返回一个生成器对象，当multiple_chunks()为True时应该使用这个方法来代替read()
                f.write(content)
        else:
            data = file.read()
            f.write(data)


def __get_file_md5(file):
    """获取文件的md5值"""
    if file.multiple_chunks():  # 超过2.5M的大文件
        m = hashlib.md5()  # 创建md5对象
        for content in file.chunks():
            m.update(content)
        return m.hexdigest()
    else:  # 小文件
        data = file.read()
        return hashlib.md5(data).hexdigest()


def __create_thumbnail(userid, full_path):
    """创建照片缩略图"""
    im = Image.open(full_path)  # 打开原始照片文件
    im.thumbnail((500, 500))  # 创建大小不超过指定值的缩略图
    # 根据当前日期创建文件夹 /photos/thumbnail/{userid}/年/月/日
    now = datetime.now()  # 当前时间，用于创建目录
    file_path = os.path.join('photos', 'thumbnail', userid, now.strftime('%Y'), now.strftime('%m'),
                             now.strftime('%d'))  # 相对路径
    real_path = os.path.join(settings.BASE_DIR, file_path)  # 物理路径
    if not os.path.exists(real_path):  # 如果目标文件夹不存在则创建
        os.makedirs(real_path, exist_ok=True)
    file_name = os.path.split(full_path)[1]
    full_path = os.path.join(real_path, file_name)  # 完整路径
    im.save(full_path)  # 保存缩略图
    return file_path, full_path


def __get_exif(full_path: str, dt: str):
    """获取照片的exif信息"""
    exif = {
        'DateTime': dt,  # 拍摄时间（默认取文件最后一次修改时间）
        'Make': '',  # 相机制造商
        'Model': '',  # 相机型号
        'LensModel': '',  # 镜头信息
        'FNumber': '',  # 光圈值
        'ExposureTime': '',  # 曝光时间
        'ISOSpeedRatings': '',  # ISO感光度
        'FocalLength': '',  # 拍摄焦距，单位毫米
        'GPSLatitude': '',  # GPS经度
        'GPSLatitudeRef': 'N',  # 缺省设置为北半球
        'GPSLongitude': '',  # GPS纬度
        'GPSLongitudeRef': 'E',   # 缺省设置为东半球
    }
    with open(full_path, 'rb') as f:
        tags = exifread.process_file(f, details=False)
        for tag in tags.keys():
            # print(tag, ":", tags[tag])
            if re.match(r'^Image DateTime$', tag, re.IGNORECASE):
                exif['DateTime'] = str(tags[tag]).replace(':', '-', 2)
            elif re.match(r'^EXIF DateTimeOriginal$', tag, re.IGNORECASE):
                exif['DateTime'] = str(tags[tag]).replace(':', '-', 2)
            if re.match(r'^Image Make$', tag, re.IGNORECASE):
                exif['Make'] = str(tags[tag])
            if re.match(r'^Image Model$', tag, re.IGNORECASE):
                exif['Model'] = str(tags[tag])
            if re.match(r'^EXIF LensModel$', tag, re.IGNORECASE):
                exif['LensModel'] = str(tags[tag])
            if re.match(r'^EXIF FNumber$', tag, re.IGNORECASE):
                exif['FNumber'] = str(tags[tag])
                if '/' in exif['FNumber']:  # 如果光圈值是9/5格式，则换算成小数
                    exif['FNumber'] = str(round(eval(str(tags[tag])), 1))
            if re.match(r'^EXIF ExposureTime$', tag, re.IGNORECASE):
                exif['ExposureTime'] = str(tags[tag])
            if re.match(r'^EXIF ISOSpeedRatings$', tag, re.IGNORECASE):
                exif['ISOSpeedRatings'] = str(tags[tag])
            if re.match(r'^EXIF FocalLength$', tag, re.IGNORECASE):
                exif['FocalLength'] = str(tags[tag])
            if re.match(r'^GPS GPSLatitude$', tag, re.IGNORECASE):
                if str(tags[tag]) != '[0, 0, 0]' and str(tags[tag]) != '[0/0, 0/0, 0/0]':  # 处理无效值
                    exif['GPSLatitude'] = str(tags[tag])
            if re.match(r'GPS GPSLatitudeRef$', tag, re.IGNORECASE):
                exif['GPSLatitudeRef'] = str(tags[tag])
            if re.match(r'^GPS GPSLongitude$', tag, re.IGNORECASE):
                if str(tags[tag]) != '[0, 0, 0]' and str(tags[tag]) != '[0/0, 0/0, 0/0]':  # 处理无效值
                    exif['GPSLongitude'] = str(tags[tag])
            if re.match(r'^GPS GPSLongitudeRef$', tag, re.IGNORECASE):
                exif['GPSLongitudeRef'] = str(tags[tag])
    return exif


def __get_address_from_gps(lat, lat_ref, lng, lng_ref):
    """根据gps坐标获取位置信息"""
    ak = 'OoD6BEoc77sczG45r8Wfw1wfeMuCM7dW'
    # 纬度
    deg, minu, sec = [x.replace(' ', '') for x in lat[1:-1].split(',')]
    lat = __convert_gps_to_decimal(deg, minu, sec, lat_ref)
    # 经度
    deg, minu, sec = [x.replace(' ', '') for x in lng[1:-1].split(',')]
    lng = __convert_gps_to_decimal(deg, minu, sec, lng_ref)
    # lat = '31.225696563611'
    # lng = '121.49884033194'
    baidu_map_api = 'http://api.map.baidu.com/reverse_geocoding/v3/?ak={0}&output=json&coordtype=wgs84ll' \
                    '&location={1},{2}'.format(ak, lat, lng)
    response = requests.get(baidu_map_api)
    result = response.json()  # 获取响应数据，并解析JSON，转化为python字典

    if result['status'] != 0:  # 接口调用失败
        raise Exception(result['message'])  # 抛出异常
    location = {
        'status': result['status'],
        'lat': result['result']['location']['lat'],
        'lng': result['result']['location']['lng'],
        'formatted_address': result['result']['formatted_address'],
        'country': result['result']['addressComponent']['country'],
        'province': result['result']['addressComponent']['province'],
        'city': result['result']['addressComponent']['city'],
        'district': result['result']['addressComponent']['district'],
        'town': result['result']['addressComponent']['town'],
    }
    return location


def __convert_gps_to_decimal(*gps):
    """将经纬度转换为小数形式"""
    # 度
    if '/' in gps[0]:
        deg = gps[0].split('/')
        if deg[0] == '0' or deg[1] == '0':
            gps_d = 0
        else:
            gps_d = float(deg[0]) / float(deg[1])
    else:
        gps_d = float(gps[0])
    # 分
    if '/' in gps[1]:
        minu = gps[1].split('/')
        if minu[0] == '0' or minu[1] == '0':
            gps_m = 0
        else:
            gps_m = (float(minu[0]) / float(minu[1])) / 60
    else:
        gps_m = float(gps[1]) / 60
    # 秒
    if '/' in gps[2]:
        sec = gps[2].split('/')
        if sec[0] == '0' or sec[1] == '0':
            gps_s = 0
        else:
            gps_s = (float(sec[0]) / float(sec[1])) / 3600
    else:
        gps_s = float(gps[2]) / 3600

    decimal_gps = gps_d + gps_m + gps_s
    # 如果是南半球或是西半球
    if gps[3] == 'W' or gps[3] == 'S' or gps[3] == "83" or gps[3] == "87":
        return str(decimal_gps * -1)
    else:
        return str(decimal_gps)
