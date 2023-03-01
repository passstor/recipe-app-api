"""
Тест для адмінки джанго
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.test import Client

class AdminSiteTests(TestCase):
    """
    Тест для адмінки
    """
    def setUp(self):
        """
        Перед тестом
        """
        self.client = Client() # створюємо клієнт для тестування адмінки джанго (входить в систему)
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="password123"
        )
        self.client.force_login(self.admin_user) # force_login - входить в систему
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='password123',
            name='Test user'
        )
    def test_user_list(self):
        """
        Тест для перевірки коректності списку користувачів
        """
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """
        Тест для перевірки коректності сторінки редагування користувача
        """
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)