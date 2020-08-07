from django.urls import path
from backend_api.views.upload_file import *
from backend_api.views.browse import *

urlpatterns = [
    path('upload_file', upload_file),
    path('photo_list', photo_list)
]
