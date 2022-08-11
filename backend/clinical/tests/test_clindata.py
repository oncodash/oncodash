from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from faker import Faker

from .utils import Provider, create_data


CLINDATA_URL = reverse("clinical:clinicaldata-list")


class ClinDataAPiTests(APITestCase):
    """Test the clinical data specifications."""

    def setUp(self):
        fake = Faker()
        fake.add_provider(Provider)
        self.valid_spec = create_data(fake)

    def test_create_clindata_successful(self) -> None:
        """
        Test a successful POST request to the API
        """
        self.valid_spec["patient"] = "Test_patient"
        res = self.client.post(
            CLINDATA_URL, self.valid_spec, format="json", follow=True
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_retrieve_clindata_successful(self) -> None:
        """
        Test a successful GET to the API
        """
        res = self.client.get(CLINDATA_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
