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
from backend_api.models import Photo, Address, Album, AlbumPhoto
from backend_api.views.album import album_auto_cover
from backend_api.views.people import people_face_detect


@require_http_methods(['POST'])  # django内置的视力装饰器，这行表示只能通过POST方法访问
@transaction.atomic  # 数据库事务处理
def upload_photo(request):
    """上传文件"""
    response = {
        'success': [],  # 上传成功的文件
        'error': []  # 上传失败的文件
    }
    try:
        userid = request.GET.get('userid')  # 当前登录的用户id
        call_mode = request.GET.get('call_mode')  # 调用模式
        album_uuid = request.GET.get('album_uuid')  # 影集uuid
        file_list = request.FILES.getlist('file')  # 前端上传的文件对象

        for file in file_list:
            save_tag = transaction.savepoint()  # 设置保存点，用于数据库事务回滚
            fullpath_original = ''  # 照片的完整路径
            fullpath_thumbnail_s = ''  # 小缩略图的完整路径
            fullpath_thumbnail_l = ''  # 大缩略图的完整路径
            try:
                # 获取文件md5值，然后检查是否已经存在，如果是在照片中添加就跳过，如果是在影集中添加则写入
                file_md5 = __get_file_md5(file)
                photo_uuid = str(uuid.uuid1()).replace('-', '')  # 生成照片唯一序列号
                photo = Photo.objects.filter(md5=file_md5).first()  # 表过滤
                if photo:
                    if call_mode == 'album':
                        album_photo = AlbumPhoto()
                        album_photo.uuid = str(uuid.uuid1()).replace('-', '')
                        album_photo.album_uuid = Album.objects.get(uuid=album_uuid)
                        album_photo.photo_uuid = Photo.objects.get(uuid=photo.uuid)
                        album_photo.save()
                        response['success'].append({'name': file.name})
                        continue
                    else:
                        response['error'].append({'name': file.name, 'msg': '照片已存在，跳过'})
                        continue

                # 存储路径：/photos/{userid}/original/年/月/日/md5值前2位/md5值第3至4位
                now = datetime.now()  # 当前时间，用于创建目录
                path_original = os.path.join('photos', userid, 'original', now.strftime('%Y'), now.strftime('%m'),
                                             now.strftime('%d'), file_md5[0:2], file_md5[2:4])  # 相对路径
                realpath_original = os.path.join(settings.BASE_DIR, path_original)  # 物理路径
                if not os.path.exists(realpath_original):  # 如果目标文件夹不存在则创建
                    os.makedirs(realpath_original, exist_ok=True)

                # 检查当前目录下是否有同名文件，如果存在则重命名
                file_name = file.name  # 原始文件名
                file_extension_name = os.path.splitext(file_name)[1]  # 原始文件扩展名
                file_new_name = photo_uuid + file_extension_name
                # 包含路径的完整文件名
                fullpath_original = os.path.join(realpath_original, file_new_name)

                # 写入原始文件
                file.seek(0)  # 因为之前获取md5时读取过文件，所以这里要将指针定位到文件头
                __write_file(fullpath_original, file)

                # 创建缩略图
                thumbnail = __create_thumbnail(userid, fullpath_original, path_original, file_md5)
                fullpath_thumbnail_s = thumbnail[1]  # 小缩略图的完整路径
                fullpath_thumbnail_l = thumbnail[3]  # 大缩略图的完整路径

                # 获取照片的尺寸
                im = Image.open(fullpath_original)  # 打开原始照片文件
                im_width = im.width
                im_height = im.height
                im.close()

                # 获取照片的Exif信息
                exif = __get_exif(fullpath_original, request.POST.get(file.name))
                # pprint.pprint(exif)

                # 写入照片数据表
                photo = Photo()
                photo.uuid = photo_uuid
                photo.userid = userid
                photo.path_original = path_original.replace('\\', '/')
                photo.path_thumbnail_s = thumbnail[0].replace('\\', '/')
                photo.path_thumbnail_l = thumbnail[2].replace('\\', '/')
                photo.name = file_new_name
                photo.name_original = file_name
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
                    address.uuid = Photo.objects.get(uuid=photo_uuid)
                    address.lat = location['lat']
                    address.lng = location['lng']
                    address.address = location['formatted_address']
                    address.country = location['country']
                    address.province = location['province']
                    address.city = location['city']
                    address.district = location['district']
                    address.town = location['town']
                    address.save()

                # 写入影集数据表
                if call_mode == 'album':
                    album_photo = AlbumPhoto()
                    album_photo.uuid = str(uuid.uuid1()).replace('-', '')
                    album_photo.album_uuid = Album.objects.get(uuid=album_uuid)
                    album_photo.photo_uuid = Photo.objects.get(uuid=photo_uuid)
                    album_photo.save()
                response['success'].append({'name': file.name})
            except Exception as e:
                traceback.print_exc()  # 输出详细的错误信息
                transaction.savepoint_rollback(save_tag)  # 回滚数据库事务
                response['error'].append({'name': file.name, 'msg': str(e)})
                if fullpath_original and os.path.exists(fullpath_original):  # 出错时删除可能已经上传的文件
                    os.remove(fullpath_original)
                if fullpath_thumbnail_s and os.path.exists(fullpath_thumbnail_s):  # 出错时删除可能已经生成的缩略图
                    os.remove(fullpath_thumbnail_s)
                if fullpath_thumbnail_l and os.path.exists(fullpath_thumbnail_l):
                    os.remove(fullpath_thumbnail_l)
                continue

        # 所有文件上传完成之后，设置影集封面
        if call_mode == 'album':
            album_auto_cover(album_uuid)

        people_face_detect.delay(userid)  # 发送人脸检测任务

        return JsonResponse(response, status=200)
    except Exception as e:
        traceback.print_exc()  # 输出详细的错误信息
        transaction.savepoint_rollback(save_tag)  # 回滚数据库事务
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


def __create_thumbnail(userid, fullpath_original, path_original, file_md5):
    """创建照片缩略图"""
    now = datetime.now()  # 当前时间，用于创建目录
    im = None
    try:
        im = Image.open(fullpath_original)  # 打开原始照片文件
        file_name = os.path.split(fullpath_original)[1]
        # 大、小缩略图路径初始值均为原图路径
        path_thumbnail_s = path_original
        fullpath_thumbnail_s = fullpath_original
        path_thumbnail_l = path_original
        fullpath_thumbnail_l = fullpath_original
        # 创建小尺寸缩略图
        if im.width > 500 or im.height > 500:
            im.thumbnail((500, 500))  # 创建大小不超过指定值的缩略图
            # 存储路径：/photos/{userid}/thumbnail/s/年/月/日/md5值前2位/md5值第3至4位
            path_thumbnail_s = os.path.join('photos', userid, 'thumbnail', 's', now.strftime('%Y'), now.strftime('%m'),
                                            now.strftime('%d'), file_md5[0:2], file_md5[2:4])  # 相对路径
            realpath_thumbnail_s = os.path.join(settings.BASE_DIR, path_thumbnail_s)  # 物理路径
            if not os.path.exists(realpath_thumbnail_s):  # 如果目标文件夹不存在则创建
                os.makedirs(realpath_thumbnail_s, exist_ok=True)
            fullpath_thumbnail_s = os.path.join(realpath_thumbnail_s, file_name)  # 完整路径
            im.save(fullpath_thumbnail_s)  # 保存缩略图

        # 创建大尺寸缩略图
        im = Image.open(fullpath_original)  # 重新打开原始照片文件
        if im.width > 1920 or im.height > 1920:
            im.thumbnail((1920, 1920))  # 创建大小不超过指定值的缩略图
            # 存储路径：/photos/{userid}/thumbnail/l/年/月/日/md5值前2位/md5值第3至4位
            path_thumbnail_l = os.path.join('photos', userid, 'thumbnail', 'l', now.strftime('%Y'), now.strftime('%m'),
                                            now.strftime('%d'), file_md5[0:2], file_md5[2:4])  # 相对路径
            realpath_thumbnail_l = os.path.join(settings.BASE_DIR, path_thumbnail_l)  # 物理路径
            if not os.path.exists(realpath_thumbnail_l):  # 如果目标文件夹不存在则创建
                os.makedirs(realpath_thumbnail_l, exist_ok=True)
            fullpath_thumbnail_l = os.path.join(realpath_thumbnail_l, file_name)  # 完整路径
            im.save(fullpath_thumbnail_l)  # 保存缩略图

        # 依次返回小尺寸缩略图目录和完整路径以及大尺寸缩略图目录和完整路径
        return path_thumbnail_s, fullpath_thumbnail_s, path_thumbnail_l, fullpath_thumbnail_l
    except Exception as e:
        traceback.print_exc()  # 输出详细的错误信息
        raise Exception(str(e))
    finally:
        if im:
            im.close()


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
    ak = settings.BMAP_AK
    # 纬度
    deg, minu, sec = [x.replace(' ', '') for x in lat[1:-1].split(',')]
    lat = __convert_gps_to_decimal(deg, minu, sec, lat_ref)
    # 经度
    deg, minu, sec = [x.replace(' ', '') for x in lng[1:-1].split(',')]
    lng = __convert_gps_to_decimal(deg, minu, sec, lng_ref)
    # lat = '31.225696563611'
    # lng = '121.49884033194'
    # 全球逆地理编码服务
    baidu_map_api = 'http://api.map.baidu.com/reverse_geocoding/v3/?ak={0}&output=json&coordtype=wgs84ll' \
                    '&location={1},{2}'.format(ak, lat, lng)
    response = requests.get(baidu_map_api)
    result = response.json()  # 获取响应数据，并解析JSON，转化为python字典

    if result['status'] != 0:  # 接口调用失败
        raise Exception(result['message'])  # 抛出异常
    location = {
        'status': result['status'],
        'lat': lat,
        'lng': lng,
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
