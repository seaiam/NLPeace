from django.db import models as fields
from django.contrib.auth import models


class User(models.User):
    bio = fields.TextField(null=True, blank=True)
    banner = fields.ImageField(upload_to='profileBanners/', null=True, blank=True)
    pic = fields.ImageField(upload_to='profilePictures/', null=True, blank=True)

    # def is_bio_updated(self, bio):
    #     return self.bio != bio

    # def is_banner_updated(self, banner):
    #     return self.banner != banner

    # def is_pic_updated(self, pic):
    #     return self.pic != pic
