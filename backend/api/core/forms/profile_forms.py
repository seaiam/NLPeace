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
