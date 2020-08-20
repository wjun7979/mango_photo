import traceback
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from backend_api.common.date_encoder import DateEncoder
from backend_api.models import Photo


@require_http_methods(['GET'])
def photo_list(request):
    """浏览照片"""
    response = {}
    try:
        userid = request.GET.get('userid')
        photos = Photo.objects.values('uuid', 'path', 'path_thumbnail', 'name', 'width', 'height', 'exif_datetime')\
            .filter(userid=userid, is_deleted=False).order_by('-exif_datetime')
        response['list'] = json.loads(json.dumps(list(photos), cls=DateEncoder))
        return JsonResponse(response, status=200)
    except Exception as e:
        traceback.print_exc()
        response['msg'] = str(e)
        return JsonResponse(response, status=500, json_dumps_params={'ensure_ascii': False})
