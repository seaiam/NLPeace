from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from .models import User
from django.contrib import messages
from .forms import *
from .models import User
from api.logger_config import configure_logger
logger = configure_logger(__name__)



def profile(request):
    return render(request, 'home.html')

def signUp(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # user is saved to the database with info provided from the form
            form.save()
            return redirect('../auth/custom-login/')
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


def update_user(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST)
        if form.is_valid():
            user = User.objects.get(uuid=form.cleaned_data['uuid'])
            updated = False
            if user.is_bio_updated(form.cleaned_data['bio']):
                user.bio = form.cleaned_data['bio']
                updated = True
            if user.is_banner_updated(form.cleaned_data['banner']):
                user.banner = form.cleaned_data['banner']
                updated = True
            if user.is_pic_updated(form.cleaned_data['pic']):
                user.pic = form.cleaned_data['pic']
                updated = True
            if updated:
                user.save()
        # TODO redirect to profile
        return redirect('/')
