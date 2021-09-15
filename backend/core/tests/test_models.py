import json
from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self) -> None:
        """
        Test creating a new user with email is succesful
        """
        email = "test@gmail.com"
        password = "T3stpass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self) -> None:
        """
        Test that the user email is normalized
        """
        email = "test@GMAIL.COM"
        user = get_user_model().objects.create_user(
            email=email,
            password="test123"
        )
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self) -> None:
        """
        Test that error is raised if email is not provided
        when user is created.
        """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email=None,
                password="dddd123"
            )

    def test_create_new_superuser(self) -> None:
        """
        Test creating a superuser
        """
        user = get_user_model().objects.create_superuser(
            email="test@gmail.com",
            password="dddd123"
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_valid_jsonspec_str(self) -> None:
        """
        Test the that json spec is valid json
        """
        net = {
            "nodes": [
                {"id": "A", "group": "samples", "order": 1},
                {"id": "B", "group": "samples", "order": 1},
                {"id": "C", "group": "cancers", "order": 2},
                {"id": "D", "group": "cancers", "order": 2},
            ],
            "links": [
                {"source": "A", "target": "C", "certainty": .5, "strength": .7},
                {"source": "B", "target": "D", "certainty": .3, "strength": .9}
            ]
        }

        spec = models.NetworkSpec.objects.create(
            json_spec=json.dumps(net)
        )

        self.assertEqual(spec.json_spec, str(spec))

