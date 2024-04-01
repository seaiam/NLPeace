from django import forms
from core.models.post_models import Post, PostDislike, PostLike, PostReport

class PostForm(forms.ModelForm):
    content = forms.CharField(label='', widget=forms.Textarea(attrs={'class': 'widget-post__textarea scroller', 'style': 'background-color: #D9D9D9;', 'placeholder': 'Start a Post...'}))
    poll_choices = forms.IntegerField(label='Number of Choices', min_value=0, initial=0, max_value=6)

    class Meta:
        model = Post
        fields = ['content', 'image','parent_post', 'video','poll_choices', 'signature', 'web3verify']
        widgets = {'image': forms.FileInput(attrs={'style': 'display:none'}),
                   'video':forms.FileInput(attrs={'accept':'video/*'}), # 'style': 'display:none'}
                   'signature':forms.HiddenInput(),
                   'web3verify':forms.HiddenInput()
                   }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['poll_choices'].required = False
        poll_choices = self.initial.get('poll_choices', 6)
        if (poll_choices > 0):
            for i in range(poll_choices):
                if (i <= 6): #limiting polls to 6 options 
                    self.fields[f'choice_{i+1}'] = forms.CharField(label=f'Choice {i+1}', max_length=30, required=False)

class PostReportForm(forms.ModelForm):
    class Meta:
        model = PostReport
        fields = ['category', 'info']
        
