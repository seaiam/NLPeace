from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User 

class GiphySearchTestCase(TestCase):

    def test_search_giphy_not_loggedin(self):
        query = 'funny'
        limit = 5
        url = f"{reverse('search_giphy')}?query={query}&limit={limit}"
        response = self.client.get(url)
        # check that user gets redirected to login page
        self.assertEqual(response.status_code, 302)

 
    def test_search_giphy_loggedin(self):
        # logging test user in
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

        query = 'funny'
        limit = 5
        url = f"{reverse('search_giphy')}?query={query}&limit={limit}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
