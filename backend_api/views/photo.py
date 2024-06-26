import os
import json
import traceback
import requests  # 调用api
import uuid
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import zipfile
from PIL import Image  # 图像处理
from django.db import transaction
from django.db.models import Count, Sum, Q, F, Min, Max, Subquery
from django.http import JsonResponse, StreamingHttpResponse
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from backend_api.common.date_encoder import DateEncoder
from backend_api.models import Photo, AlbumPhoto, Album, Address, People, PeopleFace, PhotoTag
from backend_api.views.album import album_auto_cover, __album_count
from backend_api.views.people import people_auto_cover, baidu_ai_facelib_delete
# from backend_api.views.thing import thing_get_tags


@require_http_methods(['GET'])
def photo_list(request):
    """浏览照片"""
    response = {}
    call_mode = request.GET.get('call_mode')  # 调用方式
    userid = request.GET.get('userid')
    album_uuid = request.GET.get('album_uuid')  # 影集uuid
    people_uuid = request.GET.get('people_uuid')  # 人物uuid
    province = request.GET.get('province')  # 省
    city = request.GET.get('city')  # 市
    district = request.GET.get('district')  # 县
    keyword = request.GET.get('keyword')  # 搜索关键字
    time_group = request.GET.get('time_group')  # 时间分组字段
    if not time_group:
        time_group = 'exif_datetime'  # 赋默认值
    order_by = request.GET.get('order_by')  # 排序依据
    if not order_by:
        order_by = '-exif_datetime'
    group_type = request.GET.get('group_type')  # 分组类型
    date_filter = request.GET.get('date_filter')  # 分组时间过滤
    page = request.GET.get('page')
    if page and int(page) < 1:  # 页号不能小于1
        page = 1
    pagesize = request.GET.get('pagesize')

    photos = Photo.objects.distinct()
    photos = photos.values('uuid', 'path_original', 'path_modified', 'path_thumbnail_s', 'path_thumbnail_l', 'name',
                           'width', 'height', 'exif_datetime', 'is_favorited', 'comments',
                           'address__address', 'address__poi_name', 'address__province', 'address__city',
                           'address__district')
    photos = photos.annotate(time_group=F(time_group))  # 时间分组字段
    photos = photos.annotate(faces=Count('peopleface__uuid'))  # 照片中人脸的数量
    # 过滤条件
    photos = photos.filter(userid=userid)
    if call_mode in ['photo', 'album', 'pick', 'favorites', 'cover', 'people', 'feature', 'pick_face', 'place']:
        photos = photos.filter(is_deleted=False)
        if call_mode == 'album':  # 在影集中调用
            photos = photos.filter(albumphoto__album_uuid=album_uuid)
        if call_mode == 'favorites':  # 在收藏夹中调用
            photos = photos.filter(is_favorited=True)
        if call_mode == 'cover':  # 在设置影集封面中调用
            albums = Album.objects.raw('''
                WITH RECURSIVE tmp_albums AS (
                    SELECT uuid AS rootId FROM m_album WHERE uuid= %s
                    UNION ALL
                    SELECT uuid FROM m_album a,tmp_albums b WHERE a.parent_uuid = b.rootId
                )
                SELECT uuid FROM m_album WHERE EXISTS(SELECT uuid FROM tmp_albums WHERE rootId = uuid)
            ''', [album_uuid])
            photos = photos.filter(albumphoto__album_uuid__in=albums)
        if call_mode == 'people':  # 在人物中调用
            photos = photos.filter(peopleface__people_uuid=people_uuid)
        if call_mode == 'feature':  # 在选择人物特征中调用，只显示面孔数量为1的照片
            photos = photos.filter(peopleface__people_uuid=people_uuid, faces=1, peopleface__feature_token__isnull=True,
                                   peopleface__is_delete=False)
        if call_mode == 'pick_face':  # 在选择面孔添加到人物中使用
            photos = photos.filter(peopleface__people_uuid__isnull=True, faces__gt=0, peopleface__is_delete=False)
        if call_mode == 'place':  # 在地点中调用
            if province != 'none':
                photos = photos.filter(address__province=province)
            if city != 'none':
                photos = photos.filter(address__city=city)
            if district != 'none':
                photos = photos.filter(address__district=district)
    if call_mode == 'trash':  # 在回收站中调用
        photos = photos.filter(is_deleted=True)

    # 按日期条件进行过滤
    if date_filter:
        if group_type == 'year':
            photos = photos.filter(
                time_group__lt=datetime.strptime(date_filter, '%Y-%m-%d') + relativedelta(years=1))
        if group_type == 'month':
            photos = photos.filter(
                time_group__lt=datetime.strptime(date_filter, '%Y-%m-%d') + relativedelta(months=1))
        if group_type == 'day':
            photos = photos.filter(time_group__lt=datetime.strptime(date_filter, '%Y-%m-%d') + timedelta(days=1))

    # 搜索（标签、说明、地址、poi名称）
    if keyword:
        photos = photos.filter(Q(phototag__tag_name__icontains=keyword) | Q(comments__icontains=keyword) | Q(
            address__address__icontains=keyword) | Q(address__poi_name__icontains=keyword))

    # 排序
    photos = photos.order_by(order_by)  # 默认是-exif_datetime

    # 分页
    if page:
        paginator = Paginator(photos, pagesize)
        response['total'] = paginator.count
        photos = paginator.page(page)
        response['list'] = json.loads(json.dumps(list(photos), cls=DateEncoder))
    else:
        response = json.loads(json.dumps(list(photos), cls=DateEncoder))

    # safe 控制是否只有字典类型的数据才能被序列化，这里的response是一个数组，所以要将safe设置为False
    return JsonResponse(response, safe=False, status=200)


@require_http_methods(['GET'])
def photo_get_groups(request):
    """获取照片的分组列表"""
    group_type = request.GET.get('group_type')
    call_mode = request.GET.get('call_mode')
    userid = request.GET.get('userid')
    album_uuid = request.GET.get('album_uuid')
    people_uuid = request.GET.get('people_uuid')
    province = request.GET.get('province')  # 省
    city = request.GET.get('city')  # 市
    district = request.GET.get('district')  # 县
    keyword = request.GET.get('keyword')  # 搜索关键字
    time_group = request.GET.get('time_group')  # 时间分组字段
    order_by = request.GET.get('order_by')  # 排序依据

    # 首先生成符合条件的照片集合
    photos = Photo.objects
    photos = photos.values('uuid')
    photos = photos.annotate(faces=Count('peopleface__uuid'))
    # 过滤条件
    photos = photos.filter(userid=userid)
    if call_mode in ['photo', 'album', 'pick', 'favorites', 'cover', 'people', 'feature', 'pick_face', 'place']:
        photos = photos.filter(is_deleted=False)
        if call_mode == 'album':  # 在影集中调用
            photos = photos.filter(albumphoto__album_uuid=album_uuid)
        if call_mode == 'favorites':  # 在收藏夹中调用
            photos = photos.filter(is_favorited=True)
        if call_mode == 'cover':  # 在设置影集封面中调用
            albums = Album.objects.raw('''
                WITH RECURSIVE tmp_albums AS (
                    SELECT uuid AS rootId FROM m_album WHERE uuid= %s
                    UNION ALL
                    SELECT uuid FROM m_album a,tmp_albums b WHERE a.parent_uuid = b.rootId
                )
                SELECT uuid FROM m_album WHERE EXISTS(SELECT uuid FROM tmp_albums WHERE rootId = uuid)
            ''', [album_uuid])
            photos = photos.filter(albumphoto__album_uuid__in=albums)
        if call_mode == 'people':  # 在人物中调用
            photos = photos.filter(peopleface__people_uuid=people_uuid)
        if call_mode == 'feature':  # 在选择人物特征中调用，只显示面孔数量为1的照片
            photos = photos.filter(peopleface__people_uuid=people_uuid, faces=1, peopleface__feature_token__isnull=True,
                                   peopleface__is_delete=False)
        if call_mode == 'pick_face':  # 在选择面孔添加到人物中使用
            photos = photos.filter(peopleface__people_uuid__isnull=True, faces__gt=0, peopleface__is_delete=False)
        if call_mode == 'place':  # 在地点中调用
            if province != 'none':
                photos = photos.filter(address__province=province)
            if city != 'none':
                photos = photos.filter(address__city=city)
            if district != 'none':
                photos = photos.filter(address__district=district)
    if call_mode == 'trash':  # 在回收站中调用
        photos = photos.filter(is_deleted=True)

    # 搜索（标签、说明、地址、poi名称）
    if keyword:
        photos = photos.filter(Q(phototag__tag_name__icontains=keyword) | Q(comments__icontains=keyword) | Q(
            address__address__icontains=keyword) | Q(address__poi_name__icontains=keyword))

    # 把前面生成的集合作为条件，获取时间分组列表
    groups = Photo.objects.distinct()
    if group_type == 'year':
        groups = groups.extra(select={"time_group": "DATE_FORMAT("+time_group+", '%%Y-01-01')"})
    if group_type == 'month':
        groups = groups.extra(select={"time_group": "DATE_FORMAT("+time_group+", '%%Y-%%m-01')"})
    if group_type == 'day':
        groups = groups.extra(select={"time_group": "DATE_FORMAT("+time_group+", '%%Y-%%m-%%d')"})
    groups = groups.values('time_group')
    groups = groups.filter(uuid__in=Subquery(photos.values('uuid')))

    # 排序
    groups = groups.order_by('-time_group')

    response = json.loads(json.dumps(list(groups)))
    return JsonResponse(response, safe=False, status=200)


@require_http_methods(['GET'])
def photo_get_info(request):
    """获取指定照片详细信息"""
    photo_uuid = request.GET.get('photo_uuid')
    photo = Photo.objects.values('uuid', 'name', 'name_original', 'width', 'height', 'size', 'exif_datetime',
                                 'exif_make', 'exif_model', 'exif_fnumber', 'exif_exposuretime', 'exif_focallength',
                                 'exif_isospeedratings', 'comments', photo_address=F('address__address'),
                                 photo_poi_name=F('address__poi_name'), photo_lat=F('address__lat'),
                                 photo_lng=F('address__lng'))
    photo = photo.get(uuid=photo_uuid)
    photo['exif_datetime'] = photo['exif_datetime'].strftime('%Y-%m-%d %H:%M:%S')  # 对日期型字段进行转换

    # thing_get_tags()

    return JsonResponse(photo, safe=False, status=200)


@require_http_methods(['GET'])
def photo_get_albums(request):
    """获取指定照片所属的影集列表"""
    photo_uuid = request.GET.get('photo_uuid')
    # 先得到照片所属影集的uuid列表
    album_uuid_list = AlbumPhoto.objects.values('album_uuid').filter(photo_uuid=photo_uuid)
    # 然后再得到影集列表
    albums = Album.objects.filter(uuid__in=album_uuid_list)
    albums = albums.values('uuid', 'name', cover_path=F('cover__path_thumbnail_s'),
                           cover_name=F('cover__name'))  # 通过外键关联查询封面路径

    albums = __album_count(albums)
    response = json.loads(json.dumps(albums, cls=DateEncoder))
    return JsonResponse(response, safe=False, status=200)


@require_http_methods(['GET'])
def photo_statistics(request):
    """统计照片数量和占用空间"""
    userid = request.GET.get('userid')
    photo = Photo.objects.filter(userid=userid, is_deleted=False).aggregate(nums=Count('uuid'), size=Sum('size'))
    return JsonResponse(photo, safe=False, status=200)


@require_http_methods(['POST'])
def photo_trash(request):
    """将照片移到回收站"""
    response = {}
    try:
        with transaction.atomic():  # 开启事务处理
            request_data = json.loads(request.body)
            photo_uuid_list = request_data.get('photo_list')
            Photo.objects.filter(uuid__in=photo_uuid_list).update(is_deleted=True)  # 修改删除标志
            # 如果有影集封面使用了该照片，则重新生成影集封面
            Album.objects.filter(cover__in=photo_uuid_list).update(cover_from='auto')
            albums = Album.objects.filter(cover__in=photo_uuid_list)
            for item in albums:
                album_auto_cover(item.uuid)  # 设置影集封面
            return JsonResponse({}, safe=False, status=200)
    except Exception as e:
        traceback.print_exc()  # 输出详细的错误信息
        response['msg'] = str(e)
        return JsonResponse(response, status=500)


@require_http_methods(['POST'])
def photo_restore(request):
    """将照片从回收站恢复"""
    response = {}
    try:
        with transaction.atomic():  # 开启事务处理
            request_data = json.loads(request.body)
            photo_uuid_list = request_data.get('photo_list')
            Photo.objects.filter(uuid__in=photo_uuid_list).update(is_deleted=False)  # 修改删除标志
            # 如果有影集添加了该照片，则重新生成影集封面
            albums = AlbumPhoto.objects.distinct().filter(photo_uuid__in=photo_uuid_list,
                                                          photo_uuid__is_deleted=False).values('album_uuid')
            for item in albums:
                Album.objects.filter(cover=item['album_uuid']).update(cover_from='auto')
                album_auto_cover(item['album_uuid'])  # 设置影集封面
            return JsonResponse({}, safe=False, status=200)
    except Exception as e:
        traceback.print_exc()  # 输出详细的错误信息
        response['msg'] = str(e)
        return JsonResponse(response, status=500)


@require_http_methods(['POST'])
def photo_remove(request):
    """永久删除照片"""
    response = {}
    try:
        with transaction.atomic():  # 开启事务处理
            request_data = json.loads(request.body)
            photo_uuid_list = request_data.get('photo_list')
            photos = Photo.objects.filter(uuid__in=photo_uuid_list, is_deleted=True)
            for item in photos:
                file_path = os.path.join(settings.BASE_DIR, item.path_original, item.name)
                if os.path.exists(file_path):  # 删除原图
                    os.remove(file_path)
                file_path = os.path.join(settings.BASE_DIR, item.path_thumbnail_s, item.name)
                if os.path.exists(file_path):  # 删除生成的缩略图
                    os.remove(file_path)
                file_path = os.path.join(settings.BASE_DIR, item.path_thumbnail_l, item.name)
                if os.path.exists(file_path):
                    os.remove(file_path)
                if item.path_modified:
                    file_path = os.path.join(settings.BASE_DIR, item.path_modified, item.name)
                    if os.path.exists(file_path):  # 删除修改后的原图
                        os.remove(file_path)
                # 删除人脸图像
                people_face = PeopleFace.objects.filter(photo_uuid=item.uuid)
                for face in people_face:
                    file_path = os.path.join(settings.BASE_DIR, face.path, face.name)
                    if os.path.exists(file_path):  # 删除原图
                        os.remove(file_path)
                    file_path = os.path.join(settings.BASE_DIR, face.path_thumbnail, face.name)
                    if os.path.exists(file_path):  # 删除缩略图
                        os.remove(file_path)
                    # 在人脸库中删除照片
                    if face.feature_token:
                        baidu_ai_facelib_delete.delay(face.userid.userid, face.people_uuid.uuid, face.feature_token)
            # 删除与人物相关的数据
            peoples = People.objects.filter(cover__photo_uuid__in=photos)
            for item in peoples:
                People.objects.filter(uuid=item.uuid).update(cover=None, cover_from='auto')  # 取消人物封面
                PeopleFace.objects.filter(photo_uuid__in=photos).delete()  # 删除人脸
                people_auto_cover(item.uuid)  # 重新生成人物封面
            # 删除照片，Address、AlbumPhoto、PhotoTag将会被级联删除
            Photo.objects.filter(uuid__in=photos).delete()
            return JsonResponse(response, status=200)
    except Exception as e:
        traceback.print_exc()  # 输出详细的错误信息
        response['msg'] = str(e)
        return JsonResponse(response, status=500)


@require_http_methods(['POST'])
def photo_empty_trash(request):
    """清空回收站"""
    response = {}
    try:
        with transaction.atomic():  # 开启事务处理
            request_data = json.loads(request.body)
            userid = request_data.get('userid')
            photos = Photo.objects.filter(userid=userid, is_deleted=True)
            for item in photos:
                file_path = os.path.join(settings.BASE_DIR, item.path_original, item.name)
                if os.path.exists(file_path):  # 删除原图
                    os.remove(file_path)
                file_path = os.path.join(settings.BASE_DIR, item.path_thumbnail_s, item.name)
                if os.path.exists(file_path):  # 删除生成的缩略图
                    os.remove(file_path)
                file_path = os.path.join(settings.BASE_DIR, item.path_thumbnail_l, item.name)
                if os.path.exists(file_path):
                    os.remove(file_path)
                if item.path_modified:
                    file_path = os.path.join(settings.BASE_DIR, item.path_modified, item.name)
                    if os.path.exists(file_path):  # 删除修改后的原图
                        os.remove(file_path)
                # 删除人脸图像
                people_face = PeopleFace.objects.filter(photo_uuid=item.uuid)
                for face in people_face:
                    file_path = os.path.join(settings.BASE_DIR, face.path, face.name)
                    if os.path.exists(file_path):  # 删除原图
                        os.remove(file_path)
                    file_path = os.path.join(settings.BASE_DIR, face.path_thumbnail, face.name)
                    if os.path.exists(file_path):  # 删除缩略图
                        os.remove(file_path)
                    # 在人脸库中删除照片
                    if face.feature_token:
                        baidu_ai_facelib_delete.delay(face.userid.userid, face.people_uuid.uuid, face.feature_token)
            # 删除与人物相关的数据
            peoples = People.objects.filter(cover__photo_uuid__in=photos)
            for item in peoples:
                People.objects.filter(uuid=item.uuid).update(cover=None, cover_from='auto')  # 取消人物封面
                PeopleFace.objects.filter(photo_uuid__in=photos).delete()  # 删除人脸
                people_auto_cover(item.uuid)  # 重新生成人物封面
            # 删除照片，Address、AlbumPhoto、PhotoTag将会被级联删除
            Photo.objects.filter(userid=userid, is_deleted=True).delete()
            return JsonResponse(response, status=200)
    except Exception as e:
        traceback.print_exc()  # 输出详细的错误信息
        response['msg'] = str(e)
        return JsonResponse(response, status=500)


@require_http_methods(['POST'])
def photo_set_comments(request):
    """为照片添加说明文字"""
    request_data = json.loads(request.body)
    photo_uuid = request_data.get('photo_uuid')
    comments = request_data.get('comments')
    photo = Photo.objects.get(uuid=photo_uuid)
    photo.comments = comments
    photo.save()
    return JsonResponse({}, status=200)


@require_http_methods(['POST'])
def photo_set_datetime(request):
    """修改照片的拍摄时间"""
    request_data = json.loads(request.body)
    photo_uuid_list = request_data.get('photo_list')
    photo_datetime = request_data.get('photo_datetime')
    Photo.objects.filter(uuid__in=photo_uuid_list).update(exif_datetime=photo_datetime)
    return JsonResponse({}, status=200)


@require_http_methods(['GET'])
def photo_query_location(request):
    """查询位置信息"""
    ak = settings.BMAP_AK
    query = request.GET.get('query')
    # 地点输入提示服务
    baidu_map_api = 'http://api.map.baidu.com/place/v2/suggestion?ak={0}&query={1}' \
                    '&region=全国&output=json'.format(ak, query)
    res = requests.get(baidu_map_api)
    result = res.json()
    res.close()
    if result['status'] != 0:  # 接口调用失败
        raise Exception(result['message'])  # 抛出异常
    return JsonResponse(result['result'], safe=False, status=200)


@require_http_methods(['POST'])
def photo_set_location(request):
    """修改照片的位置信息"""
    response = {}
    try:
        with transaction.atomic():  # 开启事务处理
            ak = settings.BMAP_AK
            request_data = json.loads(request.body)
            photo_uuid_list = request_data.get('photo_list')
            location = request_data.get('location')
            Address.objects.filter(uuid__in=photo_uuid_list).delete()  # 先删除再插入
            if location:
                lat = location.split(',')[0]
                lng = location.split(',')[1]
                poi_name = location.split(',')[2]
                # 全球逆地理编码服务
                baidu_map_api = 'http://api.map.baidu.com/reverse_geocoding/v3/?ak={0}&output=json&coordtype=wgs84ll' \
                                '&location={1},{2}'.format(ak, lat, lng)
                res = requests.get(baidu_map_api)
                result = res.json()
                res.close()
                if result['status'] != 0:  # 接口调用失败
                    raise Exception(result['message'])  # 抛出异常
                for item in photo_uuid_list:
                    address = Address()
                    address.uuid = Photo.objects.get(uuid=item)
                    address.lat = lat
                    address.lng = lng
                    address.address = result['result']['formatted_address']
                    address.poi_name = poi_name
                    address.country = result['result']['addressComponent']['country']
                    address.province = result['result']['addressComponent']['province']
                    address.city = result['result']['addressComponent']['city']
                    address.district = result['result']['addressComponent']['district']
                    address.town = result['result']['addressComponent']['town']
                    address.save()
                response['address'] = result['result']['formatted_address']
                response['poi_name'] = poi_name
                response['province'] = result['result']['addressComponent']['province']
                response['city'] = result['result']['addressComponent']['city']
                response['district'] = result['result']['addressComponent']['district']
                return JsonResponse(response, safe=False, status=200)
            else:  # 删除位置信息
                return JsonResponse({'address': '', 'poi_name': ''}, safe=False, status=200)
    except Exception as e:
        traceback.print_exc()  # 输出详细的错误信息
        response['msg'] = str(e)
        return JsonResponse(response, status=500)


@require_http_methods(['POST'])
def photo_favorites(request):
    """收藏"""
    request_data = json.loads(request.body)
    photo_uuid_list = request_data.get('photo_list')
    Photo.objects.filter(uuid__in=photo_uuid_list).update(is_favorited=True)  # 修改收藏标志
    return JsonResponse({}, safe=False, status=200)


@require_http_methods(['POST'])
def photo_unfavorites(request):
    """取消收藏"""
    request_data = json.loads(request.body)
    photo_uuid_list = request_data.get('photo_list')
    Photo.objects.filter(uuid__in=photo_uuid_list).update(is_favorited=False)  # 修改收藏标志
    return JsonResponse({}, safe=False, status=200)


@require_http_methods(['GET'])
def photo_get_faces(request):
    """获取指定照片中的人脸列表"""
    photo_uuid = request.GET.get('photo_uuid')
    people_face = PeopleFace.objects.filter(photo_uuid=photo_uuid, is_delete=False)
    people_face = people_face.values('uuid', 'path', 'path_thumbnail', 'name', 'input_date', 'people_uuid',
                                     'photo_uuid', 'feature_token', people_name=F('people_uuid__name'),
                                     exif_datetime=F('photo_uuid__exif_datetime'))
    people_face = people_face.order_by('-people_uuid', 'input_date')
    response = json.loads(json.dumps(list(people_face), cls=DateEncoder))
    return JsonResponse(response, safe=False, status=200)


@require_http_methods(['POST'])
def photo_rotate(request):
    """旋转照片"""
    response = {}
    im = None
    try:
        request_data = json.loads(request.body)
        photo_uuid = request_data.get('photo_uuid')
        angle = request_data.get('angle')  # 逆时针旋转的角度

        photo = Photo.objects.get(uuid=photo_uuid)
        name = photo.name  # 原文件名
        extension_name = os.path.splitext(name)[1]  # 原文件扩展名
        path_original = photo.path_original  # 原图路径
        path_thumbnail_l = photo.path_thumbnail_l  # 大缩略图路径
        path_thumbnail_s = photo.path_thumbnail_s  # 小缩略图路径
        full_path_original = os.path.join(settings.BASE_DIR, photo.path_original)  # 原图完整路径
        full_path_thumbnail_l = os.path.join(settings.BASE_DIR, photo.path_thumbnail_l)  # 大缩略图完整路径
        full_path_thumbnail_s = os.path.join(settings.BASE_DIR, photo.path_thumbnail_s)  # 小缩略图完整路径

        # 将原图、大小缩略图都进行旋转并保存为新的文件
        new_name = str(uuid.uuid1()).replace('-', '') + extension_name  # 新的文件名
        im = Image.open(os.path.join(full_path_original, name))
        im = im.rotate(angle, expand=True)
        im.save(os.path.join(full_path_original, new_name))
        new_width = im.width  # 照片旋转后新的宽度
        new_height = im.height
        im = Image.open(os.path.join(full_path_thumbnail_l, name))
        im = im.rotate(angle, expand=True)
        im.save(os.path.join(full_path_thumbnail_l, new_name))
        im = Image.open(os.path.join(full_path_thumbnail_s, name))
        im = im.rotate(angle, expand=True)
        im.save(os.path.join(full_path_thumbnail_s, new_name))

        # 回写数据库
        photo.name = new_name
        photo.width = new_width
        photo.height = new_height
        photo.save()

        # 删除原来的文件
        if os.path.join(path_original, name) and os.path.exists(os.path.join(full_path_original, name)):
            os.remove(os.path.join(full_path_original, name))
        if os.path.join(path_thumbnail_l, name) and os.path.exists(os.path.join(full_path_thumbnail_l, name)):
            os.remove(os.path.join(full_path_thumbnail_l, name))
        if os.path.join(path_thumbnail_s, name) and os.path.exists(os.path.join(full_path_thumbnail_s, name)):
            os.remove(os.path.join(full_path_thumbnail_s, name))

        response = {'file_name': new_name, 'path_thumbnail_l': path_thumbnail_l, 'width': new_width,
                    'height': new_height}
        return JsonResponse(response, safe=False, status=200)
    except Exception as e:
        traceback.print_exc()  # 输出详细的错误信息
        response['msg'] = str(e)
        return JsonResponse(response, status=500)
    finally:
        if im:
            im.close()


@require_http_methods(['GET'])
def photo_query_peoples(request):
    """查询人物列表"""
    userid = request.GET.get('userid')
    query = request.GET.get('query')
    peoples = People.objects.filter(userid=userid)
    if query:
        peoples = peoples.filter(name__contains=query)
    peoples = peoples.values('uuid', 'name')
    peoples = peoples.order_by('name')
    response = json.loads(json.dumps(list(peoples), cls=DateEncoder))
    return JsonResponse(response, safe=False, status=200)


@require_http_methods(['GET'])
def photo_get_tags(request):
    """获取指定照片的标签列表"""
    photo_uuid = request.GET.get('photo_uuid')
    photo_tags = PhotoTag.objects.values('tag_name').filter(photo_uuid=photo_uuid)
    photo_tags = photo_tags.order_by('-confidence')
    response = json.loads(json.dumps(list(photo_tags), cls=DateEncoder))
    return JsonResponse(response, safe=False, status=200)


@require_http_methods(['POST'])
def photo_download(request):
    """照片打包下载"""
    request_data = json.loads(request.body)
    userid = request_data.get('userid')
    photo_uuid_list = request_data.get('photo_list')
    photos = Photo.objects.filter(uuid__in=photo_uuid_list)
    # 在当前用户文件夹下生成下载目录
    zip_path = os.path.join(settings.BASE_DIR, 'photos', userid, 'temp')
    if not os.path.exists(zip_path):  # 如果目标文件夹不存在则创建
        os.makedirs(zip_path, exist_ok=True)
    zip_file = os.path.join(zip_path, 'photo.zip')
    zf = zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED, True)
    for photo in photos:
        photo_path = os.path.join(settings.BASE_DIR, photo.path_original, photo.name)  # 照片原图
        zf.write(photo_path, photo.name)  # 将照片写入到压缩包
    zf.close()

    def file_iterator(file_path, chunk_size=512):
        """
        文件生成器,防止文件过大，导致内存溢出
        :param file_path: 文件绝对路径
        :param chunk_size: 块大小
        :return: 生成器
        """
        with open(file_path, mode='rb') as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    response = StreamingHttpResponse(file_iterator(zip_file))
    # 以流的形式下载文件,这样可以实现任意格式的文件下载
    response['Content-Type'] = 'application/octet-stream'
    # Content-Disposition就是当用户想把请求所得的内容存为一个文件的时候提供一个默认的文件名
    response['Content-Disposition'] = 'attachment;filename="{}"'.format(os.path.basename(zip_file))
    return response

