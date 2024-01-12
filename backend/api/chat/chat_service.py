from .models import ChatRoom, ReportMessage
from .models import ChatRoom, ReportMessage
from django.contrib.auth import get_user_model
from django.db.models import Q
import requests
from django.urls import reverse
import requests
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
def messages_to_json(messages, user):
    return [message_to_json(message, user) for message in messages]

def message_to_json(message, user=None):
    if message.is_image:
            upload = message.imageupload_set.first()
            src = upload.image.url
    elif message.is_video:
            upload = message.videoupload_set.first()
            src = upload.video.url

    elif message.is_video:
            upload = message.videoupload_set.first()
            src = upload.video.url

    else:
        src = ''
    if user is None:
         user = get_target_user(message)
         print(user)
    if user and ReportMessage.objects.filter(reporter=user, message=message).exists():
        can_report = False
    else:
        can_report = True
    report_link = reverse('report_message', args=[message.id])
    return {
        'author': message.author.username,
        'content': message.content,
        'timestamp': str(message.timestamp),
        'is_file_download': message.is_file_download,
        'is_image': message.is_image,
        'is_video': message.is_video,
        'src': src,
        'gif_url': message.gif_url, 
        'can_report': can_report,
        'report_link': report_link,
    }

def classify_message(message_text):
    url = 'https://nlpeace-api-2e54e3d268ac.herokuapp.com/classify/'
    payload = {'text': message_text}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            # Handle response error
            return {'error': 'Failed to get prediction', 'status_code': response.status_code}
    except requests.exceptions.RequestException as e:
        # Handle request exception
        return {'error': str(e)}
    
def process_message(message):
    result = classify_message(message)
    if result["prediction"][0] in [1, 0]:  # Offensive or hate speech
        error_message = 'This message contains offensive language and is not allowed on our platform.' if result["prediction"][0] == 1 else 'This message contains hateful language and is not allowed on our platform.'
        return False, error_message
    elif result["prediction"][0] == 2:  # Appropriate
        return True, message
    return False

def get_target_user(message):
     if message.author == message.room_id.user1:
          return message.room_id.user2
     else:
          return message.room_id.user1
