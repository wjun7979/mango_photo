import os
import hashlib
import json
import uuid
import requests  # 调用api
import urllib
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from backend_api.common.token import Token
from backend_api.models import User


@require_http_methods(['POST'])  # django内置的视力装饰器，这行表示只能通过POST方法访问
def login(request):
    """用户登录"""
    response = {}
    request_data = json.loads(request.body)
    userid = request_data.get('userid')
    password = request_data.get('password')
    user = User.objects.filter(userid=userid).first()
    if not user:
        response['msg'] = '用户不存在'
        return JsonResponse(response, status=500)
    encrypt_pwd = hashlib.md5(password.join('Nhj10LyBc').encode("utf-8")).hexdigest()
    # Abcd1234的加密后密码为：3b4f646f390eeab7b87022bfad32f15c
    if encrypt_pwd != user.password:
        response['msg'] = '登录密码错误'
        return JsonResponse(response, status=500)

    user.last_login_ip = __get_ip_address(request)  # 记录最后一次登录IP
    user.save()
    response['userid'] = userid
    response['token'] = Token.get_token(userid)
    return JsonResponse(response, status=200)


@require_http_methods(['POST'])
def refresh_token(request):
    """刷新token"""
    response = {}
    request_data = json.loads(request.body)
    userid = request_data.get('userid')
    response['userid'] = userid
    response['token'] = Token.get_token(userid)
    return JsonResponse(response, status=200)


@require_http_methods(['GET'])
def login_get_bgimg(request):
    """获取背景图片，将bing每日图片保存到本地，解决bing被墙的问题"""
    response = {}
    # 删除之前下载的图片
    filepath = os.path.join(settings.BASE_DIR, 'photos', 'common', 'login_bg')
    del_list = os.listdir(filepath)
    for f in del_list:
        file_path = os.path.join(filepath, f)
        if os.path.isfile(file_path):
            os.remove(file_path)
    # 请求bing的每日图片，并将其保存到本地
    api = 'https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1'
    res = requests.get(api).json()
    imgurl = 'https://www.bing.com' + res['images'][0].get('url')
    save_name = str(uuid.uuid1()).replace('-', '') + '.jpg'
    savepath = os.path.join(settings.BASE_DIR, 'photos', 'common', 'login_bg', save_name)
    urllib.request.urlretrieve(imgurl, savepath)
    response['url'] = '/photos/common/login_bg/' + save_name
    return JsonResponse(response, status=200)


def __get_ip_address(request):
    """获取客户端IP地址"""
    ip = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if not ip:
        ip = request.META.get('REMOTE_ADDR', "")
    return ip
