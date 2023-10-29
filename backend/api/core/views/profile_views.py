from django.http import HttpResponseServerError
from django.http import HttpResponseNotFound
from django.http import HttpResponseForbidden
from api.logger_config import configure_logger # TODO add logging statements
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm

from core.forms.profile_forms import *
import uuid 
from django.conf import settings
from django.core.mail import send_mail
from core.models.models import *

@login_required
def profile_settings(request):
    if request.method == 'GET':
        user = User.objects.get(pk=request.user.id)
        if user is None:
            return HttpResponseNotFound
        return render(request, 'settings.html', {'user': user, 'editUsernameForm': EditUsernameForm(instance=user),'editPasswordForm': PasswordChangeForm(request.user)})
    
@login_required
def update_username(request):
    if request.method == 'POST':
        new_user = User.objects.get(pk=request.user.id)
        if new_user is None:
            return HttpResponseNotFound
        
        form = EditUsernameForm(request.POST, instance=new_user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    return HttpResponseServerError

@login_required
def update_password(request):
    if request.method == 'POST':
        new_user = User.objects.get(pk=request.user.id)
        if new_user is None:
            return HttpResponseNotFound
        
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user=form.save()
            update_session_auth_hash(request, user)
            return redirect('profile')
    return HttpResponseServerError

@login_required
def updateProfileBanner(request):
    if request.method == 'POST':
        profile = Profile.objects.get_or_create(pk=request.user.id)
        form = EditProfileBannerForm(request.POST, request.FILES, instance=profile[0])
        if form.is_valid():
            form.save()
        return redirect('profile')
    else:
        form = EditProfileBannerForm()
    context = {
        'form': form,
    }
    return render(request, 'newBanner.html', context)

@login_required
def updateBio(request):
    if request.method == 'POST':
        profile = Profile.objects.get_or_create(pk=request.user.id)
        form = EditBioForm(request.POST, instance=profile[0])
        if form.is_valid():
            form.save()
        return redirect('profile')
    # TODO render 500

@login_required
def updateProfilePicture(request):
    if request.method == 'POST':
        profile = Profile.objects.get_or_create(pk=request.user.id)
        form = EditProfilePicForm(request.POST, request.FILES, instance=profile[0])
        if form.is_valid():
            form.save()
        return redirect('profile')
    else:
        form = EditProfilePicForm()
    context = {
        'form': form
    }
    return render(request, 'newProfilepic.html', context)

@login_required
def privacy_settings_view(request, user_id):
    user = User.objects.get(pk=user_id)
    profile_instance = user.profile

    if request.user != user:  # Ensure users can only edit their own privacy settings
        return HttpResponseForbidden("You don't have permission to edit this user's settings.")

    if request.method == "POST":
        form = PrivacySettingsForm(request.POST, instance=profile_instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Privacy settings updated!")
            return redirect('privacy_settings', user_id=user_id)
    else:
        form = PrivacySettingsForm(instance=profile_instance)

    context = {
        'privacy_form': form
    }
    
    return render(request, 'privacy_settings.html', context)
