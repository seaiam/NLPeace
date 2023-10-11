from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect

from .forms import *
from .models import User


def signUp(request):
    if request.method == 'POST':
        form = UserRegistrationForm()
        if form.is_valid():
            # user is saved to the database with info provided from the form
            form.save()
            return redirect('login.html')
    else:
        # empty form 
        form = UserRegistrationForm()
    context = {
        'form': form
    }
    return render(request, 'register.html', context)


def login(request):
    if request.method == 'POST':
        form = LogInForm()
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            if username is "":
                user = authenticate(request, email=email, password=password)
            else:
                user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f'logged in')
                return redirect('home.html')

        # form is not valid or user is not authenticated
        messages.error(request, f'Invalid username/email or password')
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
