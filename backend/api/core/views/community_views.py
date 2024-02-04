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
from django.http import HttpResponseRedirect
from .services import *

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
    community_posts = CommunityPost.objects.filter(community=community).select_related('post')
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
        'community_posts': community_posts,
        'is_member': is_member,
        'form': form  
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

@login_required
def search_community(request):
    if request.method == "POST" :
        searched=request.POST.get('search')
        communities = Community.objects.filter(name__icontains=searched)
        context = {'communities': communities}
        if communities:
            return render(request, 'community_list.html', context)
        else:
            messages.error(request, f"The community '{searched}' does not exist.")
            return redirect('create_community')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        