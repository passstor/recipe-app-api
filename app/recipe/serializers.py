"""
Серіалізатори для моделей рецептів
"""
from rest_framework import serializers
from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """
    Серіалізатор для моделі рецептів
    """

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'time_minutes', 'price',
                  'link',)
        read_only_fields = ('id',)


class RecipeDetailSerializer(RecipeSerializer):
    """
    Серіалізатор для деталей рецепта
    """

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ('description',)
