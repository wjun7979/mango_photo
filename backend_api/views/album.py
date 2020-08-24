import json
import uuid
from django.forms import model_to_dict
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from backend_api.models import Album


@require_http_methods(['GET'])
def album_list(request):
    """获取影集列表"""
    userid = request.GET.get('userid')
    albums = Album.objects.filter(userid=userid).order_by('name').values('uuid', 'name', 'cover', 'photos')
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
    return JsonResponse({}, status=200)


@require_http_methods(['POST'])
def album_remove(request):
    """删除影集"""
    request_data = json.loads(request.body)
    album_uuid = request_data.get('uuid')
    Album.objects.filter(uuid=album_uuid).delete()
    return JsonResponse({}, status=200)


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
