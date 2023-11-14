from django.contrib.auth.models import User
from django.db import models
from django.conf import settings


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.RESTRICT, primary_key=True)
    following=models.ManyToManyField(User,related_name='following',blank=True)
    followers=models.ManyToManyField(User,related_name='followers',blank=True)
    follow_requests = models.ManyToManyField(User, related_name='follow_requests', blank=True)
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

class Repost(models.Model):
    post = models.ForeignKey(Post, null=True, on_delete=models.CASCADE, related_name='reposts')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} reposted {self.post.content}'


class PostReport(models.Model):
    class Category(models.IntegerChoices):
        HATE = 0, 'Hate'
        ABUSE_AND_HARASSMENT = 1, 'Abuse and harassment'
        VIOLENT_SPEECH = 2, 'Violent speech'

    reporter = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.IntegerField(choices=Category.choices)
    info = models.TextField(null=True, blank=True)
    date_reported = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.reporter.username} -- {PostReport.Category(self.category).name} -- {self.date_reported}'

class Notifications(models.Model):
    notifications=models.TextField()
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="user",null=True,blank=True)
    sent_by=models.ForeignKey(User,on_delete=models.CASCADE,related_name='sent_by',null=True,blank=True)
    type=models.CharField(null=True,blank=True)

    
    def __str__(self):
        return str(self.notifications)
