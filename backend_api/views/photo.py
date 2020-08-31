import os
import json
import traceback

from django.db import transaction
from django.db.models import Count, Sum
from django.forms import model_to_dict
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
    photos = photos.values('uuid', 'path', 'path_thumbnail', 'name', 'width', 'height', 'exif_datetime')
    photos = photos.order_by('-exif_datetime')

    response = json.loads(json.dumps(list(photos), cls=DateEncoder))
    # safe 控制是否只有字典类型的数据才能被序列化，这里的response是一个数组，所以要将safe设置为False
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
