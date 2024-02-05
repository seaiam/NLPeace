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
from core.views import authentication_views, main_pages_views, profile_views, posting_views, community_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include("django.contrib.auth.urls")),
    path('accounts/login/', authentication_views.login_user, name="login"),
    path('logout_user', authentication_views.logout_user, name="logout_user"),
    path('register_user/', authentication_views.register_user, name='register_user'),
    path('', main_pages_views.home, name='home'),
    path('accounts/profile/', main_pages_views.profile, name='profile'),
    path('accounts/profile/<int:blocked_id>/', profile_views.add_block, name='add_block'),
    path('accounts/profile/updateBio/', profile_views.updateBio, name='edit_bio'),
    path('accounts/profile/updateBanner/', profile_views.updateProfileBanner, name='edit_banner'),
    path('accounts/profile/updatePic/', profile_views.updateProfilePicture, name='edit_pic'),
    path('500/', main_pages_views.error_500, name='error_500'),
    path('accounts/profile/settings/', profile_views.profile_settings, name='profile_settings'),
    path('accounts/profile/settings/updateUsername', profile_views.update_username, name='update_username'),
    path('accounts/profile/settings/updatePassword', profile_views.update_password, name='update_password'),
    path('forget_password/', authentication_views.ForgetPassword,name='forget_password'),
    path('change_password/<token>/',authentication_views.ChangePassword,name='change_password'),
    path('user/<int:user_id>/privacy/', profile_views.privacy_settings_view, name='privacy_settings'),
    path('user/<int:user_id>/messaging_settings/', profile_views.messaging_settings_view, name='messaging_settings'),
    path('comment/<int:post_id>', posting_views.comment, name='comment'),
    path('repost/<int:post_id>/', posting_views.repost, name='repost'),
    path('accounts/profile/search/',profile_views.search_user,name="search_user"),
    path('guest/<int:user_id>/', main_pages_views.guest ,name="guest"),
    path('like/<int:post_id>/', posting_views.like, name='like'),
    path('dislike/<int:post_id>/', posting_views.dislike, name='dislike'),
    path('report/<int:post_id>', posting_views.report, name='report'),
    path('follow/', profile_views.follow_user ,name="follow_user"),
    path('unfollow/', profile_views.unfollow_user ,name="unfollow_user"),
    path('accounts/profile/notifications', main_pages_views.notifications, name='notifications'), 
    path('accounts/profile/notifications/delete_notification', profile_views.delete_notification, name='delete_notification'), 
    path('accounts/profile/notifications/invite', main_pages_views.accept_decline_invite, name='accept_decline_invite'),   
    path('guest/<int:reported_id>/reportUser/', main_pages_views.report_user, name='report_user'),
    path('save_post/<int:post_id>/', posting_views.save_post, name='save_post'),
    path('bookmarks/', main_pages_views.bookmarked_posts, name='bookmarked_posts'),
    path('delete_post/', posting_views.delete_post, name='delete_post'),
    path('chat/', include("chat.urls")),
    path('pin/<int:post_id>/', posting_views.pin, name='pin'),
    path('unpin/<int:post_id>/', posting_views.unpin, name='unpin'),
    path('edit/<int:post_id>/', posting_views.edit_post, name='edit_post'),
    path('community/create/', community_views.create_community, name='create_community'),
    path('community/<int:community_id>/', community_views.community_detail, name='community_detail'),
    path('community/<int:community_id>/create_community_post/', community_views.create_community_post, name='create_community_post'),
    path('join/', community_views.join_community ,name="join_community"),
    path('leave/', community_views.leave_community ,name="leave_community"),
    path('accounts/profile/notifications/join', community_views.accept_decline_join, name='accept_decline_join'),   
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
