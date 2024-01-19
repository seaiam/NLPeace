from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from core.utils import attempt_send_message

User=get_user_model()

class ChatRoom(models.Model):
    room_name = models.AutoField(primary_key=True, unique=True)
    user1 = models.ForeignKey(User,related_name='user1',on_delete=models.CASCADE)
    user2 = models.ForeignKey(User,related_name='user2',on_delete=models.CASCADE)


    @property
    def has_sent_message(self):
        return (Message.objects.filter(room_id=self, author=self.user1).exists() or 
               Message.objects.filter(room_id=self, author=self.user1).exists())
        
    
    
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
    
    def last_10_messages(room_name):
        return Message.objects.filter(room_id=room_name).order_by('timestamp').all()[:10]
    
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
    reporter = models.ForeignKey(User, on_delete=models.DO_NOTHING, default=None)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, default=None)
