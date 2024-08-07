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
from core.models.post_models import Post, Repost, PostReport, Vote
from core.models.profile_models import Notifications
from core.models.community_models import CommunityPost
from .services import *

def home(request, word=None):
    if not request.user.is_authenticated:
        return redirect('login')
    
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        try:
            requests.post('http://telemetry:8080/submit/data2', json={
                                                                "user_id": request.user.id,
                                                                "request_body": str(request.body).decode('utf-8'),
		                                                        "url":"post",
                                                                })
        except Exception as e:
            print(e)
        form = PostForm(request.POST, request.FILES)
        post = process_post_form(request, form)
        if post:
            try:
                requests.post('http://telemetry:8080/submit/data3', json={
                                                            "user_id": request.user.id,
		                                                    "status_code":302
                                                            })
            except Exception as e:
                print(e)
            return redirect('home')
    
    carriers = get_user_posts(request.user, word, profile.allows_offensive)
    # filtering out community post in home page
    posts = [carrier for carrier in carriers if (not hasattr(carrier.payload, 'is_community_post')) or (hasattr(carrier.payload, 'is_community_post') and not carrier.payload.is_community_post())]

    posts_without_ads = map(lambda carrier: carrier.payload, filter(lambda carrier: carrier.is_post, posts))
    likes, dislikes, saved_post_ids = get_post_interactions(request.user, posts, profile.allows_offensive)
    reposted_post_ids = Repost.objects.filter(user=request.user).values_list('post_id', flat=True)
    data = Notifications.objects.filter(user=request.user).order_by('-id')
    following_users = request.user.profile.following.all()
    
    following_carriers = get_following_posts(request.user, following_users, profile.allows_offensive)
    # filtering out community post in home page
    following_posts = [carrier for carrier in following_carriers if (not hasattr(carrier.payload, 'is_community_post')) or (hasattr(carrier.payload, 'is_community_post') and not carrier.payload.is_community_post())]


    reported_posts = [post.payload for post in posts if post.is_post and not post.payload.is_reportable_by(request.user)] #for post reporting 
    # Retrieve user's voted polls
    voted_poll_ids = Vote.objects.filter(user=request.user).values_list('choice__poll__post_id', flat=True)
    # Store polls that a user votes on
    request.session['voted_poll_ids'] = list(voted_poll_ids)
    request.session.modified = True

    if profile.allows_offensive == False:
            offensive_posts = Post.objects.filter(is_offensive=True)
            reposted_post_ids = [id for id in reposted_post_ids if id not in offensive_posts.values_list('id', flat=True)]
            reported_posts = Post.objects.filter(id__in=[p.id for p in reported_posts]).exclude(is_offensive=True)

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
    
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        post = process_post_form(request, form)
        if post:
            return redirect('profile')
        
    if request.user.is_authenticated:
        allows_offensive = profile.allows_offensive
    else:
        allows_offensive = False
    
    profile = get_user_profile(request.user)
    posts = get_user_posts_with_community_info(request, request.user, allows_offensive)
    image_posts = get_image_posts(request.user, posts)
    likes, dislikes, saved_post_ids = get_post_interactions(request.user, posts, allows_offensive)
    followers = profile.followers.all()
    following = profile.following.all()
    liked_posts = get_liked_posts(request.user, allows_offensive)
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
    community_posts = get_user_community_posts(request.user, allows_offensive) 
    # Retrieve user's voted polls
    voted_poll_ids = Vote.objects.filter(user=request.user).values_list('choice__poll__post_id', flat=True)
    # Store polls that a user votes on
    request.session['voted_poll_ids'] = list(voted_poll_ids)
    request.session.modified = True
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
    all_posts = get_user_posts_and_reposts(guest_user, False)
    
    filtered_posts = []
    current_user = request.user 
    for carrier in all_posts:
        post = carrier.payload
        if post.is_community_post():
            community_post = CommunityPost.objects.get(post=post)
            if not community_post.community.is_private or current_user in community_post.community.members.all() or current_user == guest_user.user:
                filtered_posts.append(carrier)
        else:
            filtered_posts.append(carrier)

    all_posts = filtered_posts

    image_posts = get_image_posts(guest_user, all_posts)
    likes, dislikes, _ = get_post_interactions(guest_user, all_posts, False)
    followers = profile.followers.all() 
    following = profile.following.all()
    pinned_posts = [post for post in all_posts if not post.is_post or post.payload.is_pinned_by(user=guest_user)]
    pinned_image_posts = [post for post in all_posts if not post.is_post or post.payload.is_pinned_by(user=guest_user) and post.payload.image]
    non_pinned_posts = [post for post in all_posts if not post.is_post or not post.payload.is_pinned_by(user=guest_user)]
    pinned_post_ids = [post.payload.id for post in all_posts if post.is_post and  post.payload.is_pinned_by(user=guest_user)] 
    liked_posts = get_liked_posts(guest_user, False)
    saved_post_ids = [post.payload.id for post in all_posts if post.is_post and not post.payload.is_saveable_by(guest_user)] 
    reported_posts = [post.payload for post in all_posts if post.is_post and not post.payload.is_reportable_by(request.user)] #for post reporting
    reposted_post_ids = Repost.objects.filter(user=request.user).values_list('post_id', flat=True)
    replies = [post for post in all_posts if post.is_post and post.payload.parent_post is not None]
    non_pinned_image_posts=[post for post in all_posts if post.is_post and not post.payload.is_pinned_by(request.user) and post.payload.image]
    community_posts = get_user_community_posts(guest_user, False)
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
    posts = get_bookmarked_posts(request.user, request.user.profile.allows_offensive)
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
    return redirect(reverse('home_with_word', args=[f'#{word}']))

@login_required
def trends(request):
    context = {'trends': get_trends()}
    return render(request, 'trends.html', context)

@login_required
def trend_search(request, word):
    return redirect(reverse('home_with_word', args=[word]))

def privacy_policy(request):
    return render(request, 'privacy_and_data_policy.html')