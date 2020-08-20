from django.urls import path
from backend_api.views.login import *
from backend_api.views.upload_file import *
from backend_api.views.browse import *

urlpatterns = [
    path('login', login),  # 用户登录
    path('refresh_token', refresh_token),  # 刷新token
    path('upload_file', upload_file),  # 上传照片
    path('photo_list', photo_list),  # 获取照片列表
]
