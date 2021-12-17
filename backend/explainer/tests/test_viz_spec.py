from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from explainer.models import NetworkSpec


NETWORK_URL = reverse('explainer:network-list')


class NetworkAPiTests(TestCase):
    """
    Test the network visualization specifications
    """

    def setUp(self):
        self.valid_spec = {
            "id": 1,
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

        self.network_spec = NetworkSpec(spec=self.valid_spec)
        self.client = APIClient()

    def test_create_network_successful(self) -> None:
        """
        Test a successful POST request to the API
        """
        payload = self.valid_spec
        res = self.client.post(NETWORK_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data, self.valid_spec)

    def test_retrieve_network_successful(self) -> None:
        """
        Test a successful GET to the API
        """
        res = self.client.get(NETWORK_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
