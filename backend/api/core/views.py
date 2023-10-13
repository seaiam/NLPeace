from api.logger_config import configure_logger
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from .forms import *

logger = configure_logger(__name__)


def profile(request):
    return render(request, 'home.html')

def signUp(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # user is saved to the database with info provided from the form
            form.save()
            return redirect('../auth/login')
    else:
        # empty form 
        form = UserRegistrationForm()
    context = {
        'form': form
    }
    return render(request, 'register.html', context)


def logInToApp(request):
    if request.method == 'POST':
        logger.info("logging user into app...")
        form = LogInForm(request.POST)
        if form.is_valid():
            logger.info("validating form...")
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            logger.info("Authenticated user: ", user)
            if user:
                login(request, user)
                messages.success(request, f'logged in')
                logger.info("logged in user: ", user)
                return redirect('../home')
        else:
            logger.error(form.errors)
        # form is not valid or user is not authenticated
        messages.error(request, f'Invalid email or password')
        return render(request, 'registration/login.html')
    else:
        # empty form 
        form = LogInForm()
    context = {
        'form': form
    }
    return render(request, 'registration/login.html', context)

def logout(request):
    logout(request)
    messages.success(request, f'logged out')
    return redirect('login')

def updateProfileBanner(request):
    if request.method == 'POST':
        form = EditProfileBannerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        return redirect('profile')
    else:
        form = EditProfileBannerForm()
    context = {
        'form': form
    }
    return render(request, 'newBanner.html', context)

def updateBio(request):
    if request.method == 'POST':
        form = EditBioForm(request.POST)
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
        form = EditProfilePicForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = EditProfilePicForm()
    context = {
        'form': form
    }
    return render(request, 'newProfilepic.html', context)