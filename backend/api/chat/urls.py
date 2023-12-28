# chat/urls.py
from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="messages"),
    path("<int:target_user_id>", views.room, name="room"),
    path("<str:room_name>/upload/", views.upload, name="upload"),
    path("<str:room_name>/download/<str:path>", views.download, name="download"),
]