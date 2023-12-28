# chat/urls.py
from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("<str:room_name>/", views.room, name="room"),
    path("<str:room_name>/upload/", views.upload, name="upload"),
    path("<str:room_name>/download/<str:path>", views.download, name="download"),
]