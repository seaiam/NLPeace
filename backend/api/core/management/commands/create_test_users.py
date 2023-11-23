from django.core.management.base import BaseCommand
from core.factories import UserFactory

class Command(BaseCommand):
    help = 'Create test users for development'

    def handle(self, *args, **options):
        for i in range(5):
            user = UserFactory()
            print(f"created user{i} with username: {user.username} and email {user.email}")