from django import forms
from .models import FileUpload, ImageUpload, VideoUpload

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = FileUpload
        fields = ['file']
        
class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = VideoUpload
        fields = ['video']

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = ImageUpload
        fields = ['image']
