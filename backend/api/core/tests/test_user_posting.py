from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User 
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import SimpleUploadedFile
from core.forms.posting_forms import PostForm
from core.models.post_models import Hashtag, HashtagInstance, Post, Repost, PostDislike, PostLike, PostReport, PostPin
from core.models.profile_models import Profile

class PostTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        
        try:
            self.profile = self.user.profile  # Try to access the profile
        except ObjectDoesNotExist:
            # Handle the case where the profile does not exist/ create a profile
            self.profile, created = Profile.objects.get_or_create(user=self.user)         

    def test_post_post(self):
        # Create a post using a POST request
        response = self.client.post(reverse('home'), {'content': 'Test post'})
        self.assertEqual(response.status_code, 302)  # Expect a redirect after posting
        
        # Check if the post was created in the database
        self.assertEqual(Post.objects.count(), 1)

        # Verify the post content
        post = Post.objects.first()
        self.assertEqual(post.content, 'Test post')

    def test_post_invalid_post(self):
        # Attempt to create an invalid post (empty content)
        response = self.client.post(reverse('home'), {'content': ''})
        self.assertEqual(response.status_code, 200)  # Expect a 200 response (form validation failed)

        # Check if the post was not created in the database
        self.assertEqual(Post.objects.count(), 0)

    def test_post_post_form(self):
        # Verify that the form used in the view is an instance of PostForm
        response = self.client.get(reverse('home'))
        self.assertIsInstance(response.context['form'], PostForm)
    
    def test_post_with_image(self):
        response = self.client.post(reverse('home'), {
            'content': 'Test post',
            'image': {'image': SimpleUploadedFile('../static/default.png', b'file_content')}
        })
        self.assertEqual(response.status_code, 302)
        post = Post.objects.first()
        self.assertIsNotNone(post)
        self.assertIsNotNone(post.image)
        
    def test_post_with_video(self):
        response = self.client.post(reverse('home'), {
            'content': 'Test post',
            'image': {'image': SimpleUploadedFile('../static/test-video.mp4', b'file_content')}
        })
        self.assertEqual(response.status_code, 302)
        post = Post.objects.first()
        self.assertIsNotNone(post)
        self.assertIsNotNone(post.image)

    def test_delete_post_as_poster(self):
        new_post = Post.objects.create(user=self.user,content='test post')
        post_id = new_post.id
        response = self.client.post(reverse('delete_post'),  {'post_id': post_id}) 
        post_count = Post.objects.filter(id=post_id).count()
        self.assertEquals(post_count, 0)
    
    def test_delete_post_not_as_poster(self):
        new_post = Post.objects.create(user=self.user,content='test post')
        post_id = new_post.id
        self.client.logout()
        user1 = User.objects.create_user(username='testuser1', password='password')
        Profile.objects.get_or_create(user=user1)
        self.client.login(username='testuser1', password='password')
        response = self.client.post(reverse('delete_post'), {'post_id': post_id}) 
        post_count = Post.objects.filter(id=post_id).count()
        self.assertEquals(post_count, 1)
        redirected = self.client.get(response.url)
        self.assertContains(redirected, 'You may not delete this post')
   
    def test_post_added_to_profile(self):
        #create a second user
        user2 = User.objects.create_user(username='testuser2', password='password')
        otherId = user2.id
        #make a post from first user
        self.client.post(reverse('home'), {'content': 'Post on profile'})
        #assert post is shown on user's profile
        profile = self.client.get(reverse('profile'))
        self.assertContains(profile, 'Post on profile')
        #assert post is NOT shown on another user's profile
        otherProfile = self.client.get(reverse('guest',kwargs = {'user_id': otherId}))
        self.assertNotContains(otherProfile, 'Post on profile')
    
    def test_post_with_new_hashtag_creates_new_hashtage_and_instance_entities(self):
        count = Hashtag.objects.count()
        self.client.post(reverse('home'), {'content': '#test'})
        self.assertEqual(count + 1, Hashtag.objects.count())
        post = self.user.post_set.first()
        hashtag = Hashtag.objects.get(content='test')
        self.assertTrue(HashtagInstance.objects.filter(post=post, hashtag=hashtag).exists())
    
    def test_post_with_existing_hashtag_does_not_create_new_hashtag_entity(self):
        self.client.post(reverse('home'), {'content': '#test'})
        count = Hashtag.objects.filter(content='test').count()
        self.client.post(reverse('home'), {'content': '#test'})
        self.assertEqual(count, Hashtag.objects.filter(content='test').count())
    
    def test_filtering_posts_on_hashtag_excludes_entities_without_selection(self):
        hashtag = Hashtag.objects.create(content='test')
        tagged = Post.objects.create(user=self.user, content='#test')
        HashtagInstance.objects.create(post=tagged, hashtag=hashtag)
        untagged = Post.objects.create(user=self.user, content='test')
        response = self.client.get(reverse('hashtag_search', args=['test']), follow=True)
        posts = list(map(lambda carrier: carrier.payload, filter(lambda carrier: carrier.is_post, response.context['posts'])))
        self.assertIn(tagged, posts)
        self.assertNotIn(untagged, posts)
        self.assertContains(response, 'Showing posts about #test')
    
    def test_frequently_observed_topics_are_identified_as_trends(self):
        for _ in range(settings.TRENDING_THRESHOLD + 1):
            self.client.post(reverse('home'), {'content': '#test'})
        response = self.client.get(reverse('trends'))
        self.assertContains(response, '#test')


    def test_only_appropriate_content_shown(self):        
        self.appropriate_post = Post.objects.create(user=self.user, content="This is an appropriate post.")
        self.offensive_post = Post.objects.create(user=self.user, content="This is an offensive post.", is_offensive=True)

        self.user.profile.allows_offensive = False
        self.user.profile.save()

        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "This is an offensive post.")
        self.assertContains(response, "This is an appropriate post.")

    def test_process_post_form_offensive_content(self):
        self.appropriate_post = Post.objects.create(user=self.user, content="This is an appropriate post.")
        self.offensive_post = Post.objects.create(user=self.user, content="This is an offensive post.", is_offensive=True)
        self.user.profile.allows_offensive = True
        self.user.profile.save()

        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This is an offensive post.")
        self.assertContains(response, "This is an appropriate post.")
    
    def test_anon_post(self):
        response = self.client.post(reverse('home'), {'content': 'This is an anonymous post', 'is_anonymous': True})
        self.assertEqual(response.status_code, 302)  # Expect a redirect after posting
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.content, 'This is an anonymous post')

class CommentTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.post = Post.objects.create(user=self.user, content='Parent Post')

        try:
            self.profile = self.user.profile  # Try to access the profile
        except ObjectDoesNotExist:
            # Handle the case where the profile does not exist/ create a profile
            self.profile, created = Profile.objects.get_or_create(user=self.user)
    
    def test_add_comment(self):
        Profile.objects.get_or_create(user=self.user)
        response = self.client.post(reverse('comment', args=[self.post.id]), {'content': 'Test comment'})
        self.assertEqual(response.status_code, 302)  #testing that we get redirected
        self.assertEqual(self.post.replies.count(), 1) #testing that we have 1 reply in the database
        comment = self.post.replies.first()
        self.assertEqual(comment.content, 'Test comment') #testing the content of the comment
        response = self.client.get(reverse('home'))
        self.assertContains(response, f"Replied to {self.user.username}'s post:")

    def test_invalid_comment(self):
        response = self.client.post(reverse('comment', args=[self.post.id]), {'content': ''})
        self.assertEqual(response.status_code, 200) #form validation fail
        self.assertEqual(self.post.replies.count(), 0) #testing that we have 0 reply in the database

    def test_comment_form(self):
        response = self.client.get(reverse('comment', args=[self.post.id]))
        self.assertIsInstance(response.context['form'], PostForm)

    def test_comment_with_image(self):
        imageComent={"image": SimpleUploadedFile("../static/default.jpg", b"file_content")}
        response = self.client.post(reverse('comment', args=[self.post.id]), {
            'content': 'Test comment with image',
            'image': imageComent,
        })
        self.assertEqual(response.status_code, 302) #testing that we get redirected
        self.assertEqual(self.post.replies.count(), 1) #testing that we have 1 reply in the database
        comment = self.post.replies.first()
        self.assertEqual(comment.content, 'Test comment with image')
        self.assertIsNotNone(comment.image) #testing the content of the coment

    def test_only_appropriate_comments_shown(self):
        self.parentPost = Post.objects.create(user=self.user, content="This is a test post.")
        self.appropriate_comment = Post.objects.create(user=self.user, content="This is an appropriate comment.", parent_post=self.parentPost)
        self.offensive_comment = Post.objects.create(user=self.user, content="This is an offensive comment.", parent_post=self.parentPost, is_offensive=True)
        self.user.profile.allows_offensive = False
        self.user.profile.save()

        url = reverse('comment', kwargs={'post_id': self.parentPost.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "This is an offensive comment.")
        self.assertContains(response, "This is an appropriate comment.")

    def test_inappropriate_comments_shown(self):
        self.parentPost = Post.objects.create(user=self.user, content="This is a test post.")
        self.appropriate_comment = Post.objects.create(user=self.user, content="This is an appropriate comment.", parent_post=self.parentPost)
        self.offensive_comment = Post.objects.create(user=self.user, content="This is an offensive comment.", parent_post=self.parentPost, is_offensive=True)
        self.user.profile.allows_offensive = True
        self.user.profile.save()

        url = reverse('comment', kwargs={'post_id': self.parentPost.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This is an offensive comment.")
        self.assertContains(response, "This is an appropriate comment.")

    def test_only_appropriate_comments_shown_inappropriate_parent_post(self):
        self.parentPost = Post.objects.create(user=self.user, content="This is a test post.", is_offensive=True)
        self.appropriate_comment = Post.objects.create(user=self.user, content="This is an appropriate comment.", parent_post=self.parentPost)
        self.offensive_comment = Post.objects.create(user=self.user, content="This is an offensive comment.", parent_post=self.parentPost, is_offensive=True)
        self.user.profile.allows_offensive = False
        self.user.profile.save()

        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "This is a test post.")
        self.assertNotContains(response, "This is an offensive comment.")
        self.assertNotContains(response, "This is an appropriate comment.")

    def test_inappropriate_comments_shown_inappropriate_parent_post(self):
        self.parentPost = Post.objects.create(user=self.user, content="This is a test post.", is_offensive=True)
        self.appropriate_comment = Post.objects.create(user=self.user, content="This is an appropriate comment.", parent_post=self.parentPost)
        self.offensive_comment = Post.objects.create(user=self.user, content="This is an offensive comment.", parent_post=self.parentPost, is_offensive=True)
        self.user.profile.allows_offensive = True
        self.user.profile.save()

        url = reverse('comment', kwargs={'post_id': self.parentPost.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This is a test post.")
        self.assertContains(response, "This is an offensive comment.")
        self.assertContains(response, "This is an appropriate comment.")

class LikeAndDislikeTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.other_user = User.objects.create_user(username='otheruser', password='password')
        self.post = Post.objects.create(user=self.other_user, content='Test post')
        self.client.login(username='testuser', password='password')
    
    def test_like_post(self):
        response = self.client.post(reverse('like', args=[self.post.id]))
        likes = PostLike.objects.all()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, likes.count())
        self.assertEqual(1, self.post.get_number_likes())
        self.assertEqual(0, self.post.get_number_dislikes())
        self.assertFalse(self.post.is_likeable_by(self.user))
        self.assertTrue(self.post.is_dislikeable_by(self.user))

    def test_like_post_with_previous_dislike_deletes_dislike(self):
        PostDislike.objects.create(disliker=self.user, post=self.post)
        response = self.client.post(reverse('like', args=[self.post.id]))
        likes = PostLike.objects.all()
        dislikes = PostDislike.objects.all()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, likes.count())
        self.assertEqual(0, dislikes.count())
    
    def test_like_post_with_already_liked_is_removed(self): # changed to is_removed instead of is_error
        PostLike.objects.create(liker=self.user, post=self.post)
        response = self.client.post(reverse('like', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(0, self.post.get_number_likes())
        self.assertEqual(0, self.post.get_number_dislikes())
        self.assertTrue(self.post.is_likeable_by(self.user))
        self.assertTrue(self.post.is_dislikeable_by(self.user))
    
    def test_dislike_post(self):
        response = self.client.post(reverse('dislike', args=[self.post.id]))
        dislikes = PostDislike.objects.all()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, dislikes.count())
        self.assertEqual(0, self.post.get_number_likes())
        self.assertEqual(1, self.post.get_number_dislikes())
        self.assertTrue(self.post.is_likeable_by(self.user))
        self.assertFalse(self.post.is_dislikeable_by(self.user))
    
    def test_dislike_post_with_previous_like_deletes_like(self):
        PostLike.objects.create(liker=self.user, post=self.post)
        response = self.client.post(reverse('dislike', args=[self.post.id]))
        likes = PostLike.objects.all()
        dislikes = PostDislike.objects.all()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(0, likes.count())
        self.assertEqual(1, dislikes.count())
    
    def test_dislike_post_with_already_disliked_is_removed(self): # changed to is_removed instead of is_error
        PostDislike.objects.create(disliker=self.user, post=self.post)
        response = self.client.post(reverse('dislike', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(0, self.post.get_number_likes())
        self.assertEqual(0, self.post.get_number_dislikes())
        self.assertTrue(self.post.is_likeable_by(self.user))
        self.assertTrue(self.post.is_dislikeable_by(self.user))

class RepostTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.other_user = User.objects.create_user(username='otheruser', password='password')
        self.post = Post.objects.create(user=self.other_user, content='Test post')
        self.client.login(username='testuser', password='password')

    def test_repost_post(self):
        response = self.client.post(reverse('repost', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.status_code, 200)  
        self.assertEqual(Repost.objects.count(), 1) # Check that repost was created in database

        repost = Repost.objects.first()
        self.assertEqual(repost.post, self.post)
        self.assertEqual(repost.user, self.user)

    def test_repost_unauthenticated(self):
        self.client.logout()
        response = self.client.post(reverse('repost', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.status_code, 302)  # redirect to login
        self.assertEqual(Repost.objects.count(), 0)  # repost not created in the database

    def test_reposting_own_post(self):
        self.post = Post.objects.create(user=self.user, content='Test post')
        response = self.client.post(reverse('repost', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.status_code, 200)  
        self.assertEqual(Repost.objects.count(), 1)  # Check that repost was created in the database
        response = self.client.get(reverse('profile'))
        self.assertContains(response, 'Test post', count=1)

class ReportTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.post = Post.objects.create(user=self.user, content='testpost')
    
    def test_report_post(self):
        reports = PostReport.objects.all()
        counts = reports.count()
        response = self.client.post(reverse('report', args=[self.post.id]), {'category': 0})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(counts+1, reports.count())

class PinTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.post = Post.objects.create(user=self.user, content='Parent Post')
        self.post2 = Post.objects.create(user=self.user, content='Second Post')
        self.post3 = Post.objects.create(user=self.user, content='Third Post')
        self.post4 = Post.objects.create(user=self.user, content='Fourth Post')
        
        
        try:
            self.profile = self.user.profile  # Try to access the profile
        except ObjectDoesNotExist:
            # Handle the case where the profile does not exist/ create a profile
            self.profile, created = Profile.objects.get_or_create(user=self.user)          

    
    
    def test_pin_post(self):
        response = self.client.post(reverse('pin', args=[self.post.id]))
        self.assertEqual(response.status_code, 302)
        pins = PostPin.objects.all()
        self.assertEqual(1, pins.count())
       
     
    
    def test_unpin_post(self):
        #pinned the post before unpinning it
        self.postpin = PostPin.objects.create(pinner=self.user, post=self.post)
        #check if post is pinned
        pins=PostPin.objects.all()
        self.assertEqual(1, pins.count())
        #unpin post
        response = self.client.post(reverse('unpin', args=[self.post.id]))
        self.assertEqual(response.status_code, 302)
        pins = PostPin.objects.all()
        self.assertEqual(0, pins.count())
       
       
    def test_pin_post_limit(self):
       #pinned the post before unpinning it
        self.postpin = PostPin.objects.create(pinner=self.user, post=self.post)
        self.postpin2 = PostPin.objects.create(pinner=self.user, post=self.post2)
        self.postpin3 = PostPin.objects.create(pinner=self.user, post=self.post3)
        pins=PostPin.objects.all()
        self.assertEqual(3, pins.count())

        #only three posts can be pinned
        response = self.client.post(reverse('pin', args=[self.post4.id]))
        self.assertEqual(response.status_code, 302)
        pins = PostPin.objects.all()
        self.assertEqual(3, pins.count())

class EditPostTestCase(TestCase):

    def setUp(self):
        self.original_text = "unedited content"
        self.edited_text = "edited content"
        self.user1 = User.objects.create_user(username='testuser1', password='password')
        self.user2 = User.objects.create_user(username='testuser2', password='password')
        self.post1 = Post.objects.create(user = self.user1, content = self.original_text)
        self.pid = self.post1.id
        self.post2 = Post.objects.create(user = self.user2, content = self.original_text)
        self.client.login(username='testuser1', password='password')

    def test_edit_post_as_poster_authenticated(self):
        self.client.post(reverse('edit_post',args=[self.post1.id]), {'content': self.edited_text})
        post = Post.objects.get(id = self.pid)
        self.assertEquals(post.content, self.edited_text)
        self.assertTrue(post.is_edited)

    def test_edit_post_not_as_poster_authenticated(self):
        response = self.client.post(reverse('edit_post',args=[self.post2.id]), {'content': self.edited_text})
        self.assertEqual(response.status_code, 401)
        self.assertEquals(self.post2.content, self.original_text)
        self.assertFalse(self.post2.is_edited)
        
    def test_edit_post_unauthenticated(self):
        self.client.logout() 
        response = self.client.get(reverse('edit_post', args=[self.post2.id]))
        self.assertEqual(response.status_code, 302)        
        response = self.client.post(reverse('edit_post',args=[self.post2.id]), {'content': self.edited_text})
        self.assertEqual(response.status_code, 302)  
        self.assertEquals(self.post2.content, self.original_text)
        self.assertFalse(self.post2.is_edited)
        
        
class ProfilePostCreationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

    def test_create_post_from_profile(self):
        post_content = 'This is a test post from profile'
        response = self.client.post(reverse('profile'), {
            'content': post_content,
        }, follow=True)

        self.assertRedirects(response, reverse('profile'))

        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.content, post_content)
        self.assertEqual(post.user, self.user)

class ContentModerationToggleTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test')
        self.client.login(username='test', password='test')
    
    def test_turning_content_moderation_on_with_offensive_content_hides_that_content_when_user_indicated_not_to_delete_it(self):
        Profile.objects.create(user=self.user, allows_offensive=True)
        offensive_post = Post.objects.create(content='test', user=self.user, is_offensive=True)
        self.client.post(reverse('nlp_toggle'), {'allows_offensive': False, "delete_offensive": False})
        response = self.client.get(reverse('home'))
        posts = map(lambda carrier: carrier.payload, filter(lambda carrier: carrier.is_post, response.context['posts']))
        self.assertIn(offensive_post, Post.objects.all())
        self.assertNotIn(offensive_post, posts)
    
    def test_turning_content_moderation_on_with_offensive_content_deletes_that_content_permanently_when_user_indcated_to_delete_it(self):
        Profile.objects.create(user=self.user, allows_offensive=True)
        offensive_post = Post.objects.create(content='test', user=self.user, is_offensive=True)
        self.client.post(reverse('nlp_toggle'), {'allows_offensive': False, "delete_offensive": True})
        self.assertNotIn(offensive_post, Post.objects.all())
    
    def test_turning_content_moderation_on_with_offensive_content_displays_that_content(self):
        Profile.objects.create(user=self.user, allows_offensive=False)
        offensive_post = Post.objects.create(content='test', user=self.user, is_offensive=True)
        self.client.post(reverse('nlp_toggle'), {'allows_offensive': True, "delete_offensive": False})
        response = self.client.get(reverse('home'))
        posts = map(lambda carrier: carrier.payload, filter(lambda carrier: carrier.is_post, response.context['posts']))
        self.assertIn(offensive_post, posts)

