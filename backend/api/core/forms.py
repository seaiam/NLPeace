from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .models import User

class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(label='Username',widget=forms.TextInput(attrs={'placeholder' :'Username'}), min_length=4, max_length=50)

    email = forms.EmailField(label='Email',widget=forms.EmailInput(attrs={'placeholder' :'Email'}))

    password1 = forms.CharField(label='Choose a password', widget=forms.PasswordInput(attrs={'placeholder' :'Password'}))
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput(attrs={'placeholder' :'Confirm Password'}))
  
    def username_clean(self):  
        username = self.cleaned_data['username'].lower()  
        new = User.objects.filter(username = username)  
        if new.count():  
            raise ValidationError("User Already Exist")  
        return username  
  
    def email_clean(self):  
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
            self.cleaned_data['password1'] ,
        )  
        return user  

class LogInForm(AuthenticationForm):
    # username = forms.EmailField(label='Email')
    username = forms.EmailField(label='Email',widget=forms.EmailInput(attrs={'placeholder' :'Email'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'placeholder' :'Password'}))


#class EditProfileForm(forms.Form):
    #uuid = forms.UUIDField(widget=forms.HiddenInput())
    #bio = forms.CharField(label='Bio', widget=forms.Textarea(attrs={'class': 'form-control'}))
    #banner = forms.ImageField(widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    #pic = forms.ImageField(widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

# class EditProfileForm(forms.Form):
#     uuid = forms.HiddenInput()
#     bio = forms.CharField(label='Bio', widget=forms.Textarea)
#     banner = forms.FileField()
#     pic = forms.FileField()

class EditBioForm(forms.Form):
    bio = forms.CharField(label='Bio', widget=forms.Textarea)

class EditProfilePicForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['pic']

class EditProfileBannerForm(forms.Form):
    banner = forms.ImageField()