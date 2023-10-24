from api.logger_config import configure_logger # TODO add logging statements

from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import *
import uuid 
from django.conf import settings
from django.core.mail import send_mail
from .models import Profile

def home(request):
    # TODO we need to check authentication status here and redirect to registration page if not
    return render(request, 'index.html')

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

def send_forget_password_mail(email,token):
    subject='Password reset link'
    message = f"Click the link http://localhost:8000/change_password/{token}/ to reset your password."
    email_from = settings.EMAIL_HOST_USER
    recipient_list=[email]
    send_mail(subject,message,email_from,recipient_list)
    return True


def ChangePassword(request, token):
     
    try:
        profile=Profile.objects.filter(forget_password_token=token).first()
       
        if request.method == 'POST':
            new_password=request.POST.get('new_password')
            confirm_password=request.POST.get('confirm_password')
            

            if new_password!=confirm_password:
                messages.success(request,"The passwords don't match. Make sure they do.")
                return redirect(f'/change_password/{token}/')
            user=User.objects.get(username=profile.user.username)
            user.set_password(new_password)
            user.save()
            messages.success(request,"You have successfully reset your password.")
            return redirect(f'/change_password/{token}/')
        
    except Exception as e:
        print(e)
    return render(request,'change_password.html')


def ForgetPassword(request):
    try:
        if request.method=="POST":
            email=request.POST.get('email')
            if not User.objects.filter(email=email).first():
                messages.success(request,'No user found with this email.')
                return redirect('forget_password')
            user_obj=User.objects.get(email=email)
            profile=Profile.objects.get(user=user_obj)
            token=str(uuid.uuid4())
            profile.forget_password_token=token
            profile.save()
            send_forget_password_mail(email,token)
            messages.success(request,"An email has been sent.")
            return redirect('forget_password')
    except Exception as e:
     print(e)
    return render(request,'forget_password.html')