from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.utils import IntegrityError
from core.models.models import Post, PostDislike, PostLike, PostReport
from core.forms.posting_forms import PostForm
from core.models.models import Repost

class PostTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

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
        response = self.client.post(reverse('like'), {'post': self.post.id})
        likes = PostLike.objects.all()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(1, likes.count())

    def test_like_post_with_previous_dislike_deletes_dislike(self):
        PostDislike.objects.create(disliker=self.user, post=self.post)
        response = self.client.post(reverse('like'), {'post': self.post.id})
        likes = PostLike.objects.all()
        dislikes = PostDislike.objects.all()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(1, likes.count())
        self.assertEqual(0, dislikes.count())
    
    def test_like_post_with_already_liked_is_error(self):
        PostLike.objects.create(liker=self.user, post=self.post)
        self.assertRaises(IntegrityError, lambda: self.client.post(reverse('like'), {'post': self.post.id}))
    
    def test_dislike_post(self):
        response = self.client.post(reverse('dislike'), {'post': self.post.id})
        dislikes = PostDislike.objects.all()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(1, dislikes.count())
    
    def test_dislike_post_with_previous_like_deletes_like(self):
        PostLike.objects.create(liker=self.user, post=self.post)
        response = self.client.post(reverse('dislike'), {'post': self.post.id})
        likes = PostLike.objects.all()
        dislikes = PostDislike.objects.all()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(0, likes.count())
        self.assertEqual(1, dislikes.count())
    
    def test_dislike_post_with_already_disliked_is_error(self):
        PostDislike.objects.create(disliker=self.user, post=self.post)
        self.assertRaises(IntegrityError, lambda: self.client.post(reverse('dislike'), {'post': self.post.id}))

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
        response = self.client.post(reverse('report'), {'post': self.post.id, 'category': 0})
        reports = PostReport.objects.all()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(1, reports.count())

