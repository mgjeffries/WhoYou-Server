import json
from whoYouApi.models import field_type
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


class ContentTests(APITestCase):
    fixtures = ["field_type.json", "content.json", "tokens.json", "users.json", "whoyou_user.json"]


    def setUp(self):
        """
        Create a new account, which will also create sample categories
        """
        # create field types

        url = "/register"
        data = {
            "name": "Trinity",
            "email": "trinity@theResistance.com",
            "password": "trinity",
            "phone": "1234567890"
        }
        response = self.client.post(url, data, format='json')
        json_response = json.loads(response.content)

        # Store the auth token and user id for later use
        self.token = json_response["token"]
        self.newUserId = json_response['id']

        # Assert that a user was created
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_request_content_as_unauthenticated(self):
        """
        Verify that the correct values are returned when an un-authenticated user requests a user's content
        """
        url = f"/content?owner={self.newUserId}"
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
    
    def test_request_content_as_self(self):
        """
        Verify that the correct values are returned when user requests their own content
        """
        # Make sure request is authenticated
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        
        url = f"/content?owner={self.newUserId}"
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
        

