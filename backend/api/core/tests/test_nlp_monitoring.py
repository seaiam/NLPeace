from django.test import TestCase, Client
from django.urls import reverse
import json

class ChatMonitoring(TestCase):

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



