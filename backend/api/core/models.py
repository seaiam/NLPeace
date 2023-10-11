from django.db import models as fields
from django.contrib.auth import models


class User(models.User):
    uuid = fields.UUIDField()
    bio = fields.TextField()
    banner = fields.BinaryField()
    pic = fields.BinaryField()

    def is_bio_updated(self, bio):
        return self.bio != bio

    def is_banner_updated(self, banner):
        return self.banner != banner

    def is_pic_updated(self, pic):
        return self.pic != pic
