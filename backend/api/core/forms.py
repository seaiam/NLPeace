from django import forms
from django.contrib.auth.forms import UserCreationForm  
from django.contrib.auth.forms import AuthenticationForm

class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(label='First name', min_length=2, max_length=50)
    last_name = forms.CharField(label='Last name', min_length=2, max_length=50)
    username = forms.CharField(label='Username', min_length=4, max_length=50)
    
    email = forms.EmailField(label = 'email')

    password1 = forms.CharField(label='Choose a password', widget=forms.PasswordInput)  
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)  

class LogInForm(AuthenticationForm):
    email = forms.EmailField(label = 'Log in with email ')
    username = forms.CharField(label='Log in with username', min_length=4, max_length=50)
    password = forms.CharField(label='Enter your password', widget=forms.PasswordInput)  
  
