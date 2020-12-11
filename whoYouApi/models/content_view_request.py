"""Database whoYou ContentViewRequest module"""
from django.db import models

class ContentViewRequest(models.Model):
    """Database whoYou ContentViewRequest Model"""
    requester = models.ForeignKey("WhoYouUser", on_delete=models.CASCADE)
    content = models.ForeignKey("Content", on_delete=models.CASCADE)
    is_approved = models.BinaryField()
    creation_time = models.DateTimeField()
    