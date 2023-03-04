"""
Серіалізатори для моделей користувача
"""
from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """
    Серіалізатор для моделі користувача
    """

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True,
                                     'min_length': 5}}
        # Пароль не повертається в API й має бути не менше 5 символів

    def create(self, validated_data):
        """
        Створення нового користувача
        """
        return get_user_model().objects.create_user(**validated_data)
