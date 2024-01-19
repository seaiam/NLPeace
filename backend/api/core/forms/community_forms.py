from django import forms
from core.models.models import Community

class CommunityForm(forms.ModelForm):
    is_private = forms.ChoiceField(
        choices=((False, 'Public'), (True, 'Private')),
        widget=forms.Select(attrs={'class': 'form-privacy'}),
        initial=True,
        label="Privacy"
    )

    class Meta:
        model = Community
        fields = ['name', 'is_private']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(CommunityForm, self).__init__(*args, **kwargs)
        if 'pic' in self.fields:
            self.fields['pic'].required = False
        if 'description' in self.fields:
            self.fields['description'].required = False