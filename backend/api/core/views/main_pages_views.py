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

def home(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                #extract tweet from form
                tweet_text = form.cleaned_data['content']
                #pass tweet to nlp classifier
                result = classify_tweet(tweet_text)

                if result["prediction"][0] == 2: #Post is appropriate
                    post = form.save(commit=False)
                    post.user = request.user
                    post.save()
                    return redirect('home')
                if result["prediction"][0] == 1: #Post is offensive
                    messages.error(request, f'This post contains offensive language and is not allowed on our platform.')
                    return redirect('home')

                if result["prediction"][0] == 0: #Post is hate speech:
                    messages.error(request, f'This post contains hateful language and is not allowed on our platform.')
                    return redirect('home')

        #User is authenticated
        user_ids_following = request.user.profile.following.values_list('id', flat=True)
        profile=Profile.objects.get(user=request.user)
        blocked=profile.blocked.all()
        posts = Post.objects.filter(
            Q(user__profile__is_private=False) | 
            Q(user__in=user_ids_following) |  
            Q(user=request.user) |
            ~Q(user__in=blocked)
        ).distinct().order_by('-created_at')
        likes = [post for post in posts if post.is_likeable_by(request.user)]
        dislikes = [post for post in posts if post.is_dislikeable_by(request.user)]
        
        form = PostForm()
        reposted_post_ids = Repost.objects.filter(user=request.user).values_list('post_id', flat=True)
        data=Notifications.objects.filter(user=request.user).order_by('-id')
        following_users = request.user.profile.following.all()
        following_posts = Post.objects.filter(user__in=following_users).order_by('-created_at')
        context =  {
            'posts': posts, 
            'likes': likes,
            'dislikes': dislikes,
            'form': form, 
            'data' : data,
            'reportPostForm': PostReportForm(), 
            'reposted_post_ids': reposted_post_ids,
            'followPost' : following_posts
            }
        return render(request, 'index.html',context)
    else:
        #redirect user to login page
        return redirect('login')

def repost(request, post_id):
    if request.user.is_authenticated:
        post_to_repost = Post.objects.get(id=post_id)
        Repost.objects.create(post=post_to_repost, user=request.user)
        return redirect('home')
    else:
        return redirect('login')

@login_required
def profile(request):
    profile = Profile.objects.get_or_create(pk=request.user.id)[0]
    data=Notifications.objects.filter(user=request.user).order_by('-id')
    posts = Post.objects.filter(user = request.user)
    reposts_ids = Repost.objects.filter(user = request.user).values_list('post_id', flat=True)
    reposts = Post.objects.filter(id__in = reposts_ids)
    #we combine all user posts and reposts to show them chronogically on the user profile
    all_Posts = list(chain(posts, reposts))
    all_Posts.sort(key=lambda item: item.created_at, reverse=True)
    # Create a list of posts with images
    image_posts = [post for post in posts if post.image]
    likes = [post for post in all_Posts if post.is_likeable_by(request.user)]
    dislikes = [post for post in all_Posts if post.is_dislikeable_by(request.user)]    
    followers = Profile.objects.get(user=request.user).followers.all()
    following = Profile.objects.get(user=request.user).following.all()
    liked_posts = Post.objects.filter(postlike__liker=request.user).distinct().order_by('-created_at')
        
    context = {
        'profile': profile,
        'posts': all_Posts,
        'media_posts':image_posts,
        'likes': likes,
        'dislikes': dislikes,
        'liked_posts': liked_posts,
        'data' : data,
        'editBannerForm': EditProfileBannerForm(instance=profile),
        'editPicForm': EditProfilePicForm(instance=profile),
        'editBioForm': EditBioForm(instance=profile),
        'reportPostForm': PostReportForm(),
        'reportUserForm': UserReportForm(),
        'followers' : followers,
        'following' : following,
        }
    return render(request, 'home.html', context)

@login_required
def guest(request,user_id):
    user=User.objects.get(pk=user_id)
    profile=Profile.objects.get_or_create(user=user)
    data=Notifications.objects.filter(user=request.user).order_by('-id')
    posts = Post.objects.filter(user = user)
    reposts_ids = Repost.objects.filter(user = user).values_list('post_id', flat=True)
    reposts = Post.objects.filter(id__in = reposts_ids)
    #we combine all user posts and reposts to show them chronogically on the user profile
    all_Posts = list(chain(posts, reposts))
    all_Posts.sort(key=lambda item: item.created_at, reverse=True)
     # Create a list of posts with images
    image_posts = [post for post in posts if post.image]
    likes = [post for post in all_Posts if post.is_likeable_by(user)]
    dislikes = [post for post in all_Posts if post.is_dislikeable_by(user)]
    followers = Profile.objects.get(user=user).followers.all()
    following = Profile.objects.get(user=user).following.all()

    context = {
        'user':user,
        'data':data,
        'profile': profile[0], 
        'form': EditBioForm(instance=profile[0]),
        'posts': all_Posts,
        'media_posts':image_posts,
        'likes': likes,
        'dislikes': dislikes,
        'reportUserForm': UserReportForm(),
        'followers' : followers,
        'following' : following,
        }
    return render(request,'home.html',context)

@login_required
def notifications(request):
    data=Notifications.objects.filter(user=request.user).order_by('-id')  
    return render(request,'notifications.html',{'data':data})


@login_required
def accept_decline_invite(request):
    data=Notifications.objects.filter(user=request.user).order_by('-id')
  
    if request.method == 'POST':  
        followed_user_pk = request.POST.get('followed_user')
        following_user_pk=request.POST.get('following_user')
        followed_user=User.objects.get(pk=followed_user_pk)
        following_user=User.objects.get(pk=following_user_pk)
        notification = Notifications.objects.get(user=followed_user_pk, sent_by=following_user_pk,type="request")
        action=request.POST.get('action')
        if action == "accept":
            followed_user.profile.follow_requests.remove(following_user)
            followed_user.profile.followers.add(following_user)
            following_user.profile.following.add(followed_user)
            followed_user.save()
            following_user.save()
            messages.success(request,f"{following_user} started following you.")
            notification.delete() #deletes the message after user accepts request
            notification_message = f"{followed_user.username} accepted your follow request." #message sent to notify following user that follow request has been accepted
            notification2 = Notifications(notifications=notification_message, user=following_user,sent_by=followed_user,type="")
            notification2.save()


        else:
            followed_user.profile.follow_requests.remove(following_user)
            notification.delete() 

    return render(request,'notifications.html',{'data':data})

def comment(request, post_id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                #extract text from comment
                comment_text = form.cleaned_data['content']
                #pass comment to nlp classifier
                result = classify_tweet(comment_text)

                if result["prediction"][0] == 2: #Comment is appropriate
                    post = form.save(commit=False)
                    post.user = request.user
                    post.parent_post = Post.objects.get(pk=post_id)
                    post.save()
                    return redirect('comment', post_id = post_id)
                if result["prediction"][0] == 1: #Comment is offensive
                    messages.error(request, f'This comment contains offensive language and is not allowed on our platform.')
                    return redirect('comment', post_id = post_id)

                if result["prediction"][0] == 0: #Comment is hate speech:
                    messages.error(request, f'This comment contains hateful language and is not allowed on our platform.')
                    return redirect('comment', post_id = post_id)

                post = form.save(commit=False)
                post.user = request.user
                post.parent_post = Post.objects.get(pk=post_id)
                post.save()
                return redirect('comment', post_id = post_id)
        #User is authenticated
        post = Post.objects.get(pk=post_id)
        replies = Post.objects.filter(parent_post=post_id)
        form = PostForm()
        context = {'post': post, 'form': form, 'replies':replies}
        return render(request, 'comment.html', context)
    else:
        #redirect user to login page
        return redirect('login')
    
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
