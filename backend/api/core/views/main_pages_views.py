from api.logger_config import configure_logger # TODO add logging statements
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import *
from django.urls import reverse
from core.forms.user_forms import UserReportForm
from core.forms.profile_forms import EditProfileBannerForm, EditProfilePicForm, EditBioForm
from core.forms.posting_forms import PostForm, PostReportForm
from core.models.post_models import Post, Repost, PostReport
from core.models.profile_models import Notifications
from core.models.community_models import CommunityPost
from .services import *

def home(request, word=None):
    if not request.user.is_authenticated:
        return redirect('login')
      
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        post = process_post_form(request, form)
        if post:
            return redirect('home')

    
    carriers = get_user_posts(request.user, word)
    # filtering out community post in home page
    posts = [carrier for carrier in carriers if (not hasattr(carrier.payload, 'is_community_post')) or (hasattr(carrier.payload, 'is_community_post') and not carrier.payload.is_community_post())]

    posts_without_ads = map(lambda carrier: carrier.payload, filter(lambda carrier: carrier.is_post, posts))
    likes, dislikes, saved_post_ids = get_post_interactions(request.user, posts)
    reposted_post_ids = Repost.objects.filter(user=request.user).values_list('post_id', flat=True)
    data = Notifications.objects.filter(user=request.user).order_by('-id')
    following_users = request.user.profile.following.all()
    
    following_carriers = get_following_posts(request.user, following_users)
    # filtering out community post in home page
    following_posts = [carrier for carrier in following_carriers if (not hasattr(carrier.payload, 'is_community_post')) or (hasattr(carrier.payload, 'is_community_post') and not carrier.payload.is_community_post())]


    reported_posts = [post.payload for post in posts if post.is_post and not post.payload.is_reportable_by(request.user)] #for post reporting

    context = {
        'posts': posts,
        'likes': likes,
        'dislikes': dislikes,
        'saved_post_ids': saved_post_ids,
        'form': PostForm(),
        'reportPostForm': PostReportForm(),
        'reportUserForm': UserReportForm(),
        'data': data,
        'reportPostForm': PostReportForm(),
        'reposted_post_ids': reposted_post_ids,
        'followPost': following_posts,
        'reported_posts' : reported_posts, #for post reporting
        'word': word,
    }
    return render(request, 'index.html', context)

@login_required
def profile(request):
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        post = process_post_form(request, form)
        if post:
            return redirect('profile')
    
    profile = get_user_profile(request.user)
    posts = get_user_posts_with_community_info(request, request.user)
    image_posts = get_image_posts(request.user, posts)
    likes, dislikes, saved_post_ids = get_post_interactions(request.user, posts)
    followers = profile.followers.all()
    following = profile.following.all()
    liked_posts = get_liked_posts(request.user)
    data = Notifications.objects.filter(user=request.user).order_by('-id')
    #TEMP
    pinned_posts = [post for post in posts if not post.is_post or post.payload.is_pinned_by(request.user)]
    pinned_image_posts = [post for post in posts if not post.is_post or post.payload.is_pinned_by(request.user) and post.payload.image]
    non_pinned_posts = [post for post in posts if not post.is_post or  not post.payload.is_pinned_by(request.user)]
    saved_post_ids = [post.payload.id for post in posts if post.is_post and not post.payload.is_saveable_by(request.user)] # ADDED THIS
    pinned_post_ids = [post.payload.id for post in posts if post.is_post and post.payload.is_pinned_by(request.user)]
    reported_posts = [post.payload for post in posts if post.is_post and not post.payload.is_reportable_by(request.user)] #for post reporting
    reposted_post_ids = Repost.objects.filter(user=request.user).values_list('post_id', flat=True)    
    replies = [post for post in posts if post.is_post and post.payload.parent_post is not None]
    non_pinned_image_posts=[post for post in posts if post.is_post and not post.payload.is_pinned_by(request.user) and post.payload.image]
    community_posts = get_user_community_posts(request.user) 

    context = {
        'profile': profile,
        'posts': posts,
        'media_posts': image_posts,
        'likes': likes,
        'dislikes': dislikes,
        'saved_post_ids': saved_post_ids,
        'liked_posts': liked_posts,
        'data': data,
        'form': PostForm(),
        'editBannerForm': EditProfileBannerForm(instance=profile),
        'editPicForm': EditProfilePicForm(instance=profile),
        'editBioForm': EditBioForm(instance=profile),
        'reportPostForm': PostReportForm(),
        'reportUserForm': UserReportForm(),
        'followers' : followers,
        'following' : following,
        'pinned_post_ids' : pinned_post_ids,
        'pinned_posts' : pinned_posts,
        'non_pinned_posts' : non_pinned_posts,
        'pinned_image_posts' : pinned_image_posts,
        'replies' : replies,
        'reposted_post_ids': reposted_post_ids,
        'reported_posts' : reported_posts, #for post reporting
        'non_pinned_image_posts' : non_pinned_image_posts,
        'community_posts' : community_posts
        }
    return render(request, 'home.html', context)

@login_required
def guest(request, user_id):
    guest_user = get_user_by_id(user_id)
    profile = get_user_profile(guest_user)
    data = Notifications.objects.filter(user=request.user).order_by('-id')
    all_posts = get_user_posts_with_community_info(request, guest_user)

    image_posts = get_image_posts(guest_user, all_posts)
    likes, dislikes, _ = get_post_interactions(guest_user, all_posts)
    followers = profile.followers.all() 
    following = profile.following.all()
    pinned_posts = [post for post in all_posts if not post.is_post or post.payload.is_pinned_by(user=guest_user)]
    pinned_image_posts = [post for post in all_posts if not post.is_post or post.payload.is_pinned_by(user=guest_user) and post.payload.image]
    non_pinned_posts = [post for post in all_posts if not post.is_post or not post.payload.is_pinned_by(user=guest_user)]
    pinned_post_ids = [post.payload.id for post in all_posts if post.is_post and  post.payload.is_pinned_by(user=guest_user)] 
    liked_posts = get_liked_posts(guest_user)
    saved_post_ids = [post.payload.id for post in all_posts if post.is_post and not post.payload.is_saveable_by(guest_user)] 
    reported_posts = [post.payload for post in all_posts if post.is_post and not post.payload.is_reportable_by(request.user)] #for post reporting
    reposted_post_ids = Repost.objects.filter(user=request.user).values_list('post_id', flat=True)
    replies = [post for post in all_posts if post.is_post and post.payload.parent_post is not None]
    non_pinned_image_posts=[post for post in all_posts if post.is_post and not post.payload.is_pinned_by(request.user) and post.payload.image]
    community_posts = get_user_community_posts(guest_user)
    community_posts = [post for post in all_posts if post.is_post and post.payload.is_community_post()]
    

    context = {
        'user': guest_user,
        'data': data,
        'profile': profile,
        'form': EditBioForm(instance=profile),
        'posts': all_posts,
        'media_posts': image_posts,
        'likes': likes,
        'dislikes': dislikes,
        'liked_posts': liked_posts,
        'saved_post_ids': saved_post_ids,
        'reportPostForm': PostReportForm(),
        'reportUserForm': UserReportForm(),
        'followers' : followers,
        'following' : following,
        'pinned_posts' : pinned_posts,
        'non_pinned_posts': non_pinned_posts,
        'pinned_image_posts' : pinned_image_posts,
        "pinned_post_ids" : pinned_post_ids,
        'reposted_post_ids': reposted_post_ids,
        'replies' : replies,
        'reported_posts' : reported_posts, #for post reporting
        'non_pinned_image_posts' : non_pinned_image_posts,
        'community_posts' : community_posts
        }
    return render(request,'home.html',context)

@login_required
def notifications(request):
    community_notifications, personal_notifications = get_user_notifications(request.user)
    context = {
        'community_notifications': community_notifications,
        'personal_notifications': personal_notifications
    }
    return render(request, 'notifications.html', context)

@login_required
def accept_decline_invite(request):
    community_notifications, personal_notifications  = get_user_notifications(request.user)
    if request.method == 'POST':
        followed_user_pk = request.POST.get('followed_user')
        following_user_pk = request.POST.get('following_user')
        action = request.POST.get('action')
        handle_invitation(followed_user_pk, following_user_pk, action)
        if action == "accept":
            messages.success(request, f"Follow request accepted.")
        else:
            messages.info(request, "Follow request declined.")
    context = {
        'community_notifications': community_notifications,
        'personal_notifications': personal_notifications
    }
    return render(request, 'notifications.html', context)

@login_required
def report_user(request, reported_id):
    if request.method == 'POST':
        form = UserReportForm(request.POST)
        if form.is_valid():
            report_user_service(request, reported_id, form)
            messages.success(request, 'User successfully reported.')
        else:
            messages.error(request, 'User not reported.')
        return redirect('guest', reported_id)
    
def error_404(request):
    return render(request, '404.html', status=404)

def error_500(request):
    raise ValueError("Error 500, Server error")

@login_required
def bookmarked_posts(request):
    posts = get_bookmarked_posts(request.user)
    reported_posts = [post for post in posts if post.is_post and not post.payload.is_reportable_by(request.user)]
    likes = [post for post in posts if post.is_post and post.payload.is_likeable_by(request.user)]
    dislikes = [post for post in posts if post.is_post and post.payload.is_dislikeable_by(request.user)]
    saved_post_ids = [post.payload.id for post in posts if post.is_post and not post.payload.is_saveable_by(request.user)]
    reposted_post_ids = Repost.objects.filter(user=request.user).values_list('post_id', flat=True)
    data = Notifications.objects.filter(user=request.user).order_by('-id')
    following_users = request.user.profile.following.all()
    following_posts = Post.objects.filter(user__in=following_users).order_by('-created_at')
    pinned_post_ids = [post.payload.id for post in posts if post.is_post and post.payload.is_pinned_by(request.user)] 
    

    context = {
        'bookmarked_posts': posts,
        'likes': likes,
        'dislikes': dislikes,
        'saved_post_ids': saved_post_ids,
        'form': PostForm(),
        'data': data,
        'reportPostForm': PostReportForm(),
        'reposted_post_ids': reposted_post_ids,
        'followPost' : following_posts,
        'reported_posts' : reported_posts,
        'pinned_post_ids': pinned_post_ids
        }
    return render(request, 'bookmark.html', context)

@login_required
def hashtag_search(request, word):
    return redirect(reverse('home_with_word', args=[word]))