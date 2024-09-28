from rest_framework import serializers
from django.contrib.auth import get_user_model
from djoser.serializers import (
    UserCreateSerializer as BaseUserCreateSerializer,
    UserSerializer as BaseUserSerializer)

from recipes.models import Recipe
from foodgram_backend.serializers import Base64ImageField

User = get_user_model()


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSerializer(BaseUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        cur_user = self.context.get('request').user
        return bool(cur_user.is_authenticated
                    and obj in cur_user.subscriptions.all())


class UserSerializerWithRecipes(UserSerializer):
    recipes = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, obj):
        if recipes_limit := self.context.get('recipes_limit'):
            recipes = obj.recipes.all()[:recipes_limit]
        else:
            recipes = obj.recipes.all()
        return ShortRecipeSerializer(recipes, many=True).data


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'password')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
        read_only_fields = ('id',)


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)
