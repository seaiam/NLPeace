import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.safestring import mark_safe
from .chat_service import getChatRoom
from .forms import *

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
   
    context = {
        'room_name': chat_room.room_name,
        'room_name_json':mark_safe(json.dumps(chat_room.room_name)),
        'username':mark_safe(json.dumps(request.user.username)),
        'target_user': target_user,
        'file_upload_form': FileUploadForm(),
        'image_upload_form': ImageUploadForm(),
    }
    return render(request, "room.html", context)

@login_required
def upload_file(request, target_user_id):
    return redirect(reverse("room", args=[target_user_id]))

@login_required
def upload_image(request, target_user_id):
    return redirect(reverse("room", args=[target_user_id]))
