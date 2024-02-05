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

    def test_search_community(self):
        # Create a test community
        community = Community.objects.create(name='Test', admin=self.user, is_private=True)

        # Make a POST request to the search_community view with the search parameter
        response = self.client.post(reverse('search_community'), {'search': 't'})

        # Check if the response contains the community name
        self.assertContains(response, 'Test')

    
    def test_search_community_nonexistent(self):
        

        # Make a POST request to the search_community view with the search parameter
        response = self.client.post(reverse('search_community'), {'search': 'm'})
        self.assertRedirects(response, reverse('create_community'))



class CommunityJoinTest(TestCase):

    def setUp(self):

        self.admin = User.objects.create_user(username = "admin", password = "password")
        self.joiner = User.objects.create_user(username = "joiner", password = "password")
        self.public_community = Community.objects.create(name = "public", admin = self.admin, is_private = False)
        self.private_community = Community.objects.create(name = "private", admin = self.admin)
        self.client.login(username = "joiner", password = "password")
    
    def test_join_public_community(self):

        response = self.client.post(reverse('join_community'), {
            'community_id': self.public_community.id,
            'requester_id': self.joiner.id
        },follow = True)
        
        self.assertContains(response, f"You have joined {self.public_community.name}.")
        self.assertIn(self.joiner, list(self.public_community.members.all()))
    
    def test_join_private_community(self):

        response = self.client.post(reverse('join_community'), {
            'community_id': self.private_community.id,
            'requester_id': self.joiner.id
        },follow = True)
        
        self.assertContains(response, "A join request has been sent.")
        self.assertIn(self.joiner, list(self.private_community.join_requests.all()))

        self.client.logout()
        self.client.login(username = "admin", password = "password")

        response = self.client.post(reverse('accept_decline_join'), {
            'joined_community_id': self.private_community.id,
            'joiner_id': self.joiner.id,
            'action': "accept"
        },follow = True)
        
        self.assertContains(response, "Join request accepted.")
        self.assertIn(self.joiner, list(self.private_community.members.all()))
        self.assertNotIn(self.joiner, list(self.private_community.join_requests.all()))