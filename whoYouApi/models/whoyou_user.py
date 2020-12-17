"""Database whoYou user module"""
from django.db import models
from django.contrib.auth.models import User

class WhoYouUser(models.Model):
    """Database whoYou user Model"""
    profile_image_path = models.CharField(max_length=100)
    cover_image_path = models.CharField(max_length=100)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
