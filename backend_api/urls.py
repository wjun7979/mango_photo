from django.urls import path
from backend_api.views.login import *
from backend_api.views.upload_file import *
from backend_api.views.browse import *
from backend_api.views.user import *

urlpatterns = [
    path('login', login),  # 用户登录
    path('refresh_token', refresh_token),  # 刷新token
    path('upload_photo', upload_photo),  # 上传照片
    path('photo_list', photo_list),  # 获取照片列表
    path('get_user', get_user),  # 获取指定用户的基本信息
    path('upload_avatar', upload_avatar)  # 上传用户头像
]
