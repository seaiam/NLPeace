from django import forms
from core.models.models import Profile, User

class EditBioForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio']
        
class EditUsernameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']
        widgets = {'username': forms.TextInput(attrs={'class': 'form-username'})}

class EditProfilePicForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['pic']
        widgets = {'pic': forms.FileInput(attrs={'style': 'display:none'})}

class EditProfileBannerForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['banner']
        widgets = {'banner': forms.FileInput(attrs={'style': 'display:none'})}

class PrivacySettingsForm(forms.ModelForm):
    is_private = forms.ChoiceField(
        choices=((False, 'Public'), (True, 'Private')),
        widget=forms.Select(attrs={'class': 'form-privacy'}),
        initial=True
    )

    class Meta:
        model = Profile
        fields = ['is_private'] 
