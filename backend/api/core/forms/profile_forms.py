from django import forms
from core.models.profile_models import Profile, User

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

class MessagingSettingsForm(forms.ModelForm):
    messaging_is_private = forms.ChoiceField(
        choices=((False, 'Everyone'), (True, 'Followers')),
        widget=forms.Select(attrs={'class': 'form-privacy'}),
        initial=True
    )

    class Meta:
        model = Profile
        fields = ['messaging_is_private'] 

class NLPToggleForm(forms.ModelForm):
    allows_offensive= forms.ChoiceField(
        choices=((False, 'on'), (True, 'off')),
        widget=forms.Select(attrs={'class': 'form-privacy'}),
        initial=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''

    class Meta:
        model = Profile
        fields = ['allows_offensive', 'delete_offensive']
        labels = {'delete_offensive': 'Delete my offensive posts when I turn content moderation on'}
