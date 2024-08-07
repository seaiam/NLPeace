from api.logger_config import configure_logger # TODO add logging statements
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import requests
from core.forms.user_forms import UserRegistrationForm

#import BLL auth_services
from .auth_services import *

def register_user(request):
    if request.method == 'POST':
        if register_new_user(request, request.POST):
            messages.success(request, "Registration Successful!")
            return redirect('profile')  # Redirect to 'profile' on successful registration
        else:
            form = UserRegistrationForm(request.POST)
            messages.error(request, "Registration Error!")
    else:
        form = UserRegistrationForm()

    context = {'form': form}
    return render(request, 'registration/register.html', context)

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        try:
            requests.post('http://telemetry:8080/submit/data2', json={
                "user_id": 0,
                "request_body": "REDACTED",
                "url": "login",
            })
        except Exception as e:
            print(e)

        user = authenticate(request, username=username, password=password)
        if user is not None:
            profile = Profile.objects.filter(user=user).first()
            
            if profile is not None and not profile.is_banned:
                if profile.is_2fa_enabled:
                    code = generate_2fa_code()
                    request.session['2fa_code'] = str(code)
                    request.session['user_id'] = user.id
                    send_mail(
                        'Your 2FA Code',
                        f'Your code is: {code}',
                        settings.EMAIL_HOST_USER,
                        [user.email],
                        fail_silently=False,
                    )
                    try:
                        requests.post('http://telemetry:8080/submit/data3', json={
                            "user_id": user.id,
                            "status_code": 302  
                        })
                    except Exception as e:
                        print(e)
                    return redirect('verify_2fa')
                else:
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')

                    try:
                        requests.post('http://telemetry:8080/submit/data3', json={
                            "user_id": user.id,
                            "status_code": 302  
                        })
                    except Exception as e:
                        print(e)

                    return redirect('profile')
            else:
                messages.error(request, 'There was an error logging in. Try again...')
                return redirect('login')
        else:
            messages.error(request, 'Invalid login credentials!')
            #return redirect('login')
        try:
            requests.post('http://telemetry:8080/submit/data3', json={
                "user_id": 0,  
                "status_code": 401 
            })
        except Exception as e:
            print(e)
        return redirect('login')
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
        handle_forget_password(email)
        messages.success(request, "An email will be sent if a user with this email exists.")
        return redirect('/accounts/login/')
    return render(request, 'forget_password.html')
  
def verify_2fa(request):
    if request.method == "POST":
        user_code = request.POST.get('code', '')
        stored_code = request.session.get('2fa_code', '')
        user_id = request.session.get('user_id', None)

        if user_code == stored_code and user_id is not None:
            del request.session['2fa_code']
            del request.session['user_id']
            user = User.objects.get(id=user_id)
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            return redirect('profile')
        else:
            messages.error(request, 'Invalid 2FA code.')
            return redirect('verify_2fa')
    
    return render(request, 'verify_2fa.html')
