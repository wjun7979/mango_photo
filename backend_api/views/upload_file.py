import os
import hashlib
import uuid
from datetime import datetime
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from PIL import Image
import exifread
from backend_api.models import Photo


@require_http_methods(['POST'])
def upload_file(request):
    """上传文件"""
    response = {}
    try:
        now = datetime.now()  # 当前时间，用于创建目录
        file = request.FILES['file']  # 前端上传的文件对象

        # 获取文件md5值，然后检查是否已经存在，如果存在就跳过
        file_md5 = get_file_md5(file)
        photo = Photo.objects.filter(md5=file_md5)  # 表过滤
        if len(photo) > 0:
            response['msg'] = '照片已存在，跳过'
            return JsonResponse(response, status=500, json_dumps_params={'ensure_ascii': False})

        # 根据当前日期创建文件夹 /photos/original/年/月/日
        file_path = os.path.join('photos', 'original', now.strftime('%Y'), now.strftime('%m'),
                                 now.strftime('%d'))  # 相对路径
        real_path = os.path.join(settings.BASE_DIR, file_path)  # 物理路径
        if not os.path.exists(real_path):  # 如果目标文件夹不存在则创建
            os.makedirs(real_path, exist_ok=True)

        # 检查当前目录下是否有同名文件，如果存在则重命名
        file_name = file.name  # 原始文件名
        full_path = os.path.join(real_path, file_name)  # 包含路径的完整文件名
        if os.path.exists(full_path):
            splitext = os.path.splitext(full_path)
            full_path = splitext[0] + '_' + str(uuid.uuid1()).replace('-', '') + splitext[1]

        # 写入文件
        file.seek(0)  # 因为之前获取md5时读取过文件，所以这里要将指针定位到文件头
        write_file(full_path, file)

        # 创建缩略图
        thumbnail = create_thumbnail(full_path)

        # 获取照片的拍摄时间，优先从Exif信息中获取，否则取文件的最后一次修改时间
        dt = request.POST['dt']  # 从前端传入的文件最后一次修改时间
        with open(full_path, 'rb') as f:
            tags = exifread.process_file(f)
            if 'EXIF DateTimeOriginal' in tags.keys():
                dt = str(tags['EXIF DateTimeOriginal'])
            if 'Image DateTime' in tags.keys():
                dt = str(tags['Image DateTime'])
        if dt[4:5] == ':':  # 从Exif信息中获取的日期分隔符是冒号，需要替换
            dt = str(dt).replace(':', '-', 2)

        # 获取照片的尺寸
        im = Image.open(full_path)  # 打开原始照片文件
        im_width = im.width
        im_height = im.height

        # 写入数据库
        photo = Photo()
        photo.uuid = str(uuid.uuid1()).replace('-', '')
        photo.path = file_path
        photo.name = os.path.split(full_path)[1]
        photo.md5 = file_md5
        photo.size = file.size
        photo.thumbnail_path = thumbnail
        photo.exif_datetime = dt
        photo.width = im_width
        photo.height = im_height
        photo.save()

        response['msg'] = 'success'
    except Exception as e:
        print(str(e))
        if os.path.exists(full_path):  # 出错时删除可能已经上传的文件
            os.remove(full_path)
        response['msg'] = str(e)
        return JsonResponse(response, status=500, json_dumps_params={'ensure_ascii': False})
    return JsonResponse(response)


def write_file(full_path, file):
    """写入文件"""
    with open(full_path, 'wb') as f:  # wb表示写二进制文件
        if file.multiple_chunks():  # 判断文件是否足够大，一般为2.5M
            for content in file.chunks():  # 返回一个生成器对象，当multiple_chunks()为True时应该使用这个方法来代替read()
                f.write(content)
        else:
            data = file.read()
            f.write(data)


def get_file_md5(file):
    """获取文件的md5值"""
    if file.multiple_chunks():  # 超过2.5M的大文件
        m = hashlib.md5()  # 创建md5对象
        for content in file.chunks():
            m.update(content)
        return m.hexdigest()
    else:  # 小文件
        data = file.read()
        return hashlib.md5(data).hexdigest()


def create_thumbnail(full_path):
    """创建照片缩略图"""
    im = Image.open(full_path)  # 打开原始照片文件
    im.thumbnail((500, 500))  # 创建大小不超过指定值的缩略图
    # 根据当前日期创建文件夹 /photos/thumbnail/年/月/日
    now = datetime.now()  # 当前时间，用于创建目录
    file_path = os.path.join('photos', 'thumbnail', now.strftime('%Y'), now.strftime('%m'),
                             now.strftime('%d'))  # 相对路径
    real_path = os.path.join(settings.BASE_DIR, file_path)  # 物理路径
    if not os.path.exists(real_path):  # 如果目标文件夹不存在则创建
        os.makedirs(real_path, exist_ok=True)
    file_name = os.path.split(full_path)[1]
    im.save(os.path.join(real_path, file_name))  # 保存缩略图
    return file_path
