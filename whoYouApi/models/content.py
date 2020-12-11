"""Database whoYou content module"""
from django.db import models

class Content(models.Model):
    """Database whoYou content Model"""
    field_type = models.ForeignKey("FieldType", on_delete=models.CASCADE)
    value = models.CharField(max_length=200)
    owner = models.ForeignKey("WhoYouUser", on_delete=models.CASCADE)
    verification_time = models.DateTimeField()
    