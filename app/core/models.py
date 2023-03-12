"""
Модель для роботи з базою даних
"""
from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)


class UserManager(BaseUserManager):
    """
    Менеджер користувачів
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Створення користувача
        """
        if not email:
            raise ValueError('Користувач повинен мати email адресу')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        # використовуємо базу даних за замовчуванням
        return user

    def create_superuser(self, email, password):
        """
        Створення супер користувача
        """
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Користувач
    """
    email = models.EmailField(max_length=255, unique=True)
    # поле для email адреси користувача (унікальне)
    name = models.CharField(max_length=255)
    # поле для імені користувача
    is_active = models.BooleanField(default=True)
    # поле для активації користувача
    is_staff = models.BooleanField(default=False)
    # поле для перевірки чи є користувач адміном

    objects = UserManager()  # менеджер користувачів

    USERNAME_FIELD = 'email'  # поле для входа в систему


class Recipe(models.Model):
    """
    Об'єкт рецепта
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # зв'язок з моделлю користувача
        on_delete=models.CASCADE  # поведінка при видаленні користувача
    )
    # поле для зв'язку з користувачем
    title = models.CharField(max_length=255)
    # поле для назви рецепту
    description = models.CharField(max_length=255, blank=True)
    # поле для опису рецепту
    time_minutes = models.IntegerField()
    # поле для часу приготування
    price = models.DecimalField(max_digits=5, decimal_places=2)
    # поле для ціни
    link = models.CharField(max_length=255, blank=True)
    # поле для посилання на рецепт
    tags = models.ManyToManyField('Tag')
    # зв'язок з моделлю тегів
    ingredients = models.ManyToManyField('Ingredient')
    # зв'язок з моделлю інгредієнтів

    def __str__(self):
        return self.title


class Tag(models.Model):
    """
    Об'єкт тегу
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # зв'язок з моделлю користувача
        on_delete=models.CASCADE  # поведінка при видаленні користувача
    )
    # поле для зв'язку з користувачем
    name = models.CharField(max_length=255)

    # поле для назви тегу

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """
    Об'єкт інгредієнта
    """
    name = models.CharField(max_length=255)
    # поле для назви інгредієнта
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # зв'язок з моделлю користувача
        on_delete=models.CASCADE  # поведінка при видаленні користувача
    )

    def __str__(self):
        return self.name
