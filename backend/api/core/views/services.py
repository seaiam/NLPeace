import requests

from api.logger_config import configure_logger # TODO add logging statements
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q
from django.http import *
from django.shortcuts import get_object_or_404
from itertools import chain, cycle
from core.forms.profile_forms import EditBioForm, EditUsernameForm, EditProfilePicForm, EditProfileBannerForm, PrivacySettingsForm
from core.interest_resolver import RESOLVERS
from core.models.post_models import Post, Repost, PostReport, PostLike, PostDislike, PostSave, PostPin, Advertisement
from core.models.profile_models import Profile, Notifications, User

class ContentCarrier:

    def __init__(self, payload):
        self.payload = payload
        self.is_post = isinstance(payload, Post)

def process_post_form(request, form):
    if form.is_valid():
        tweet_text = form.cleaned_data['content']
        result = classify_text(tweet_text)
        if result["prediction"][0] in [1, 0]:  # Offensive or hate speech
            message = 'This post contains offensive language and is not allowed on our platform.' if result["prediction"][0] == 1 else 'This post contains hateful language and is not allowed on our platform.'
            messages.error(request, message)
            return None
        elif result["prediction"][0] == 2:  # Appropriate
            update_interests(request.user, tweet_text)
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return post
    return None

def classify_text(text):
    url = 'https://nlpeace-api-2e54e3d268ac.herokuapp.com/classify/'
    payload = {'text': text}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            # Handle response error
            return {'error': 'Failed to get prediction', 'status_code': response.status_code}
    except requests.exceptions.RequestException as e:
        # Handle request exception
        return {'error': str(e)}

def update_interests(user, text):
    profile = get_user_profile(user)
    profile.remove_interests(settings.INTEREST_DAYS_THRESHOLD)
    profile.insert_interests(get_interests(text))

def get_interests(text):
    return get_hashtags(text) + get_sentiments(text)

def get_hashtags(text):
    return list(map(lambda hashtag: hashtag[1:] ,filter(lambda word: word.startswith('#'), text.split(' '))))

def get_sentiments(text):
    # TODO implement sentiment analysis for interest inference.
    return []
    
def get_user_posts(user):
    profile = get_user_profile(user)
    user_ids_following = profile.following.values_list('id', flat=True)
    blocked = profile.blocked.all()
    posts = Post.objects.filter(
        (Q(user__profile__is_private=False) | 
        Q(user__in=user_ids_following) |  
        Q(user=user)) &
        ~Q(user__in=blocked)
    ).distinct().order_by('-created_at')
    carriers = list(map(lambda post: ContentCarrier(post), posts))
    return mix(carriers, get_ads(user))

def get_ads(user):
    resolver = RESOLVERS[settings.AD_SELECTION_STRATEGY]
    profile = get_user_profile(user)
    ads = {ad: resolver.get_interest_in(profile, ad) for ad in get_all_ads()}
    to_include = list(filter(lambda item: item[1] > settings.TOPIC_INCLUSION_THRESHOLD, ads.items()))
    if len(to_include):
        return list(map(lambda item: item[0], sorted(to_include, key=lambda item: item[1])))
    return list(ads.keys())

def get_all_ads():
    ads = Advertisement.objects.all()
    if (len(ads) > 1):
        return list(filter(lambda ad: not ad.advertiser == 'NLPeace', ads))
    return list(ads)

def mix(posts, ads):
    iter = cycle(ads)
    rate = settings.AD_MIX_RATE
    return list(chain(*[posts[i: i + rate] + [ContentCarrier(next(iter))]
                       if len(posts[i: i + rate]) == rate
                       else posts[i: i + rate]
                       for i in range(0, len(posts), rate)]))

def create_repost(user, post_id):
    post_to_repost = get_object_or_404(Post, id=post_id)
    if Repost.objects.filter(post=post_to_repost, user=user).exists():
        Repost.objects.filter(post=post_to_repost, user=user).delete()
    else:
        Repost.objects.create(post=post_to_repost, user=user)

def get_user_profile(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile

def get_user_posts_and_reposts(user):
    posts = Post.objects.filter(Q(user=user) & Q(parent_post=None))
    reposts_ids = Repost.objects.filter(user=user).values_list('post_id', flat=True)
    reposts = Post.objects.filter(id__in=reposts_ids)
    replies = Post.objects.filter(Q(user=user) & ~Q(parent_post=None))
    all_posts = sorted(chain(posts, reposts, replies), key=lambda post: post.created_at, reverse=True)
    carriers = list(map(lambda post: ContentCarrier(post), all_posts))
    return mix(carriers, get_ads(user))

def get_image_posts(user, carriers):
    image_posts = sorted([post for post in get_posts_from(carriers) if post.image], key=lambda post: post.created_at, reverse=True)
    image_carriers = list(map(lambda post: ContentCarrier(post), image_posts))
    return mix(image_carriers, get_ads(user))

def get_post_interactions(user, carriers):
    posts = get_posts_from(carriers)
    likes = [post for post in posts if post.is_likeable_by(user)]
    dislikes = [post for post in posts if post.is_dislikeable_by(user)]
    saved_post_ids = [post.id for post in posts if not post.is_saveable_by(user)]
    return likes, dislikes, saved_post_ids

def get_posts_from(carriers):
    return list(map(lambda carrier: carrier.payload, filter(lambda carrier: carrier.is_post, carriers)))

def get_liked_posts(user):
    liked_posts = list(map(lambda post: ContentCarrier(post), Post.objects.filter(postlike__liker=user).distinct().order_by('-created_at')))
    return mix(liked_posts, get_ads(user))

def get_following_posts(user, following):
    following_posts = list(map(lambda post: ContentCarrier(post), Post.objects.filter(user__in=following).order_by('-created_at')))
    return mix(following_posts, get_ads(user))


def get_user_by_id(user_id):
    return User.objects.get(pk=user_id)

def get_user_notifications(user):
    return Notifications.objects.filter(user=user).order_by('-id')
    
def handle_invitation(followed_user_pk, following_user_pk, action):
    followed_user = User.objects.get(pk=followed_user_pk)
    following_user = User.objects.get(pk=following_user_pk)
    notification = Notifications.objects.get(user=followed_user_pk, sent_by=following_user_pk, type="request")
    if action == "accept":
        followed_user.profile.follow_requests.remove(following_user)
        followed_user.profile.followers.add(following_user)
        following_user.profile.following.add(followed_user)
        notification_message = f"{followed_user.username} accepted your follow request."
        Notifications.objects.create(notifications=notification_message, user=following_user, sent_by=followed_user, type="")
    else:
        followed_user.profile.follow_requests.remove(following_user)

    notification.delete()

def process_comment_form(request, form, post_id):
    if form.is_valid():
        comment_text = form.cleaned_data['content']
        result = classify_text(comment_text)

        if result["prediction"][0] in [1, 0]:  # Offensive or hate speech
            message = 'This comment contains offensive language and is not allowed on our platform.' if result["prediction"][0] == 1 else 'This comment contains hateful language and is not allowed on our platform.'
            messages.error(request, message)
            return None
        elif result["prediction"][0] == 2:  # Appropriate
            update_interests(request.user, comment_text)
            comment = form.save(commit=False)
            comment.user = request.user
            comment.parent_post = Post.objects.get(pk=post_id)
            comment.save()
            return comment
    return None

def handle_like(user, post_id):
    post = Post.objects.get(pk=post_id)

    #check if post is disliked
    dislike = PostDislike.objects.filter(disliker=user, post=post).first()
    if dislike:
        dislike.delete()
    
    #unlike if post is already liked
    liked = PostLike.objects.filter(liker=user, post=post).exists()
    if liked:
        PostLike.objects.filter(liker=user, post=post).delete()
    else:
        #like post
        like = PostLike.objects.create(liker=user, post=post)

def handle_dislike(user, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    #check if post is liked already
    like = PostLike.objects.filter(liker=user, post=post).first()
    if like:
        like.delete()

    #undislike if already disliked
    disliked = PostDislike.objects.filter(disliker=user, post=post).exists()
    if disliked:
        PostDislike.objects.filter(disliker=user, post=post).delete()
    else:
        #dislike post
        dislike = PostDislike.objects.create(disliker=user, post=post)

def report_post_service(request, post_id, form):
    post = get_object_or_404(Post, pk=post_id)
    if post.is_reported_by(request.user):
        PostReport.objects.filter(post=post, reporter=request.user).delete()
        messages.success(request, 'Post un-reported')
    else:
        report = form.save(commit=False)
        report.reporter = request.user
        report.post = post
        report.save()
        messages.success(request, 'Post successfully reported.')
    
def report_user_service(request, reported_id, form):
    report = form.save(commit=False)
    report.reporter = request.user
    report.reported = get_object_or_404(User, id=reported_id)
    report.save()

def save_or_unsave_post(user, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_save, created = PostSave.objects.get_or_create(saver=user, post=post)
    if created:
        message = 'Post saved successfully.'
    else:
        post_save.delete()
        message = 'Post unsaved.'
    return message

def get_bookmarked_posts(user):
    saves = PostSave.objects.filter(saver=user).select_related('post').order_by('-post__created_at')
    saved_posts = [ContentCarrier(save.post) for save in saves]
    return mix(list(saved_posts), get_ads(user))

def block_user(request_user_id, blocked_user_id):
    updated_user = Profile.objects.get(pk=request_user_id)
    blocked_user = User.objects.get(pk=blocked_user_id)
    blocked_user_profile = Profile.objects.get(user_id=blocked_user_id)
    # Handle unblocking
    if updated_user.blocked.filter(id=blocked_user_id).exists():
        updated_user.blocked.remove(blocked_user)
        updated_user.save()
        message = 'User Unblocked Successfully.'
    else: # Handle blocking 
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
        message = 'User Blocked Successfully.'
    return message

def update_user_username(request_user_id, form_data):
    user = User.objects.get(pk=request_user_id)
    form = EditUsernameForm(form_data, instance=user)
    if form.is_valid():
        form.save()

def update_user_password(request, form_data):
    form = PasswordChangeForm(request.user, form_data)
    if form.is_valid():
        updated_user = form.save()
        update_session_auth_hash(request, updated_user)

def update_user_profile_banner(request_user_id, form_data, files_data):
    profile = Profile.objects.get_or_create(pk=request_user_id)
    form = EditProfileBannerForm(form_data, files_data, instance=profile[0])
    if form.is_valid():
        form.save()

def update_user_bio(request_user_id, form_data):
    profile, _ = Profile.objects.get_or_create(pk=request_user_id)
    form = EditBioForm(form_data, instance=profile)
    if form.is_valid():
        form.save()

def update_user_profile_picture(request_user_id, form_data, files_data):
    profile, _ = Profile.objects.get_or_create(pk=request_user_id)
    form = EditProfilePicForm(form_data, files_data, instance=profile)
    if form.is_valid():
        form.save()

def update_privacy_settings(user_id, form_data):
    user = User.objects.get(pk=user_id)
    form = PrivacySettingsForm(form_data, instance=user.profile)
    if form.is_valid():
        form.save()
        return True
    return False

def search_for_users(search_query):
    return User.objects.filter(username__icontains=search_query).order_by('username')

def handle_follow_request(followed_user_id, following_user_id):
    followed_user = User.objects.get(pk=followed_user_id)
    following_user = User.objects.get(pk=following_user_id)
    
    is_private = followed_user.profile.is_private
    followed_username = followed_user.username

    if is_private:
        # Handle follow request for a private profile
        followed_user.profile.follow_requests.add(following_user)
        notification_message = f"{following_user.username} sent you a follow request."
    else:
        # Handle immediate following for a public profile
        followed_user.profile.followers.add(following_user)
        following_user.profile.following.add(followed_user)
        notification_message = f"{following_user.username} has started following you."

    Notifications.objects.create(
        notifications=notification_message, 
        user=followed_user, 
        sent_by=following_user, 
        type="request" if is_private else ""
    )

    return is_private, followed_username

def handle_unfollow_request(unfollowed_user_id, unfollowing_user_id):
    unfollowed_user = User.objects.get(pk=unfollowed_user_id)
    unfollowing_user = User.objects.get(pk=unfollowing_user_id)

    if unfollowed_user.profile.is_private:
        if unfollowed_user.profile.follow_requests.filter(id=unfollowing_user_id).exists():
            unfollowed_user.profile.follow_requests.remove(unfollowing_user)
            # Delete follow request notification if exists
            Notifications.objects.filter(user=unfollowed_user_id, sent_by=unfollowing_user_id, type="request").delete()
        else:
            unfollowed_user.profile.followers.remove(unfollowing_user)
            unfollowing_user.profile.following.remove(unfollowed_user)
    else:
        unfollowed_user.profile.followers.remove(unfollowing_user)
        unfollowing_user.profile.following.remove(unfollowed_user)

def delete_user_notification(notification_id):
    notification = Notifications.objects.get(pk=notification_id)
    notification.delete()

def delete_user_post(user_id, post_id):
    post = Post.objects.get(pk=post_id)
    if user_id == post.user.id:
        post.delete()
        return True
    return False

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

def handle_edit_post(request,form, post, remove_image, parent_post):
    if form.is_valid():
        edited_text = form.cleaned_data['content']
        result = classify_text(edited_text)
        if result["prediction"][0] in [1, 0]:  # Offensive or hate speech
            message = 'This edit contains offensive language and is not allowed on our platform.' if result["prediction"][0] == 1 else 'This post contains hateful language and is not allowed on our platform.'
            messages.error(request, message)
        elif result["prediction"][0] == 2:  # Appropriate
            if remove_image and post.image:
                post.image.delete(save=True)
                post.image = None
            post = form.save()
            post.is_edited = True
            post.parent_post = parent_post
            post.save()
    else:
        messages.error(request, "There was an error editing your post. Try again.")
    return post