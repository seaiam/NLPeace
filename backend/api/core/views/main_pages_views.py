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
        return render(request, 'index.html', {'posts': posts, 'form': form})
    else:
        #redirect user to login page
        return redirect('login')
    

def repost(request, post_id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            original_post = get_object_or_404(Post, id=post_id)
            repost_content = f"Reposted from @{original_post.user.username}: {original_post.content}"
            new_post = Post(content=repost_content, user=request.user)
            new_post.save()
            return redirect('home')
    else:
        return redirect('login')

@login_required
def profile(request):
    profile = Profile.objects.get_or_create(pk=request.user.id)
    return render(request, 'home.html', {'profile': profile[0], 'form': EditBioForm(instance=profile[0])})

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

def error_404(request):
    return render(request, '404.html', status=404)

def error_500(request):
    raise ValueError("Error 500, Server error")