from api.logger_config import configure_logger # TODO add logging statements
from django.contrib.auth import login, authenticate, logout

from core.forms.user_forms import UserRegistrationForm
import uuid 
from django.conf import settings
from django.core.mail import send_mail
from core.models.profile_models import Profile, User

def register_new_user(request, form_data):
    form = UserRegistrationForm(form_data)
    if form.is_valid():
        form.save()
        username = form.cleaned_data['username']
        password = form.cleaned_data['password1']
        user = authenticate(request, username=username, password=password)
        # Create a profile for the user
        profile = Profile.objects.create(user=user)
        profile.save()
        
        login(request, user)
        return True
    return False

def user_login(request, username, password):
    user = authenticate(request, username=username, password=password)
    profile = Profile.objects.filter(user=user).first()
    if user is not None and (profile is None or not profile.is_banned):
        login(request, user)
        return True
    return False

def user_logout(request):
    logout(request)

def change_password(token, new_password, confirm_password):
    profile = Profile.objects.filter(forget_password_token=token).first()
    if profile and new_password == confirm_password:
        user = User.objects.get(username=profile.user.username)
        user.set_password(new_password)
        user.save()
        return True
    return False

def send_password_reset_mail(email, token):
    subject = 'Password reset link'
    message = f"Click the link http://localhost:8000/change_password/{token}/ to reset your password."
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    return True

def handle_forget_password(email):
    user_obj = User.objects.filter(email=email).first()
    if user_obj:
        profile = Profile.objects.get(user=user_obj)
        token = str(uuid.uuid4())
        profile.forget_password_token = token
        profile.save()
        send_password_reset_mail(email, token)
        return True
    return False
