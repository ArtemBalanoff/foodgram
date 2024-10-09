import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
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


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)
