from api.logger_config import configure_logger # TODO add logging statements
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import *
from django.views.decorators.http import require_POST
from core.forms.posting_forms import PostForm, PostReportForm
from core.models.post_models import Post
from django.http import HttpResponseRedirect, JsonResponse
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
@require_POST
def repost(request, post_id):
    try:
        requests.post('http://telemetry:8080/submit/data2', json={
                                                                "user_id": request.user.id,
                                                                "request_body": request.body.decode('utf-8'),
		                                                        "url":"repost",
                                                                })
        requests.post('http://telemetry:8080/submit/data3', json={
                                                                "user_id": request.user.id,
		                                                        "status_code":200
                                                          
                                                                })
    except Exception as e:
        print(e)
    reposts = create_repost(request.user, post_id)
    return JsonResponse({'reposted': True, 'reposts_count': reposts})

@login_required
def comment(request, post_id):
    post = Post.objects.get(pk=post_id)
    replies = Post.objects.filter(parent_post=post_id)

    #check if user allows offensive content
    profile, created = Profile.objects.get_or_create(user=request.user)
    if profile.allows_offensive == False:
        replies = Post.objects.filter(id__in=[p.id for p in replies]).exclude(is_offensive=True)

    reposted_post_ids = Repost.objects.filter(user=request.user).values_list('post_id', flat=True)
    likes = [post for post in replies if post.is_likeable_by(request.user)]
    dislikes = [post for post in replies if post.is_dislikeable_by(request.user)]
    likeable = post.is_likeable_by(request.user)
    dislikeable = post.is_dislikeable_by(request.user)
    saved_post_ids = [post.id for post in replies if post.is_saveable_by(request.user)]
    reported_posts = [post for post in replies if not post.is_reportable_by(request.user)]
    reportable = post.is_reportable_by(request.user)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        processed_comment = process_comment_form(request, form, post_id)
        if processed_comment:
            return redirect('comment', post_id=post_id)
    
    form = PostForm()
    context = {
        'post': post, 
        'form': form, 
        'replies': replies,
        'reportPostForm': PostReportForm(),
        'reposted_post_ids': reposted_post_ids,
        'saved_post_ids': saved_post_ids,
        'likes': likes,
        'dislikes': dislikes,
        'likeable': likeable,
        'dislikeable': dislikeable,
        'reported_posts' : reported_posts,
        'reportable': reportable
        }
    return render(request, 'comment.html', context)
    
@login_required
@require_POST
def like(request, post_id):
    likes = handle_like(request.user, post_id)
    return JsonResponse({'liked': True, 'likes_count': likes})

@login_required
@require_POST
def dislike(request, post_id):
    dislikes = handle_dislike(request.user, post_id)
    return JsonResponse({'disliked': True, 'dislikes_count': dislikes})

@login_required
def report(request, post_id):
    if request.method == 'POST':
        form = PostReportForm(request.POST)
        if form.is_valid():
            report_post_service(request, post_id, form)
        referer = request.META.get('HTTP_REFERER')
        if referer and 'profile' in referer.lower():
            return redirect('profile')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


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
@require_POST
def save_post(request, post_id):
    message, saved, saves_count = save_or_unsave_post(request.user, post_id)
    messages.info(request, message)
    return JsonResponse({'saved': saved, 'saves_count': saves_count})

