from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class SearchUserTest(TestCase):
    def setUp(self):
        # Create a test user with email as the login identifier
        self.email = 'testuser@email.com'
        self.username = 'testuser'
        self.password = 'testpassword123'
        self.user = User.objects.create_user(username=self.username, email=self.email, password=self.password)
        # Create another user
        self.email = 'testuser2@email.com'
        self.username = 'testuser2'
        self.password = 'testpassword123'
        self.user = User.objects.create_user(username=self.username, email=self.email, password=self.password)


    def test_search_existing_user(self):
        self.client.login(username='testuser', password='testpassword123')
        search_query={'search':'testuser2'}
        response = self.client.post(reverse('search_user'), search_query,follow=True)
         
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser2')
        
    def test_search_invalid_user(self):
        
        self.client.login(username='testuser', password='testpassword123')
        search_query = {'search':'nonexistentuser'}
        response = self.client.post(reverse('search_user'), search_query,follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('profile'))
