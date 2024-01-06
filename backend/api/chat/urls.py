# chat/urls.py
from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="messages"),
    path("<int:target_user_id>", views.room, name="room"),
    path("<int:target_user_id>/upload_file", views.upload_file, name="upload_file"),
    path("<int:target_user_id>/upload_image", views.upload_image, name="upload_image"),
]