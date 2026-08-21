from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status


class AuthAppTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_registration_success(self):
        response = self.client.post("/api/registration/", {
            "fullname": "Test User",
            "email": "test@example.com",
            "password": "password123",
            "repeated_password": "password123"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertTrue(User.objects.filter(email="test@example.com").exists())

    def test_registration_duplicate_email(self):
        User.objects.create_user(username="test@example.com", email="test@example.com", password="password123")
        response = self.client.post("/api/registration/", {
            "fullname": "Test User",
            "email": "test@example.com",
            "password": "password123",
            "repeated_password": "password123"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_login_success(self):
        User.objects.create_user(username="login@example.com", email="login@example.com", password="password123")
        response = self.client.post("/api/login/", {
            "email": "login@example.com",
            "password": "password123"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

