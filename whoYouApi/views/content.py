""" View module for handling requests about content"""
from whoYouApi.models import field_type
from whoYouApi.models.field_type import FieldType
from rest_framework.viewsets import ViewSet
from whoYouApi.models import WhoYouUser, Content
from django.utils import timezone
from rest_framework import serializers
from rest_framework.response import Response


class ContentViewSet(ViewSet):
    """ WhoYou Content """

    def create(self, request):
        """Handle POST operations
        Returns:
            Response -- JSON serialized Content instance
        """
        content_owner = WhoYouUser.objects.get(user=request.auth.user)
        content = Content()
        content.owner = content_owner
    
        field_type = FieldType.objects.get(pk=request.data["field_type"])
        content.field_type = field_type
        content.value = request.data["value"]
        content.is_public = request.data["is_public"] == "true"
        content.verification_time = timezone.now()

        serializer = ContentSerializer(content, context={'request': request})
        return Response(serializer.data)

    def list(self, request):
        """Handle GET requests to Content resource

        Returns:
            Response -- JSON serialized list of Content
        """
        content_objects = Content.objects.all()

        # Filter content based on query parameters
        # e.g.: /content?owner=1
        user_id = self.request.query_params.get('owner', None)
        if user_id is not None:
            content_objects = content_objects.filter(owner=user_id)
        
        # Censor out values that the user shouldn't be able to access
        censored_content_objects = []
        for content_object in content_objects:
            isRequesterContentOwner = WhoYouUser.objects.get(user=request.auth.user) == content_object.owner
            if content_object.is_public or isRequesterContentOwner:
                censored_content_objects.append(content_object)
            #TODO: check if the requester has a valid view request for this content
            else:
                content_object.value = "restricted value"
                censored_content_objects.append(content_object)

        serializer = ContentSerializer(
            content_objects, many=True, context={'request': request}
        )
        return Response(serializer.data)



class ContentSerializer(serializers.ModelSerializer):
    """Serializer for Content"""     
    class Meta:
        model = Content
        fields = ( 'id', 'field_type','value', 'owner', 'is_public', 'verification_time')
        depth = 1