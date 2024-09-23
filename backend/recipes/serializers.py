from rest_framework import serializers

from recipes.models import RecipeIngredient


class RecipeIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount', 'ingredient', 'recipe')


class RecipeSerializer(serializers.ModelSerializer):
    class Me