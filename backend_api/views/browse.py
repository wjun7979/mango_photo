from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from backend_api.common.date_encoder import DateEncoder
from backend_api.models import Photo


@require_http_methods(['GET'])
def photo_list(request):
    """浏览照片"""
    response = {}
    userid = request.GET.get('userid')
    photos = Photo.objects.filter(userid=userid, is_deleted=False).order_by('-exif_datetime')\
        .values('uuid', 'path', 'path_thumbnail', 'name', 'width', 'height', 'exif_datetime')
    response = json.loads(json.dumps(list(photos), cls=DateEncoder))
    # safe 控制是否只有字典类型的数据才能被序列化，这里的response是一个数组，所以要将safe设置为False
    return JsonResponse(response, safe=False, status=200)
