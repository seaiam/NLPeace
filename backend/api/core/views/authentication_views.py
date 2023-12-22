from api.logger_config import configure_logger # TODO add logging statements
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm

from core.forms.user_forms import UserRegistrationForm
import uuid 
from django.conf import settings
from django.core.mail import send_mail
from core.models.models import Profile, User

#import BLL auth_services
from .auth_services import *

@login_required
def register_user(request):
    if request.method == 'POST':
        if register_new_user(request, request.POST):
            messages.success(request, "Registration Successful!")
            return redirect('profile')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        if user_login(request, username, password):
            return redirect('profile')
        else:
            messages.error(request, 'There was an error logging in. Try again...')
    return render(request, 'registration/login.html')

def logout_user(request):
    user_logout(request)
    return redirect('login')

def ChangePassword(request, token):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if change_password(token, new_password, confirm_password):
            messages.success(request, "You have successfully reset your password.")
            return redirect('/accounts/login/')
        else:
            messages.error(request, "The passwords are not matching. Make sure they do.")
    return render(request, 'change_password.html')

def ForgetPassword(request):
    if request.method == "POST":
        email = request.POST.get('email')
        if handle_forget_password(email):
            messages.success(request, "An email will be sent if a user with this email exists.")
            return redirect('/accounts/login/')
    return render(request, 'forget_password.html')
