import json
from rest_framework import status
from rest_framework.test import APITestCase


class ContentTests(APITestCase):
    fixtures = ["field_type.json", "content.json", "tokens.json", "users.json", "whoyou_user.json"]

    def setUp(self):
        """
        Create a new account and create sample category
        """
        # create field types

        url = "/register"
        data = {
            "name": "Trinity",
            "email": "trinity@theResistance.com",
            "password": "trinity",
            "phone": "1234567890"
        }
        # Initiate request and capture response
        response = self.client.post(url, data, format='json')

        # Parse the JSON in the response body
        json_response = json.loads(response.content)

        # Store the auth token
        self.token = json_response["token"]
        self.newUserId =json_response['id']

        # Assert that a user was created
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_request_content(self):
        """
        Verify that the correct values are returned when a user requests another user's content
        """

        # Authenticate as Agent Smith from the fixtures
        # self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

        url = f"/content?user={self.newUserId}"
        # Initiate request and store response
        response = self.client.get(url, format='json')

        # Parse the JSON in the response body
        json_response = json.loads(response.content)

        # Assert that the response code is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the properties on the created resource are correct
        self.assertEqual(json_response[0]["value"], "Trinity")
        # self.assertEqual(json_response["maker"], "Milton Bradley")
        # self.assertEqual(json_response["skill_level"], 5)
        # self.assertEqual(json_response["number_of_players"], 6)
