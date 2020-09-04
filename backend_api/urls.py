from django.urls import path
from backend_api.views.login import *
from backend_api.views.upload_file import *
from backend_api.views.photo import *
from backend_api.views.user import *
from backend_api.views.album import *

urlpatterns = [
    path('login', login),  # 用户登录
    path('refresh_token', refresh_token),  # 刷新token
    path('login_get_bgimg', login_get_bgimg),  # 获取背景图片
    path('upload_photo', upload_photo),  # 上传照片
    path('user_getinfo', user_getinfo),  # 获取指定用户的基本信息
    path('user_upload_avatar', user_upload_avatar),  # 上传用户头像
    path('photo_list', photo_list),  # 获取照片列表
    path('photo_get_info', photo_get_info),  # 获取指定照片详细信息
    path('photo_get_albums', photo_get_albums),  # 获取指定照片所属的影集列表
    path('photo_statistics', photo_statistics),  # 统计照片数量和占用空间等信息
    path('photo_trash', photo_trash),  # 将照片移到回收站
    path('photo_restore', photo_restore),  # 将照片从回收站恢复
    path('photo_remove', photo_remove),  # 永久删除照片
    path('photo_empty_trash', photo_empty_trash),  # 清空回收站
    path('photo_set_comments', photo_set_comments),  # 为照片添加说明文字
    path('album_list', album_list),  # 获取影集列表
    path('album_get', album_get),  # 获取指定的影集信息
    path('album_new', album_new),  # 创建影集
    path('album_add_photo', album_add_photo),  # 添加照片到影集
    path('album_remove_photo', album_remove_photo),  # 从影集中移除照片
    path('album_pick_photo', album_pick_photo),  # 选择照片到影集，包括添加和移除
    path('album_remove', album_remove),  # 删除影集
    path('album_rename', album_rename),  # 重命名影集
]
