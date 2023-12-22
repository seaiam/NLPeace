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
from django.http import HttpResponseRedirect

from .services import *

def home(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        post = process_post_form(request, form)
        if post:
            return redirect('home')

    posts = get_user_posts(request.user)
    likes = [post for post in posts if post.is_likeable_by(request.user)]
    dislikes = [post for post in posts if post.is_dislikeable_by(request.user)]
    saved_post_ids = [post.id for post in posts if not post.is_saveable_by(request.user)]
    reposted_post_ids = Repost.objects.filter(user=request.user).values_list('post_id', flat=True)
    data = Notifications.objects.filter(user=request.user).order_by('-id')
    following_users = request.user.profile.following.all()
    following_posts = Post.objects.filter(user__in=following_users).order_by('-created_at')

    context = {
        'posts': posts,
        'likes': likes,
        'dislikes': dislikes,
        'saved_post_ids': saved_post_ids,
        'form': PostForm(),
        'data': data,
        'reportPostForm': PostReportForm(),
        'reposted_post_ids': reposted_post_ids,
        'followPost': following_posts
    }
    return render(request, 'index.html', context)


def repost(request, post_id):
    create_repost(request.user, post_id)
    return redirect('home')

@login_required
def profile(request):
    profile = get_user_profile(request.user)
    all_posts = get_user_posts_and_reposts(request.user)
    image_posts = get_image_posts(all_posts)
    likes, dislikes, saved_post_ids = get_post_interactions(request.user, all_posts)
    followers = profile.followers.all()
    following = profile.following.all()
    liked_posts = Post.objects.filter(postlike__liker=request.user).distinct().order_by('-created_at')
    data = Notifications.objects.filter(user=request.user).order_by('-id')

    context = {
        'profile': profile,
        'posts': all_posts,
        'media_posts': image_posts,
        'likes': likes,
        'dislikes': dislikes,
        'saved_post_ids': saved_post_ids,
        'liked_posts': liked_posts,
        'data': data,
        'editBannerForm': EditProfileBannerForm(instance=profile),
        'editPicForm': EditProfilePicForm(instance=profile),
        'editBioForm': EditBioForm(instance=profile),
        'reportPostForm': PostReportForm(),
        'reportUserForm': UserReportForm(),
        'followers': followers,
        'following': following,
    }
    return render(request, 'home.html', context)

@login_required
def guest(request, user_id):
    guest_user = get_user_by_id(user_id)
    profile = get_user_profile(guest_user)
    data = Notifications.objects.filter(user=request.user).order_by('-id')
    all_posts = get_user_posts_and_reposts(guest_user)
    image_posts = get_image_posts(all_posts)
    likes, dislikes, _ = get_post_interactions(guest_user, all_posts)
    followers = profile.followers.all()
    following = profile.following.all()

    context = {
        'user': guest_user,
        'data': data,
        'profile': profile,
        'form': EditBioForm(instance=profile),
        'posts': all_posts,
        'media_posts': image_posts,
        'likes': likes,
        'dislikes': dislikes,
        'reportUserForm': UserReportForm(),
        'followers': followers,
        'following': following,
    }
    return render(request, 'home.html', context)

@login_required
def notifications(request):
    data = get_user_notifications(request.user)
    return render(request, 'notifications.html', {'data': data})


@login_required
def accept_decline_invite(request):
    data = get_user_notifications(request.user)
  
    if request.method == 'POST':
        followed_user_pk = request.POST.get('followed_user')
        following_user_pk = request.POST.get('following_user')
        action = request.POST.get('action')
        handle_invitation(followed_user_pk, following_user_pk, action)
        if action == "accept":
            messages.success(request, f"Follow request accepted.")
        else:
            messages.info(request, "Follow request declined.")

    return render(request, 'notifications.html', {'data': data})

@login_required
def comment(request, post_id):
    post = Post.objects.get(pk=post_id)
    replies = Post.objects.filter(parent_post=post_id)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        processed_comment = process_comment_form(request, form, post_id)
        if processed_comment:
            return redirect('comment', post_id=post_id)
    
    form = PostForm()
    context = {'post': post, 'form': form, 'replies': replies}
    return render(request, 'comment.html', context)
    
@login_required
def like(request, post_id):
    if request.user.is_authenticated:
        post = Post.objects.get(pk=post_id)
        dislike = PostDislike.objects.filter(disliker=request.user, post=post).first()
        if dislike:
            dislike.delete()
        PostLike.objects.create(liker=request.user, post=post)
        referer = request.META.get('HTTP_REFERER')
        if referer and 'profile' in referer.lower():
            return redirect('profile')
        #return redirect('home')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    return redirect('login')

@login_required
def dislike(request, post_id):
    if request.user.is_authenticated:
        post = Post.objects.get(pk=post_id)
        like = PostLike.objects.filter(liker=request.user, post=post).first()
        if like:
            like.delete()
        PostDislike.objects.create(disliker=request.user, post=post)
        referer = request.META.get('HTTP_REFERER')
        if referer and 'profile' in referer.lower():
            return redirect('profile')
        #return redirect('home')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    return redirect('login')


@login_required
def report(request, post_id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = PostReportForm(request.POST)
            if form.is_valid():
                report = form.save(commit=False)
                report.reporter = request.user
                report.post = Post.objects.get(pk=post_id)
                report.save()
                messages.success(request, 'Post successfully reported.')
        return redirect('home')
    return redirect('login')

@login_required
def report_user(request, reported_id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = UserReportForm(request.POST)
            if form.is_valid():
                report = form.save(commit=False)
                report.reporter = request.user
                reported = User.objects.get(id=reported_id)
                report.reported = reported
                report.save()
                messages.success(request, 'User successfully reported.')
            else:
                messages.error(request, 'User not reported.')
        return redirect('guest', reported_id)
    return redirect('login')
    
def error_404(request):
    return render(request, '404.html', status=404)

def error_500(request):
    raise ValueError("Error 500, Server error")

@login_required
def save_post(request, post_id):
    # Only allow POST requests for saving a post. Better to keep, I ran into this issue wasted time because no message telling me it wasn't POST
    if request.user.is_authenticated:
        if request.method == 'POST':
            post = get_object_or_404(Post, pk=post_id)
            # Check if the post is already saved by the user.
            post_save, created = PostSave.objects.get_or_create(saver=request.user, post=post)
            if created:
                # The post was not saved before and now is saved.
                messages.success(request, 'Post saved successfully.')
            else:
                post_save.delete()
                messages.info(request, 'Post unsaved.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        else:
        # If it's not a POST request, do not allow the operation.
            return HttpResponseForbidden('Invalid request method.')
    return redirect('home')

@login_required
def bookmarked_posts(request):
    saved_posts = PostSave.objects.filter(saver=request.user).select_related('post').order_by('-post__created_at') #orders the results by the creation date of the posts in descending order (newest first).
    posts = [save.post for save in saved_posts]

    likes = [post for post in posts if post.is_likeable_by(request.user)]
    dislikes = [post for post in posts if post.is_dislikeable_by(request.user)]
    saved_post_ids = [post.id for post in posts if not post.is_saveable_by(request.user)] 
    form = PostForm()
    reposted_post_ids = Repost.objects.filter(user=request.user).values_list('post_id', flat=True)
    data=Notifications.objects.filter(user=request.user).order_by('-id')
    following_users = request.user.profile.following.all()
    following_posts = Post.objects.filter(user__in=following_users).order_by('-created_at')

    context =  {
        'bookmarked_posts': posts,
        'posts': posts, 
        'likes': likes,
        'dislikes': dislikes,
        'saved_post_ids': saved_post_ids,  
        'form': form, 
        'data' : data,
        'reportPostForm': PostReportForm(), 
        'reposted_post_ids': reposted_post_ids,
        'followPost' : following_posts
        }
    return render(request, 'bookmark.html', context)
