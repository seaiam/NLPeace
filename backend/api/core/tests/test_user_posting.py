from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User 
from core.models.models import  Profile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.utils import IntegrityError
from core.models.models import Post, PostDislike, PostLike, PostReport,PostPin
from core.forms.posting_forms import PostForm
from core.models.models import Repost
from django.core.exceptions import ObjectDoesNotExist

class PostTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        
        try:
            self.profile = self.user.profile  # Try to access the profile
        except ObjectDoesNotExist:
            # Handle the case where the profile does not exist/ create a profile
            self.profile = Profile.objects.create(user=self.user)          

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
        Profile.objects.create(user=user1)
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
    

class CommentTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.post = Post.objects.create(user=self.user, content='Parent Post')
    
    def test_add_comment(self):
        response = self.client.post(reverse('comment', args=[self.post.id]), {'content': 'Test comment'})
        self.assertEqual(response.status_code, 302)  #testing that we get redirected
        self.assertEqual(self.post.replies.count(), 1) #testing that we have 1 reply in the database
        comment = self.post.replies.first()
        self.assertEqual(comment.content, 'Test comment') #testing the content of the comment

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

class LikeAndDislikeTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.other_user = User.objects.create_user(username='otheruser', password='password')
        self.post = Post.objects.create(user=self.other_user, content='Test post')
        self.client.login(username='testuser', password='password')
    
    def test_like_post(self):
        response = self.client.get(reverse('like', args=[self.post.id]))
        likes = PostLike.objects.all()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(1, likes.count())
        self.assertEqual(1, self.post.get_number_likes())
        self.assertEqual(0, self.post.get_number_dislikes())
        self.assertFalse(self.post.is_likeable_by(self.user))
        self.assertTrue(self.post.is_dislikeable_by(self.user))

    def test_like_post_with_previous_dislike_deletes_dislike(self):
        PostDislike.objects.create(disliker=self.user, post=self.post)
        response = self.client.get(reverse('like', args=[self.post.id]))
        likes = PostLike.objects.all()
        dislikes = PostDislike.objects.all()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(1, likes.count())
        self.assertEqual(0, dislikes.count())
    
    def test_like_post_with_already_liked_is_error(self):
        PostLike.objects.create(liker=self.user, post=self.post)
        self.assertRaises(IntegrityError, lambda: self.client.get(reverse('like', args=[self.post.id]),))
    
    def test_dislike_post(self):
        response = self.client.get(reverse('dislike', args=[self.post.id]))
        dislikes = PostDislike.objects.all()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(1, dislikes.count())
        self.assertEqual(0, self.post.get_number_likes())
        self.assertEqual(1, self.post.get_number_dislikes())
        self.assertTrue(self.post.is_likeable_by(self.user))
        self.assertFalse(self.post.is_dislikeable_by(self.user))
    
    def test_dislike_post_with_previous_like_deletes_like(self):
        PostLike.objects.create(liker=self.user, post=self.post)
        response = self.client.get(reverse('dislike', args=[self.post.id]))
        likes = PostLike.objects.all()
        dislikes = PostDislike.objects.all()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(0, likes.count())
        self.assertEqual(1, dislikes.count())
    
    def test_dislike_post_with_already_disliked_is_error(self):
        PostDislike.objects.create(disliker=self.user, post=self.post)
        self.assertRaises(IntegrityError, lambda: self.client.get(reverse('dislike', args=[self.post.id])))

class RepostTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.other_user = User.objects.create_user(username='otheruser', password='password')
        self.post = Post.objects.create(user=self.other_user, content='Test post')
        self.client.login(username='testuser', password='password')

    def test_repost_post(self):
        response = self.client.post(reverse('repost', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.status_code, 302)  # Expect a redirect after reposting
        self.assertEqual(Repost.objects.count(), 1) # Check that repost was created in database

        repost = Repost.objects.first()
        self.assertEqual(repost.post, self.post)
        self.assertEqual(repost.user, self.user)

    def test_repost_unauthenticated(self):
        self.client.logout()
        response = self.client.post(reverse('repost', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.status_code, 302)  # redirect to login
        self.assertEqual(Repost.objects.count(), 0)  # repost not created in the database

class ReportTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.post = Post.objects.create(user=self.user, content='testpost')
    
    def test_report_post(self):
        response = self.client.post(reverse('report', args=[self.post.id]), {'category': 0})
        reports = PostReport.objects.all()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(1, reports.count())

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
            self.profile = Profile.objects.create(user=self.user)          

    
    
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


