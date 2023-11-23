import factory
from django.contrib.auth.models import User
from faker import Faker

fake = Faker()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.LazyAttribute(lambda user: fake.user_name())
    email = factory.LazyAttribute(lambda user: f"{user.username}@mailinator.com")
    password = factory.PostGenerationMethodCall('set_password', 'NLPeace123')
