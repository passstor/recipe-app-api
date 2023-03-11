"""
Тест для моделей
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_user(email='user@example.com', password='testpass123'):
    """
    Створення і виведенння користувача
    """
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    """
    Тест для моделей
    """

    def test_create_user_with_email_successful(self):
        """
        Тест создания пользователя с email
        """
        email = 'testtest@test.com'
        password = "password"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """
        Тест для нормализации email
        """
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(
                email=email,
                password='sample123'
            )
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """
        Тест для створення користувача без email та викиду помилки
        """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'sample123')

    def test_create_new_superuser(self):
        """
        Тест для створення нового cуперюзера
        """
        user = get_user_model().objects.create_superuser(
            'test@test.com',
            'sample123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """
        Створення рецепта
        """
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123'
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title='Steak and mushroom sauce',
            time_minutes=5,
            price=Decimal(5.50),
            description='Place steak in a large resealable plastic bag. '
                        'Add the steak sauce, Worcestershire sauce, '
                        'garlic powder, onion powder, and black pepper. '
                        'Seal the bag, and shake to coat. Refrigerate '
                        'for at least 2 hours.'
        )
        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """
        Створення тегу
        """
        user = create_user()
        tag = models.Tag.objects.create(
            user=user,
            name='Tag1'
        )
        self.assertEqual(str(tag), tag.name)
