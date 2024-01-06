import json
import re

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.safestring import mark_safe
from .chat_service import getChatRoom, message_to_json
from .forms import *
from .models import Message

FILE_PATH_PATTERN = r'.*/(?P<filename>.+)$'


User = get_user_model()

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
            _send_file_message(room, message)
    return redirect(reverse('room', args=[target_user_id]))

def _send_file_message(room, message):
    content = {
        'command': 'new_message',
        'message': message_to_json(message),
    }
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(f'chat_{room.room_name}', {"type": "chat.message", "message": content})

@login_required
def upload_image(request, target_user_id):
    return redirect(reverse('room', args=[target_user_id]))
