import json
from django.http import JsonResponse
from django.db.models import Count, Case, When
from django.views.decorators.http import require_http_methods
from backend_api.models import Address


@require_http_methods(['GET'])
def location_list(request):
    """获取地点列表"""
    userid = request.GET.get('userid')
    locations = Address.objects.filter(uuid__userid=userid, uuid__is_deleted=False)
    locations = locations.values('province', name=Case(When(city='', then='district'), default='city'))
    locations = locations.annotate(photos=Count('uuid'))
    locations = locations.order_by('-photos')
    # 获取地点的封面图片
    address = Address.objects.values('uuid__path_thumbnail_s', 'uuid__name')
    address = address.filter(uuid__userid=userid, uuid__is_deleted=False)
    for location in locations:
        # 首先以市级条件进行查找
        cover = address.filter(province=location['province'], city=location['name'])
        cover = cover.order_by('-uuid__exif_datetime')
        cover = cover.first()
        if cover:
            location['cover'] = cover['uuid__path_thumbnail_s'] + '/' + cover['uuid__name']
        # 市级名称为空时(例如湖北省神农架林区)，以县级条件进行查找
        if location.get('cover') is None:
            cover = address.filter(province=location['province'], district=location['name'])
            cover = cover.order_by('-uuid__exif_datetime')
            cover = cover.first()
            if cover:
                location['cover'] = cover['uuid__path_thumbnail_s'] + '/' + cover['uuid__name']
    response = json.loads(json.dumps(list(locations)))
    return JsonResponse(response, safe=False, status=200)


@require_http_methods(['GET'])
def location_show(request):
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
