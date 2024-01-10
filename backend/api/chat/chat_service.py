from .models import ChatRoom
from django.contrib.auth import get_user_model
from django.db.models import Q

#We get the chat room that is mapped to the two users in question
def getChatRoom(current_user, target_user):

    chat_room = ChatRoom.objects.filter(
            Q(user1=current_user, user2=target_user) | 
            Q(user1=target_user, user2=current_user)
        ).first()
    if not chat_room:
        chat_room = ChatRoom.objects.create(
            user1=current_user,
            user2=target_user
        )

    return chat_room

def messages_to_json(messages):
    return [message_to_json(message) for message in messages]

def message_to_json(message):
    if message.is_image:
            upload = message.imageupload_set.first()
            src = upload.image.url
    elif message.is_video:
            upload = message.videoupload_set.first()
            src = upload.video.url

    else:
        src = ''
    return {
        'author': message.author.username,
        'content': message.content,
        'timestamp': str(message.timestamp),
        'is_file_download': message.is_file_download,
        'is_image': message.is_image,
        'is_video': message.is_video,
        'src': src
    }