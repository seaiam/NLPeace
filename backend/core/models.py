from django.db import models as fields
from django.contrib.auth import models


class User(models.User):
    uuid = fields.UUIDField()
    bio = fields.TextField()
    banner = fields.BinaryField()
    pic = fields.BinaryField()
