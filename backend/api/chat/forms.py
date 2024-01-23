from django import forms
from .models import FileUpload, ImageUpload, VideoUpload, ReportMessage

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


class DMReportForm(forms.ModelForm):
    class Meta:
        model = ReportMessage
        fields = ['category']