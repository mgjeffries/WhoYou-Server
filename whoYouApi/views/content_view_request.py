""" View module for handling requests about content"""
from whoYouApi.models import content, field_type
from whoYouApi.models.field_type import FieldType
from rest_framework.viewsets import ViewSet
from whoYouApi.models import WhoYouUser, ContentViewRequest, Content
from django.utils import timezone
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q    


class ContentViewRequestViewSet(ViewSet):
    """ WhoYou Content """

    def create(self, request):
        """Handle POST operations
        Returns:
            Response -- JSON serialized ContentViewRequest instance
        """

        content_view_request = ContentViewRequest()
        requester = WhoYouUser.objects.get(user=request.auth.user)
        content_view_request.requester = requester
        requested_content = request.data["content"]
        content = Content.objects.get(pk=requested_content)
        try:
            existingRequest = ContentViewRequest.objects.get(content=requested_content, requester=requester)
            return Response({"reason": "Request already exists"}, status=status.HTTP_400_BAD_REQUEST)
        except ContentViewRequest.DoesNotExist:
            content_view_request.content = content
            content_view_request.is_approved = False
            content_view_request.creation_time = timezone.now()

            content_view_request.save()

            serializer = ContentViewRequestSerializer(content_view_request, context={'request': request})
            return Response(serializer.data)

    def list(self, request):
        """Handle GET requests to contentViewRequest resource

        Returns:
            Response -- JSON serialized list of content view requests
        """
        
        request_author = WhoYouUser.objects.get(user=request.auth.user)
        filteredRequests = ContentViewRequest.objects.filter(Q(content__owner=request_author) | Q(requester=request_author))

        serializer = ContentViewRequestSerializer(
            filteredRequests, many=True, context={'request': request}
        )
        return Response(serializer.data)


    def retrieve(self, request, pk=None):
        """Handle GET request for single contentViewRequest instance
        Returns:
            Response JSON serialized contentViewRequest instance
        """
        requester = WhoYouUser.objects.get(user=request.auth.user)
        contentViewRequest = ContentViewRequest.objects.get(pk=pk)
        if requester == contentViewRequest.requester or requester == contentViewRequest.content.owner:    
            serializer = ContentViewRequestSerializer(contentViewRequest, context={'request': request})
            return Response(serializer.data)
        else:
            return Response({"message": "Permission denied"}, status=status.HTTP_401_UNAUTHORIZED)
        
    def partial_update(self, request, pk=None):
        """ Handle an PATCH request for single contentViewRequest
        Returns:
            Response code
        """
        contentViewRequest = ContentViewRequest.objects.get(pk=pk)

        requester = WhoYouUser.objects.get(user=request.auth.user)
        if requester != contentViewRequest.content.owner:
            return Response({"message": "Permission denied"}, status=status.HTTP_401_UNAUTHORIZED)

        contentViewRequest.is_approved = request.data["is_approved"]

        contentViewRequest.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """ Handle an DELETE request for single contentViewRequest
        Returns:
            Response code
        """
        try:
            contentViewRequest = ContentViewRequest.objects.get(pk=pk)


            #Prevent users from deleting posts from other users
            requesting_user = WhoYouUser.objects.get(user=request.auth.user)
            if requesting_user == contentViewRequest.requester:
                contentViewRequest.delete()
                return Response({}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"message": "Permission denied"}, status=status.HTTP_401_UNAUTHORIZED)
                
        except contentViewRequest.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
class ContentSerializerNoValue(serializers.ModelSerializer):
    """ Serializer for Content that """
    class Meta:
        model = Content
        # Content Value is NOT included to prevent exposing data
        fields = ('id',)

class ContentViewRequestSerializer(serializers.ModelSerializer):
    """Serializer for Content_View_Requests"""
    # A custom serializer is used to prevent exposing the content value
    content = ContentSerializerNoValue(many=False)

    class Meta:
        model = ContentViewRequest
        fields = ( 'id', 'requester', 'content', 'is_approved', 'creation_time')
        depth = 1