from django.contrib.auth.models import User
from django.db import models
from .post_models import Post

class Community(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(User, related_name='communities')
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='administered_communities')
    is_private = models.BooleanField(default=True)
    pic = models.ImageField(upload_to='communityPics/', null=True, blank=True)
    join_requests = models.ManyToManyField(User, related_name='join_requests', blank=True)
        
class CommunityPost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
  