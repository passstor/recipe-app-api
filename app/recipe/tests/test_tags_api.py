"""
Тести для тегів API
"""
from decimal import Decimal
from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    """
    Повертає URL для деталей тега
    """
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email='email@email.com', password='testpass123'):
    """
    Створення і повернення користувача
    """
    return get_user_model().objects.create_user(email, password)


class PublicTagsApiTests(TestCase):
    """
    Тести для тегів API (публічні)
    """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """
        Тест для перевірки авторизації
        """
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """
    Тести для тегів API (приватні)
    """

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """
        Тест для отримання тегів
        """
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """
        Тест для перевірки тегів для поточного користувача
        """
        user2 = create_user(
            email='exa2@example.com',
            password='testpass123'
        )
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):
        """
        Тест для оновлення тега
        """
        tag = Tag.objects.create(user=self.user, name='Afters')
        payload = {'name': 'New Afters'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tad(self):
        """
        Тест для видалення тега
        """
        tag = Tag.objects.create(user=self.user, name='Afters')
        url = detail_url(tag.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(id=tag.id).exists())

    def test_filter_tags_assigned_to_recipes(self):
        """
        Тест для фільтрації тегів по призначенню рецептів
        """
        tag1 = Tag.objects.create(user=self.user, name='Breakfast')
        tag2 = Tag.objects.create(user=self.user, name='Lunch')
        recipe = Recipe.objects.create(
            title='Eggs on toast',
            time_minutes=10,
            price=Decimal('3.00'),
            user=self.user
        )
        recipe.tags.add(tag1)
        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filter_tags_assigned_unique(self):
        """
        Тест для фільтрації тегів по призначенню рецептів
        """
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        Tag.objects.create(user=self.user, name='Lunch')
        recipe1 = Recipe.objects.create(
            title='Pancakes',
            time_minutes=5,
            price=Decimal('3.00'),
            user=self.user
        )
        recipe1.tags.add(tag)
        recipe2 = Recipe.objects.create(
            title='Porridge',
            time_minutes=3,
            price=Decimal('3.00'),
            user=self.user
        )
        recipe2.tags.add(tag)
        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)
