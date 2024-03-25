from django import forms
from core.models.post_models import Post, PostDislike, PostLike, PostReport

class PostForm(forms.ModelForm):
    content = forms.CharField(label='', widget=forms.Textarea(attrs={'class': 'widget-post__textarea scroller', 'style': 'background-color: #D9D9D9;', 'placeholder': 'Start a Post...'}))
    class Meta:
        model = Post
        fields = ['content', 'image','parent_post', 'video', 'signature']
        widgets = {'image': forms.FileInput(attrs={'style': 'display:none'}),
                   'video':forms.FileInput(attrs={'accept':'video/*'}), # 'style': 'display:none'}
                   'signature':forms.HiddenInput()
                   }

class PostReportForm(forms.ModelForm):
    class Meta:
        model = PostReport
        fields = ['category', 'info']
        
