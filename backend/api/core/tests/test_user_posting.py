from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import Post
from core.forms import PostForm

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