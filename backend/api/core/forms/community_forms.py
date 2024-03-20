from django import forms
from core.models.community_models import Community,CommunityReport

class CommunityForm(forms.ModelForm):
    is_private = forms.ChoiceField(
        choices=((False, 'Public'), (True, 'Private')),
        widget=forms.Select(attrs={'class': 'form-community'}),
        initial=True,
        label="Community Visibility"
    )
    allows_offensive =  forms.ChoiceField(
        choices=((False, 'On'), (True, 'Off')),
        widget=forms.Select(attrs={'class': 'form-community'}),
        initial=False,
        label="Content monitoring"
    )
    class Meta:
        model = Community
        fields = ['name', 'is_private','allows_offensive', 'pic', 'description'] 
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-name'}),
        }

    def __init__(self, *args, **kwargs):
        super(CommunityForm, self).__init__(*args, **kwargs)
        self.fields['pic'].required = False
        self.fields['description'].required = False

class CommunityReportForm(forms.ModelForm):
    class Meta:
        model = CommunityReport
        fields = ['reason', 'info']
