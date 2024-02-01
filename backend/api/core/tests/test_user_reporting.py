from django.test import TestCase
from django.urls import reverse
from core.models.profile_models import User , UserReport

class ReportTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.client.login(username='user1', password='password')
        
    def test_report_user_authenticated(self):
        self.client.login(username='user1', password='password')
        response = self.client.post(reverse('report_user', args=[self.user2.id]), {'reported': self.user2, 'reason': 0})
        reports = UserReport.objects.all()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(1, reports.count())
    
    def test_report_user_unauthenticated(self):
        self.client.logout()
        response = self.client.post(reverse('report_user', args=[self.user2.id]), {'reported': self.user2, 'reason': 0})
        self.assertRedirects(response, '/accounts/login/?next=' + reverse('report_user', args=[self.user2.id]))
