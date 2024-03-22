from api.logger_config import configure_logger # TODO add logging statements
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import *
from core.forms.community_forms import CommunityForm,CommunityReportForm
from core.models.community_models import Community, CommunityPost
from core.models.post_models import Post, Repost
from core.models.profile_models import Notifications
from core.forms.posting_forms import PostForm, PostReportForm
from django.http import HttpResponseRedirect
from .services import get_post_interactions, handle_join_request, handle_leave_request, get_user_notifications, handle_admin_join, handle_delete_community, report_community_service, process_community_post, handle_user_banning, handle_user_unbanning, search_for_users
from collections import namedtuple
from django.template.loader import render_to_string

@login_required
def create_community(request):
    data = Notifications.objects.filter(user=request.user).order_by('-id')
    data = Notifications.objects.filter(user=request.user).order_by('-id')
    if request.method == 'POST':
        form = CommunityForm(request.POST, request.FILES)
        if form.is_valid():
            community = form.save(commit=False)
            community.admin = request.user
            community.is_private = form.cleaned_data['is_private'] == 'True'
            community.allows_offensive = form.cleaned_data['allows_offensive'] == 'True'
            community.save()
            messages.success(request, 'Community created successfully.')
            return redirect('community_detail', community_id=community.id)
    else:
        form = CommunityForm()
    communities = Community.objects.all()[:10]

    user_communities = Community.objects.filter(admin=request.user).order_by('-created_at')
    joined_communities = Community.objects.filter(members=request.user).exclude(admin=request.user).order_by('-created_at')

    context = {
        'data':data,
        'data':data,
        'form': form,
        'communities': communities,
        'user_communities': user_communities,
        'joined_communities': joined_communities,
    }
    return render(request, 'create_community.html', context)

@login_required
def community_detail(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    members = community.members.all()
    show_offensive  = community.allows_offensive and request.user.profile.allows_offensive
    community_posts = CommunityPost.objects.filter(community = community, post__is_offensive = show_offensive)
    Carrier = namedtuple('Carrier', ['is_post', 'payload'])
    community_carriers = [Carrier(is_post=True, payload=cp.post) for cp in community_posts]
    likes, dislikes, saved_post_ids = get_post_interactions(request.user, community_carriers, False)
    reposted_post_ids = Repost.objects.filter(user=request.user).values_list('post_id', flat=True)
    reported_posts = [post.payload for post in community_carriers if post.is_post and not post.payload.is_reportable_by(request.user)]
    
    is_member = request.user in community.members.all()
    
    if request.user in community.banned_users.all():
         messages.success(request, "This community can't be accessed because you have been banned from it.")
         return redirect('create_community')
    
    if request.method == 'GET':
        search_query = request.GET.get('search', None)
        if search_query:
            members = search_for_users(search_query).filter(communities=community)
    
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        print("AJAX request received")
        search_query = request.POST.get('search', '')
        print("Search query:", search_query)
        members = search_for_users(search_query).filter(communities=community)
        html = render_to_string('members_list_partial.html', {'members': members}, request=request)
        
        return JsonResponse({'html': html})

    if request.method == 'POST':
        # Check if user is the admin of the community
        if request.user == community.admin:
            form = CommunityForm(request.POST, request.FILES, instance=community)

            action = request.POST.get('action')
            if action == "ban_user":
             community_id = request.POST.get('community_id')
             user_to_ban = request.POST.get('member_id')
             handle_user_banning(community_id, user_to_ban)
             messages.success(request, "User has been banned.")

            if action == "unban_user":
             community_id = request.POST.get('community_id')
             user_to_unban = request.POST.get('member_id')
             handle_user_unbanning(community_id, user_to_unban)
             messages.success(request, "User has been unbanned.")

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
        'members' : members,
        'community_posts': community_carriers,
        'is_member': is_member,
        'form': form,
        'reportCommunityForm': CommunityReportForm(),
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
        community = get_object_or_404(Community, id=community_to_join_id)
        requester_id = request.POST.get('requester_id')
         # Preserve the search context if it exists
        if request.user in community.banned_users.all():
         messages.success(request, "This community can't be joined because you have been banned from it.")
         return redirect('create_community')
        search = request.POST.get('search')
        if search:
          request.session['search'] = search
         # Preserve the search context if it exists
        search = request.POST.get('search')
        if search:
          request.session['search'] = search
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
        # Preserve the search context if it exists
        search = request.POST.get('search')
        if search:
          request.session['search'] = search
        # Preserve the search context if it exists
        search = request.POST.get('search')
        if search:
          request.session['search'] = search
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
def create_community_post(request, community_id):
    community = get_object_or_404(Community, id=community_id) 
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        community_post = process_community_post(request, community, form) 
        if community_post:
            return redirect('community_detail', community_id=community_id)
        else:
            print(form.errors) 
            messages.error(request, "Error creating post.") 
    else:
        form = PostForm()
    context =  {
        'form': form, 
        'community': community, 
        }
    return render(request, 'community_detail.html', context)

@login_required
def search_community(request):
    if request.method == "POST" :
        search=request.POST.get('search')
        if search == "":
            return redirect('create_community')
        if search:
         communities = Community.objects.filter(name__icontains=search)         
        context = {'search':search,'communities':communities,'form': CommunityForm(request.POST, request.FILES)}
        if communities:
            return render(request, 'community_list.html', context)
        else:
            messages.error(request, f"The community '{search}' does not exist.")
            return redirect('create_community')     
    search = request.session.get('search')
    if search:
        communities = Community.objects.filter(name__icontains=search)
        context = {'search':search, 'communities': communities, 'form': CommunityForm(request.POST, request.FILES)}
        return render(request,'community_list.html',context)
    else:
        return redirect('create_community')
   
@login_required
def delete_community(request, community_id):
    if request.method == 'POST':
        success, message = handle_delete_community(community_id, request.user)
        if success:
            messages.success(request, message)
            return redirect('create_community')  
        else:
            messages.error(request, message)
            return redirect('community_detail', community_id=community_id)
    return redirect('community_detail', community_id=community_id)        

@login_required
def report_community(request, reported_id):
    if request.method == 'POST':
        form = CommunityReportForm(request.POST)
        if form.is_valid():
            report_community_service(request, reported_id, form)
            messages.success(request, 'Community successfully reported.')
        else:
            messages.error(request, 'Community not reported.')
        return redirect('community_detail', reported_id)

