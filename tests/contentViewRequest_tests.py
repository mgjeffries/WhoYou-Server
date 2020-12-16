import json
from whoYouApi.models import field_type
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


    
class ContentViewRequestTests(APITestCase):
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
        

    def test_view_request_for_content_no_value_returned(self):
        """
        Verify that the correct values are returned when user requests their own content
        """
        # Make sure request is authenticated
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.agentSmithToken)
        
        data = {
            "content": 2
        }
        url = "/contentViewRequest"
        response = client.post(url, data, format='json')
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response["is_approved"], False)

        # Make sure that the value from the content was NOT returned with the contentViewRequest
        if "value" in json_response['content']:
            isValueInContent = True
        else:
            isValueInContent = False    
        self.assertEqual(isValueInContent, False)
        
