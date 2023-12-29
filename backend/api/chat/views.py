from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.safestring import mark_safe
from django.urls import reverse
from .chat_service import getChatRoom
from .forms import UploadForm
from .models import Message
import json
import mimetypes
import re

FILE_PATH_PATTERN = r'.*/(?P<filename>.+)$'

User = get_user_model()

@login_required
def index(request):
    users = User.objects.all()
    
    context = {
        'users' : users
    }
    return render(request, "messages.html", context)

@login_required
def room(request,target_user_id):
    target_user = User.objects.filter(id = target_user_id).first()
    chat_room = getChatRoom(request.user, target_user)
    
    context = {
        'room_name': chat_room.room_name,
        'room_name_json':mark_safe(json.dumps(chat_room.room_name)),
        'username':mark_safe(json.dumps(request.user.username)),
        'upload': UploadForm(),
        'target_user': target_user
    }
    return render(request, "room.html", context)

@login_required
def upload(request, target_user_id):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = UploadForm(request.POST, request.FILES)
            if form.is_valid():
                target_user = User.objects.filter(id=target_user_id).first()
                room = getChatRoom(request.user, target_user)
                upload = form.save(commit=False)
                match = re.match(FILE_PATH_PATTERN, upload.file.path)
                message = Message.objects.create(author=request.user, content=match.group("filename"), room_id=room, is_file_download=True)
                upload.message = message
                upload.save()
    return redirect(reverse("room", args=[target_user_id]))

@login_required
def download(request, path):
    if request.user.is_authenticated:
        with open(f'api/core/media/messageFiles/{path}', 'rb') as f:
            match = re.match(FILE_PATH_PATTERN, path)
            response = HttpResponse(f.read(), content_type=mimetypes.guess_type(path))
            response['Content-Disposition'] = f'attachment; filename={path}'
            return response
