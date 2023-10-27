from django.test import TestCase 
from django.urls import reverse 

class Error404Test(TestCase):
    def test_404_page(self):
        response = self.client.get('/abc/') #random path which leads to a 404 error
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

class Error500Test(TestCase):
    def test_500_page(self):
        self.client.raise_request_exception = False
        response = self.client.get(reverse('error_500'))
        self.assertEqual(response.status_code, 500)
        self.assertTrue(
            'ERROR 500'
            in response.content.decode('utf8'))