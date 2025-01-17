from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import RefreshToken
from .utils import generate_access_token
from django.utils import timezone
from datetime import timedelta
import uuid


class AuthenticationTests(APITestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(
            username=self.user_data['email'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )

    def test_user_registration(self):
        url = reverse('register')
        data = {
            'email': 'newuser@example.com',
            'password': 'newpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=data['email']).exists())

    def test_user_login(self):
        url = reverse('login')
        response = self.client.post(url, self.user_data, format='json')
        print("Login response:", response.data)  
        print("Status code:", response.status_code)  
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_login(self):
        url = reverse('login')
        invalid_data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RefreshTokenTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )
        self.refresh_token = RefreshToken.objects.create(user=self.user)

    def test_valid_refresh_token(self):
        url = reverse('token-refresh')
        data = {'refresh_token': str(self.refresh_token.token)}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)
        self.assertNotEqual(response.data['refresh_token'], str(self.refresh_token.token))

    def test_invalid_refresh_token(self):
        url = reverse('token-refresh')
        data = {'refresh_token': str(uuid.uuid4())}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_expired_refresh_token(self):
        expired_token = RefreshToken.objects.create(
            user=self.user,
            expires_at=timezone.now() - timedelta(days=1)
        )
        url = reverse('token-refresh')
        data = {'refresh_token': str(expired_token.token)}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )
        self.refresh_token = RefreshToken.objects.create(user=self.user)

    def test_successful_logout(self):
        url = reverse('logout')
        data = {'refresh_token': str(self.refresh_token.token)}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], 'User logged out.')
        
        # Verify token is invalidated
        self.refresh_token.refresh_from_db()
        self.assertFalse(self.refresh_token.is_active)

    def test_invalid_token_logout(self):
        url = reverse('logout')
        data = {'refresh_token': str(uuid.uuid4())}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserProfileTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )
        self.access_token = generate_access_token(self.user.id)

    def test_get_user_profile_authenticated(self):
        url = reverse('user-profile')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.user.id)
        self.assertEqual(response.data['email'], self.user.email)

    def test_get_user_profile_unauthenticated(self):
        url = reverse('user-profile')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_profile_invalid_token(self):
        url = reverse('user-profile')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_user_profile(self):
        url = reverse('user-profile')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        data = {'username': 'john_smith'}  # valid format for username
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'john_smith')
        self.assertEqual(response.data['email'], self.user.email)
        
        # Verify changes in database
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'john_smith')

    def test_update_user_profile_invalid_data(self):
        url = reverse('user-profile')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        data = {'username': 'ab'}  # too short username
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_profile_unauthenticated(self):
        url = reverse('user-profile')
        data = {'username': 'john_smith'}
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)