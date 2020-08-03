from django.urls import path
from .views import *

urlpatterns = [
    path('uploadfile', upload_file),
]
