from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from .forms import UploadForm
from .models import Message
import json
import mimetypes
import re

FILE_PATH_PATTERN = r'^.*/messageFiles/(?P<filename>.+)$'

def index(request):
    return render(request, "test.html")

# def room(request, room_name):
#     return render(request, "room.html", {"room_name": room_name})
@login_required
def room(request,room_name):
    return render(request, "room.html",{
        'room_name': room_name,
        'room_name_json':mark_safe(json.dumps(room_name)),
        'username':mark_safe(json.dumps(request.user.username)),
        'upload': UploadForm()

                                                                   })

@login_required
def upload(request, room_name):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = UploadForm(request.POST, request.FILES)
            if form.is_valid():
                upload = form.save()
                match = re.match(FILE_PATH_PATTERN, upload.file.path)
                Message.objects.create(author=request.user, content=match.group("filename"), is_file_download=True)
    return redirect(reverse("room", args=[room_name]))

@login_required
def download(request, room_name, path):
    if request.user.is_authenticated:
        with open(f'api/core/media/messageFiles/{path}', 'rb') as f:
            match = re.match(FILE_PATH_PATTERN, path)
            response = HttpResponse(f.read(), content_type=mimetypes.guess_type(path))
            response['Content-Disposition'] = f'attachment; filename={path}'
            return response
