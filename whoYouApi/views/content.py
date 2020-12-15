""" View module for handling requests about content"""
from whoYouApi.models import field_type
from whoYouApi.models.field_type import FieldType
from rest_framework.viewsets import ViewSet
from whoYouApi.models import WhoYouUser, Content
from django.utils import timezone
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status


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
            censored_content = censorContent(content_object, request.auth.user)
            censored_content_objects.append(censored_content)

        serializer = ContentSerializer(
            censored_content_objects, many=True, context={'request': request}
        )
        return Response(serializer.data)


    def retrieve(self, request, pk=None):
        """Handle GET request for single content instance
        Returns:
            Response JSON serialized content instance
        """
        content = Content.objects.get(pk=pk)
        censoredContent = censorContent(content, request.auth.user)
        serializer = ContentSerializer(content, context={'request': request})
        return Response(serializer.data)
        
    def update(self, request, pk=None):
        """ Handle an PUT request for content
        Returns:
            Response code
        """

        # Find the post being updated based on it's primary key
        content = Content.objects.get(pk=pk)

        #Prevent non-admin users from modifying other user's posts
        requester = WhoYouUser.objects.get(user=request.auth.user)
        if requester != content.owner:
            return Response({"message": "Permission denied"}, status=status.HTTP_401_UNAUTHORIZED)

        # save basic (non-associated) properties
        content.owner = requester
        field_type = FieldType.objects.get(pk=request.data["field_type"])
        content.field_type = field_type
        content.value = request.data["value"]
        content.is_public = request.data["is_public"] == "true"
        content.verification_time = timezone.now()

        # save content object
        content.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)


def censorContent(content_object, requestingUser):
    isRequesterContentOwner = WhoYouUser.objects.get(user=requestingUser) == content_object.owner
    if content_object.is_public or isRequesterContentOwner:
    #TODO: check if the requester has a valid view request for this content
        return content_object
    else:
        content_object.value = "restricted value"
        return content_object

class ContentSerializer(serializers.ModelSerializer):
    """Serializer for Content"""     
    class Meta:
        model = Content
        fields = ( 'id', 'field_type','value', 'owner', 'is_public', 'verification_time')
        depth = 1