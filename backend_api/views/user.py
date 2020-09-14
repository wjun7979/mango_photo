import os
import traceback
from django.conf import settings
from django.db import transaction
from django.forms import model_to_dict
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from PIL import Image
from backend_api.models import User


@require_http_methods(['GET'])
def user_getinfo(request):
    """获取指定用户的基本信息"""
    userid = request.GET.get('userid')
    user = User.objects.get(userid=userid)
    response = model_to_dict(user)
    return JsonResponse(response, safe=False, status=200)


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
        im = Image.open(file)
        if im.width > 300 or im.height > 300:
            im.thumbnail((300, 300))  # 创建大小不超过指定值的缩略图
        ext_filename = os.path.splitext(file.name)[1]
        file_path = os.path.join('photos', userid, 'avatar')  # 相对路径
        real_path = os.path.join(settings.BASE_DIR, file_path)  # 物理路径
        if not os.path.exists(real_path):  # 如果目标文件夹不存在则创建
            os.makedirs(real_path, exist_ok=True)
        full_path = os.path.join(real_path, userid + ext_filename)  # 包含路径的完整文件名
        im.save(full_path)
        im.close()
        # 将头像路径存入数据库
        user = User.objects.get(userid=userid)
        user.avatar = os.path.join(file_path, userid + ext_filename)
        user.save()
        # 向前端返回头像路径
        response['path'] = os.path.join(file_path, userid + ext_filename)
        return JsonResponse(response, status=200)
    except Exception as e:
        traceback.print_exc()  # 输出详细的错误信息
        transaction.savepoint_rollback(save_tag)  # 回滚数据库事务
        if full_path and os.path.exists(full_path):  # 出错时删除可能已经上传的文件
            os.remove(full_path)
        response['msg'] = str(e)
        return JsonResponse(response, status=500)

