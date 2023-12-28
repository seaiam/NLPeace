from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.utils.safestring import mark_safe
from .chatService import getChatRoom
import json
User = get_user_model()

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
    users = User.objects.all()
    context = {
        'room_name_json':mark_safe(json.dumps(chat_room.room_name)),
        'username':mark_safe(json.dumps(request.user.username)),
        'users' : users,
        'receiver' : target_user
    }
    return render(request, "room.html", context)