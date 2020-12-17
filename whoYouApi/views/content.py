""" View module for handling requests about content"""
from whoYouApi.models.field_type import FieldType
from rest_framework.viewsets import ViewSet
from whoYouApi.models import WhoYouUser, Content, ContentViewRequest
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
            try: 
                requester = WhoYouUser.objects.get(user=request.auth.user)
            except AttributeError:
                requester = None
            censored_content = censorContent(content_object, requester)
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
        requester = WhoYouUser.objects.get(user=request.auth.user)
        censoredContent = censorContent(content, requester)
        serializer = ContentSerializer(censoredContent, context={'request': request})
        return Response(serializer.data)
        
    def update(self, request, pk=None):
        """ Handle an PUT request for content
        Returns:
            Response code
        """

        content = Content.objects.get(pk=pk)

        requester = WhoYouUser.objects.get(user=request.auth.user)
        if requester != content.owner:
            return Response({"message": "Permission denied"}, status=status.HTTP_401_UNAUTHORIZED)

        content.owner = requester
        field_type = FieldType.objects.get(pk=request.data["field_type"])
        content.field_type = field_type
        content.value = request.data["value"]
        content.is_public = request.data["is_public"] == "true"
        content.verification_time = timezone.now()

        content.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """ Handle an DELETE request for content
        Returns:
            Response code
        """
        try:
            content = Content.objects.get(pk=pk)

            requesting_user = WhoYouUser.objects.get(user=request.auth.user)
            if requesting_user == content.owner:
                content.delete()
                return Response({}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"message": "Permission denied"}, status=status.HTTP_401_UNAUTHORIZED)
                
        except Content.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
    

def censorContent(content_object, requestingUser):
    isRequesterContentOwner = requestingUser == content_object.owner
    isRequesterApprovedToView = False
    try:
        matchingViewRequest = ContentViewRequest.objects.get(content=content_object, requester=requestingUser)
        isRequesterApprovedToView = matchingViewRequest.is_approved
    except ContentViewRequest.DoesNotExist:
        pass
    if content_object.is_public or isRequesterContentOwner or isRequesterApprovedToView:
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