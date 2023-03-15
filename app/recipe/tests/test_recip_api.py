"""
Тести для рецептів API
"""
from django.test import TestCase
import tempfile
import os
from PIL import Image
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Recipe, Tag, Ingredient
from decimal import Decimal
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Повертає URL для рецепта"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def image_upload_url(recipe_id):
    """Повертає URL для завантаження зображення"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


def create_recipe(user, **params):
    """Створення рецепта"""
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': Decimal(5.00),
        'link': 'https://www.google.com',
        'description': 'Sample description',
    }
    defaults.update(params)
    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def create_user(**params):
    """Створення користувача"""
    return get_user_model().objects.create_user(**params)


class PublicRecipeApiTests(TestCase):
    """Тести для рецептів API (публічні)"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Тест для авторизації"""
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Тести для рецептів API (приватні)"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com',
                                password='testpass123')
        self.client.force_authenticate(self.user)

    def test_retrive_recipes(self):
        """Тест для отримання рецептів"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Тест для перевірки рецептів користувача"""
        other_user = create_user(
            email='other@example.com',
            password='testpass123',
        )
        create_recipe(user=other_user)
        create_recipe(user=self.user)
        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Тест для отримання деталей рецепту"""
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        res = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Тест для створення рецепту"""
        payload = {
            'title': 'Chocolate cheesecake',
            'time_minutes': 30,
            'price': Decimal('5.90'),
            'description': 'Sample description',
        }
        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))
        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """Тест для часткового оновлення рецепту"""
        original_link = 'https://www.google.com'
        recipe = create_recipe(user=self.user,
                               title='Chocolate cheesecake',
                               link=original_link)
        payload = {
            'title': 'New Chocolate cheesecake',
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Тест для повного оновлення рецепта"""
        recipe = create_recipe(user=self.user,
                               title='Chocolate cheesecake',
                               link='https://www.google.com',
                               description='Semple description'
                               )

        payload = {
            'title': 'New Chocolate cheesecake',
            'link': 'https://example.com',
            'description': 'New Sample description',
            'time_minutes': 10,
            'price': Decimal('3.00'),

        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))
        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        """Тест для оновлення користувача"""
        new_user = create_user(email='user@example2.com',
                               password='testpass123')
        recipe = create_recipe(user=self.user)
        payload = {
            'user': new_user.id,
        }
        url = detail_url(recipe.id)
        self.client.patch(url, payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Тест для видалення рецепта"""
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_recipe_other_user_recipe_error(self):
        """Тест для перевірки чи користувач може видалити чужий рецепт"""
        other_user = create_user(email='user@example2.com,'
                                       'password=testpass123')
        recipe = create_recipe(user=other_user)
        url = detail_url(recipe.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, 404)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_new_tags(self):
        """
        Тест для перевірки чи можна створити рецепт з новими тегами
        """
        payload = {
            'title': 'Brodie',
            'time_minutes': 30,
            'price': Decimal('5.90'),
            'tags': [{'name': 'Thai'}, {'name': 'Asia'}],
        }
        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes.first()
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            exists = recipe.tags.filter(name=tag['name'],
                                        user=self.user).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        """
        Тест для перевірки чи можна створити рецепт з наявними тегами
        """
        tag_indian = Tag.objects.create(user=self.user, name='Indian')
        payload = {
            'title': 'Brodie',
            'time_minutes': 30,
            'price': Decimal('5.90'),
            'tags': [{'name': 'Thai'}, {'name': 'Indian'}],

        }
        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes.first()
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_indian, recipe.tags.all())
        for tag in payload['tags']:
            exists = recipe.tags.filter(name=tag['name'],
                                        user=self.user).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """
        Тест для перевірки чи можна оновити рецепт з новими тегами
        """
        recipe = create_recipe(user=self.user)

        payload = {
            'tags': [{'name': 'Thai'}],
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='Thai')
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        """
        Тест для перевірки чи можна оновити рецепт з наявними тегами
        """
        tag_indian = Tag.objects.create(user=self.user, name='Indian')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_indian)

        tag_thai = Tag.objects.create(user=self.user, name='Thai')
        payload = {
            'tags': [{'name': 'Thai'}],
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_thai, recipe.tags.all())
        self.assertNotIn(tag_indian, recipe.tags.all())

    def test_clear_recipe_tags(self):
        """
        Тест для перевірки чи можна очистити теги рецепту
        """
        tag = Tag.objects.create(user=self.user, name='Indian')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)

        payload = {'tags': []}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)
        self.assertNotIn(tag, recipe.tags.all())

    def test_create_recipe_with_new_ingredients(self):
        """
        Тест для перевірки чи можна створити рецепт з новими інгредієнтами
        """
        payload = {
            'title': 'Brodie',
            'time_minutes': 30,
            'price': Decimal('5.90'),
            'ingredients': [{'name': 'Chicken'}, {'name': 'Rice'}],
        }
        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes.first()
        self.assertEqual(recipe.ingredients.count(), 2)
        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(name=ingredient['name'],
                                               user=self.user).exists()
            # цикл перевіряє чи існує інгредієнт в базі даних для даного
            # користувача і чи він відповідає тому, що ми передали
            self.assertTrue(exists)

    def test_create_recipe_with_existing_ingredients(self):
        """
        Тест для перевірки чи можна створити рецепт з наявними інгредієнтами
        """
        ingredient_lemon = Ingredient.objects.create(user=self.user,
                                                     name='Lemon')
        payload = {
            'title': 'Brodie',
            'time_minutes': 30,
            'price': Decimal('5.90'),
            'ingredients': [{'name': 'Lemon'}, {'name': 'Rice'}],
        }
        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes.first()
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(ingredient_lemon, recipe.ingredients.all())
        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(name=ingredient['name'],
                                               user=self.user).exists()
            self.assertTrue(exists)

    def test_create_ingredient_on_update(self):
        """
        Тест для перевірки чи можна оновити рецепт з новими інгредієнтами
        """
        recipe = create_recipe(user=self.user)

        payload = {
            'ingredients': [{'name': 'Limes'}],
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_ingredient = Ingredient.objects.get(user=self.user, name='Limes')
        self.assertIn(new_ingredient, recipe.ingredients.all())

    def test_update_recipe_assign_ingredient(self):
        """
        Тест для перевірки чи можна оновити рецепт з наявними інгредієнтами
        """
        ingredient_lemon = Ingredient.objects.create(user=self.user,
                                                     name='Lemon')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient_lemon)

        ingredient_limes = Ingredient.objects.create(user=self.user,
                                                     name='Limes')
        payload = {
            'ingredients': [{'name': 'Limes'}],
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ingredient_limes, recipe.ingredients.all())
        self.assertNotIn(ingredient_lemon, recipe.ingredients.all())

    def test_clear_recipe_ingredients(self):
        """
        Тест для перевірки чи можна очистити інгредієнти рецепта
        """
        ingredient = Ingredient.objects.create(user=self.user, name='Lemon')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)

        payload = {'ingredients': []}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)
        self.assertNotIn(ingredient, recipe.ingredients.all())

    def test_filter_by_tags(self):
        """
        Тест для перевірки чи можна фільтрувати рецепти по тегах
        """
        recipe1 = create_recipe(user=self.user, title='Recipe 1')
        recipe2 = create_recipe(user=self.user, title='Recipe 2')
        tag1 = Tag.objects.create(user=self.user, name='Tag 1')
        tag2 = Tag.objects.create(user=self.user, name='Tag 2')
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)
        recipe3 = create_recipe(user=self.user, title='Recipe 3')
        params = {'tags': f'{tag1.id},{tag2.id}'}
        res = self.client.get(RECIPES_URL, params)
        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_by_ingredients(self):
        """
        Тест для перевірки чи можна фільтрувати рецепти по інгредієнтах
        """
        recipe1 = create_recipe(user=self.user, title='Recipe 1')
        recipe2 = create_recipe(user=self.user, title='Recipe 2')
        ingredient1 = Ingredient.objects.create(
            user=self.user, name='Ingredient 1')
        ingredient2 = Ingredient.objects.create(
            user=self.user, name='Ingredient 2')
        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)
        recipe3 = create_recipe(user=self.user, title='Recipe 3')
        params = {'ingredients': f'{ingredient1.id},{ingredient2.id}'}
        res = self.client.get(RECIPES_URL, params)
        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)


class ImageUploadTests(TestCase):
    """
    Тести для перевірки завантаження зображення
    """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@21example.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image(self):
        """
        Тест для перевірки чи можна завантажити зображення
        """
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'image': image_file}
            res = self.client.post(url, payload, format='multipart')
        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """
        Тест для перевірки чи можна завантажити погане зображення
        """
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
