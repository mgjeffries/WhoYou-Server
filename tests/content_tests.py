import json
from whoYouApi.models import field_type
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


    
class ContentTests(APITestCase):
    fixtures = ["field_type.json"]    
    
    
    def setUp(self):
        """
        Create two new accounts, which will be used to verify that the right level of content is exposed
        """
        def createUser(userData):
            url = "/register"
            
            response = self.client.post(url, userData, format='json')
            json_response = json.loads(response.content)

            # Assert that a user was created
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            return json_response

        trinityData = {
            "name": "Trinity",
            "email": "trinity@theResistance.com",
            "password": "trinity",
            "phone": "1234567890"
        }
        agentSmithData = {
            "name": "Agent Smith",
            "email": "smith@test.com",
            "password": "smith",
            "phone": "1234567890"
        }
        trinityResponse = createUser(trinityData)
        self.trinityId = trinityResponse["id"]
        self.trinityToken = trinityResponse["token"]

        smithResponse = createUser(agentSmithData)
        self.agentSmithId = smithResponse["id"]
        self.agentSmithToken = smithResponse["token"]
        

    def test_get_content_as_unauthenticated_expect_restriced_unless_public(self):
        """
        Verify that the correct values are returned when an un-authenticated user GETs a user's content
        """
        url = f"/content?owner={self.trinityId}"
        response = self.client.get(url, format='json')
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for content in json_response:
            if content["field_type"]["name"] == "name":
                self.assertEqual(content["value"], "Trinity")
            if content["field_type"]["name"] == "phone":
                self.assertEqual(content["value"], "restricted value")
            if content["field_type"]["name"] == "email":
                self.assertEqual(content["value"], "restricted value")
    

    def test_get_content_as_owner_expect_unrestricted(self):
        """
        Verify that the correct values are returned when user GETs their own content
        """
        # Make sure request is authenticated
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.trinityToken)
        
        url = f"/content?owner={self.trinityId}"
        response = client.get(url, format='json')
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for content in json_response:
            if content["field_type"]["name"] == "name":
                self.assertEqual(content["value"], "Trinity")
            if content["field_type"]["name"] == "phone":
                self.assertEqual(content["value"], "1234567890")
            if content["field_type"]["name"] == "email":
                self.assertEqual(content["value"], "trinity@theResistance.com")


    def test_get_content_as_other_expect_restriced_unless_public(self):
        """
        Verify that the correct values are returned when user GETs another user's content
        """
        # Make sure request is authenticated
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.agentSmithToken)
        
        url = f"/content?owner={self.trinityId}"
        response = client.get(url, format='json')
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for content in json_response:
            if content["field_type"]["name"] == "name":
                self.assertEqual(content["value"], "Trinity")
            if content["field_type"]["name"] == "phone":
                self.assertEqual(content["value"], "restricted value")
            if content["field_type"]["name"] == "email":
                self.assertEqual(content["value"], "restricted value")

    def test_get_content_as_approved_other_expect_unrestricted(self):
        """
        When a user has an approved content_view_request, they should 
        be able to access content that isn't public
        """
        
        

# TODO Add tests for retrieving a specific piece of content by id
# TODO Add tests for creating content (This should only be allowed by authenticated users)
# TODO Add tests for updating content (This should only be allowed by the content owner)
# TODO Add tests for deleting content (This should only be allowed by the content owner)