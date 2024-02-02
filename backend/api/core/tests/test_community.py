from django.test import TestCase
from django.urls import reverse
from core.models.community_models import Community
from core.models.profile_models import User
from core.forms.community_forms import CommunityForm

class CommunityTestCase(TestCase):
    def setUp(self):
        # Creating test user and loging in
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

    def test_create_community(self):
        # creating comunity
        response = self.client.post(reverse('create_community'), {
            'name': 'Test Community',
            'description': 'A test community',
            'is_private': True
        })
        
        # check that we get redirected after successfull creation of comunity
        self.assertEqual(response.status_code, 302)

        # check that comunity gets added in the db
        self.assertEqual(Community.objects.count(), 1)
        
        # check community details 
        community = Community.objects.first()
        self.assertEqual(community.name, 'Test Community')
        self.assertEqual(community.admin, self.user)
        self.assertTrue(community.is_private)
        self.assertIsNotNone(community.pic)

    def test_edit_community(self):
        community = Community.objects.create(name='Test Community', admin=self.user, is_private=True)
        response = self.client.post(reverse('community_detail', kwargs={'community_id': community.id}), {
            'name': 'Updated Community',
            'description': 'Updated description',
            'is_private': False,
        })
        
        # check that we get redirected after successfull editing of comunity
        self.assertEqual(response.status_code, 302)
        
        # check that community details changed
        community.refresh_from_db()
        self.assertEqual(community.name, 'Updated Community')
        self.assertEqual(community.description, 'Updated description')
        self.assertFalse(community.is_private)

    def test_community_form_validation(self):
        # try to create community without entering a name 
        form_data = {'name': '', 'is_private': True}
        form = CommunityForm(data=form_data)
        # check that form doesnt valid
        self.assertFalse(form.is_valid())

    # try to edit community if user is NOT the admin of the community
    def test_edit_community_NonAdmin(self):
        community = Community.objects.create(name='Test Community', admin=self.user, is_private=True)
        
        # Create another user and try to edit community 
        other_user = User.objects.create_user(username='otheruser', password='password')
        self.client.login(username='otheruser', password='password')
        
        response = self.client.post(reverse('community_detail', kwargs={'community_id': community.id}), {
            'name': 'Unauthorized Update',
        })
        
        self.assertNotEqual(response.status_code, 200)
        
        # check that community name not changed
        community.refresh_from_db()
        self.assertNotEqual(community.name, 'Unauthorized Update')
