from celery import Celery
from celery.schedules import crontab
from django.conf import settings
import os

# 获取当前文件夹名，即为该Django的项目名
project_name = os.path.split(os.path.abspath('.'))[-1]
project_settings = '%s.settings' % project_name

# 设置环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', project_settings)

# 实例化Celery,网上很多教程这里都是没有设置broker造成启动失败
app = Celery('tasks', broker='redis://127.0.0.1:6379/0')

# 使用django的settings文件配置celery
app.config_from_object('django.conf:settings')

# 下面的设置就是关于调度器beat的设置
app.conf.beat_schedule = {
    'auto_get_photo_tag': {  # 定时获取图像标签
        'task': 'backend_api.views.thing.thing_get_tags',  # 设置是要将哪个任务进行定时
        'schedule': crontab(hour=0, minute=0),  # 调用crontab进行具体时间的定义
    },
}

# Celery加载所有注册的应用
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
