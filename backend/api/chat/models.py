from django.contrib.auth import get_user_model
from django.db import models

User=get_user_model()

class ChatRoom(models.Model):
    room_name = models.AutoField(primary_key=True, unique=True)
    user1 = models.ForeignKey(User,related_name='user1',on_delete=models.CASCADE)
    user2 = models.ForeignKey(User,related_name='user2',on_delete=models.CASCADE)

class Message(models.Model):
    author =models.ForeignKey(User,related_name='author_messages',on_delete=models.CASCADE)
    content=models.TextField()
    timestamp=models.DateTimeField(auto_now_add=True)
    room_id = models.ForeignKey(ChatRoom,related_name='room_id',on_delete=models.CASCADE)
    is_file_download = models.BooleanField(default=False)
    is_image = models.BooleanField(default=False)
    
    def __str__(self):
        return self.author.username
    
    def last_10_messages(room_name):
        return Message.objects.filter(room_id=room_name).order_by('timestamp').all()[:10]

class FileUpload(models.Model):
    file = models.FileField(upload_to='messageFiles')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, default=None)

class ImageUpload(models.Model):
    image = models.ImageField(upload_to='messageImages')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, default=None)