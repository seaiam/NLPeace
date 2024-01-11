from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from unittest.mock import patch
import json

from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from core.forms.posting_forms import PostForm
from core.views.services import process_post_form, classify_text


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


class NLPMonitoring(TestCase):
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


