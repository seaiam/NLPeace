from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.RESTRICT, primary_key=True)
    following=models.ManyToManyField(User,related_name='following',blank=True)
    followers=models.ManyToManyField(User,related_name='followers',blank=True)
    blocked=models.ManyToManyField(User,related_name='blocked',blank=True)
    follow_requests = models.ManyToManyField(User, related_name='follow_requests', blank=True)
    bio = models.TextField(null=True, blank=True)
    banner = models.ImageField(upload_to='profileBanners/', null=True, blank=True)
    pic = models.ImageField(upload_to='profilePictures/', null=True, blank=True)
    forget_password_token=models.CharField(max_length=100,default='')
    is_private = models.BooleanField(default=True)
    is_banned = models.BooleanField(default=False)
    messaging_is_private = models.BooleanField(default=True)

class ProfileWarning(models.Model):
    offender = models.ForeignKey(User, related_name='offender', on_delete=models.CASCADE)
    issuer = models.OneToOneField(User, on_delete=models.DO_NOTHING)
    issued_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.issued_at)


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=280)
    image = models.ImageField(upload_to='postImages/', null=True, blank=True)
    video= models.FileField(upload_to='postVideos/', null=True, blank=True)
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

    def get_number_saves(self):
        return self.postsave_set.all().count()

    def is_saveable_by(self, user):
        return user not in {save.saver for save in self.postsave_set.all()}
    
    def is_pinned_by(self, user):
        return self.postpin_set.filter(pinner=user).exists()
    
   
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
    #post = models.ForeignKey(Post, on_delete=models.Case)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)  

    class Meta:
        constraints = [models.UniqueConstraint(fields=['liker', 'post'], name='liker_post_unique')]

class PostDislike(models.Model):
    disliker = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['disliker', 'post'], name='disliker_post_unique')]

class Notifications(models.Model):
    notifications=models.TextField()
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="user",null=True,blank=True)
    sent_by=models.ForeignKey(User,on_delete=models.CASCADE,related_name='sent_by',null=True,blank=True)
    type=models.CharField(null=True,blank=True)

    
    def __str__(self):
        return str(self.notifications)

class UserReport(models.Model):
    class Reason(models.IntegerChoices):
        HATE_SPEECH = 0, 'Hate'
        ABUSE_AND_HARASSMENT = 1, 'Abuse and harassment'
        IMPOSTER = 2, 'User is pretending to be someone else'

    reporter = models.ForeignKey(User, on_delete=models.DO_NOTHING,  related_name='reporter')
    reported = models.ForeignKey(User, on_delete=models.CASCADE,  related_name='reported')
    reason = models.IntegerField(choices=Reason.choices)
    info = models.TextField(null=True, blank=True)
    date_reported = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.reporter.username} -- {UserReport.Reason(self.reason).name} -- {self.date_reported}'
    

class PostSave(models.Model):
    saver = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['saver', 'post'], name='saver_post_unique')
        ]

    def __str__(self):
        return f'{self.saver.username} saved {self.post.content}'

class PostPin(models.Model):
    pinner = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['pinner', 'post'], name='pinner_post_unique')
        ]

   
