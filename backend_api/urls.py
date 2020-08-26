from django.urls import path
from backend_api.views.login import *
from backend_api.views.upload_file import *
from backend_api.views.photo import *
from backend_api.views.user import *
from backend_api.views.album import *

urlpatterns = [
    path('login', login),  # 用户登录
    path('refresh_token', refresh_token),  # 刷新token
    path('upload_photo', upload_photo),  # 上传照片
    path('photo_list', photo_list),  # 获取照片列表
    path('user_getinfo', user_getinfo),  # 获取指定用户的基本信息
    path('user_upload_avatar', user_upload_avatar),  # 上传用户头像
    path('album_list', album_list),  # 获取影集列表
    path('album_get', album_get),  # 获取指定的影集信息
    path('album_new', album_new),  # 创建影集
    path('album_addphoto', album_addphoto),  # 添加照片到影集
    path('album_remove', album_remove),  # 删除影集
    path('album_rename', album_rename),  # 重命名影集
]
