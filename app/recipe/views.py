"""
Вью для рецептів
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Recipe
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Вью для рецептів
    """
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        Отримання рецептів для поточного користувача
        """
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def perform_create(self, serializer):
        """
        Створення нового рецепту
        """
        serializer.save(user=self.request.user)
