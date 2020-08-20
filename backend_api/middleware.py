import re
import json
from django.http import HttpResponse
from backend_api.common.token import Token

from django.utils.deprecation import MiddlewareMixin


class LoginMiddleware(MiddlewareMixin):
    """用户身份验证中间件"""

    def process_request(self, request):
        response = {}
        path = request.path
        if path == '/api/login' or path == '/api/refresh_token':
            return None
        if re.match(r'^/api/.*', path):  # 仅针对api的请求进行身份验证
            # 从Header中获取token等信息
            userid = request.META.get('HTTP_USERID')
            token = request.META.get('HTTP_TOKEN')
            if not Token.out_token(userid, token):
                response['msg'] = '您未登录或登录信息过期'
                return HttpResponse(json.dumps({'msg': '您未登录或登录信息过期'}), status=401)
        return None
