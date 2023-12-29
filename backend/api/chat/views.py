import uuid
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.safestring import mark_safe
import json
from django.http import JsonResponse
from .models import Message
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import JsonResponse
import requests
from django.conf import settings


def index(request):
    return render(request, "test.html")

# def room(request, room_name):
#     return render(request, "room.html", {"room_name": room_name})
@login_required
def room(request,room_name):
    return render(request, "room.html",{
        'room_name_json':mark_safe(json.dumps(room_name)),
        'username':mark_safe(json.dumps(request.user.username))

                                                                   })
def save_gif_and_get_url(gif):
    # unique name for GIF
    file_name = f"gifs/{uuid.uuid4()}-{gif.name}"
    file_path = default_storage.save(file_name, ContentFile(gif.read()))

    gif_url = f"{settings.MEDIA_URL}{file_path}"
    return gif_url

def upload_gif(request):
    if request.method == 'POST' and request.FILES['gif']:
        gif = request.FILES['gif']
        gif_url = save_gif_and_get_url(gif)

        return JsonResponse({'gif_url': gif_url})
    return JsonResponse({'error': 'Invalid request'}, status=400)



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