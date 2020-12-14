""" View module for handling requests about content"""
from whoYouApi.models.field_type import FieldType
from rest_framework.viewsets import ViewSet
from whoYouApi.models import WhoYouUser, Content
from django.utils import timezone

class ContentViewSet(ViewSet):
    """ WhoYou Content """

    def create(self, request):
        """Handle POST operations
        Returns:
            Response -- JSON serialized post instance
        """
        content_owner = WhoYouUser.objects.get(user=request.auth.user)
        content = Content()
        content.owner = content_owner
    
        field_type = FieldType.objects.get(pk=request.data["field_type"])
        content.field_type = field_type
        content.value = request.data["value"]
        content.is_public = request.data["is_public"] == "true"
        content.verification_time = timezone.now()

