# chat/urls.py
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views



urlpatterns = [
    path('search-giphy/', views.search_giphy, name='search_giphy'),
    path("", views.index, name="messages"),
    path("<int:target_user_id>", views.room, name="room"),
    path("<int:target_user_id>/upload_file", views.upload_file, name="upload_file"),
    path("<int:target_user_id>/upload_image", views.upload_image, name="upload_image"),
    path("download/<str:path>", views.download, name="download"),
    path("classifyMessage/", views.classifyMessage, name="classifyMessage"),
    path("<int:message_id>/report_message", views.report_message, name="report_message"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
