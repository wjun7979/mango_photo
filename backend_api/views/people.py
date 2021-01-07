import os
import uuid
import json
import time
import base64
import requests
from datetime import datetime
import traceback  # 输出更详细的错误信息
import pprint
from PIL import Image  # 图像处理
from celery import task
from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from django.db.models import Count, F, Q
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from backend_api.common.date_encoder import DateEncoder
from backend_api.models import User, Photo, People, PeopleFace, PeopleFaceExcept


@task  # 后台任务
def people_face_detect(userid):
    """人脸检测"""
    print('开始执行用户' + userid + '的人脸检测任务...')

    # 百度AI的相关参数
    access_token = baidu_ai_get_token()  # 获取鉴权token
    api = "https://aip.baidubce.com/rest/2.0/face/v3/detect" + "?access_token=" + access_token
    headers = {'content-type': 'application/json'}

    # 从Photo中获取没有执行人脸检测的照片列表
    photos = Photo.objects.filter(userid=userid, is_detect_face=False)
    total = len(photos)
    for index, photo in enumerate(photos):
        print('正在执行用户' + userid + '的人脸检测：' + str(index + 1) + '/' + str(total) + ' ' + str(
            round((index + 1) / total * 100, 2)) + '%')
        fullpath_original = ''  # 人脸照片的完整路径
        fullpath_thumbnail = ''  # 缩略图的完整路径
        try:
            with transaction.atomic():
                photo_path = os.path.join(settings.BASE_DIR, photo.path_thumbnail_l, photo.name)  # 照片绝对路径
                with open(photo_path, 'rb') as f:
                    photo_data = f.read()
                    photo_base64_data = base64.b64encode(photo_data)  # base64编码
                file_md5 = photo.md5  # 原始照片的md5值
                # 调用百度AI的api
                params = {
                    'image': photo_base64_data,
                    'image_type': 'BASE64',
                    'max_face_num': 10,  # 最多处理人脸的数目
                    # 年龄,照片质量,颜值,表情,是否戴眼镜,情绪,口罩识别
                    'face_field': 'age,quality,beauty,expression,glasses,emotion,mask'
                }
                res = requests.post(api, data=params, headers=headers)
                result = res.json()  # 获取响应数据，并解析JSON，转化为python字典
                res.close()
                if result['error_code'] != 0:  # 接口调用失败
                    raise Exception(
                        str(result['error_code']) + ' ' + result['error_msg'] + '. photo_uuid:' + photo.uuid)
                for face in result['result']['face_list']:
                    # 人脸必须满足以下条件:人脸置信度为100%；大小在50px以上；模糊程度小于0.7；光照程度大于40；人脸完整度100%
                    if face['face_probability'] == 1 and face['location']['width'] > 50 and face['location']['height'] > 50 and \
                            face['quality']['blur'] < 0.7 and face['quality']['illumination'] > 40 and \
                            face['quality']['completeness'] == 1:
                        # pprint.pprint(face)
                        location = face['location']  # 人脸的位置信息
                        left = round(location['left'], 2)
                        top = round(location['top'], 2)
                        right = round(location['left'] + location['width'], 2)
                        bottom = round(location['top'] + location['height'], 2)
                        im = Image.open(photo_path)
                        # 照片是否需要旋转
                        rotation = location['rotation']
                        if rotation != 0:
                            if rotation < 0:
                                rotation = 360 - abs(rotation)
                            im = im.rotate(rotation, expand=False, center=(left, top))  # 围绕检测出的左上角坐标逆时针旋转
                        # 裁剪得到人脸
                        im = im.crop((left, top, right, bottom))

                        # 存储人脸图，路径：/photos/{userid}/people/original/年/月/日/md5值前2位/md5值第3至4位
                        file_name = str(uuid.uuid1()).replace('-', '')  # 生成人像文件名
                        now = datetime.now()  # 当前时间，用于创建目录
                        path_original = os.path.join('photos', userid, 'people', 'original', now.strftime('%Y'),
                                                     now.strftime('%m'), now.strftime('%d'), file_md5[0:2],
                                                     file_md5[2:4])  # 相对路径
                        realpath_original = os.path.join(settings.BASE_DIR, path_original)  # 物理路径
                        if not os.path.exists(realpath_original):  # 如果目标文件夹不存在则创建
                            os.makedirs(realpath_original, exist_ok=True)
                        fullpath_original = os.path.join(realpath_original, file_name + '.jpg')
                        im.save(fullpath_original, format='JPEG')

                        # 创建人脸缩略图，路径初始值与原图相同
                        path_thumbnail = path_original
                        fullpath_thumbnail = fullpath_original
                        if im.width > 500 or im.height > 500:
                            im.thumbnail((500, 500))  # 创建大小不超过指定值的缩略图
                            # 存储路径：/photos/{userid}/people/thumbnail/s/年/月/日/md5值前2位/md5值第3至4位
                            path_thumbnail = os.path.join('photos', userid, 'people', 'thumbnail',
                                                          now.strftime('%Y'), now.strftime('%m'), now.strftime('%d'),
                                                          file_md5[0:2], file_md5[2:4])  # 相对路径
                            realpath_thumbnail = os.path.join(settings.BASE_DIR, path_thumbnail)  # 物理路径
                            if not os.path.exists(realpath_thumbnail):  # 如果目标文件夹不存在则创建
                                os.makedirs(realpath_thumbnail, exist_ok=True)
                            fullpath_thumbnail = os.path.join(realpath_thumbnail, file_name + '.jpg')  # 完整路径
                            im.save(fullpath_thumbnail, format='JPEG')  # 保存缩略图
                        im.close()

                        # 写人脸数据表
                        people_face = PeopleFace()
                        people_face.uuid = file_name
                        people_face.userid = User.objects.get(userid=userid)
                        people_face.photo_uuid = Photo.objects.get(uuid=photo.uuid)
                        people_face.path = path_original.replace('\\', '/')
                        people_face.path_thumbnail = path_thumbnail.replace('\\', '/')
                        people_face.name = file_name + '.jpg'
                        people_face.location = location
                        people_face.ai_age = face['age']
                        people_face.ai_beauty = face['beauty']
                        if face['expression']['probability'] > 0.9:  # 表情 probability:置信度
                            people_face.ai_expression = face['expression']['type']
                        if face['emotion']['probability'] > 0.9:  # 情绪
                            people_face.ai_emotion = face['emotion']['type']
                        if face['glasses']['probability'] > 0.9:  # 眼镜
                            people_face.ai_glasses = face['glasses']['type']
                        if face['mask']['probability'] > 0.9:  # 口罩
                            people_face.ai_mask = face['mask']['type']
                        people_face.face_token = face['face_token']
                        people_face.save()
        except Exception as e:
            print(str(e))
            if fullpath_original and os.path.exists(fullpath_original):  # 出错时删除可能已经生成的文件
                os.remove(fullpath_original)
            if fullpath_thumbnail and os.path.exists(fullpath_thumbnail):  # 出错时删除可能已经生成的缩略图
                os.remove(fullpath_thumbnail)
            time.sleep(0.5)
            continue
        finally:
            # 写入Photo表的人脸检测标志
            Photo.objects.filter(uuid=photo.uuid).update(is_detect_face=True)
        time.sleep(0.5)  # 暂停一会儿，避免qps超限额
    print('用户' + userid + '的人脸检测任务执行成功...')
    # 执行人脸识别
    people_face_compare.delay(userid)


@task
def people_face_compare(userid):
    """人脸识别"""
    print('开始执行用户' + userid + '的人脸识别任务...')

    # 百度AI的相关参数
    access_token = baidu_ai_get_token()  # 获取鉴权token
    api = "https://aip.baidubce.com/rest/2.0/face/v3/multi-search" + "?access_token=" + access_token
    headers = {'content-type': 'application/json'}

    # 获取待识别的人脸列表
    # photos = Photo.objects.distinct().filter(peopleface__userid=userid, peopleface__people_uuid__isnull=True)
    photos = PeopleFace.objects
    photos = photos.filter(userid=userid, people_uuid__isnull=True, is_delete=False)
    photos = photos.values(p_uuid=F('photo_uuid__uuid'), p_path_thumbnail_l=F('photo_uuid__path_thumbnail_l'),
                           p_name=F('photo_uuid__name'))
    total = len(photos)
    for index, photo in enumerate(photos):
        print('正在执行用户' + userid + '的人脸识别：' + str(index + 1) + '/' + str(total) + ' ' + str(
            round((index + 1) / total * 100, 2)) + '%')
        try:
            with transaction.atomic():
                photo_path = os.path.join(settings.BASE_DIR, photo['p_path_thumbnail_l'], photo['p_name'])  # 照片绝对路径
                with open(photo_path, 'rb') as f:
                    photo_data = f.read()
                    photo_base64_data = base64.b64encode(photo_data)  # base64编码
                # 调用百度AI的api
                params = {
                    'image': photo_base64_data,
                    'image_type': 'BASE64',
                    'group_id_list': userid,
                    'max_face_num': 10,  # 最多处理人脸的数目
                }
                res = requests.post(api, data=params, headers=headers)
                result = res.json()  # 获取响应数据，并解析JSON，转化为python字典
                res.close()
                if result['error_code'] != 0:  # 接口调用失败
                    raise Exception(
                        str(result['error_code']) + ' ' + result['error_msg'] + '. photo_uuid:' + photo['p_uuid'])
                # pprint.pprint(result)
                for item in result['result']['face_list']:
                    people_face = PeopleFace.objects.filter(photo_uuid=photo['p_uuid'], face_token=item['face_token'])
                    if people_face:
                        for user in item['user_list']:
                            if user['score'] >= 80:  # 用户的匹配得分，推荐阈值80分
                                # 考虑人工排除项
                                face_except = PeopleFaceExcept.objects.filter(face_uuid=people_face[0].uuid,
                                                                              people_uuid=user['user_id'])
                                if len(face_except) == 0:
                                    people_face.update(people_uuid=People.objects.get(uuid=user['user_id']))
                                    break
        except Exception as e:
            print(str(e))
            time.sleep(0.5)
            continue
        time.sleep(0.5)  # 暂停一会儿，避免qps超限额
    print('用户' + userid + '的人脸识别任务执行成功...')


@require_http_methods(['GET'])
def people_list(request):
    """获取人物列表"""
    userid = request.GET.get('userid')
    peoples = People.objects.filter(userid=userid)
    peoples = peoples.values('uuid', 'name', cover_path=F('cover__path_thumbnail'), cover_name=F('cover__name'))
    peoples = peoples.annotate(photos=Count('peopleface__photo_uuid', distinct=True))
    peoples = peoples.annotate(faces=Count('peopleface'))
    peoples = peoples.annotate(features=Count('peopleface__feature_token'))
    peoples = peoples.order_by('-faces')
    response = json.loads(json.dumps(list(peoples), cls=DateEncoder))
    return JsonResponse(response, safe=False, status=200)


@require_http_methods(['GET'])
def people_get(request):
    """获取指定的人物信息"""
    people_uuid = request.GET.get('uuid')
    people = People.objects.values('uuid', 'name', cover_path=F('cover__path_thumbnail'),
                                   cover_name=F('cover__name'))
    people = people.annotate(photos=Count('peopleface__photo_uuid', distinct=True))
    people = people.annotate(faces=Count('peopleface'))
    people = people.annotate(features=Count('peopleface__feature_token'))
    people = people.filter(uuid=people_uuid).first()
    return JsonResponse(people, safe=False, status=200)


@require_http_methods(['POST'])
def people_add_face(request):
    """向人物中增加面孔"""
    response = {}
    request_data = json.loads(request.body)
    userid = request_data.get('userid')  # 当前用户id
    face_uuid = request_data.get('face_uuid')  # 人脸uuid
    name = request_data.get('name')  # 人物姓名
    is_feature = request_data.get('is_feature')  # 是否设为人物特征
    try:
        with transaction.atomic():  # 开启事务处理
            # 如果人物不存在则创建
            people_uuid = str(uuid.uuid1()).replace('-', '')
            people = People.objects.filter(name=name)
            if len(people) == 0:
                people = People()
                people.uuid = people_uuid
                people.userid = User.objects.get(userid=userid)
                people.name = name
                people.save()
            else:
                people_uuid = people[0].uuid
            # 写入人脸对应的人物
            people_face = PeopleFace.objects.get(uuid=face_uuid)
            people_face.people_uuid = People.objects.get(uuid=people_uuid)
            if is_feature:
                people_face.feature_token = 'wait...'
            people_face.save()
            # 删除人工排除项
            PeopleFaceExcept.objects.filter(face_uuid=face_uuid).delete()
            # 设置人物封面
            people_auto_cover(people_uuid)
    except Exception as e:
        traceback.print_exc()  # 输出详细的错误信息
        response['msg'] = str(e)
        return JsonResponse(response, status=500)
    # 向人脸库中注册照片
    if is_feature:
        baidu_ai_facelib_add.delay(face_uuid)
    return JsonResponse({}, safe=False, status=200)


@require_http_methods(['POST'])
def people_add_faces(request):
    """批量添加面孔"""
    response = {}
    try:
        with transaction.atomic():  # 开启事务处理
            request_data = json.loads(request.body)
            people_uuid = request_data.get('people_uuid')  # 人物uuid
            face_uuid_list = request_data.get('face_list')  # 人脸uuid

            # 写入人脸对应的人物
            PeopleFace.objects.filter(uuid__in=face_uuid_list).update(
                people_uuid=People.objects.get(uuid=people_uuid))

            # 删除人工排除项
            PeopleFaceExcept.objects.filter(face_uuid__in=face_uuid_list).delete()
            # 设置人物封面
            people_auto_cover(people_uuid)

            return JsonResponse({}, safe=False, status=200)
    except Exception as e:
        traceback.print_exc()  # 输出详细的错误信息
        response['msg'] = str(e)
        return JsonResponse(response, status=500)


@require_http_methods(['POST'])
def people_remove_face(request):
    """删除面孔"""
    request_data = json.loads(request.body)
    face_list = request_data.get('face_list')
    PeopleFace.objects.filter(uuid__in=face_list).update(is_delete=True)  # 修改删除标志
    return JsonResponse({}, safe=False, status=200)


@require_http_methods(['POST'])
def people_remove_name(request):
    """删除姓名"""
    response = {}
    try:
        with transaction.atomic():  # 开启事务处理
            request_data = json.loads(request.body)
            filter_type = request_data.get('filter_type')  # 过滤类型:face:按face_uuid; photo:按photo_uuid
            people_uuid = request_data.get('people_uuid')  # 人物uuid
            face_uuid_list = request_data.get('face_list')  # 人脸uuid
            # 如果是按照片来删除人脸，则根据photo_list来获取face_uuid_list
            if filter_type == 'photo':
                photo_uuid_list = request_data.get('photo_list')
                faces = PeopleFace.objects.filter(people_uuid=people_uuid, photo_uuid__in=photo_uuid_list)
                faces = faces.values('uuid')
                face_uuid_list = []
                for face in faces:
                    face_uuid_list.append(face['uuid'])

            for face_uuid in face_uuid_list:
                # 写入人工排除项，先删除再增加
                PeopleFaceExcept.objects.filter(face_uuid=face_uuid, people_uuid=people_uuid).delete()
                face_except = PeopleFaceExcept()
                face_except.uuid = str(uuid.uuid1()).replace('-', '')
                face_except.face_uuid = PeopleFace.objects.get(uuid=face_uuid)
                face_except.people_uuid = People.objects.get(uuid=people_uuid)
                face_except.save()

                # 在人脸库中删除照片
                people_face = PeopleFace.objects.get(uuid=face_uuid)
                if people_face.feature_token:
                    baidu_ai_facelib_delete.delay(people_face.userid.userid, people_face.people_uuid.uuid,
                                                  people_face.feature_token)

            # 清除人脸所属的人物
            PeopleFace.objects.filter(uuid__in=face_uuid_list).update(people_uuid=None, feature_token=None,
                                                                      feature_ctime=None)

            # 如果有人物封面使用了该人脸，则重新生成人物封面
            People.objects.filter(cover__in=face_uuid_list).update(cover_from='auto')
            people_auto_cover(people_uuid)
            return JsonResponse({}, safe=False, status=200)
    except Exception as e:
        traceback.print_exc()  # 输出详细的错误信息
        response['msg'] = str(e)
        return JsonResponse(response, status=500)


@require_http_methods(['POST'])
def people_add_feature(request):
    """增加人物特征"""
    request_data = json.loads(request.body)
    face_uuid = request_data.get('face_uuid')  # 人脸uuid
    face = PeopleFace.objects.get(uuid=face_uuid)
    face.feature_token = 'wait...'
    face.save()
    baidu_ai_facelib_add.delay(face_uuid)
    return JsonResponse({}, safe=False, status=200)


@require_http_methods(['POST'])
def people_remove_feature(request):
    """删除人物特征"""
    request_data = json.loads(request.body)
    face_uuid = request_data.get('face_uuid')  # 人脸uuid
    face = PeopleFace.objects.get(uuid=face_uuid)
    # 从人脸库中删除
    baidu_ai_facelib_delete.delay(face.userid.userid, face.people_uuid.uuid, face.feature_token)
    # 写入数据库
    face.feature_token = None
    face.feature_ctime = None
    face.save()
    return JsonResponse({}, safe=False, status=200)


def people_auto_cover(people_uuid):
    """自动设置指定人物的封面"""
    people = People.objects.get(uuid=people_uuid)
    if people.cover_from == 'auto':
        people_face = PeopleFace.objects.filter(people_uuid=people_uuid).order_by('-input_date').first()
        if people_face:
            People.objects.filter(uuid=people_uuid).update(cover=people_face.uuid)
        else:
            People.objects.filter(uuid=people_uuid).update(cover=None)


@require_http_methods(['POST'])
def people_set_cover(request):
    """手动设置人物封面"""
    request_data = json.loads(request.body)
    people_uuid = request_data.get('people_uuid')
    face_uuid = request_data.get('face_uuid')
    people = People.objects.get(uuid=people_uuid)
    people.cover = PeopleFace.objects.get(uuid=face_uuid)
    people.cover_from = 'manual'
    people.save()
    return JsonResponse({}, status=200)


@require_http_methods(['GET'])
def people_get_faces(request):
    """获取面孔列表"""
    response = {}
    call_mode = request.GET.get('call_mode')
    userid = request.GET.get('userid')
    people_uuid = request.GET.get('people_uuid')
    page = request.GET.get('page')
    pagesize = request.GET.get('pagesize')

    faces = PeopleFace.objects
    faces = faces.filter(userid=userid, is_delete=False)
    if call_mode == 'people':
        faces = faces.filter(people_uuid=people_uuid)
    if call_mode == 'pick_face':
        faces = faces.filter(people_uuid__isnull=True)
    faces = faces.values('uuid', 'path', 'path_thumbnail', 'name', 'input_date', 'people_uuid', 'photo_uuid',
                         'feature_token', people_name=F('people_uuid__name'),
                         exif_datetime=F('photo_uuid__exif_datetime'))
    faces = faces.order_by('-exif_datetime')

    # 分页
    if page:
        paginator = Paginator(faces, pagesize)
        response['total'] = paginator.count
        faces = paginator.page(page)
        response['list'] = json.loads(json.dumps(list(faces), cls=DateEncoder))
    else:
        response = json.loads(json.dumps(list(faces), cls=DateEncoder))
    return JsonResponse(response, safe=False, status=200)


@require_http_methods(['POST'])
def people_rename(request):
    """重命名人物"""
    request_data = json.loads(request.body)
    people_uuid = request_data.get('uuid')
    name = request_data.get('name')
    people = People.objects.get(uuid=people_uuid)
    people.name = name
    people.save()
    return JsonResponse({}, status=200)


@require_http_methods(['POST'])
def people_remove(request):
    """删除人物"""
    response = {}
    try:
        with transaction.atomic():  # 开启事务处理
            request_data = json.loads(request.body)
            userid = request_data.get('userid')
            people_uuid = request_data.get('uuid')

            # 删除人脸库中已经注册的照片
            features = PeopleFace.objects.filter(people_uuid=people_uuid, feature_token__isnull=False)
            for feature in features:
                baidu_ai_facelib_delete.delay(userid, people_uuid, feature.feature_token)

            PeopleFaceExcept.objects.filter(people_uuid=people_uuid).delete()
            PeopleFace.objects.filter(people_uuid=people_uuid).update(people_uuid=None, feature_token=None,
                                                                      feature_ctime=None)
            People.objects.filter(uuid=people_uuid).delete()
            return JsonResponse({}, status=200)
    except Exception as e:
        traceback.print_exc()  # 输出详细的错误信息
        response['msg'] = str(e)
        return JsonResponse(response, status=500)


def baidu_ai_get_token():
    """获取百度AI鉴权token"""
    api = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={0}&client_secret={1}'.format(
        'IVeeKBHfqpt9kGNuLo8CjF33', 'EfEwCvIjxneuCGpcGDqpGfIYL5xSMVqz')
    response = requests.get(api)
    response.close()
    if response:
        return response.json()['access_token']


@task
def baidu_ai_facelib_add(face_uuid):
    """向人脸库中注册照片"""
    response = {}
    face_token = None
    try:
        with transaction.atomic():  # 开启事务处理
            # 由于是异步任务，排队到执行时可能目标记录已被删除，所以这里要判断一下
            people_face = PeopleFace.objects.filter(uuid=face_uuid)
            if not people_face:
                return
            # 只有仅包含一张面孔的照片才能作为人物的特征
            photo_uuid = people_face[0].photo_uuid.uuid  # 照片uuid
            if len(PeopleFace.objects.filter(photo_uuid=photo_uuid)) > 1:
                return
            # 注册之前先检查人物特征库是否达到上限，如果达到了，则删除最先加入的照片
            features = PeopleFace.objects.filter(people_uuid=people_face[0].people_uuid.uuid,
                                                 feature_token__isnull=False)
            features = features.order_by('feature_ctime')
            if len(features) >= 20:
                PeopleFace.objects.filter(uuid=features[0].uuid).update(feature_token=None, feature_ctime=None)
                baidu_ai_facelib_delete(features[0].userid.userid, features[0].people_uuid.uuid,
                                        features[0].feature_token)

            people_face = PeopleFace.objects.get(uuid=face_uuid)
            access_token = baidu_ai_get_token()  # 获取鉴权token
            api = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/user/add" + "?access_token=" + access_token
            headers = {'content-type': 'application/json'}
            photo = Photo.objects.get(uuid=photo_uuid)
            photo_path = os.path.join(settings.BASE_DIR, photo.path_thumbnail_l, photo.name)  # 照片绝对路径
            with open(photo_path, 'rb') as f:
                photo_data = f.read()
                photo_base64_data = base64.b64encode(photo_data)  # base64编码
            params = {
                'image': photo_base64_data,
                'image_type': 'BASE64',
                'group_id': people_face.userid.userid,  # 用户组id
                'user_id': people_face.people_uuid.uuid,  # 用户id
                'user_info': people_face.people_uuid.name,  # 用户资料
            }
            res = requests.post(api, data=params, headers=headers)
            result = res.json()  # 获取响应数据，并解析JSON，转化为python字典
            res.close()
            if result['error_code'] != 0:  # 接口调用失败
                raise Exception(str(result['error_code']) + result['error_msg'])  # 抛出异常
            face_token = result['result']['face_token']
            PeopleFace.objects.filter(uuid=face_uuid).update(feature_token=face_token,
                                                             feature_ctime=time.strftime("%Y-%m-%d %H:%M:%S",
                                                                                         time.localtime()))
            print('在人脸库中' + people_face.userid.userid + '注册了照片:' + result['result']['face_token'])
            print('暂停5秒等待上传到人脸库的照片生效...')
            time.sleep(5)  # 等待上传到人脸库的照片生效
    except Exception as e:
        traceback.print_exc()  # 输出详细的错误信息
        response['msg'] = str(e)
        # 删除可能已经注册的人脸
        if face_token:
            people_face = PeopleFace.objects.get(uuid=face_uuid)
            baidu_ai_facelib_delete(people_face.userid.userid, people_face.people_uuid.uuid, face_token)
        return JsonResponse(response, status=500)
    # 执行人脸识别
    people_face_compare.delay(people_face.userid.userid)


@task
def baidu_ai_facelib_delete(userid, people_uuid, feature_token):
    """在人脸库中删除照片"""
    response = {}
    try:
        access_token = baidu_ai_get_token()  # 获取鉴权token
        api = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/face/delete" + "?access_token=" + access_token
        headers = {'content-type': 'application/json'}
        params = {
            'group_id': userid,  # 用户组id
            'user_id': people_uuid,  # 用户id
            'face_token': feature_token,  # 需要删除的人脸图片token
        }
        res = requests.post(api, data=params, headers=headers)
        result = res.json()  # 获取响应数据，并解析JSON，转化为python字典
        res.close()
        if result['error_code'] != 0:  # 接口调用失败
            raise Exception(str(result['error_code']) + result['error_msg'])  # 抛出异常
        time.sleep(0.5)  # 暂停一会儿，避免qps超限额
        print('在人脸库中' + userid + '删除了照片:' + feature_token)
    except Exception as e:
        traceback.print_exc()  # 输出详细的错误信息
        response['msg'] = str(e)
        return JsonResponse(response, status=500)
