"""
Вью для апі користувачів
"""

from rest_framework import generics
from user.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """
    Створення нового користувача
    """
    serializer_class = UserSerializer
