from django.contrib.auth import models
from django.db import models as fields

class User(models.User):
    bio = fields.TextField(null=True, blank=True)
    banner = fields.ImageField(upload_to='profileBanners/', null=True, blank=True)
    pic = fields.ImageField(upload_to='profilePictures/', null=True, blank=True)
    forget_password_token=fields.CharField(max_length=100,default='')

