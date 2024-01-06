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
        self.email2 = 'testuser2@email.com'
        self.username2 = 'testuser2'
        self.user = User.objects.create_user(username=self.username2, email=self.email2, password=self.password)


    def test_search_existing_user(self):
        self.client.login(username=self.username, password=self.password)
        search_query={'search': self.username2}
        response = self.client.post(reverse('search_user'), search_query,follow=True)
         
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.username2)
        
    def test_search_invalid_user(self):    
        self.client.login(username=self.username, password=self.password)
        search_query = {'search':'nonexistentuser'}
        response = self.client.post(reverse('search_user'), search_query,follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('profile'))
