from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.serializers import serialize
import json
from backend_api.models import Photo


@require_http_methods(['GET'])
def photo_list(request):
    """浏览照片"""
    response = {}
    try:
        photos = Photo.objects.values('uuid', 'thumbnail_path', 'path', 'name').order_by('-exif_datetime')
        response['msg'] = 'success'
        response['list'] = json.loads(json.dumps(list(photos)))
    except Exception as e:
        print(str(e))
        response['msg'] = str(e)
    return JsonResponse(response)
