import json
from whoYouApi.models import field_type
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
    
class ContentViewRequestTests(APITestCase):
    fixtures = ["field_type.json"]    
    
    
    def setUp(self):
        """
        Create two new accounts
        """
        def createUser(userData):
            url = "/register"
            response = self.client.post(url, userData, format='json')
            json_response = json.loads(response.content)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            return json_response

        trinityData = {
            "name": "Trinity",
            "email": "trinity@theMatrix.com",
            "password": "trinity",
            "phone": "1234567890"
        }
        agentSmithData = {
            "name": "Agent Smith",
            "email": "smith@theMatrix.com",
            "password": "smith",
            "phone": "1234567890"
        }
        
        trinityResponse = createUser(trinityData)
        self.trinityId = trinityResponse["id"]
        self.trinityToken = trinityResponse["token"]

        smithResponse = createUser(agentSmithData)
        self.agentSmithId = smithResponse["id"]
        self.agentSmithToken = smithResponse["token"]


        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.agentSmithToken)
        # Post a request to view trinity's content as smith
        data = {
           "content": 2
        }
        url = "/contentViewRequest"
        response = client.post(url, data, format='json')
        json_response = json.loads(response.content)
        self.agentSmithRequestForTrinityInfo = json_response["id"]
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Change authentication to trinity 
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.trinityToken)
        # Post a request to view smith's content as trinity
        data = {
           "content": 6
        }
        response = client.post(url, data, format='json')
        json_response = json.loads(response.content)
        self.trinityRequestForSmithInfo = json_response["id"]
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_view_request_for_content_no_value_returned(self):
        """
        Verify that the correct values are returned when user requests their access to another user's content
        """
        # Make sure request is authenticated
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.agentSmithToken)
        url = "/contentViewRequest"
        response = client.get(url, format='json')
        json_response = json.loads(response.content)

        # Make sure that the value from the content was NOT returned with the contentViewRequest
        for viewRequest in json_response:
            if "value" in viewRequest['content']:
                isValueInContent = True
            else:
                isValueInContent = False    
            self.assertEqual(viewRequest["is_approved"], False)
            self.assertEqual(isValueInContent, False)

        
    def test_duplicate_request_for_content_expect_create_only_one(self): 
        """
        Verify that the correct values are returned when user requests their access to another user's content
        """
        # Make sure request is authenticated
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.agentSmithToken)
        
        data = {
           "content": 5
        }
        url = "/contentViewRequest"
        # Create the first request to view content
        response = client.post(url, data, format='json')
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Create the second request to view content
        response = client.post(url, data, format='json')
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json_response["reason"], "Request already exists")


    def test_get_content_requests(self): 
        """
        Verify that the correct values are returned when user gets content requests
        """
        client = APIClient()
        url = "/contentViewRequest"
        # Get Trinity's content requests
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.trinityToken)
        response = client.get(url, format='json')
        json_response = json.loads(response.content)

        is_smith_content_request_in_response = any( elm["requester"]["id"] == self.agentSmithId for elm in json_response)
        is_trinity_content_request_in_response = any( elm["requester"]["id"] == self.trinityId for elm in json_response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(is_smith_content_request_in_response, True)
        self.assertEqual(is_trinity_content_request_in_response, True)
        self.assertEqual(len(json_response), 2)
    
    def test_approve_own_request_expect_error(self):
        """
        Test that a user can NOT approve a content view request for content that 
        they do NOT own
        """
        client = APIClient()
        url = F"/contentViewRequest/{self.agentSmithRequestForTrinityInfo}"
        # Get Trinity's content requests
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.agentSmithToken)
        data = {
           "is_approved": True
        }
        response = client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    
    def test_approve_request_for_own_content_expect_success(self):
        """
        Test that a user CAN approve a content view request for content that 
        they DO own
        """
        client = APIClient()
        url = F"/contentViewRequest/{self.agentSmithRequestForTrinityInfo}"
        # Get Trinity's content requests
        client.credentials(HTTP_AUTHORIZATION='Token ' + self.trinityToken)
        data = {
           "is_approved": True
        }
        response = client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)



        # TODO: Add tests for getting single content view request. 
        # Users should only be able to get requests that they created, 
        # or that are addressed to their content


        # TODO: Add tests for deleting a content view request.
        # Users should only be able to delete a content view request
        # that they created