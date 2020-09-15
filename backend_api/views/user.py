import os
import hashlib
import json
import uuid
import traceback
from django.conf import settings
from django.db import transaction
from django.forms import model_to_dict
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from PIL import Image
from backend_api.models import User


@require_http_methods(['GET'])
def user_get_info(request):
    """获取指定用户的基本信息"""
    userid = request.GET.get('userid')
    user = User.objects.get(userid=userid)
    response = model_to_dict(user)
    return JsonResponse(response, safe=False, status=200)


@require_http_methods(['POST'])
def user_save_info(request):
    """保存用户信息"""
    request_data = json.loads(request.body)
    userid = request_data.get('userid')
    user = User.objects.get(userid=userid)
    user.first_name = request_data.get('first_name')
    user.last_name = request_data.get('last_name')
    user.mobile_number = request_data.get('mobile_number')
    user.email = request_data.get('email')
    user.save()
    return JsonResponse({}, safe=False, status=200)


@require_http_methods(['POST'])
def user_save_pwd(request):
    """保存登录密码"""
    response = {}
    request_data = json.loads(request.body)
    userid = request_data.get('userid')
    old_pwd = request_data.get('old_pwd')
    new_pwd = request_data.get('new_pwd')
    encrypt_pwd = hashlib.md5(old_pwd.join('Nhj10LyBc').encode("utf-8")).hexdigest()
    user = User.objects.get(userid=userid)
    if encrypt_pwd != user.password:
        response['msg'] = '原登录密码错误'
        return JsonResponse(response, status=500)
    user.password = hashlib.md5(new_pwd.join('Nhj10LyBc').encode("utf-8")).hexdigest()
    user.save()
    return JsonResponse({}, safe=False, status=200)


@require_http_methods(['POST'])
@transaction.atomic  # 数据库事务处理
def user_upload_avatar(request):
    """上传用户头像"""
    save_tag = transaction.savepoint()  # 设置保存点，用于数据库事务回滚
    response = {}
    full_path = ''  # 头像文件的完整路径
    try:
        userid = request.POST['userid']  # 当前登录的用户id
        file = request.FILES['file']  # 前端上传的文件对象
        # 首先删除原先的头像文件
        user = User.objects.get(userid=userid)
        if user.avatar:
            avatar_path = os.path.join(settings.BASE_DIR, user.avatar)
            if user.avatar and os.path.exists(avatar_path):
                os.remove(avatar_path)
        # 然后再保存新的头像文件
        im = Image.open(file)
        if im.width > 300 or im.height > 300:
            im.thumbnail((300, 300))  # 创建大小不超过指定值的缩略图
        ext_filename = os.path.splitext(file.name)[1]
        file_path = os.path.join('photos', userid, 'avatar')  # 相对路径
        real_path = os.path.join(settings.BASE_DIR, file_path)  # 物理路径
        if not os.path.exists(real_path):  # 如果目标文件夹不存在则创建
            os.makedirs(real_path, exist_ok=True)
        avatar_uuid = str(uuid.uuid1()).replace('-', '')
        full_path = os.path.join(real_path, avatar_uuid + ext_filename)  # 包含路径的完整文件名
        im.save(full_path)
        im.close()
        # 将头像路径存入数据库
        user.avatar = os.path.join(file_path, avatar_uuid + ext_filename)
        user.save()
        # 向前端返回头像路径
        response['path'] = os.path.join(file_path, avatar_uuid + ext_filename)
        return JsonResponse(response, status=200)
    except Exception as e:
        traceback.print_exc()  # 输出详细的错误信息
        transaction.savepoint_rollback(save_tag)  # 回滚数据库事务
        if full_path and os.path.exists(full_path):  # 出错时删除可能已经上传的文件
            os.remove(full_path)
        response['msg'] = str(e)
        return JsonResponse(response, status=500)


@require_http_methods(['GET'])
def user_remove_avatar(request):
    """清除用户头像"""
    userid = request.GET.get('userid')
    user = User.objects.get(userid=userid)
    avatar_path = os.path.join(settings.BASE_DIR, user.avatar)
    if os.path.exists(avatar_path):
        os.remove(avatar_path)
    user.avatar = ''
    user.save()
    return JsonResponse({}, safe=False, status=200)
