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
    banned_users = models.ManyToManyField(User, related_name='banned_users')
    allows_offensive = models.BooleanField(default=False)
    
class CommunityPost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)

class CommunityReport(models.Model):
    class Reason(models.IntegerChoices):
        HATE_SPEECH = 0, 'Hate'
        ABUSE_AND_HARASSMENT = 1, 'Abuse and harassment'

    reporter = models.ForeignKey(User, on_delete=models.DO_NOTHING,  related_name='reporting_user')
    reported = models.ForeignKey(Community, on_delete=models.CASCADE,  related_name='reported_community')
    reason = models.IntegerField(choices=Reason.choices)
    info = models.TextField(null=True, blank=True)
    date_reported = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.reporter.username} -- {CommunityReport.Reason(self.reason).name} -- {self.date_reported}' 
  
