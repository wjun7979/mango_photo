import os
import traceback
import uuid
import requests
import base64
import json
from celery import task
from django.conf import settings
from backend_api.models import Photo, PhotoTag


@task
def thing_get_tags():
    """获取图像标签"""
    print('开始执行图像标签检测任务...')

    access_token = huawei_ai_get_token()  # 获取鉴权token
    api = 'https://image.cn-north-4.myhuaweicloud.com/v1.0/image/tagging'
    headers = {'content-type': 'application/json;charset=utf8', 'X-Auth-Token': access_token}

    # 从Photo中获取没有执行图像标签检测的照片列表
    photos = Photo.objects.filter(is_get_tag=False).all()[:2000]
    total = len(photos)
    for index, photo in enumerate(photos):
        print('正在执行图像标签检测：' + str(index + 1) + '/' + str(total) + ' ' + str(
            round((index + 1) / total * 100, 2)) + '%')
        try:
            photo_path = os.path.join(settings.BASE_DIR, photo.path_thumbnail_l, photo.name)  # 照片绝对路径
            with open(photo_path, 'rb') as f:
                photo_data = f.read()
                photo_base64_data = base64.b64encode(photo_data)  # base64编码
            data = {
                'image': photo_base64_data.decode("utf-8"),
                'limit': 10,
                'threshold': 60,
            }
            res = requests.post(api, json.dumps(data), headers=headers)
            result_status_code = res.status_code
            result = res.json()  # 获取响应数据，并解析JSON，转化为python字典
            res.close()
            if result_status_code != 200:  # 接口调用失败
                raise Exception(str(result['error_code']) + ': ' + result['error_msg'])  # 抛出异常
            # print(result)
            for tag in result['result']['tags']:
                photo_tag = PhotoTag()
                photo_tag.uuid = str(uuid.uuid1()).replace('-', '')
                photo_tag.userid = photo.userid
                photo_tag.photo_uuid = Photo.objects.get(uuid=photo.uuid)
                photo_tag.tag_name = tag['tag']
                photo_tag.confidence = tag['confidence']
                photo_tag.save()
        except Exception as e:
            traceback.print_exc()  # 输出详细的错误信息
            print(str(e))
            continue
        finally:
            # 写入Photo表的图像标签检测标志
            Photo.objects.filter(uuid=photo.uuid).update(is_get_tag=True)
    print('图像标签检测任务执行成功...')


def huawei_ai_get_token():
    """获取华为AI鉴权token"""
    api = 'https://iam.cn-north-4.myhuaweicloud.com/v3/auth/tokens'
    headers = {'content-type': 'application/json;charset=utf8'}
    params = {
        "auth": {
            "identity": {
                "methods": [
                    "password"
                ],
                "password": {
                    "user": {
                        "domain": {
                            "name": "wjun7979"
                        },
                        "name": "wjun7979",
                        "password": "Feng2@jun4hw"
                    }
                }
            },
            "scope": {
                "project": {
                    "id": "0a891574f4000f192f92c01242a9011e",
                    "name": "cn-north-4"
                }
            }
        }
    }
    res = requests.post(api, data=json.dumps(params), headers=headers)
    if res.status_code == 201:
        token = res.headers['X-Subject-Token']
    res.close()
    return token
