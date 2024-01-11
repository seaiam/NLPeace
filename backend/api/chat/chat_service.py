from .models import ChatRoom, ReportMessage
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.urls import reverse

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

def messages_to_json(messages, user):
    return [message_to_json(message, user) for message in messages]

def message_to_json(message, user=None):
    if message.is_image:
            upload = message.imageupload_set.first()
            src = upload.image.url
    else:
        src = ''
    if user and ReportMessage.objects.filter(reporter=user).exists():
        can_report = False
        report_link = ''
    else:
        can_report = True
        report_link = reverse('report_message', args=[message.id])
    return {
        'author': message.author.username,
        'content': message.content,
        'timestamp': str(message.timestamp),
        'is_file_download': message.is_file_download,
        'is_image': message.is_image,
        'src': src,
        'can_report': can_report,
        'report_link': report_link,
    }