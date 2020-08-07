from django.db import models


class Photo(models.Model):
    """照片"""
    uuid = models.CharField(primary_key=True, max_length=32)
    path = models.CharField(max_length=500)  # 照片文件存储路径
    name = models.CharField(max_length=200)  # 照片文件名
    md5 = models.CharField(max_length=32)  # 照片文件MD5值
    size = models.FloatField()  # 照片文件大小
    width = models.IntegerField(null=True)  # 照片宽度
    height = models.IntegerField(null=True)  # 照片高度
    thumbnail_path = models.CharField(null=True, max_length=500)  # 缩略图存储路径
    exif_exposure_time = models.CharField(null=True, max_length=100)  # 曝光时间
    exif_fnumber = models.CharField(null=True, max_length=100)  # 光圈
    exif_datetime = models.DateTimeField(null=True)  # 拍摄时间
    exif_gpslatitude = models.CharField(null=True, max_length=100)  # GPS纬度
    exif_gpslongitude = models.CharField(null=True, max_length=100)  # GPS经度
    deleted_flag = models.BooleanField(default=False)  # 删除标志
    input_date = models.DateTimeField(auto_now_add=True)  # 录入时间
    update_date = models.DateTimeField(auto_now=True)  # 修改时间

    class Meta:
        db_table = 'photo'  # 指定数据库表名

    def __str__(self):
        return self.uuid
