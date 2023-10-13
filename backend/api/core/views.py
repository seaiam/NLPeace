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
            return redirect('../auth/login/')
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
            print("valid form")
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                messages.success(request, f'logged in')
                stored_messages = messages.get_messages(request)
                for msg in stored_messages:
                    logger.info(msg)
                return redirect('../home')

        # form is not valid or user is not authenticated
        messages.error(request, f'Invalid email or password')
        return render(request, 'login.html')
    else:
        # empty form 
        form = LogInForm()
    context = {
        'form': form
    }
    return render(request, 'login.html', context)

def logout(request):
    logout(request)
    messages.success(request, f'logged out')
    return redirect('login.html')


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
    
def settings(request):
    return render(request, 'settings.html')
