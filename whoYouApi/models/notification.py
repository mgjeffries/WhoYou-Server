"""Database whoYou notification module"""
from django.db import models

class Notification(models.Model):
    """Database whoYou notification Model"""
    target_user = models.ForeignKey("WhoYouUser", on_delete=models.CASCADE)
    content = models.CharField(max_length=500)
    # TODO: add a property to tell if the user has dismissed the notification
