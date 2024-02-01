from django.test import TestCase
from django.contrib.auth.models import User
from core.models.post_models import Post, PostSave
from django.db.utils import IntegrityError
from django.urls import reverse



class PostSaveTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.post = Post.objects.create(user=self.user, content='Test post') # creates a post with content 'Test post' for user created above

    def test_post_save_creation(self):
        post_save = PostSave.objects.create(saver=self.user, post=self.post) # the user saves the post they created above
        self.assertEqual(post_save.saver, self.user) # ensures correct user is associated to the saved post
        self.assertEqual(post_save.post, self.post) # ensures correct post is associated to the saved post

    def test_unique_constraint(self):
        PostSave.objects.create(saver=self.user, post=self.post) # creates a post for self.user, and tries to create another 
        with self.assertRaises(IntegrityError):
            PostSave.objects.create(saver=self.user, post=self.post)  # attemps to create another post, shouldn't work 


class SavePostViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.post = Post.objects.create(user=self.user, content='Test post')
        self.client.login(username='testuser', password='password')

    def test_save_post(self):
        response = self.client.post(reverse('save_post', args=[self.post.id]))
        self.assertEqual(response.status_code, 302)  # expect a redirect after saving
        self.assertEqual(PostSave.objects.count(), 1)

    def test_unsave_post(self):
        PostSave.objects.create(saver=self.user, post=self.post)
        response = self.client.post(reverse('save_post', args=[self.post.id]))
        self.assertEqual(response.status_code, 302)  # expect a redirect after unsaving
        self.assertEqual(PostSave.objects.count(), 0)

