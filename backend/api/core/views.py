from api.logger_config import configure_logger
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from PIL import Image
from .forms import *

def home(request):
    return render(request, 'index.html')

def profile(request):
    return render(request, 'home.html')

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

import os

def updateProfileBanner(request):
    if request.method == 'POST':
        form = EditProfileBannerForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            pic = form.cleaned_data['banner']
            with Image.open(pic) as im:
                im.save(f'api/core/media/profileBanners/{request.user.username}.{pic.image.format}')
        return redirect('profile')
    else:
        form = EditProfileBannerForm()
    context = {
        'form': form
    }
    return render(request, 'newBanner.html', context)

def updateBio(request):
    if request.method == 'POST':
        form = EditBioForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
        return redirect('profile')
    else:
        form = EditBioForm()
    context = {
        'form': form
    }
    return render(request, 'newBio.html', context)

def updateProfilePicture(request):
    if request.method == 'POST':
        form = EditProfilePicForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            pic = form.cleaned_data['pic']
            with Image.open(pic) as im:
                im.save(f'api/core/media/profilePictures/{request.user.username}.{pic.image.format}')
            return redirect('profile')
    else:
        form = EditProfilePicForm()
    context = {
        'form': form
    }
    return render(request, 'newProfilepic.html', context)
