import os
from datetime import datetime

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods


@require_http_methods(['POST'])
def upload_file(request):
    """上传文件"""
    response = {}
    try:
        now = datetime.now()
        file = request.FILES['file']
        file_name = file.name  # 原始文件名
        # 根据当前日期创建文件夹 /photos/年/月/日
        file_path = os.path.join(settings.BASE_DIR, 'photos', now.strftime('%Y'), now.strftime('%m'),
                                 now.strftime('%d'))
        # 如果目标文件夹不存在则创建
        if not os.path.exists(file_path):
            os.makedirs(file_path, exist_ok=True)
        write_file(os.path.join(file_path, file_name), file)
        response['msg'] = 'success'
    except Exception as e:
        print(str(e))
        response['msg'] = str(e)
    return JsonResponse(response)


def write_file(file_full_path, file):
    """写入文件"""
    with open(file_full_path, 'wb') as f:  # wb表示写二进制文件
        if file.multiple_chunks():  # 判断文件是否足够大，一般为2.5M
            for content in file.chunks():  # 返回一个生成器对象，当multiple_chunks()为True时应该使用这个方法来代替read()
                f.write(content)
        else:
            data = file.read()
            f.write(data)
