from django.contrib.auth import get_user_model
from django.db import models

User=get_user_model()
# Create your models here.
class Message(models.Model):
    author =models.ForeignKey(User,related_name='author_messages',on_delete=models.CASCADE)
    content=models.TextField()
    gif_url = models.URLField(null=True, blank=True)  
    #gif = models.ImageField(upload_to='message_gifs/', null=True, blank=True)  
    timestamp=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.author.username
    
    def last_10_messages():
        return Message.objects.order_by('timestamp').all()[:100]