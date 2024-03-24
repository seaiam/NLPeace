from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from time import sleep

from core.models.post_models import Advertisement, AdvertisementTopic, Post
from core.models.profile_models import Profile, ProfileInterest, User


class AdvertisementTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test')
        self.profile = Profile.objects.create(user=self.user)
        for i in range(0, settings.AD_MIX_RATE):
            Post.objects.create(user=self.user, content=str(i))
        self.ad = Advertisement.objects.create(advertiser='test', content='test')
        self.client.login(username='test', password='test')
        settings.AD_SELECTION_STRATEGY = 'constant'
    
    def test_ads_mixed_with_posts(self):
        response = self.client.get(reverse('home'))
        ads = list(filter(lambda carrier: not carrier.is_post, response.context['posts']))
        self.assertEqual(1, len(ads))
    
    def test_hashtags_parsed_as_interests(self):
        self.client.post(reverse('home'), {'content': '#test'})
        self.assertEqual(1, self.profile.profileinterest_set.count())
    
    def test_interests_are_unique_and_timestamps_are_updated_on_duplication(self):
        self.client.post(reverse('home'), {'content': '#test'})
        interest = self.profile.profileinterest_set.get(name='test')
        count = self.profile.profileinterest_set.count()
        created_at = interest.last_expressed
        sleep(1) # Ensure that the second post request cannot be made too quickly after the first.
        self.client.post(reverse('home'), {'content': '#test'})
        interest.refresh_from_db()
        self.assertEqual(count, self.profile.profileinterest_set.count())
        self.assertLess(created_at, interest.last_expressed)
    
    def test_ads_are_filtered_on_user_interests_when_indicated_by_settings(self):
        other_ad = Advertisement.objects.create(advertiser='test', content='other')
        AdvertisementTopic.objects.create(ad=other_ad, name='other')
        AdvertisementTopic.objects.create(ad=self.ad, name='test')
        ProfileInterest.objects.create(profile=self.profile, name='test')
        settings.AD_SELECTION_STRATEGY = 'jaccard'
        response = self.client.get(reverse('home'))
        ads = list(map(lambda carrier: carrier.payload, filter(lambda carrier: not carrier.is_post, response.context['posts'])))
        self.assertIn(self.ad, ads)
        self.assertNotIn(other_ad, ads)
