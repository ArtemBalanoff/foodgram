from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RecipeInstanceField(serializers.Field):
    def to_internal_value(self, data):
        from recipes.models import Recipe
        if not isinstance(data, Recipe):
            raise serializers.ValidationError(
                'Ожидается объект класса Recipe')
        return data


class UserInstanceField(serializers.Field):
    def to_internal_value(self, data):
        if not isinstance(data, User):
            raise serializers.ValidationError(
                'Ожидается объект класса User')
        return data
