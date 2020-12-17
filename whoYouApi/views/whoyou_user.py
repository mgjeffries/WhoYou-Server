""" View module for handling requests about content"""
from whoYouApi.models.field_type import FieldType
from rest_framework.viewsets import ViewSet
from whoYouApi.models import WhoYouUser, Content, ContentViewRequest
from django.utils import timezone
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status


class WhoYouUserViewSet(ViewSet):
    """ WhoYou User """

    def list(self, request):
        """Handle GET requests to users resource

        Returns:
            Response -- JSON serialized list of Content
        """
        users = WhoYouUser.objects.all()

        serializer = WhoYouUserSerializer(
            users, many=True, context={'request': request}
        )
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Handle GET request for single user instance
        Returns:
            Response JSON serialized user instance
        """
        requested_user = WhoYouUser.objects.get(pk=pk)
        serializer = WhoYouUserSerializer(requested_user, context={'request': request})
        return Response(serializer.data)
        
    def partial_update(self, request, pk=None):
        """ Handle an PATCH request for a user
        Returns:
            Response code
        """

        user_to_update = WhoYouUser.objects.get(pk=pk)

        requester = WhoYouUser.objects.get(user=request.auth.user)
        if requester != user_to_update:
            return Response({"message": "Permission denied"}, status=status.HTTP_401_UNAUTHORIZED)

        if "profile_image_path" in request.data:
            user_to_update.profile_image_path = request.data["profile_image_path"]
        if "cover_image_path" in request.data:
            user_to_update.cover_image_path = request.data["cover_image_path"]

        user_to_update.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)


class WhoYouUserSerializer(serializers.ModelSerializer):
    """Serializer for WhoYouUsers"""     
    class Meta:
        model = WhoYouUser
        fields = ( 'id', 'profile_image_path', 'cover_image_path')
        depth = 1