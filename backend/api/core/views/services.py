from core.forms.profile_forms import *

def block_user(request_user_id, blocked_user_id):
    updated_user = Profile.objects.get(pk=request_user_id)
    blocked_user = User.objects.get(pk=blocked_user_id)
    blocked_user_profile = Profile.objects.get(user_id=blocked_user_id)
    updated_user.blocked.add(blocked_user)
    updated_user.following.remove(blocked_user)
    updated_user.followers.remove(blocked_user)
    updated_user.save()    
    blocked_user_profile.followers.remove(updated_user.user)
    blocked_user_profile.following.remove(updated_user.user)
    blocked_user_profile.save()