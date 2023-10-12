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

urlpatterns = [
    path('admin/', admin.site.urls),
    path("auth/", include("django.contrib.auth.urls")),
    path("auth/custom-login/", views.logInToApp, name="custom-login"),
    path('register/', views.signUp, name='register'),
    path('accounts/profile/', views.profile, name='profile'),
    path('accounts/profile/update_user/bio/', views.update_user, {'section': 'bio'}, name='edit_bio'),
    path('accounts/profile/update_user/banner/', views.update_user, {'section': 'banner'}, name='edit_banner'),
    path('accounts/profile/update_user/pic/', views.update_user, {'section': 'pic'}, name='edit_pic'),

]