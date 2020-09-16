import json
import traceback
import uuid
from django.db import transaction
from django.db.models import Count, Q, Min, Max
from django.db.models import F
from django.forms import model_to_dict
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from backend_api.common.date_encoder import DateEncoder
from backend_api.models import Album, AlbumPhoto, Photo


@require_http_methods(['GET'])
def album_list(request):
    """获取影集列表"""
    userid = request.GET.get('userid')
    parent_uuid = request.GET.get('parent_uuid')

    albums = Album.objects.filter(userid=userid, parent_uuid=parent_uuid)
    albums = albums.values('uuid', 'name', 'parent_uuid', cover_path=F('cover__path_thumbnail_s'),
                           cover_name=F('cover__name'))  # 通过外键关联查询封面路径
    # 影集中的照片数量通过外键表获取
    albums = albums.annotate(photos=Count('albumphoto', filter=Q(albumphoto__photo_uuid__is_deleted=False)))
    albums = albums.annotate(
        min_time=Min('albumphoto__photo_uuid__exif_datetime', filter=Q(albumphoto__photo_uuid__is_deleted=False)))
    albums = albums.annotate(
        max_time=Max('albumphoto__photo_uuid__exif_datetime', filter=Q(albumphoto__photo_uuid__is_deleted=False)))
    albums = albums.order_by('name')

    response = json.loads(json.dumps(list(albums), cls=DateEncoder))
    return JsonResponse(response, safe=False, status=200)


@require_http_methods(['GET'])
def album_target_list(request):
    """获取影集列表（用于影集移动）"""
    userid = request.GET.get('userid')
    parent_uuid = request.GET.get('parent_uuid')
    curr_album_uuid = request.GET.get('curr_album_uuid')

    albums = Album.objects.filter(userid=userid, parent_uuid=parent_uuid)
    albums = albums.filter(~Q(uuid=curr_album_uuid))  # 目标影集不能是自己或者子集
    albums = albums.values('uuid', 'name', 'parent_uuid', cover_path=F('cover__path_thumbnail_s'),
                           cover_name=F('cover__name'))  # 通过外键关联查询封面路径
    # 影集中的照片数量通过外键表获取
    albums = albums.annotate(photos=Count('albumphoto', filter=Q(albumphoto__photo_uuid__is_deleted=False)))
    albums = albums.annotate(
        min_time=Min('albumphoto__photo_uuid__exif_datetime', filter=Q(albumphoto__photo_uuid__is_deleted=False)))
    albums = albums.annotate(
        max_time=Max('albumphoto__photo_uuid__exif_datetime', filter=Q(albumphoto__photo_uuid__is_deleted=False)))
    albums = albums.order_by('name')

    response = json.loads(json.dumps(list(albums), cls=DateEncoder))
    return JsonResponse(response, safe=False, status=200)


@require_http_methods(['GET'])
def album_get(request):
    """获取指定的影集信息"""
    album_uuid = request.GET.get('uuid')
    album = Album.objects.values('uuid', 'name', cover_path=F('cover__path_thumbnail_s'),
                                 cover_name=F('cover__name')).get(uuid=album_uuid)
    return JsonResponse(album, safe=False, status=200)


@require_http_methods(['POST'])
def album_new(request):
    """创建影集"""
    response = {}
    request_data = json.loads(request.body)
    name = request_data.get('name')  # 影集标题
    userid = request_data.get('userid')  # 当前登录用户名
    parent_uuid = request_data.get('parent_uuid')  # 上级影集uuid
    album_uuid = str(uuid.uuid1()).replace('-', '')  # 生成影集唯一序列号
    album = Album()
    album.uuid = album_uuid
    album.name = name
    album.userid = userid
    if parent_uuid is not None:  # 创建子影集
        album.parent_uuid = parent_uuid
    album.save()
    response['uuid'] = album_uuid  # 返回新创建的影集uuid
    return JsonResponse(response, status=200)


@require_http_methods(['POST'])
@transaction.atomic  # 数据库事务处理
def album_add_photo(request):
    """添加照片到影集"""
    save_tag = transaction.savepoint()  # 设置保存点，用于数据库事务回滚
    response = {}
    try:
        request_data = json.loads(request.body)
        album_uuid = request_data.get('album_uuid')
        photo_list = request_data.get('photo_list')
        for item in photo_list:
            AlbumPhoto.objects.filter(album_uuid=album_uuid, photo_uuid=item).delete()  # 先删除再添加
            album_photo = AlbumPhoto()
            album_photo.uuid = str(uuid.uuid1()).replace('-', '')
            album_photo.album_uuid = Album.objects.get(uuid=album_uuid)
            album_photo.photo_uuid = Photo.objects.get(uuid=item)
            album_photo.save()
        album_auto_cover(album_uuid)  # 设置影集封面
        return JsonResponse(response, status=200)
    except Exception as e:
        traceback.print_exc()  # 输出详细的错误信息
        transaction.savepoint_rollback(save_tag)  # 回滚数据库事务
        response['msg'] = str(e)
        return JsonResponse(response, status=500)


@require_http_methods(['POST'])
@transaction.atomic  # 数据库事务处理
def album_remove_photo(request):
    """从影集中移除照片"""
    save_tag = transaction.savepoint()  # 设置保存点，用于数据库事务回滚
    response = {}
    try:
        request_data = json.loads(request.body)
        album_uuid = request_data.get('album_uuid')
        photo_list = request_data.get('photo_list')
        AlbumPhoto.objects.filter(album_uuid=album_uuid, photo_uuid__in=photo_list).delete()
        # 如果该影集使用了即将被移除的照片作为封面，则首先将其取消
        Album.objects.filter(uuid=album_uuid, cover__in=photo_list, cover_from='user').update(cover=None,
                                                                                              cover_from='auto')
        album_auto_cover(album_uuid)  # 设置影集封面
        return JsonResponse(response, status=200)
    except Exception as e:
        traceback.print_exc()  # 输出详细的错误信息
        transaction.savepoint_rollback(save_tag)  # 回滚数据库事务
        response['msg'] = str(e)
        return JsonResponse(response, status=500)


@require_http_methods(['POST'])
@transaction.atomic  # 数据库事务处理
def album_pick_photo(request):
    """选择照片到影集，包括添加和移除"""
    save_tag = transaction.savepoint()  # 设置保存点，用于数据库事务回滚
    response = {}
    try:
        request_data = json.loads(request.body)
        album_uuid = request_data.get('album_uuid')
        add_list = request_data.get('add_list')
        remove_list = request_data.get('remove_list')
        for item in add_list:
            AlbumPhoto.objects.filter(album_uuid=album_uuid, photo_uuid=item).delete()  # 先删除再添加
            album_photo = AlbumPhoto()
            album_photo.uuid = str(uuid.uuid1()).replace('-', '')
            album_photo.album_uuid = Album.objects.get(uuid=album_uuid)
            album_photo.photo_uuid = Photo.objects.get(uuid=item)
            album_photo.save()
        AlbumPhoto.objects.filter(album_uuid=album_uuid, photo_uuid__in=remove_list).delete()
        # 如果该影集使用了即将被移除的照片作为封面，则首先将其取消
        Album.objects.filter(uuid=album_uuid, cover__in=remove_list, cover_from='user').update(cover=None,
                                                                                               cover_from='auto')
        album_auto_cover(album_uuid)  # 设置影集封面
        return JsonResponse(response, status=200)
    except Exception as e:
        traceback.print_exc()  # 输出详细的错误信息
        transaction.savepoint_rollback(save_tag)  # 回滚数据库事务
        response['msg'] = str(e)
        return JsonResponse(response, status=500)


@require_http_methods(['POST'])
@transaction.atomic  # 数据库事务处理
def album_remove(request):
    """删除影集（包含自身和所有的子集）"""
    save_tag = transaction.savepoint()  # 设置保存点，用于数据库事务回滚
    response = {}
    try:
        request_data = json.loads(request.body)
        album_uuid = request_data.get('uuid')
        albums = Album.objects.raw('''
            WITH RECURSIVE tmp_albums AS (
                SELECT uuid AS rootId FROM m_album WHERE uuid= %s
                UNION ALL
                SELECT uuid FROM m_album a,tmp_albums b WHERE a.parent_uuid = b.rootId
            )
            SELECT uuid FROM m_album WHERE EXISTS(SELECT uuid FROM tmp_albums WHERE rootId = uuid)
        ''', [album_uuid])
        for item in albums:
            Album.objects.filter(uuid=item.uuid).delete()
        return JsonResponse({}, status=200)
    except Exception as e:
        traceback.print_exc()  # 输出详细的错误信息
        transaction.savepoint_rollback(save_tag)  # 回滚数据库事务
        response['msg'] = str(e)
        return JsonResponse(response, status=500)


@require_http_methods(['POST'])
def album_rename(request):
    """重命名影集"""
    request_data = json.loads(request.body)
    album_uuid = request_data.get('uuid')
    name = request_data.get('name')
    album = Album.objects.get(uuid=album_uuid)
    album.name = name
    album.save()
    return JsonResponse({}, status=200)


@require_http_methods(['POST'])
def album_move(request):
    """移动影集"""
    request_data = json.loads(request.body)
    album_uuid = request_data.get('uuid')
    parent_uuid = request_data.get('parent_uuid')
    album = Album.objects.get(uuid=album_uuid)
    album.parent_uuid = parent_uuid
    album.save()
    return JsonResponse({}, status=200)


@transaction.atomic  # 数据库事务处理
def album_auto_cover(album_uuid):
    """自动设置指定影集及其父集的封面"""
    # 写入封面，遍历从该影集开始的所有上级，如果封面是由系统自动产生的，则替换它，否则保留原封面
    albums = Album.objects.raw('''
        SELECT t2.uuid, t2.cover, t2.cover_from FROM (
            SELECT @r AS _id,
                (SELECT @r := parent_uuid FROM m_album WHERE uuid = _id ) AS parent_uuid,
                @l:=@l+1 AS lvl
            FROM (select @r:=%s, @l:=0) vars, m_album 
            WHERE @r<>''
        ) t1 JOIN m_album t2 on t1._id = t2.uuid 
        ORDER BY t1.lvl DESC
    ''', [album_uuid])
    for item in albums:
        if item.cover_from != 'manual':
            # 以该影集及其子集中最后一次添加的照片作为封面
            albums = Album.objects.raw('''
                WITH RECURSIVE tmp_albums AS (
                    SELECT uuid AS rootId FROM m_album WHERE uuid= %s
                    UNION ALL
                    SELECT uuid FROM m_album a,tmp_albums b WHERE a.parent_uuid = b.rootId
                )
                SELECT uuid FROM m_album WHERE EXISTS(SELECT uuid FROM tmp_albums WHERE rootId = uuid)
            ''', [item.uuid])
            album_photo = AlbumPhoto.objects.filter(album_uuid__in=albums, photo_uuid__is_deleted=False).order_by(
                '-input_date').first()
            # 设置封面，如果影集和子集中没有任何照片时，则将封面设置为空
            if album_photo:
                Album.objects.filter(uuid=item.uuid).update(cover=album_photo.photo_uuid)
            else:
                Album.objects.filter(uuid=item.uuid).update(cover=None)


@require_http_methods(['POST'])
def album_set_cover(request):
    """手动设置影集封面"""
    request_data = json.loads(request.body)
    album_uuid = request_data.get('album_uuid')
    photo_uuid = request_data.get('photo_uuid')
    album = Album.objects.get(uuid=album_uuid)
    album.cover = Photo.objects.get(uuid=photo_uuid)
    album.cover_from = 'manual'
    album.save()
    return JsonResponse({}, status=200)
