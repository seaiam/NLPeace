from api.logger_config import configure_logger # TODO add logging statements
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

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
        posts = Post.objects.all().order_by('-created_at')
        form = PostForm()
        reposted_post_ids = Repost.objects.filter(user=request.user).values_list('post_id', flat=True)
        context =  {
            'posts': posts, 
            'form': form, 
            'reportPostForm': PostReportForm(), 
            'reposted_post_ids': reposted_post_ids
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
    profile = Profile.objects.get_or_create(pk=request.user.id)
   
    return render(request, 'home.html', {'profile': profile[0], 'form': EditBioForm(instance=profile[0])})

@login_required
def guest(request,user_id):
    user=User.objects.get(pk=user_id)
    profile=Profile.objects.get(user=user)
    
    return render(request,'home.html',{'user':user,'profile':profile,})

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
def like(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = PostLikeForm(request.POST)
            if form.is_valid():
                dislike = PostDislike.objects.filter(disliker=request.user, post=form.cleaned_data['post']).first()
                if dislike:
                    dislike.delete()
                like = form.save(commit=False)
                like.liker = request.user
                like.save()
        return redirect('home')
    return redirect('login')

@login_required
def dislike(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = PostDislikeForm(request.POST)
            if form.is_valid():
                like = PostLike.objects.filter(liker=request.user, post=form.cleaned_data['post']).first()
                if like:
                    like.delete()
                dislike = form.save(commit=False)
                dislike.disliker = request.user
                dislike.save()
        return redirect('home')
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