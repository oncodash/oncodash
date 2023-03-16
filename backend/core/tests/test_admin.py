from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):

    def setUp(self) -> None:
        """
        Set up the client and mock_up user & super_user
        """
        self.client = Client()  # Used to simulate HTTP requests
        self.admin_user = get_user_model().objects.create_superuser(
            email="test@test.com",
            password="ggg444"
        )
        self.client.force_login(self.admin_user)

        self.user = get_user_model().objects.create_user(
            email="lol@test.com",
            password="gg2123",
            name="Test user full name"
        )

    def test_users_listed(self) -> None:
        """
        Test that users are listed on user page
        """
        url = reverse("admin:core_user_changelist")
        response = self.client.get(url)  # HTTP GET
        self.assertContains(response, self.user.name)
        self.assertContains(response, self.user.email)

    def test_user_change_page(self) -> None:
        """
        Test that the user-edit page works
        """
        url = reverse("admin:core_user_change", args=[self.user.id])
        response = self.client.get(url)  # HTTP GET

        self.assertEqual(response.status_code, 200)

    def test_create_user_page(self) -> None:
        """
        Test that the create user page works
        """
        url = reverse("admin:core_user_add")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
