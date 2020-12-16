""" View module for handling requests about content"""
from whoYouApi.models import content, field_type
from whoYouApi.models.field_type import FieldType
from rest_framework.viewsets import ViewSet
from whoYouApi.models import WhoYouUser, ContentViewRequest, Content
from django.utils import timezone
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status


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

    # def list(self, request):
    #     """Handle GET requests to Content resource

    #     Returns:
    #         Response -- JSON serialized list of Content
    #     """
    #     content_objects = Content.objects.all()

    #     # Filter content based on query parameters
    #     # e.g.: /content?owner=1
    #     user_id = self.request.query_params.get('owner', None)
    #     if user_id is not None:
    #         content_objects = content_objects.filter(owner=user_id)
        
    #     # Censor out values that the user shouldn't be able to access
    #     censored_content_objects = []
    #     for content_object in content_objects:
    #         try: 
    #             requester = WhoYouUser.objects.get(user=request.auth.user)
    #         except AttributeError:
    #             requester = None
    #         censored_content = censorContent(content_object, requester)
    #         censored_content_objects.append(censored_content)

    #     serializer = ContentSerializer(
    #         censored_content_objects, many=True, context={'request': request}
    #     )
    #     return Response(serializer.data)


#     def retrieve(self, request, pk=None):
#         """Handle GET request for single content instance
#         Returns:
#             Response JSON serialized content instance
#         """
#         content = Content.objects.get(pk=pk)
#         censoredContent = censorContent(content, request.auth.user)
#         serializer = ContentSerializer(censoredContent, context={'request': request})
#         return Response(serializer.data)
        
#     def update(self, request, pk=None):
#         """ Handle an PUT request for content
#         Returns:
#             Response code
#         """

#         # Find the post being updated based on it's primary key
#         content = Content.objects.get(pk=pk)

#         #Prevent non-admin users from modifying other user's posts
#         requester = WhoYouUser.objects.get(user=request.auth.user)
#         if requester != content.owner:
#             return Response({"message": "Permission denied"}, status=status.HTTP_401_UNAUTHORIZED)

#         # save basic (non-associated) properties
#         content.owner = requester
#         field_type = FieldType.objects.get(pk=request.data["field_type"])
#         content.field_type = field_type
#         content.value = request.data["value"]
#         content.is_public = request.data["is_public"] == "true"
#         content.verification_time = timezone.now()

#         # save content object
#         content.save()

#         return Response({}, status=status.HTTP_204_NO_CONTENT)

#     def destroy(self, request, pk=None):
#         """ Handle an DELETE request for content
#         Returns:
#             Response code
#         """
#         try:
#             content = Content.objects.get(pk=pk)

#             #Prevent non-admin users from deleting posts from other users
#             requesting_user = WhoYouUser.objects.get(user=request.auth.user)
#             if requesting_user == content.owner:
#                 content.delete()
#                 return Response({}, status=status.HTTP_204_NO_CONTENT)
#             else:
#                 return Response({"message": "Permission denied"}, status=status.HTTP_401_UNAUTHORIZED)
                
#         except Content.DoesNotExist as ex:
#             return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
    

# def censorContent(content_object, requestingUser):
#     isRequesterContentOwner = requestingUser == content_object.owner
#     if content_object.is_public or isRequesterContentOwner:
#     #TODO: check if the requester has a valid view request for this content
#         return content_object
#     else:
#         content_object.value = "restricted value"
#         return content_object


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