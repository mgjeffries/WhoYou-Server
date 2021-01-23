"""Database whoYou user module"""
from whoYouApi.models import Content, FieldType
from django.db import models
from django.contrib.auth.models import User


class WhoYouUser(models.Model):
    """Database whoYou user Model"""
    profile_image_path = models.ImageField(upload_to='profileImage', height_field=None, width_field=None, null=True, max_length=None)
    cover_image_path = models.CharField(max_length=100)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


    @property
    def name(self):
        name_field_type = FieldType.objects.get(name="name")
        name_content = Content.objects.get(owner=self, field_type=name_field_type)
        # NOTE a users's name is publicly available through this property
        return name_content.value
    