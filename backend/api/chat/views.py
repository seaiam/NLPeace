from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.urls import reverse
from .chat_service import getChatRoom
from .forms import UploadForm
from .models import Message
import json
import mimetypes
import re

FILE_PATH_PATTERN = r'^.*/messageFiles/(?P<filename>.+)$'

User = get_user_model()

def index(request):
    users = User.objects.all()
    
    context = {
        'users' : users
    }
    return render(request, "messages.html", context)
            
def room(request,target_user_id):
    target_user = User.objects.filter(id = target_user_id).first()
    chat_room = getChatRoom(request.user, target_user)
    
    context = {
        'room_name_json':mark_safe(json.dumps(chat_room.room_name)),
        'username':mark_safe(json.dumps(request.user.username))
    }
    return render(request, "room.html", context)

def upload(request, room_name):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = UploadForm(request.POST, request.FILES)
            if form.is_valid():
                upload = form.save()
                match = re.match(FILE_PATH_PATTERN, upload.file.path)
                Message.objects.create(author=request.user, content=match.group("filename"), is_file_download=True)
    return redirect(reverse("room", args=[room_name]))

def download(request, room_name, path):
    if request.user.is_authenticated:
        with open(f'api/core/media/messageFiles/{path}', 'rb') as f:
            match = re.match(FILE_PATH_PATTERN, path)
            response = HttpResponse(f.read(), content_type=mimetypes.guess_type(path))
            response['Content-Disposition'] = f'attachment; filename={path}'
            return response
