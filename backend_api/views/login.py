import traceback
import hashlib
import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from backend_api.common.token import Token
from backend_api.models import User


@require_http_methods(['POST'])  # django内置的视力装饰器，这行表示只能通过POST方法访问
def login(request):
    """用户登录"""
    response = {}
    try:
        request_data = json.loads(request.body)
        userid = request_data.get('userid')
        password = request_data.get('password')
        user = User.objects.filter(userid=userid).first()
        if not user:
            response['msg'] = '用户不存在'
            return JsonResponse(response, status=500, json_dumps_params={'ensure_ascii': False})
        encrypt_pwd = hashlib.md5(password.join('Nhj10LyBc').encode("utf-8")).hexdigest()
        if encrypt_pwd != user.password:
            response['msg'] = '登录密码错误'
            return JsonResponse(response, status=500, json_dumps_params={'ensure_ascii': False})

        user.last_login_ip = __get_ip_address(request)  # 记录最后一次登录IP
        user.save()
        response['userid'] = userid
        response['token'] = Token.get_token(userid)
        return JsonResponse(response, status=200)
    except Exception as e:
        traceback.print_exc()
        response['msg'] = str(e)
        return JsonResponse(response, status=500, json_dumps_params={'ensure_ascii': False})


@require_http_methods(['POST'])
def refresh_token(request):
    """刷新token"""
    response = {}
    request_data = json.loads(request.body)
    userid = request_data.get('userid')
    response['userid'] = userid
    response['token'] = Token.get_token(userid)
    return JsonResponse(response, status=200)


def __get_ip_address(request):
    """获取客户端ip地址"""
    ip = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if not ip:
        ip = request.META.get('REMOTE_ADDR', "")
    return ip
