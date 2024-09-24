from rest_framework import serializers

from users.serializers import UserSerializer
from foodgram_backend.serializers import Base64ImageField
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag


class RecipeIngredientSerializer(serializers.Serializer):
    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount', 'ingredient')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True)
    image = Base64ImageField()
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'text', 'image', 'ingredients', 'author',
                  'cooking_time', 'tags')


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')
