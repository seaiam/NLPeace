from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django import forms
from .models import Profile, User

class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(label='Username',widget=forms.TextInput(attrs={'class': 'form-login'}), min_length=4, max_length=50)

    email = forms.EmailField(label='Email',widget=forms.EmailInput(attrs={'class': 'form-login'}))

    password1 = forms.CharField(label='Choose a password', widget=forms.PasswordInput(attrs={'class': 'form-login'}))
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput(attrs={'class': 'form-login'}))
  
    def clean_username(self):  
        username = self.cleaned_data['username'] 
        new = User.objects.filter(username = username)  
        if new.count():  
            raise ValidationError("User Already Exist")  
        return username  
  
    def clean_email(self):  
        email = self.cleaned_data['email'].lower()  
        new = User.objects.filter(email=email)  
        if new.count():  
            raise ValidationError(" Email Already Exist")  
        return email  
  
    def clean_password2(self):  
        password1 = self.cleaned_data['password1']  
        password2 = self.cleaned_data['password2']  
  
        if password1 and password2 and password1 != password2:  
            raise ValidationError("Password don't match")  
        return password2 

    def save(self, commit = True):  
        user = User.objects.create_user(  
            self.cleaned_data['username'],  
            self.cleaned_data['email'],  
            self.cleaned_data['password1'],
        )  
        return user

class EditBioForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio']

class EditProfilePicForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['pic']

class EditProfileBannerForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['banner']

class PrivacySettingsForm(forms.ModelForm):
    is_private = forms.ChoiceField(
        choices=((False, 'Public'), (True, 'Private')),
        widget=forms.Select,
        initial=True
    )

    class Meta:
        model = Profile
        fields = ['is_private']
