from django.contrib.auth.models import User
from django.db import models
from django.conf import settings


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

    def get_number_likes(self):
        return self.postlike_set.all().count()
    
    def get_number_dislikes(self):
        return self.postdislike_set.all().count()
    
    def is_likeable_by(self, user):
        return user not in {like.liker for like in self.postlike_set.all()}
    
    def is_dislikeable_by(self, user):
        return user not in {dislike.disliker for dislike in self.postdislike_set.all()}

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

class PostLike(models.Model):
    liker = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.Case)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['liker', 'post'], name='liker_post_unique')]

class PostDislike(models.Model):
    disliker = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['disliker', 'post'], name='disliker_post_unique')]
