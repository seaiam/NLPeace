from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from unittest.mock import patch
import json
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.storage.session import SessionStorage

from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from core.models.post_models import *
from core.forms.posting_forms import PostForm
from core.views.services import process_post_form, classify_text

from core.models.post_models import Post

class ChatMonitoringTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.classify_message_url = reverse('classifyMessage')

    def test_valid_post_request(self):
        # Simulate valid POST request
        response = self.client.post(self.classify_message_url, {'message': 'test message'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
    def test_get_request_rejected(self):
        # Test that GET requests are rejected
        response = self.client.get(self.classify_message_url)
        self.assertEqual(response.status_code, 405)


class NLPMonitoringTest(TestCase):
    def test_classify_text(self):
        test_text = "This is a test message."
        response = classify_text(test_text)

        # Confirm response structure
        self.assertIsInstance(response, dict)
        
        # Check for the presence of 'prediction' key
        self.assertIn('prediction', response)
        self.assertIsInstance(response['prediction'], list)

        # Validate the prediction value (assuming it's an integer)
        if response['prediction']:
            self.assertIn(response['prediction'][0], [0, 1, 2])

        # Validate response format and types
        if 'error' in response:
            self.assertIn('status_code', response)
            self.assertIsInstance(response['error'], str)
            self.assertIsInstance(response['status_code'], int)

class PostProcessing(TestCase):
    def setUp(self):
        self.email = 'testuser@email.com'
        self.username = 'testuser'
        self.password = 'testpassword123'
        self.user = User.objects.create_user(username=self.username, email=self.email, password=self.password)
        self.client.login(username=self.username, password=self.password )

    def test_offensive_post(self):
        response = self.client.post(reverse('home'), {'content': 'bitch'}, follow = True)
        self.assertContains(response, 'This post contains offensive language. It will only be showed to users who turn off content filtering.')
        self.assertNotContains(response, 'bitch')
    
    def test_inoffensive_post(self):
        response = self.client.post(reverse('home'), {'content': 'hello world'})
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.content, 'hello world')

class ForeignLanguagePost(TestCase):
    def setUp(self):
        self.email = 'testuser@email.com'
        self.username = 'testuser'
        self.password = 'testpassword123'
        self.user = User.objects.create_user(username=self.username, email=self.email, password=self.password)
        self.client.login(username=self.username, password=self.password )

    def test_offensive_post_in_another_language(self):
        response = self.client.post(reverse('home'), {'content': 'maldita perra'}, follow = True)
        self.assertContains(response, 'This post contains offensive language. It will only be showed to users who turn off content filtering.')
        self.assertNotContains(response, 'maldita perra')
    
    def test_inoffensive_post_in_another_language(self):
        response = self.client.post(reverse('home'), {'content': 'ella una chica hermosa'})
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.content, 'ella una chica hermosa')

    @patch('core.views.services.classify_text')
    def test_poll_choices_creation(self, mock_classify_text):
        mock_classify_text.return_value = {"prediction": [2]}  # Appropriate content

        request = self.factory.post('/home/', self.form_data)
        request.user = self.user
        form = PostForm(data=self.form_data)

        def dummy_get_response(request):
            return None

        middleware = SessionMiddleware(dummy_get_response)
        middleware.process_request(request)
        request.session.save()

        messages = SessionStorage(request)
        setattr(request, '_messages', messages)

        if form.is_valid():
            process_post_form(request, form)
            # Check if the correct number of PollChoice objects are created
            self.assertEqual(PollChoice.objects.count(), self.form_data['poll_choices'])

class ForeignLanguagePost(TestCase):
    def setUp(self):
        self.email = 'testuser@email.com'
        self.username = 'testuser'
        self.password = 'testpassword123'
        self.user = User.objects.create_user(username=self.username, email=self.email, password=self.password)
        self.client.login(username=self.username, password=self.password )

    def test_offensive_post_in_another_language(self):
        response = self.client.post(reverse('home'), {'content': 'maldita perra'}, follow = True)
        self.assertContains(response, 'This post contains offensive language. It will only be showed to users who turn off content filtering.')
        self.assertNotContains(response, 'maldita perra')
    
    def test_inoffensive_post_in_another_language(self):
        response = self.client.post(reverse('home'), {'content': 'ella una chica hermosa'})
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.content, 'ella una chica hermosa')