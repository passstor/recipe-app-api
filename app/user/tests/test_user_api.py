"""
Тест для API користувача
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')


def create_user(**params):
    """Створення користувача"""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Тести API користувача (публічні)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Тест створення користувача"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass',
            'name': 'Test name',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """Тест створення користувача email що існує """
        payload = {
            'email': 'test@example.com',
            'password': 'testpass',
            'name': 'Test name',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Тест пароль занадто короткий"""
        payload = {
            'email': 'test@example.com',
            'password': 'pw',
            'name': 'Test name', }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()  #
        # Перевірка чи існує користувач з таким email в базі даних
        self.assertFalse(user_exists)
