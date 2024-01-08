import json
import mimetypes
import re
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
from redis.exceptions import ConnectionError
from .chat_service import getChatRoom, message_to_json
from .forms import *
from .models import Message
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .chat_service import *

FILE_PATH_PATTERN = r'.*/(?P<filename>.+)$'


User = get_user_model()

logger = configure_logger("chat_logger")

def index(request):
    users = User.objects.all()
    searched_term = request.GET.get('search','')
    searched_users = User.objects.filter(username__icontains=searched_term)
    if searched_term and not searched_users.exists():
        messages.warning(request, f'No user found with the username: {searched_term}')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    context = {
        'users' : users,
        'searched_term': searched_term,
        'searched_users': searched_users
    }   
    return render(request, "messages.html", context)

@login_required
def room(request,target_user_id):
    target_user = User.objects.filter(id = target_user_id).first()
    chat_room = getChatRoom(request.user, target_user)
    print(chat_room.room_name)
    context = {
        'room_name_json':mark_safe(json.dumps(chat_room.room_name)),
        'username':mark_safe(json.dumps(request.user.username)),
        'target_user': target_user,
        'file_upload_form': FileUploadForm(),
        'image_upload_form': ImageUploadForm(),
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
def download(request, path):
    with open(f'{settings.MEDIA_ROOT}/messageFiles/{path}', 'rb') as f:
        match = re.match(FILE_PATH_PATTERN, path)
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
    channel_layer = get_channel_layer()
    try:
        async_to_sync(channel_layer.group_send)(f'chat_{room.room_name}', {"type": "chat.message", "message": content})
    except ConnectionError:
        pass

@csrf_exempt
@require_POST
def classifyMessage(request):
    try:
        data = json.loads(request.body)
        message = data.get('message')
        is_allowed, result = process_message(message)
        logger.info(f"message: {message}")
        logger.info(f"is allowed: {is_allowed}")
        logger.info(f"result: {result}")
        return JsonResponse({'is_allowed': is_allowed, 'error_message': result})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)