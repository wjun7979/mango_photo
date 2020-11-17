import json
from django.http import JsonResponse
from django.db.models import Count, Case, When
from django.views.decorators.http import require_http_methods
from backend_api.models import Address


@require_http_methods(['GET'])
def place_list(request):
    """获取地点列表"""
    userid = request.GET.get('userid')
    places = Address.objects.filter(uuid__userid=userid, uuid__is_deleted=False)
    places = places.values('province', name=Case(When(city='', then='district'), default='city'))
    places = places.annotate(photos=Count('uuid'))
    places = places.order_by('-photos')
    # 获取地点的封面图片
    photos = Address.objects.values('uuid__path_thumbnail_s', 'uuid__name')
    photos = photos.filter(uuid__userid=userid, uuid__is_deleted=False)
    for place in places:
        # 首先以市级条件进行查找
        cover = photos.filter(province=place['province'], city=place['name'])
        cover = cover.order_by('-uuid__exif_datetime')
        cover = cover.first()
        if cover:
            place['cover'] = cover['uuid__path_thumbnail_s'] + '/' + cover['uuid__name']
        # 市级名称为空时(例如湖北省神农架林区)，以县级条件进行查找
        if place.get('cover') is None:
            cover = photos.filter(province=place['province'], district=place['name'])
            cover = cover.order_by('-uuid__exif_datetime')
            cover = cover.first()
            if cover:
                place['cover'] = cover['uuid__path_thumbnail_s'] + '/' + cover['uuid__name']
    response = json.loads(json.dumps(list(places)))
    return JsonResponse(response, safe=False, status=200)


@require_http_methods(['GET'])
def place_show(request):
    """根据输入参数返回省、市、县三级名称"""
    userid = request.GET.get('userid')
    province = request.GET.get('province')  # 省
    name = request.GET.get('name')  # 市或县
    response = {
        'province': province,
        'city': 'none',
        'district': 'none',
    }

    address = Address.objects
    address = address.filter(uuid__userid=userid, uuid__is_deleted=False, province=province)
    res = address.filter(city=name)
    res = res.first()
    if res:
        response['city'] = res.city
    else:
        res = address.filter(district=name)
        res = res.first()
        if res:
            response['district'] = res.district
    return JsonResponse(response, safe=False, status=200)
