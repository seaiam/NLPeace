from django.contrib.admin import AdminSite
from django.test import TestCase
from core.admin import UserAdmin
from core.models.profile_models import Notifications, ProfileWarning, User
from unittest.mock import Mock

def mock_formset(instances):
    return Mock(deleted_objects=[], save=lambda commit=False: instances, save_m2m=lambda: None)

class ProfileWarningTestCase(TestCase):

    def test_issue_profile_warning(self):
        admin = User.objects.create_superuser(username='admin', password='admin')
        user = User.objects.create_user(username='user', password='user')
        request = Mock(user=admin)
        warning = ProfileWarning(offender=user)
        userAdmin = UserAdmin(User, AdminSite())
        userAdmin.save_formset(request, None, mock_formset([warning]), None)
        self.assertIn(warning, ProfileWarning.objects.filter(offender=user))
        self.assertEqual(admin, ProfileWarning.objects.filter(offender=user).first().issuer)
        self.assertEqual(1, Notifications.objects.filter(user=user).count())