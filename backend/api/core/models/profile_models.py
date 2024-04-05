from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from core.models.community_models import Community

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
    allows_offensive = models.BooleanField(default=False)
    delete_offensive = models.BooleanField(default=False)
    is_2fa_enabled = models.BooleanField(default=False)
    is_anonymous = models.BooleanField(default=False)
    anonymous_username = models.CharField(max_length=150, blank=True, null=True)

    def insert_interests(self, interests):
        for name in map(lambda n: n.lower(), interests):
            interest = self.profileinterest_set.filter(name=name)
            if interest.exists():
                # Update the last_expressed field on an already existing interest.
                interest.first().save()
            else:
                # Otherwise record the new interest.
                self.profileinterest_set.add(ProfileInterest.objects.create(profile=self, name=name))

    def remove_interests(self, threshold):
        now = timezone.now()
        to_delete = []
        for interest in self.profileinterest_set.all():
            difference = now - interest.last_expressed
            if difference.days > threshold:
                to_delete.append(interest)
        for interest in to_delete:
            interest.delete()

    def get_display_name(self):
        return self.anonymous_username if self.anonymous_username else self.user.username

class ProfileInterest(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    name = models.CharField(max_length=1024)
    last_expressed = models.DateTimeField()

    def save(self, *args, **kwargs):
        self.last_expressed = timezone.now()
        super(ProfileInterest, self).save(*args, **kwargs)

class ProfileWarning(models.Model):
    offender = models.ForeignKey(User, related_name='offender', on_delete=models.CASCADE)
    issuer = models.OneToOneField(User, on_delete=models.DO_NOTHING)
    issued_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.issued_at)

class Notifications(models.Model):
    notifications=models.TextField()
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="user",null=True,blank=True)
    sent_by=models.ForeignKey(User,on_delete=models.CASCADE,related_name='sent_by',null=True,blank=True)
    type=models.CharField(null=True,blank=True)

    
    def __str__(self):
        return str(self.notifications)

class CommunityNotifications(models.Model):
    notifications = models.TextField()
    receiver = models.ForeignKey(User,on_delete=models.CASCADE,related_name="receiver",null=True,blank=True)
    sent_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='requester',null=True,blank=True)
    community =  models.ForeignKey(Community,on_delete=models.CASCADE,related_name='community')
    type = models.CharField(null=True,blank=True)

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