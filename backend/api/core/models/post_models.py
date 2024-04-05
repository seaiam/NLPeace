import re

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from core.utils import attempt_send_message

whitespace_pattern = re.compile(r'(\S+)')

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=280)
    image = models.ImageField(upload_to='postImages/', null=True, blank=True)
    video= models.FileField(upload_to='postVideos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    parent_post = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    is_edited = models.BooleanField(default = False)
    is_offensive = models.BooleanField(default=False)
    signature = models.CharField(max_length=400, null=True, blank=True)
    web3verify = models.BooleanField(default = False)

    def get_number_likes(self):
        return self.postlike_set.all().count()
    
    # ADDED FOR POST UNREPORT 
    def is_reportable_by(self, user):
        return user not in {report.reporter for report in self.postreport_set.all()}
    
    def get_number_reports(self):
        return self.postreport_set.all().count()
    
    def get_number_dislikes(self):
        return self.postdislike_set.all().count()
    
    def get_number_comments(self):
        return Post.objects.filter(parent_post=self).count()
    
    def get_number_reposts(self):
        return self.reposts.all().count()
    
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
    
    def save(self, *args, **kwargs):
        super(Post, self).save(*args, **kwargs)
        if self.parent_post is not None:
            attempt_send_message(
                f'notifications_{self.parent_post.user.id}',
                {
                    'type': 'notification',
                    'message': {
                        'type': 'comment',
                        'author': self.user.get_username(),
                        'timestamp': str(self.created_at),
                        'url': reverse('home'),
                }
            })
    
    def is_reported_by(self, user):
        return PostReport.objects.filter(reporter=user, post=self).exists()
    
    def is_community_post(self):
        from .community_models import CommunityPost #had to import here to avoid circular import issue
        return CommunityPost.objects.filter(post=self).exists()
    def is_tagged_by(self, hashtag):
        return HashtagInstance.objects.filter(post=self, hashtag=hashtag).exists()
    
    def get_words(self):
        return whitespace_pattern.split(self.content)

   
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
    category = models.IntegerField(choices=Category.choices, default = Category.VIOLENT_SPEECH) # todo use user input instead of default value for category
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

class Hashtag(models.Model):
    content = models.CharField(max_length=280, unique=True)

class HashtagInstance(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    hashtag = models.ForeignKey(Hashtag, null=True, on_delete=models.SET_NULL)
    
class Advertisement(models.Model):
    advertiser = models.CharField(max_length=512)
    logo = models.ImageField(upload_to='adLogos/', null=True, blank=True)
    content = models.CharField(max_length=280)

    def __str__(self):
        return f'{self.advertiser}: {self.content}'

class AdvertisementTopic(models.Model):
    ad = models.ForeignKey(Advertisement, on_delete=models.CASCADE)
    name = models.CharField(max_length=1024)

class Poll(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='poll')
    question = models.CharField(max_length=255)
    total_votes = models.IntegerField(default=0)

class PollChoice(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='choices', null=True)
    choice_text = models.CharField(blank=True, max_length=50, null=False)
    choice_votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text
   
class Vote(models.Model):
    choice = models.ForeignKey(PollChoice, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Vote by {self.user} for {self.choice.choice_text} in Poll {self.choice.post_id}"