import os
import json
import traceback

from django.db import transaction
from django.db.models import Count, Sum, Q
from django.db.models import F
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.http import require_http_methods
from backend_api.common.date_encoder import DateEncoder
from backend_api.models import Photo, AlbumPhoto, Album
from backend_api.views.album import album_auto_cover


@require_http_methods(['GET'])
def photo_list(request):
    """浏览照片"""
    call_mode = request.GET.get('call_mode')
    userid = request.GET.get('userid')
    album_uuid = request.GET.get('album_uuid')

    photos = Photo.objects.distinct()
    photos = photos.filter(userid=userid)
    if call_mode in ['photo', 'album']:
        photos = photos.filter(is_deleted=False)
        if call_mode == 'album':  # 在影集中调用
            photos = photos.filter(albumphoto__album_uuid=album_uuid)
    if call_mode == 'trash':  # 在回收站中调用
        photos = photos.filter(is_deleted=True)
    photos = photos.values('uuid', 'path', 'path_thumbnail', 'name', 'width', 'height', 'exif_datetime', 'comments')
    photos = photos.order_by('-exif_datetime')

    response = json.loads(json.dumps(list(photos), cls=DateEncoder))
    # safe 控制是否只有字典类型的数据才能被序列化，这里的response是一个数组，所以要将safe设置为False
    return JsonResponse(response, safe=False, status=200)


@require_http_methods(['GET'])
def photo_get_info(request):
    """获取指定照片详细信息"""
    photo_uuid = request.GET.get('photo_uuid')
    photo = Photo.objects.values('uuid', 'name', 'width', 'height', 'size', 'exif_datetime', 'exif_make', 'exif_model',
                                 'exif_fnumber', 'exif_exposuretime', 'exif_focallength', 'exif_isospeedratings',
                                 'comments', photo_address=F('address__address'), photo_lat=F('address__lat'),
                                 photo_lng=F('address__lng'))
    photo = photo.get(uuid=photo_uuid)
    photo['exif_datetime'] = photo['exif_datetime'].strftime('%Y-%m-%d %H:%M:%S')  # 对日期型字段进行转换
    return JsonResponse(photo, safe=False, status=200)


@require_http_methods(['GET'])
def photo_get_albums(request):
    """获取指定照片所属的影集列表"""
    photo_uuid = request.GET.get('photo_uuid')
    # 先得到照片所属影集的uuid列表
    album_uuid_list = AlbumPhoto.objects.values('album_uuid').filter(photo_uuid=photo_uuid)
    # 然后再得到影集列表
    albums = Album.objects.filter(uuid__in=album_uuid_list)
    albums = albums.values('uuid', 'name', cover_path=F('cover__path_thumbnail'),
                           cover_name=F('cover__name'))  # 通过外键关联查询封面路径
    # 影集中的照片数量通过外键表获取
    albums = albums.annotate(photos=Count('albumphoto', filter=Q(albumphoto__photo_uuid__is_deleted=False)))
    albums = albums.order_by('name')
    # 返回结果
    response = json.loads(json.dumps(list(albums)))
    return JsonResponse(response, safe=False, status=200)


@require_http_methods(['GET'])
def photo_statistics(request):
    """统计照片数量和占用空间"""
    userid = request.GET.get('userid')
    photo = Photo.objects.filter(userid=userid, is_deleted=False).aggregate(nums=Count('uuid'), size=Sum('size'))
    return JsonResponse(photo, safe=False, status=200)


@require_http_methods(['POST'])
@transaction.atomic  # 数据库事务处理
def photo_trash(request):
    """将照片移到回收站"""
    save_tag = transaction.savepoint()  # 设置保存点，用于数据库事务回滚
    response = {}
    try:
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
        transaction.savepoint_rollback(save_tag)  # 回滚数据库事务
        response['msg'] = str(e)
        return JsonResponse(response, status=500)


@require_http_methods(['POST'])
@transaction.atomic  # 数据库事务处理
def photo_restore(request):
    """将照片从回收站恢复"""
    save_tag = transaction.savepoint()  # 设置保存点，用于数据库事务回滚
    response = {}
    try:
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
        transaction.savepoint_rollback(save_tag)  # 回滚数据库事务
        response['msg'] = str(e)
        return JsonResponse(response, status=500)


@require_http_methods(['POST'])
@transaction.atomic  # 数据库事务处理
def photo_remove(request):
    """永久删除照片"""
    save_tag = transaction.savepoint()  # 设置保存点，用于数据库事务回滚
    response = {}
    try:
        request_data = json.loads(request.body)
        photo_uuid_list = request_data.get('photo_list')
        photos = Photo.objects.filter(uuid__in=photo_uuid_list, is_deleted=True)
        for item in photos:
            file_path = os.path.join(settings.BASE_DIR, item.path, item.name)
            if os.path.exists(file_path):  # 删除上传的文件
                os.remove(file_path)
            file_path = os.path.join(settings.BASE_DIR, item.path_thumbnail, item.name)
            if os.path.exists(file_path):  # 删除生成的缩略图
                os.remove(file_path)
            if item.path_original:
                file_path = os.path.join(settings.BASE_DIR, item.path_original, item.name)
                if os.path.exists(file_path):  # 删除备份的原图
                    os.remove(file_path)
        AlbumPhoto.objects.filter(photo_uuid__in=photo_uuid_list).delete()
        Photo.objects.filter(uuid__in=photo_uuid_list).delete()
        return JsonResponse(response, status=200)
    except Exception as e:
        traceback.print_exc()  # 输出详细的错误信息
        transaction.savepoint_rollback(save_tag)  # 回滚数据库事务
        response['msg'] = str(e)
        return JsonResponse(response, status=500)


@require_http_methods(['POST'])
@transaction.atomic  # 数据库事务处理
def photo_empty_trash(request):
    """清空回收站"""
    save_tag = transaction.savepoint()  # 设置保存点，用于数据库事务回滚
    response = {}
    try:
        request_data = json.loads(request.body)
        userid = request_data.get('userid')
        photos = Photo.objects.filter(userid=userid, is_deleted=True)
        for item in photos:
            file_path = os.path.join(settings.BASE_DIR, item.path, item.name)
            if os.path.exists(file_path):  # 删除上传的文件
                os.remove(file_path)
            file_path = os.path.join(settings.BASE_DIR, item.path_thumbnail, item.name)
            if os.path.exists(file_path):  # 删除生成的缩略图
                os.remove(file_path)
            if item.path_original:
                file_path = os.path.join(settings.BASE_DIR, item.path_original, item.name)
                if os.path.exists(file_path):  # 删除备份的原图
                    os.remove(file_path)
        AlbumPhoto.objects.filter(photo_uuid__in=photos).delete()
        Photo.objects.filter(userid=userid, is_deleted=True).delete()
        return JsonResponse(response, status=200)
    except Exception as e:
        traceback.print_exc()  # 输出详细的错误信息
        transaction.savepoint_rollback(save_tag)  # 回滚数据库事务
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
