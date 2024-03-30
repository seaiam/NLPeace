from django.http import *
from api.logger_config import configure_logger # TODO add logging statements
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm

from core.forms.profile_forms import *
from core.models.profile_models import Profile
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from .services import *
from faker import Faker

@login_required
def add_block(request, blocked_id):
    message = block_user(request.user.id, blocked_id)
    messages.info(request, message)
    return redirect('profile')

@login_required
def profile_settings(request):
    data = get_user_notifications(request.user)
    if request.method == 'GET':
      user = get_user_by_id(request.user.id)
      if not user:
        return HttpResponseNotFound()
     
      context = {
        'user': user,
        'data' : data, 
        'editUsernameForm': EditUsernameForm(instance=user),
        'editPasswordForm': PasswordChangeForm(request.user),
        'privacy_form':PrivacySettingsForm(instance=user.profile),
        'messaging_form':MessagingSettingsForm(instance=user.profile),
        'NLPToggle_form' : NLPToggleForm(instance=user.profile)
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
        update_user_password(request, request.POST)
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
def messaging_settings_view(request, user_id):
    user = User.objects.get(pk=user_id)
    profile_instance = user.profile

    if request.user != user:  
        return HttpResponseForbidden("You don't have permission to edit this user's settings.")

    if request.method == "POST":
        form = MessagingSettingsForm(request.POST, instance=profile_instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Messaging settings updated!")
            return redirect('profile')
    else:
        form = MessagingSettingsForm(instance=profile_instance)

    context = {
        'messaging_form': form
    }
    
    return render(request, 'settings.html', context)

@login_required
def search_user(request):
    if request.method == "POST":
        search = request.POST.get('search')
        searched = search_for_users(search) if search else None
        if searched:
            return render(request,'search_user.html',{'search':search,'searched':searched})

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
        #Needs refactoring
        followed_user=User.objects.get(pk=followed_user_id)
        following_user=User.objects.get(pk=following_user_id)
        
        # deny the follow if the user is blocked 
        if followed_user.profile.blocked.filter(id=following_user_id).exists():
            messages.error(request, "You cannot follow this user because they have blocked you.")
            return redirect('profile')
          
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
        unfollowed_user = User.objects.get(pk=unfollowed_user_id)

        handle_unfollow_request(unfollowed_user_id, unfollowing_user_id)
        messages.success(request, f"You have unfollowed {unfollowed_user.username}.")

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
def nlp_toggle(request):
    if request.method == "POST":
        if update_content_filtering_settings(request.user.id, request.POST):
            messages.success(request, "Content filtering settings updated!")
            return redirect('profile')
    else:
        form = NLPToggleForm(instance=request.user.profile)

    return render(request, 'settings.html', {'NLPToggle_form': form})

@login_required
def switch_to_main_profile(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
    
    profile.is_anonymous = False
    profile.save()

    request.session['active_profile_id'] = profile.pk
    return redirect('profile')

@login_required
def switch_to_anonymous_profile(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
    fake = Faker()
    # Generate a random name
    anonymous_username = fake.user_name()
    profile.anonymous_username = anonymous_username
    
    profile.is_anonymous = True
    profile.save()

    request.session['active_profile_id'] = profile.pk
    return redirect('profile')