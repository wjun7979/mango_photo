from django.db import models


class User(models.Model):
    """用户"""
    userid = models.CharField(primary_key=True, max_length=50)  # 用户ID
    password = models.CharField(max_length=50)  # 登录密码
    first_name = models.CharField(max_length=50)  # 姓
    last_name = models.CharField(max_length=50)  # 名
    mobile_number = models.CharField(unique=True, max_length=20)  # 移动电话
    email = models.CharField(unique=True, max_length=50)  # 电子邮件
    avatar = models.CharField(null=True, max_length=500)  # 用户头像
    last_login_time = models.DateTimeField(null=True, auto_now=True)  # 最后一次登录时间
    last_login_ip = models.CharField(null=True, max_length=50)  # 最后一次登录IP
    is_active = models.BooleanField(default=True)  # 有效标志

    class Meta:
        db_table = 'm_user'  # 指定数据库表名

    def __str__(self):
        return 'user:' + self.userid


class Photo(models.Model):
    """照片"""
    uuid = models.CharField(primary_key=True, max_length=32)
    userid = models.CharField(max_length=50)  # 所属用户
    path_original = models.CharField(max_length=500)  # 原始照片文件存储路径
    path_modified = models.CharField(null=True, max_length=500)  # 修改后的原始照片存储路径
    path_thumbnail_s = models.CharField(null=True, max_length=500)  # 小缩略图存储路径
    path_thumbnail_l = models.CharField(null=True, max_length=500)  # 大缩略图存储路径
    name = models.CharField(max_length=200)  # 照片文件名
    md5 = models.CharField(max_length=32)  # 照片文件MD5值
    size = models.FloatField()  # 照片文件大小
    width = models.IntegerField()  # 照片宽度
    height = models.IntegerField()  # 照片高度
    exif_datetime = models.DateTimeField(null=True)  # 拍摄时间
    exif_make = models.CharField(null=True, max_length=500)  # 相机制造商
    exif_model = models.CharField(null=True, max_length=500)  # 相机型号
    exif_lensmodel = models.CharField(null=True, max_length=500)  # 镜头信息
    exif_fnumber = models.CharField(null=True, max_length=500)  # 光圈值
    exif_exposuretime = models.CharField(null=True, max_length=500)  # 曝光时间
    exif_isospeedratings = models.CharField(null=True, max_length=500)  # ISO感光度
    exif_focallength = models.CharField(null=True, max_length=500)  # 拍摄焦距，单位毫米
    exif_gpslatitude = models.CharField(null=True, max_length=500)  # GPS经度
    exif_gpslatituderef = models.CharField(null=True, max_length=100)  # 南北半球标志
    exif_gpslongitude = models.CharField(null=True, max_length=500)  # GPS纬度
    exif_gpslongituderef = models.CharField(null=True, max_length=100)  # 东西半球标志
    comments = models.CharField(null=True, max_length=500)  # 备注
    is_favorited = models.BooleanField(default=False)  # 收藏标志
    is_deleted = models.BooleanField(default=False)  # 删除标志
    input_date = models.DateTimeField(auto_now_add=True)  # 录入时间
    update_date = models.DateTimeField(auto_now=True)  # 修改时间

    class Meta:
        db_table = 'm_photo'  # 指定数据库表名

    def __str__(self):
        return 'photo:' + self.uuid


class Address(models.Model):
    """位置"""
    uuid = models.OneToOneField('Photo', on_delete=models.CASCADE, primary_key=True, db_column='uuid')
    lat = models.CharField(max_length=100)  # 纬度
    lng = models.CharField(max_length=100)  # 经度
    address = models.CharField(max_length=500)  # 结构化地址信息
    poi_name = models.CharField(null=True, max_length=500)  # poi名称
    country = models.CharField(null=True, max_length=500)  # 国家
    province = models.CharField(null=True, max_length=500)  # 省
    city = models.CharField(null=True, max_length=500)  # 城市
    district = models.CharField(null=True, max_length=500)  # 区县
    town = models.CharField(null=True, max_length=500)  # 乡镇

    class Meta:
        db_table = 'm_address'  # 指定数据库表名

    def __str__(self):
        return 'address:' + self.uuid


class Album(models.Model):
    """影集"""
    uuid = models.CharField(primary_key=True, max_length=32)
    userid = models.CharField(max_length=50)  # 所属用户
    name = models.CharField(max_length=200)  # 影集名称
    cover = models.ForeignKey('Photo', null=True, on_delete=models.CASCADE, db_column='cover')  # 封面
    cover_from = models.CharField(default='auto', max_length=10)  # 封面产生的方式:auto自动产生,user用户指定
    parent_uuid = models.CharField(null=True, max_length=32)  # 上级影集uuid
    input_date = models.DateTimeField(auto_now_add=True)  # 创建时间
    update_date = models.DateTimeField(auto_now=True)  # 修改时间

    class Meta:
        db_table = 'm_album'

    def __str__(self):
        return 'album:' + self.uuid


class AlbumPhoto(models.Model):
    """影集中的照片"""
    uuid = models.CharField(primary_key=True, max_length=32)
    album_uuid = models.ForeignKey('Album', on_delete=models.CASCADE, db_column='album_uuid')  # 影集uuid
    photo_uuid = models.ForeignKey('Photo', on_delete=models.CASCADE, db_column='photo_uuid')  # 照片uuid
    input_date = models.DateTimeField(auto_now_add=True)  # 添加时间

    class Meta:
        db_table = 'm_album_photo'

    def __str__(self):
        return 'album_photo:' + self.uuid
