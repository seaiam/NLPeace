"""
URL configuration for api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from core import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include("django.contrib.auth.urls")),
    path('accounts/login/', views.login_user, name="login"),
    path('logout_user', views.logout_user, name="logout_user"),
    path('register_user', views.register_user, name='register_user'),
    path('', views.home, name='home'),
    path('accounts/profile/', views.profile, name='profile'),
    path('accounts/profile/updateBio/', views.updateBio, name='edit_bio'),
    path('accounts/profile/updateBanner/', views.updateProfileBanner, name='edit_banner'),
    path('accounts/profile/updatePic/', views.updateProfilePicture, name='edit_pic'),
    path('500/', views.error_500, name='error_500'),
    path('accounts/profile/settings/', views.profile_settings, name='profile_settings'),
    path('accounts/profile/settings/updateUsername', views.update_username, name='update_username'),
    path('accounts/profile/settings/updatePassword', views.update_password, name='update_password'),
    path('forget_password/',views.ForgetPassword,name='forget_password'),
    path('change_password/<token>/',views.ChangePassword,name='change_password'),
    path('user/<int:user_id>/privacy/', views.privacy_settings_view, name='privacy_settings'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
