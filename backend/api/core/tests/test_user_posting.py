from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from core.models.models import Post
from core.forms.posting_forms import PostForm

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

class RepostTestCase(TestCase):
    def setUp(self):
        # Create two users and log in one of them
        self.user1 = User.objects.create_user(username='testuser1', password='password1')
        self.user2 = User.objects.create_user(username='testuser2', password='password2')
        self.client.login(username='testuser2', password='password2')

        # Create an original post by user1
        self.original_post = Post.objects.create(user=self.user1, content='Original post content')

    def test_repost_post(self):
        # Repost the original post u
        response = self.client.post(reverse('repost', args=[self.original_post.id]))
        self.assertEqual(response.status_code, 302)  # redirect after reposting

        self.assertEqual(Post.objects.count(), 2)  # Check that a new post was created in the database

        # Verify the content of the repost
        repost = Post.objects.exclude(id=self.original_post.id).first()
        expected_content = f"Reposted from @{self.original_post.user.username}: {self.original_post.content}"
        self.assertEqual(repost.content, expected_content)
        self.assertEqual(repost.user, self.user2)  # Verify that the author of the repost is actually user2
