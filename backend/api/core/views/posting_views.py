from api.logger_config import configure_logger # TODO add logging statements
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import *
from core.forms.posting_forms import PostForm, PostReportForm
from core.models.models import Post
from django.http import HttpResponseRedirect
from .services import *

@login_required
def delete_post(request):
    if request.method == "POST":
        post_id = request.POST.get('post_id')
        if delete_user_post(request.user.id, post_id):
            messages.success(request, "Post deleted successfully.")
        else:
            messages.error(request, "You may not delete this post.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def repost(request, post_id):
    create_repost(request.user, post_id)
    return redirect('home')

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
    handle_like(request.user, post_id)

    referer = request.META.get('HTTP_REFERER')
    if referer and 'profile' in referer.lower():
        return redirect('profile')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def dislike(request, post_id):
    handle_dislike(request.user, post_id)

    referer = request.META.get('HTTP_REFERER')
    if referer and 'profile' in referer.lower():
        return redirect('profile')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def report(request, post_id):
    if request.method == 'POST':
        form = PostReportForm(request.POST)
        if form.is_valid():
            report_post(request.user, post_id, request.POST)
            messages.success(request, 'Post successfully reported.')
        return redirect('home')

@login_required
def pin(request, post_id):     
    message = handle_pin(request.user, post_id)
    messages.info(request, message)
    referer = request.META.get('HTTP_REFERER')
    if referer and 'profile' in referer.lower():
        return redirect('profile')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    
@login_required
def unpin(request, post_id):     
    message = handle_unpin(request.user, post_id)
    messages.info(request, message)
    referer = request.META.get('HTTP_REFERER')
    if referer and 'profile' in referer.lower():
        return redirect('profile')        
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    original_poster = post.user

    if request.user == original_poster:
        if request.method == 'POST':
            image_flag = request.POST.get('remove_image', 'false') == 'true'
            form = PostForm(request.POST, request.FILES, instance = post)
            result = handle_edit_post(request, form, post, image_flag, post.parent_post)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))  
        else:
            return render(request, '401.html', status=400)
    else:
        return render(request, '401.html', status=401)

@login_required
def save_post(request, post_id):
    if request.method == 'POST':
        message = save_or_unsave_post(request.user, post_id)
        messages.info(request, message)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    return HttpResponseForbidden('Invalid request method.')
