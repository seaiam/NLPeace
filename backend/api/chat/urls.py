# chat/urls.py
from django.urls import path

from django.conf import settings
from django.conf.urls.static import static
from . import views
# from django.conf import settings
# from django.conf.urls.static import static


urlpatterns = [
    path("", views.index, name="index"),
    path("<str:room_name>/", views.room, name="room"),
    path('search-giphy/', views.search_giphy, name='search_giphy'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
