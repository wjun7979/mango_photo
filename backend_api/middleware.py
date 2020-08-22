import re
import traceback
from django.http import JsonResponse
from backend_api.common.token import Token
from django.utils.deprecation import MiddlewareMixin


class MyMiddleware(MiddlewareMixin):
    """用户自定义中间件"""

    def process_request(self, request):
        """产生request对象之后，url匹配之前调用"""
        response = {}
        try:
            # return None  # 临时放开验证
            path = request.path
            if path == '/api/login' or path == '/api/refresh_token':
                return None
            if re.match(r'^/api/.*', path):  # 仅针对api的请求进行身份验证
                # 从Header中获取token等信息
                userid = request.META.get('HTTP_USERID')
                token = request.META.get('HTTP_TOKEN')
                if not Token.out_token(userid, token):
                    response['msg'] = '您未登录或登录信息过期'
                    return JsonResponse(response, status=401)
            return None
        except Exception as e:
            traceback.print_exc()
            response['msg'] = str(e)
            return JsonResponse(response, status=500)

    def process_exception(self, request, exception):
        """视图函数发生异常时调用"""
        response = {}
        traceback.print_exc()
        response['msg'] = str(exception)
        return JsonResponse(response, status=500)
