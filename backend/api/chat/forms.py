from django import forms

from .models import FileUpload, ImageUpload

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = FileUpload
        fields = ['file']

class UploadImageForm(forms.ModelForm):
    class Meta:
        model = ImageUpload
        fields = ['image']
