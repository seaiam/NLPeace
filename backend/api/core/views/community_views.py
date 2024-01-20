from api.logger_config import configure_logger # TODO add logging statements
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import *
from core.forms.community_forms import CommunityForm
from core.models.models import Community, CommunityPost
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
    return render(request, 'create_community.html', {'form': form})

# @login_required
# def edit_community(request, community_id):
#     community = get_object_or_404(Community, id=community_id, admin=request.user)
#     if request.method == 'POST':
#         form = CommunityForm(request.POST, request.FILES, instance=community)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Community updated successfully.')
#             return redirect('community_detail', community_id=community.id)
#     else:
#         form = CommunityForm(instance=community)
#     return render(request, 'edit_community.html', {'form': form, 'community': community})

# def community_detail(request, community_id):
#     community = get_object_or_404(Community, id=community_id)
#     community_posts = CommunityPost.objects.filter(community=community).select_related('post')

#     is_member = request.user in community.members.all()

#     context = {
#         'community': community,
#         'community_posts': community_posts,
#         'is_member': is_member,
#     }
#     return render(request, 'community_detail.html', context)


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
