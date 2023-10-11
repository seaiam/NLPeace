from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class UserLoginTest(TestCase):

    def setUp(self):
        # Create a test user
        self.username = 'testuser'
        self.password = 'testpassword123'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_correct_login(self):
        # Send a POST request to the login view with valid credentials
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': self.password,
        })

        # Check if the user is authenticated
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertRedirects(response, '/home/')

    def test_incorrect_login(self):
        # Send a POST request to the login view with invalid credentials
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': 'wrongpassword',
        })

        # Check if the user is not authenticated
        self.assertFalse(response.wsgi_request.user.is_authenticated)

        # Check if the response is as expected
        self.assertEqual(response.status_code, 200)

