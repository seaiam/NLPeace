from api.logger_config import configure_logger # TODO add logging statements
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.http import JsonResponse
from django.db.models import Q

from core.forms.profile_forms import *
from core.forms.posting_forms import *
from core.models.models import *

def home(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                post = form.save(commit=False)
                post.user = request.user
                post.save()
                return redirect('home')
    
        #User is authenticated
        user_ids_following = request.user.profile.following.values_list('id', flat=True)

        posts = Post.objects.filter(
            Q(user__profile__is_private=False) | 
            Q(user__in=user_ids_following) |  
            Q(user=request.user) 
        ).distinct().order_by('-created_at')

        form = PostForm()
        data=Notifications.objects.all().order_by('-id')
        return render(request, 'index.html', {'posts': posts, 'form': form,'data':data ,'reportPostForm': PostReportForm()})
    else:
        #redirect user to login page
        return redirect('login')
    
@login_required
def profile(request):
    profile = Profile.objects.get_or_create(pk=request.user.id)
    data=Notifications.objects.all().order_by('-id')
   
    return render(request, 'home.html' ,{'profile': profile[0],'data':data,'form': EditBioForm(instance=profile[0])})

@login_required
def guest(request,user_id):
    user=User.objects.get(pk=user_id)
    profile=Profile.objects.get(user=user)
    data=Notifications.objects.all().order_by('-id')
    return render(request,'home.html',{'user':user,'data':data,'profile':profile,})

@login_required
def notifications(request):
    data=Notifications.objects.all().order_by('-id')
    return render(request,'notifications.html',{'data':data})


@login_required
def accept_decline_invite(request):
    data=Notifications.objects.all().order_by('-id')
  
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
def report(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = PostReportForm(request.POST)
            if form.is_valid():
                report = form.save(commit=False)
                report.reporter = request.user
                report.save()
                messages.success(request, 'Post successfully reported.')
        return redirect('home')
    return redirect('login')


def error_404(request):
    return render(request, '404.html', status=404)

def error_500(request):
    raise ValueError("Error 500, Server error")