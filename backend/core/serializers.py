from rest_framework import serializers
from models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['uuid', 'username' 'first_name', 'last_name', 'email', 'last_login', 'date_joined', 'bio', 'pic',
                  'banner']