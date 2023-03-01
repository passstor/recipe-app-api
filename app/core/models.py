"""
Модель для роботи з базою даних
"""
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
