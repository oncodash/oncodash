from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status


NETWORK_URL = reverse('explainer:networkspec-list')


class NetworkAPiTests(APITestCase):
    """
    Test the network visualization specifications
    """

    def setUp(self):
        self.valid_spec = {
            "spec": {
                "nodes": [
                    {"id": "Ascites", "group": "samples", "order": 1},
                    {"id": "Peritoneum", "group": "samples", "order": 1},
                    {"id": "HGSOC", "group": "cancers", "order": 2},
                    {"id": "CIN2", "group": "cancers", "order": 2}
                ],
                "links": [
                    {"source": "Ascites", "target": "HGSOC",
                        "certainty": 0.5, "strenth": 0.7},
                    {"source": "Peritoneum", "target": "CIN2",
                        "certainty": 0.3, "strenth": 0.9}
                ]
            }
        }

    def test_create_network_successful(self) -> None:
        """
        Test a successful POST request to the API
        """
        spec = self.valid_spec        
        res = self.client.post(NETWORK_URL, spec, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_retrieve_network_successful(self) -> None:
        """
        Test a successful GET to the API
        """
        res = self.client.get(NETWORK_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
