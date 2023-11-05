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
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpResponseRedirect



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

@login_required
def search_user(request):
    
    if request.method=="POST":
        #Grab the value of search from the form
        search=request.POST.get('search')
        # if the ther is searching then grab the searched user
        if search:
         searched=User.objects.filter(username__icontains=search).order_by('username')
        #Display search results if searched exists
         if searched:
        
          return render(request,'search_user.html',{'search':search,'searched':searched})
         else:
             messages.success(request, f"No results found for '{search}'.")

    search=request.session.get('search')
    if search is not None :
         searched=User.objects.filter(username__icontains=search).order_by('username')
         return render(request,'search_user.html',{'search':search,'searched':searched})
    #else: 
       # return redirect('profile')
   # messages.success(request, f"{search} and {searched}.")
    return redirect('profile')



@login_required
def follow_user(request):
    if request.method == 'POST':
        followed_user_id = request.POST.get('followed_user')
        following_user_id = request.POST.get('following_user')
        followed_user=User.objects.get(pk=followed_user_id)
        following_user=User.objects.get(pk=following_user_id)
        search=request.POST.get('search')
        request.session['search'] = search
        

        if followed_user.profile.is_private:
            followed_user.profile.follow_requests.add(following_user)
            messages.success(request,'A follow request has been sent.')
            followed_user.save()    
        else:
            followed_user.profile.followers.add(following_user)
            following_user.profile.following.add(followed_user)
            followed_user.save()
            following_user.save()
            messages.success(request,f"You have started following {followed_user}.")
   
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
   
    

    

@login_required
def unfollow_user(request):
    if request.method == 'POST':
        unfollowed_user_id = request.POST.get('unfollowed_user')
        unfollowing_user_id = request.POST.get('unfollowing_user')
        unfollowed_user=User.objects.get(pk=unfollowed_user_id)
        unfollowing_user=User.objects.get(pk=unfollowing_user_id)
        search=request.POST.get('search')
        request.session['search'] = search
        if unfollowed_user.profile.is_private:
            unfollowed_user.profile.follow_requests.remove(unfollowing_user)
            unfollowed_user.save()
        else:
            unfollowed_user.profile.followers.remove(unfollowing_user)
            unfollowing_user.profile.following.remove(unfollowed_user)
            unfollowed_user.save()
            unfollowing_user.save()
        
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
   







