from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.utils.timezone import make_aware
from django.db import models
from django.urls import reverse

from core.utils import attempt_send_message

User = get_user_model()

class ChatRoom(models.Model):
    room_name = models.AutoField(primary_key=True, unique=True)
    user1 = models.ForeignKey(User,related_name='user1',on_delete=models.CASCADE)
    user2 = models.ForeignKey(User,related_name='user2',on_delete=models.CASCADE)
    initiated_by_user1 = models.BooleanField(default=False)
    initiated_by_user2 = models.BooleanField(default=False)


    @property
    def has_sent_message(self):
        return (Message.objects.filter(room_id=self, author=self.user1).exists() or 
               Message.objects.filter(room_id=self, author=self.user2).exists())
    
    def sent_first_message(self):
        has_messages=Message.objects.filter(room_id=self).exists()
        if has_messages:
            first_message = Message.objects.filter(room_id=self).order_by('timestamp').first()
            return first_message.author
        else:
            return None
    
    
 
class Message(models.Model):
    author =models.ForeignKey(User,related_name='author_messages',on_delete=models.CASCADE)
    content=models.TextField()
    timestamp=models.DateTimeField(auto_now_add=True)
    room_id = models.ForeignKey(ChatRoom,related_name='room_id',on_delete=models.CASCADE)
    is_file_download = models.BooleanField(default=False)
    is_image = models.BooleanField(default=False)
    is_video =models.BooleanField(default=False)
    gif_url = models.URLField(null=True, blank=True)  
    
    def __str__(self):
        return self.author.username
    
    def change_message_to_deleted(passed_room_id):
        print(passed_room_id)
        message=Message.objects.get(pk=passed_room_id)
        message.content='DELETED'
        message.is_image=False
        message.save()
    
    def more_messages(room_name, m):
        messages=Message.objects.filter(room_id=room_name,timestamp__lt=m).order_by('timestamp').all().reverse()[:10]
        return messages
            


    def last_10_messages(room_name):
        length=len(Message.objects.filter(room_id=room_name).order_by('timestamp').all())
        left=0
        right=0
        if length<10:
            left=0
            right=length
        elif length>=10:
            left=length-10
            right=length
        messages=Message.objects.filter(room_id=room_name).order_by('timestamp').all()[left:right]
        return messages
    
    def save(self, *args, **kwargs):
        super(Message, self).save(*args, **kwargs)
        attempt_send_message(
            f'notifications_{self._get_target_id()}',
            {
                'type': 'notification',
                'message': {
                    'type': 'message',
                    'author': self.author.get_username(),
                    'timestamp': str(self.timestamp),
                    'url': reverse("room", args=[self.author.id])
            },
        })
    
    def _get_target_id(self):
        if self.room_id.user1 == self.author:
            return self.room_id.user2.id
        else:
            return self.room_id.user1.id
        
    def is_reported_by(self, user):
        return ReportMessage.objects.filter(reporter=user, message=self).exists()


class FileUpload(models.Model):
    file = models.FileField(upload_to='messageFiles')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, default=None)
    
class VideoUpload(models.Model):
    video = models.FileField(upload_to='messageVideos')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, default=None)

class ImageUpload(models.Model):
    image = models.ImageField(upload_to='messageImages')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, default=None)

class ReportMessage(models.Model):
    class Category(models.IntegerChoices):
        HATE = 0, "Hate"
        ABUSE_AND_HARASSMENT = 1, 'Abuse and harassment'
        VIOLENT_SPEECH = 2, 'Violent speech'
    reporter = models.ForeignKey(User, on_delete=models.DO_NOTHING, default=None)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, default=None)
    category = models.IntegerField(choices=Category.choices, default=0)