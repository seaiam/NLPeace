from api.logger_config import configure_logger # TODO add logging statements
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.http import JsonResponse
from django.db.models import Q
from django.shortcuts import get_object_or_404
from itertools import chain
from django.http import *
import requests

from core.forms.user_forms import UserReportForm
from core.forms.profile_forms import *
from core.forms.posting_forms import *
from core.models.models import *
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash


def process_post_form(request, form):
    if form.is_valid():
        tweet_text = form.cleaned_data['content']
        result = classify_tweet(tweet_text)
        if result["prediction"][0] in [1, 0]:  # Offensive or hate speech
            message = 'This post contains offensive language and is not allowed on our platform.' if result["prediction"][0] == 1 else 'This post contains hateful language and is not allowed on our platform.'
            messages.error(request, message)
            return None
        elif result["prediction"][0] == 2:  # Appropriate
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return post
    return None

def classify_tweet(tweet_text):
    url = 'https://nlpeace-api-2e54e3d268ac.herokuapp.com/classify/'
    payload = {'text': tweet_text}
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
    
def get_user_posts(user):
    user_ids_following = user.profile.following.values_list('id', flat=True)
    blocked = user.profile.blocked.all()
    posts = Post.objects.filter(
        Q(user__profile__is_private=False) | 
        Q(user__in=user_ids_following) |  
        Q(user=user) |
        ~Q(user__in=blocked)
    ).distinct().order_by('-created_at')
    return posts

def create_repost(user, post_id):
    post_to_repost = get_object_or_404(Post, id=post_id)
    Repost.objects.create(post=post_to_repost, user=user)

def get_user_profile(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile

def get_user_posts_and_reposts(user):
    posts = Post.objects.filter(user=user)
    reposts_ids = Repost.objects.filter(user=user).values_list('post_id', flat=True)
    reposts = Post.objects.filter(id__in=reposts_ids)
    all_posts = sorted(chain(posts, reposts), key=lambda post: post.created_at, reverse=True)
    return all_posts

def get_image_posts(posts):
    return sorted([post for post in posts if post.image], key=lambda post: post.created_at, reverse=True)

def get_post_interactions(user, posts):
    likes = [post for post in posts if post.is_likeable_by(user)]
    dislikes = [post for post in posts if post.is_dislikeable_by(user)]
    saved_post_ids = [post.id for post in posts if not post.is_saveable_by(user)]
    return likes, dislikes, saved_post_ids

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
        result = classify_tweet(comment_text)

        if result["prediction"][0] in [1, 0]:  # Offensive or hate speech
            message = 'This comment contains offensive language and is not allowed on our platform.' if result["prediction"][0] == 1 else 'This comment contains hateful language and is not allowed on our platform.'
            messages.error(request, message)
            return None
        elif result["prediction"][0] == 2:  # Appropriate
            comment = form.save(commit=False)
            comment.user = request.user
            comment.parent_post = Post.objects.get(pk=post_id)
            comment.save()
            return comment
    return None

def handle_like(user, post_id):
    post = Post.objects.get(pk=post_id)
    dislike = PostDislike.objects.filter(disliker=user, post=post).first()
    if dislike:
        dislike.delete()
    PostLike.objects.create(liker=user, post=post)

def handle_dislike(user, post_id):
    post = get_object_or_404(Post, id=post_id)
    like = PostLike.objects.filter(liker=user, post=post).first()
    if like:
        like.delete()
    PostDislike.objects.create(disliker=user, post=post)

def report_post(user, post_id, form_data):
    report = PostReportForm(form_data).save(commit=False)
    report.reporter = user
    report.post = get_object_or_404(Post, pk=post_id)
    report.save()

def report_user(user, reported_id, form_data):
    report = UserReportForm(form_data).save(commit=False)
    report.reporter = user
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
    saved_posts = PostSave.objects.filter(saver=user).select_related('post').order_by('-post__created_at')
    return [save.post for save in saved_posts]

def block_user(request_user_id, blocked_user_id):
    updated_user = Profile.objects.get(pk=request_user_id)
    blocked_user = User.objects.get(pk=blocked_user_id)
    updated_user.blocked.add(blocked_user)
    updated_user.save()

def update_user_username(request_user_id, form_data):
    user = User.objects.get(pk=request_user_id)
    form = EditUsernameForm(form_data, instance=user)
    if form.is_valid():
        form.save()

def update_user_password(user, form_data):
    form = PasswordChangeForm(user, form_data)
    if form.is_valid():
        updated_user = form.save()
        update_session_auth_hash(user, updated_user)

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