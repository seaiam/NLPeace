from api.logger_config import configure_logger # TODO add logging statements
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import *
from core.forms.community_forms import CommunityForm
from core.models.community_models import Community, CommunityPost
from core.models.post_models import Post
from core.forms.posting_forms import PostForm, PostReportForm
from django.http import HttpResponseRedirect
from .services import *
from collections import namedtuple

@login_required
def create_community(request):
    if request.method == 'POST':
        form = CommunityForm(request.POST, request.FILES)
        if form.is_valid():
            community = form.save(commit=False)
            community.admin = request.user
            community.is_private = form.cleaned_data['is_private'] == 'True'
            community.save()
            messages.success(request, 'Community created successfully.')
            return redirect('community_detail', community_id=community.id)
    else:
        form = CommunityForm()
    communities = Community.objects.all()[:10]
    context = {
        'form': form,
        'communities': communities
    }
    return render(request, 'create_community.html', context)

@login_required
def community_detail(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    community_posts = CommunityPost.objects.filter(community=community)
    Carrier = namedtuple('Carrier', ['is_post', 'payload'])
    community_carriers = [Carrier(is_post=True, payload=cp.post) for cp in community_posts]
    likes, dislikes, saved_post_ids = get_post_interactions(request.user, community_carriers)
    reposted_post_ids = Repost.objects.filter(user=request.user).values_list('post_id', flat=True)
    reported_posts = [post.payload for post in community_carriers if post.is_post and not post.payload.is_reportable_by(request.user)]
    
    is_member = request.user in community.members.all()
    
    if request.method == 'POST':
        # Check if user is the admin of the community
        if request.user == community.admin:
            form = CommunityForm(request.POST, request.FILES, instance=community)
            if form.is_valid():
                form.save()
                messages.success(request, 'Community updated successfully.')
                return redirect('community_detail', community_id=community.id)
        else:
            messages.error(request, "You don't have permission to edit this community.")
            return redirect('community_detail', community_id=community.id)
    else:
        form = CommunityForm(instance=community)

    context = {
        'community': community,
        'community_posts': community_carriers,
        'is_member': is_member,
        'form': form,
        'likes': likes,
        'dislikes': dislikes,
        'saved_post_ids': saved_post_ids,
        'reported_posts' : reported_posts,
        'reportPostForm': PostReportForm(),
        'reposted_post_ids': reposted_post_ids,
    }
    return render(request, 'community_detail.html', context)

@login_required
def join_community(request):
    if request.method == 'POST':
        community_to_join_id = request.POST.get('community_id')
        requester_id = request.POST.get('requester_id')
        is_private = handle_join_request(community_to_join_id, requester_id)
        if is_private:
            messages.success(request, 'A join request has been sent.')
        else:
            community_to_join = Community.objects.get(pk = community_to_join_id)
            messages.success(request, f"You have joined {community_to_join.name}.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    return HttpResponseForbidden()
   
@login_required
def leave_community(request):
    if request.method == 'POST':

        community_to_leave_id = request.POST.get('community_id')
        requester_id = request.POST.get('requester_id')
        handle_leave_request(community_to_leave_id, requester_id)
        community_to_leave = Community.objects.get(pk = community_to_leave_id)
        messages.success(request, f"You have left {community_to_leave.name}.")

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    return HttpResponseForbidden()

@login_required
def accept_decline_join(request):
    if request.method == 'POST':
        community_id = request.POST.get('joined_community_id')
        joiner_id = request.POST.get('joiner_id')
        action = request.POST.get('action')
        handle_admin_join(community_id, joiner_id, action)
        if action == "accept":
            messages.success(request, f"Join request accepted.")
        else:
            messages.info(request, "Join request declined.")
    
    community_notifications, personal_notifications = get_user_notifications(request.user)
    context = {
        'community_notifications': community_notifications,
        'personal_notifications': personal_notifications
    }
    return render(request, 'notifications.html', context)

def create_community_post(request, community_id):
    community = get_object_or_404(Community, id=community_id) 
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user 
            post.save()

            CommunityPost.objects.create(post=post, community=community)
            messages.success(request, "Post created successfully!")  
            return redirect('community_detail', community_id=community_id)
        else:
            print(form.errors) 
            messages.error(request, "Error creating post.") 
    else:
        form = PostForm()

    community_posts = CommunityPost.objects.filter(community=community)
    return render(request, 'community_detail.html', {'form': form, 'community': community, 'community_posts': community_posts})