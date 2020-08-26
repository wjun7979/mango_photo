import json
import traceback
import uuid

from django.db import transaction
from django.db.models import Count
from django.db.models import F
from django.forms import model_to_dict
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from backend_api.models import Album, AlbumPhoto, Photo


@require_http_methods(['GET'])
def album_list(request):
    """获取影集列表"""
    userid = request.GET.get('userid')
    parent_uuid = request.GET.get('parent_uuid')

    albums = Album.objects.filter(userid=userid, parent_uuid=parent_uuid)
    albums = albums.values('uuid', 'name', cover_path=F('cover__path_thumbnail'),
                           cover_name=F('cover__name'))  # 通过外键关联查询封面路径
    albums = albums.annotate(photos=Count('albumphoto'))  # 影集中的照片数量通过外键表获取
    albums = albums.order_by('name')

    response = json.loads(json.dumps(list(albums)))
    return JsonResponse(response, safe=False, status=200)


@require_http_methods(['GET'])
def album_get(request):
    """获取指定的影集信息"""
    album_uuid = request.GET.get('uuid')
    album = Album.objects.get(uuid=album_uuid)
    response = model_to_dict(album)
    return JsonResponse(response, safe=False, status=200)


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
def album_addphoto(request):
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

        # 写入封面，遍历从该影集开始的所有上级，如果封面是由系统自动产生的，则替换它，否则保留原封面
        last_photo_uuid = photo_list[-1]  # 将本次添加的最后一张照片作为封面
        albums = Album.objects.raw('''
            SELECT t2.uuid, t2.cover, t2.cover_from FROM (
                SELECT @r AS _id,
                    (SELECT @r := parent_uuid FROM m_album WHERE uuid = _id ) AS parent_uuid,
                    @l:=@l+1 AS lvl
                FROM (select @r:=%s, @l:=0) vars, m_album 
                WHERE @r<>'' AND parent_uuid <>''
            ) t1 JOIN m_album t2 on t1._id = t2.uuid 
            ORDER BY t1.lvl DESC
        ''', [album_uuid])
        for item in albums:
            if item.cover_from == 'auto':
                album = Album.objects.get(uuid=item.uuid)
                album.cover = Photo.objects.get(uuid=last_photo_uuid)
                album.save()
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
