from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.RESTRICT, primary_key=True)
    bio = models.TextField(null=True, blank=True)
    banner = models.ImageField(upload_to='profileBanners/', null=True, blank=True)
    pic = models.ImageField(upload_to='profilePictures/', null=True, blank=True)
    forget_password_token=models.CharField(max_length=100,default='')

    is_private = models.BooleanField(default=True)

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=280)
    image = models.ImageField(upload_to='postImages/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    parent_post = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    def __str__(self):
        return self.content
