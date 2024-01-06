from core.forms.profile_forms import *
from core.models.models import *


def block_user(request_user_id, blocked_user_id):
    updated_user = Profile.objects.get(pk=request_user_id)
    blocked_user = User.objects.get(pk=blocked_user_id)
    blocked_user_profile = Profile.objects.get(user_id=blocked_user_id)
    updated_user.blocked.add(blocked_user)
    if updated_user.following.filter(id=blocked_user_id).exists():    
        updated_user.following.remove(blocked_user)
    if updated_user.followers.filter(id=blocked_user_id).exists():    
        updated_user.followers.remove(blocked_user)    
    updated_user.save()    
    if blocked_user_profile.following.filter(id=request_user_id).exists(): 
        blocked_user_profile.following.remove(updated_user.user)
    if blocked_user_profile.followers.filter(id=request_user_id).exists():     
        blocked_user_profile.followers.remove(updated_user.user)
    blocked_user_profile.save()


def handle_unpin(user, post_id):
    post = Post.objects.get(pk=post_id)
    postpin= PostPin.objects.filter(pinner=user, post=post)
    if postpin.exists():
         postpin.delete()
         message='Post unpinned.'
         return message

def handle_pin(user, post_id):
    post = Post.objects.get(pk=post_id)
    if PostPin.objects.filter(pinner=user).count() >= 3:
        message='You can only pin up to three posts.'
        return message
    else:
        PostPin.objects.create(pinner=user, post=post)
        message='Post pinned successfully.'
        return message