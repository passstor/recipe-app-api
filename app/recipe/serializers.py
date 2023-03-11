"""
Серіалізатори для моделей рецептів
"""
from rest_framework import serializers
from core.models import Recipe, Tag


class TagSerializer(serializers.ModelSerializer):
    """
    Серіалізатор для моделі тегів
    """

    class Meta:
        model = Tag
        fields = ('id', 'name',)
        read_only_fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    """
    Серіалізатор для моделі рецептів
    """
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'time_minutes', 'price',
                  'link', 'tags')
        read_only_fields = ('id',)

    def _get_or_create_tags(self, tags, recipe):
        """
        Створення тегів
        """
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipe.tags.add(tag_obj)

    def create(self, validated_data):
        """
        Створення рецепта
        """
        tags = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        """
        Оновлення рецепта
        """
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """
    Серіалізатор для деталей рецепта
    """

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ('description',)
