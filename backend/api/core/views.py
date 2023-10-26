from django.http import HttpResponseForbidden
from django.http import HttpResponseServerError
from django.http import HttpResponseNotFound
from api.logger_config import configure_logger # TODO add logging statements

from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import *
from .models import Profile

def home(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = PostForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                post.user = request.user
                post.save()
                return redirect('home')
            
        #User is authenticated
        posts = Post.objects.all().order_by('-created_at')
        form = PostForm()
        return render(request, 'index.html', {'posts': posts, 'form': form})
    else:
        #redirect user to login page
        return redirect('login')

@login_required
def profile(request):
    profile = Profile.objects.get_or_create(pk=request.user.id)
    return render(request, 'home.html', {'profile': profile[0], 'form': EditBioForm(instance=profile[0])})

def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # user is saved to the database with info provided from the form
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(request, username=username, password=password)
            login(request, user)
            messages.success(request, ("Registration Successful!"))
            return redirect('profile')
    else:
        # empty form
        form = UserRegistrationForm()
    context = {
        'form': form
    }
    return render(request, 'registration/register.html', context)


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile')
        else:
            messages.success(request, ("There was an error logging in. Try again..."))
            return redirect('login')
    else:
        return render(request, 'registration/login.html', {})

def logout_user(request):
    logout(request)
    # messages.success(request, f'logged out')
    return redirect('login')

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
def update_username_password(request):
    if request.method == 'POST':
        new_user = User.objects.get_or_create(pk=request.user.id)
        if new_user[1] is False:
            return HttpResponseNotFound
        
        form = EditUsernamePasswordForm(request.POST, instance=new_user[0])
        if form.is_valid():
            form.save()
            return redirect('profile')
    return HttpResponseServerError

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

