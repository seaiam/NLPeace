import json
import mimetypes
import re
import requests
from api.logger_config import configure_logger 
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.safestring import mark_safe
from .chat_service import getChatRoom, message_to_json
from .forms import *
from .models import Message
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .chat_service import *
from .models import Message, ReportMessage, getUserModel
from core.utils import attempt_send_message


FILE_PATH_PATTERN = r'.*/(?P<filename>.+)$'


User = getUserModel()

logger = configure_logger("chat_logger")

def index(request):
    users = User.objects.all()
    searched_term = request.GET.get('search','')
    chatroom = ChatRoom.objects.filter(Q(user1=request.user) | Q(user2=request.user) ).all()
    contacted_users = []
    
    handle_contacted_users(request.user,chatroom,contacted_users)

    contacted_searched_users = User.objects.filter(username__icontains=searched_term)

    # all the other users that haven't been contacted
    searched_users = User.objects.filter(username__icontains=searched_term).exclude(pk__in=[user.id for user in contacted_users])

    # Concatenate the two lists
    all_users = [user for user in contacted_users if user in contacted_searched_users] + list(searched_users)

    if searched_term and not contacted_searched_users.exists():
        messages.warning(request, f'No user found with the username: {searched_term}')
        return redirect('messages')
    
    context = {
        'users' : users,
        'searched_term': searched_term,
        'searched_users': searched_users,
        'chatroom' : chatroom,
        'all_users' : all_users,
        'contacted_users' : contacted_users
        
       
    }   
    return render(request, "messages.html", context)

@login_required
def room(request, target_user_id):
    target_user = User.objects.filter(id = target_user_id).first()
    chat_room = getChatRoom(request.user, target_user)
    handle_chatroom_initiation(request.user, chat_room)
  

    context = {
        'room_name_json':mark_safe(json.dumps(chat_room.room_name)),
        'username':mark_safe(json.dumps(request.user.username)),
        'target_user': target_user,
        'file_upload_form': FileUploadForm(),
        'image_upload_form': ImageUploadForm(),
        'video_upload_form': VideoUploadForm(),
        'dm_report_form': DMReportForm(),
    }
    return render(request, "room.html", context)

@login_required
def upload_file(request, target_user_id):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            room = getChatRoom(request.user, User.objects.filter(id=target_user_id).first())
            upload = form.save(commit=False)
            match = re.match(FILE_PATH_PATTERN, upload.file.path)
            message = Message.objects.create(author=request.user, content=match.group("filename"), room_id=room, is_file_download=True)
            upload.message = message
            upload.save()
            _send_message(room, message)
    return redirect(reverse('room', args=[target_user_id]))

@login_required
def upload_video(request, target_user_id):
    if request.method == "POST":
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            room = getChatRoom(request.user, User.objects.filter(id=target_user_id).first())
            upload = form.save(commit=False)
            message = Message.objects.create(author=request.user, content='', room_id=room, is_video=True)
            upload.message = message
            upload.save()
            _send_message(room, message)
    return redirect(reverse("room", args=[target_user_id]))

@login_required
def download(request, path):
    with open(f'{settings.MEDIA_ROOT}/messageFiles/{path}', 'rb') as f:
        response = HttpResponse(f.read(), content_type=mimetypes.guess_type(path))
        response['Content-Disposition'] = f'attachment; filename={path}'
        return response

@login_required
def upload_image(request, target_user_id):
    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            room = getChatRoom(request.user, User.objects.filter(id=target_user_id).first())
            upload = form.save(commit=False)
            message = Message.objects.create(author=request.user, content='', room_id=room, is_image=True)
            upload.message = message
            upload.save()
            _send_message(room, message)
    return redirect(reverse("room", args=[target_user_id]))

def _send_message(room, message):
    content = {
        'command': 'new_message',
        'message': message_to_json(message),
    }
    attempt_send_message(f'chat_{room.room_name}', {"type": "chat.message", "message": content})

@csrf_exempt
@require_POST
def classifyMessage(request):
    try:
        #ajax call is made when user clicks send
        data = json.loads(request.body)
        message = data.get('message')
        #process message by using nlp to see if message is allowed
        is_allowed, result = process_message(message)
        ##log message and any error statements
        #logger.info(f"message: {message}")
        #logger.info(f"is allowed: {is_allowed}")
        #logger.info(f"result: {result}")
        #return message or error message to user
        return JsonResponse({'is_allowed': is_allowed, 'error_message': result})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@login_required
def report_message(request, message_id):
    if request.method == "POST":
        reported = Message.objects.get(pk=message_id)
        if reported.is_reported_by(request.user):
            ReportMessage.objects.filter(reporter=request.user, message=reported).delete()
            messages.success(request, 'Report removed')
        else:
            ReportMessage.objects.create(reporter=request.user, message=reported)
            messages.success(request, 'Message reported')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    
    else:
        return redirect('login')
    
def search_giphy(request):
    if request.method == 'GET':
        query = request.GET.get('query', '')
        limit = request.GET.get('limit', 10)
        api_key = settings.GIPHY_API_KEY
        giphy_api_url = f"https://api.giphy.com/v1/gifs/search?api_key={api_key}&q={query}&limit={limit}"
        response = requests.get(giphy_api_url)
        if response.status_code == 200:
            return JsonResponse(response.json())
        else:
            return JsonResponse({'error': 'Failed to fetch GIFs'}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)
