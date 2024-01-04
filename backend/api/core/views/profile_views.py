from django.http import *
from api.logger_config import configure_logger # TODO add logging statements
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm

from core.forms.profile_forms import *
from core.models.models import *
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from .services import *

@login_required
def add_block(request, blocked_id):
    block_user(request.user.id, blocked_id)
    messages.error(request, "User Blocked Successfully.")
    return redirect('profile')


@login_required
def profile_settings(request):
    data = get_user_notifications(request.user)
    user = get_user_by_id(request.user.id)
    if not user:
        return HttpResponseNotFound()
    
    context = {
        'user': user,
        'data': data,
        'editUsernameForm': EditUsernameForm(instance=user),
        'editPasswordForm': PasswordChangeForm(request.user),
        'privacy_form': PrivacySettingsForm(instance=user.profile)
    }
    return render(request, 'settings.html', context)


@login_required
def update_username(request):
    if request.method == 'POST':
        update_user_username(request.user.id, request.POST)
        return redirect('profile')
    return HttpResponseServerError()


@login_required
def update_password(request):
    if request.method == 'POST':
        update_user_password(request.user, request.POST)
        return redirect('profile')
    return HttpResponseServerError()


@login_required
def updateProfileBanner(request):
    if request.method == 'POST':
        update_user_profile_banner(request.user.id, request.POST, request.FILES)
        return redirect('profile')
    return redirect('error_500')


@login_required
def updateBio(request):
    if request.method == 'POST':
        update_user_bio(request.user.id, request.POST)
        return redirect('profile')
    return redirect('error_500')


@login_required
def updateProfilePicture(request):
    if request.method == 'POST':
        update_user_profile_picture(request.user.id, request.POST, request.FILES)
        return redirect('profile')
    return redirect('error_500')

@login_required
def privacy_settings_view(request, user_id):
    if request.user.id != user_id:
        return HttpResponseForbidden("You don't have permission to edit this user's settings.")
    if request.method == "POST":
        if update_privacy_settings(user_id, request.POST):
            messages.success(request, "Privacy settings updated!")
            return redirect('profile')
    else:
        form = PrivacySettingsForm(instance=request.user.profile)

    return render(request, 'settings.html', {'privacy_form': form})


@login_required
def search_user(request):
    if request.method == "POST":
        search = request.POST.get('search')
        searched = search_for_users(search) if search else None
        search=request.session.get('search')

    search = request.session.get('search')
    if search:
        searched = search_for_users(search)
        return render(request,'search_user.html',{'search':search,'searched':searched})
    else:
        return redirect('profile')


@login_required
def follow_user(request):
    if request.method == 'POST':
        followed_user_id = request.POST.get('followed_user')
        following_user_id = request.POST.get('following_user')
        
        # Handle the follow request and get response details
        is_private, followed_username = handle_follow_request(followed_user_id, following_user_id)
        if is_private:
            messages.success(request, 'A follow request has been sent.')
        else:
            messages.success(request, f"You have started following {followed_username}.")

        # Preserve the search context if it exists
        search = request.POST.get('search')
        if search:
            request.session['search'] = search

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    return HttpResponseForbidden()
   
@login_required
def unfollow_user(request):
    if request.method == 'POST':
        unfollowed_user_id = request.POST.get('unfollowed_user')
        unfollowing_user_id = request.POST.get('unfollowing_user')
        
        handle_unfollow_request(unfollowed_user_id, unfollowing_user_id)
        messages.success(request, f"You have unfollowed the user.")

        search = request.POST.get('search')
        if search:
            request.session['search'] = search

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    return HttpResponseForbidden()

@login_required
def delete_notification(request):
    if request.method == "POST":
        clicked = request.POST.get('clicked')
        if clicked == "exit":
            notification_id = request.POST.get('notification')
            delete_user_notification(notification_id)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def delete_post(request):
    if request.method == "POST":
        post_id = request.POST.get('post_id')
        if delete_user_post(request.user.id, post_id):
            messages.success(request, "Post deleted successfully.")
        else:
            messages.error(request, "You may not delete this post.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


