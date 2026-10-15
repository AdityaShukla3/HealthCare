from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthAPITests(APITestCase):
    def setUp(self):
        self.register_url = reverse('auth-register')
        self.login_url = reverse('auth-login')
        self.valid_user_data = {
            'name': 'Dr. Test User',
            'email': 'testuser@healthcare.com',
            'password': 'StrongPassword123!',
        }

    def test_register_user_success(self):
        response = self.client.post(self.register_url, self.valid_user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertEqual(response.data['user']['email'], 'testuser@healthcare.com')
        self.assertTrue(User.objects.filter(email='testuser@healthcare.com').exists())

    def test_register_duplicate_email_fails(self):
        self.client.post(self.register_url, self.valid_user_data)
        response = self.client.post(self.register_url, self.valid_user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        User.objects.create_user(
            name=self.valid_user_data['name'],
            email=self.valid_user_data['email'],
            password=self.valid_user_data['password']
        )
        login_data = {
            'email': self.valid_user_data['email'],
            'password': self.valid_user_data['password']
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['email'], self.valid_user_data['email'])

    def test_login_invalid_password(self):
        User.objects.create_user(
            name=self.valid_user_data['name'],
            email=self.valid_user_data['email'],
            password=self.valid_user_data['password']
        )
        login_data = {
            'email': self.valid_user_data['email'],
            'password': 'WrongPassword!'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
