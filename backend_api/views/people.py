import os
import uuid
import json
from datetime import datetime
import traceback  # 输出更详细的错误信息
import numpy
from PIL import Image  # 图像处理
import face_recognition
from celery import task
from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from backend_api.models import User, Photo, People, PeopleFace


@task  # 后台任务
@transaction.atomic  # 数据库事务处理
def people_face_detect(userid):
    """人脸检测"""
    # 检查当前用户是否正在执行后台操作，如果是则忽略本次请求
    user = User.objects.get(userid=userid)
    if user.celery_working:
        print('有其他celery任务正在执行，忽略本次请求...')
        return
    else:
        user.celery_working = True
        user.save()
    try:
        # 从Photo中获取没有执行人脸检测的照片列表
        photos = Photo.objects.filter(userid=userid, is_detect_face=False)
        total = len(photos)
        for index, photo in enumerate(photos):
            print('正在执行用户' + userid + '的人脸检测：' + str(index + 1) + '/' + str(total) + ' ' + str(
                round((index + 1) / total * 100, 2)) + '%')
            save_tag = transaction.savepoint()  # 设置保存点，用于数据库事务回滚
            fullpath_original = ''  # 人脸照片的完整路径
            fullpath_thumbnail = ''  # 缩略图的完整路径
            try:
                photo_path = os.path.join(settings.BASE_DIR, photo.path_thumbnail_l, photo.name)  # 照片绝对路径
                file_md5 = photo.md5  # 原始照片的md5值
                face_numpy = face_recognition.load_image_file(photo_path)  # 将图像文件加载到numpy数组中
                face_locations = face_recognition.face_locations(face_numpy)  # 返回图像中人脸边界框的数组
                for face_location in face_locations:
                    top, right, bottom, left = face_location
                    face_image = Image.fromarray(face_numpy[top:bottom, left:right])
                    # 忽略掉小于50像素的人脸
                    if face_image.width <= 50 or face_image.height <= 50:
                        photo.is_detect_face = True
                        photo.save()
                        continue
                    file_name = str(uuid.uuid1()).replace('-', '')  # 生成人像文件名

                    # 存储人脸图，路径：/photos/{userid}/people/original/年/月/日/md5值前2位/md5值第3至4位
                    now = datetime.now()  # 当前时间，用于创建目录
                    path_original = os.path.join('photos', userid, 'people', 'original', now.strftime('%Y'),
                                                 now.strftime('%m'), now.strftime('%d'), file_md5[0:2],
                                                 file_md5[2:4])  # 相对路径
                    realpath_original = os.path.join(settings.BASE_DIR, path_original)  # 物理路径
                    if not os.path.exists(realpath_original):  # 如果目标文件夹不存在则创建
                        os.makedirs(realpath_original, exist_ok=True)
                    fullpath_original = os.path.join(realpath_original, file_name + '.jpg')
                    face_image.save(fullpath_original, format='JPEG')

                    # 创建人脸缩略图，路径初始值与原图相同
                    path_thumbnail = path_original
                    fullpath_thumbnail = fullpath_original
                    if face_image.width > 500 or face_image.height > 500:
                        face_image.thumbnail((500, 500))  # 创建大小不超过指定值的缩略图
                        # 存储路径：/photos/{userid}/people/thumbnail/s/年/月/日/md5值前2位/md5值第3至4位
                        path_thumbnail = os.path.join('photos', userid, 'people', 'thumbnail',
                                                      now.strftime('%Y'), now.strftime('%m'), now.strftime('%d'),
                                                      file_md5[0:2], file_md5[2:4])  # 相对路径
                        realpath_thumbnail = os.path.join(settings.BASE_DIR, path_thumbnail)  # 物理路径
                        if not os.path.exists(realpath_thumbnail):  # 如果目标文件夹不存在则创建
                            os.makedirs(realpath_thumbnail, exist_ok=True)
                        fullpath_thumbnail = os.path.join(realpath_thumbnail, file_name + '.jpg')  # 完整路径
                        face_image.save(fullpath_thumbnail, format='JPEG')  # 保存缩略图

                    # 返回图像中的128维面部编码
                    face_image = face_recognition.load_image_file(fullpath_original)
                    face_encodings = face_recognition.face_encodings(face_image)
                    if len(face_encodings) > 0:
                        # 写人脸数据表
                        people_face = PeopleFace()
                        people_face.uuid = file_name
                        people_face.photo_uuid = Photo.objects.get(uuid=photo.uuid)
                        people_face.path = path_original.replace('\\', '/')
                        people_face.path_thumbnail = path_thumbnail.replace('\\', '/')
                        people_face.name = file_name + '.jpg'
                        people_face.encoding = __encoding_face_str(face_encodings[0])
                        people_face.save()
                    else:
                        # 如果无法获取128维面部编码，则删除人脸图像
                        if fullpath_original and os.path.exists(fullpath_original):  # 出错时删除可能已经生成的文件
                            os.remove(fullpath_original)
                        if fullpath_thumbnail and os.path.exists(fullpath_thumbnail):  # 出错时删除可能已经生成的缩略图
                            os.remove(fullpath_thumbnail)
            except Exception as e:
                print(str(e))
                traceback.print_exc()  # 输出详细的错误信息
                transaction.savepoint_rollback(save_tag)  # 回滚数据库事务
                if fullpath_original and os.path.exists(fullpath_original):  # 出错时删除可能已经生成的文件
                    os.remove(fullpath_original)
                if fullpath_thumbnail and os.path.exists(fullpath_thumbnail):  # 出错时删除可能已经生成的缩略图
                    os.remove(fullpath_thumbnail)
                continue
            finally:
                # 写入Photo表的人脸检测标志
                photo.is_detect_face = True
                photo.save()

        # 再次检查Photo中是否有没有执行人脸检测的照片
        photos = Photo.objects.filter(userid=userid, is_detect_face=False)
        if len(photos) > 0:
            people_face_detect()
        print('celery任务执行成功...')
    except Exception as e:
        print(str(e))
        traceback.print_exc()  # 输出详细的错误信息
    finally:
        # 重置当前用户的工作状态
        user = User.objects.get(userid=userid)
        user.celery_working = False
        user.save()


@require_http_methods(['POST'])
@transaction.atomic  # 数据库事务处理
def people_add_feature(request):
    """新增人物特征"""
    save_tag = transaction.savepoint()  # 设置保存点，用于数据库事务回滚
    response = {}
    try:
        request_data = json.loads(request.body)
        userid = request_data.get('userid')  # 当前用户id
        face_uuid = request_data.get('face_uuid')  # 人脸uuid
        name = request_data.get('name')  # 人物姓名
        # 如果人物不存在则创建
        people_uuid = str(uuid.uuid1()).replace('-', '')
        people = People.objects.filter(name=name)
        if len(people) == 0:
            people = People()
            people.uuid = people_uuid
            people.userid = userid
            people.name = name
            people.save()
        else:
            people_uuid = people[0].uuid
        # 写入人脸对应的人物
        people_face = PeopleFace.objects.get(uuid=face_uuid)
        people_face.people_uuid = People.objects.get(uuid=people_uuid)
        people_face.is_feature = True  # 设置为人物特征
        people_face.save()
        # 设置人物封面
        people_auto_cover(people_uuid)
        # 进行人脸识别
        # TODO 添加人脸识别功能
        return JsonResponse({}, safe=False, status=200)
    except Exception as e:
        traceback.print_exc()  # 输出详细的错误信息
        transaction.savepoint_rollback(save_tag)  # 回滚数据库事务
        response['msg'] = str(e)
        return JsonResponse(response, status=500)


@require_http_methods(['POST'])
@transaction.atomic  # 数据库事务处理
def people_remove_feature(request):
    """删除人物特征"""
    save_tag = transaction.savepoint()  # 设置保存点，用于数据库事务回滚
    response = {}
    try:
        request_data = json.loads(request.body)
        face_uuid_list = request_data.get('face_uuid')  # 人脸uuid
        # 获取人脸对应的人物uuid
        people = PeopleFace.objects.filter(uuid__in=face_uuid_list).first()
        people_uuid = people.people_uuid.uuid
        # 删除人脸对应的人物
        PeopleFace.objects.filter(uuid__in=face_uuid_list).update(people_uuid=None, is_feature=False)
        # 如果有人物封面使用了该人脸，则重新生成人物封面
        People.objects.filter(cover__in=face_uuid_list).update(cover_from='auto')
        people_auto_cover(people_uuid)
        people_check(people_uuid)  # 人物检测
        return JsonResponse({}, safe=False, status=200)
    except Exception as e:
        traceback.print_exc()  # 输出详细的错误信息
        transaction.savepoint_rollback(save_tag)  # 回滚数据库事务
        response['msg'] = str(e)
        return JsonResponse(response, status=500)


def people_auto_cover(people_uuid):
    """自动设置指定人物的封面"""
    people = People.objects.get(uuid=people_uuid)
    if people.cover_from == 'auto':
        people_face = PeopleFace.objects.filter(people_uuid=people_uuid, is_active=True).order_by('-input_date').first()
        if people_face:
            People.objects.filter(uuid=people_uuid).update(cover=people_face.uuid)
        else:
            People.objects.filter(uuid=people_uuid).update(cover=None)


def people_check(people_uuid):
    """人物检测：保证至少有1个特征，如果没有人脸，则删除该人物"""
    people_face = PeopleFace.objects.filter(people_uuid=people_uuid, is_active=True)
    if len(people_face) == 0:
        People.objects.filter(uuid=people_uuid).delete()
    else:
        people_feature = PeopleFace.objects.filter(people_uuid=people_uuid, is_active=True, is_feature=True)
        if len(people_feature) == 0:
            feature = PeopleFace.objects.filter(people_uuid=people_uuid, is_active=True).order_by('-input_date').first()
            feature.is_feature = True
            feature.save()


def __encoding_face_str(face_encoding):
    """将面部编码转换为字符串"""
    encoding_array_list = face_encoding.tolist()  # 将numpy array类型转化为列表
    encoding_str_list = [str(i) for i in encoding_array_list]  # 将列表里的元素转化为字符串
    encoding_str = ','.join(encoding_str_list)  # 拼接列表里的字符串
    return encoding_str


def __decoding_face_str(encoding_str):
    """将字符串转换为面部编码"""
    # 将字符串转为numpy ndarray类型，即矩阵
    dlist = encoding_str.strip(' ').split(',')  # 转换成一个list
    dfloat = list(map(float, dlist))  # 将list中str转换为float
    face_encoding = numpy.array(dfloat)
    return face_encoding
