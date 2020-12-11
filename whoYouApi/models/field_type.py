"""Database whoYou FieldType module"""
from django.db import models

class FieldType(models.Model):
    """Database whoYou FieldType Model"""
    name = models.CharField(max_length=500)
    isAddressRelated = models.BooleanField()
