import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import serializers

from foodgram_backend.fields import UserInstanceField
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Subscription
from .abstract_classes import FavoriteShoppingCartSerializer

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


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


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class SubscriptionSerializer(serializers.ModelSerializer):
    subscriber = UserInstanceField()
    author = UserInstanceField()

    class Meta:
        model = Subscription
        fields = ('subscriber', 'author')

    def validate(self, attrs):
        subscriber = attrs.get('subscriber')
        author = attrs.get('author')
        if subscriber in author.subscribers.all():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого автора.')
        if subscriber == author:
            raise serializers.ValidationError(
                'Вы пытаетесь подписаться на себя.')
        return attrs

    def create(self, validated_data):
        super().create(validated_data)
        return validated_data.get('author')

    def to_representation(self, instance):
        return UserSerializerWithRecipes(
            instance,
            context={'request': self.context.get('request'),
                     'recipes_limit': self.context.get('recipes_limit')}).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')

    def get_measurement_unit(self, obj):
        return obj.get_measurement_unit_display()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = ('ingredient', 'amount')

    def to_representation(self, instance):
        repr_dict = IngredientSerializer(instance.ingredient).data
        repr_dict['amount'] = instance.amount
        return repr_dict


class RecipeIngredientCreateSerializer(RecipeIngredientReadSerializer):
    class Meta(RecipeIngredientReadSerializer.Meta):
        pass

    def to_internal_value(self, data):
        data['ingredient'] = data.pop('id')
        return super().to_internal_value(data)


class RecipeReadSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientReadSerializer(many=True)
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'text', 'image', 'ingredients', 'author',
            'cooking_time', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return obj.favorite_users_related.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return obj.shoppingcart_users_related.filter(user=user).exists()

    def to_representation(self, instance):
        repr_dict = super().to_representation(instance)
        repr_dict['tags'] = [
            TagSerializer(tag).data for tag in instance.tags.all()]
        return repr_dict


class RecipeCreateSerializer(RecipeReadSerializer):
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta(RecipeReadSerializer.Meta):
        pass

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Ингредиенты - обязательное поле')
        ingredients_ids = [ingredient['ingredient'].id
                           for ingredient in ingredients]
        if len(ingredients_ids) != len(set(ingredients_ids)):
            raise serializers.ValidationError(
                'В вашем списке ингредиентов есть повторяющиеся позиции')
        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                'Теги - обязательное поле')
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                'В вашем списке тегов есть повторяющиеся позиции')
        return tags

    def validate(self, attrs):
        required_fields = {'ingredients', 'tags', 'name',
                           'text', 'cooking_time'}
        exc_dict = {}
        for required_field in required_fields:
            if not attrs.get(required_field):
                exc_dict[required_field] = 'Это обязательное поле.'
        if exc_dict:
            raise serializers.ValidationError(exc_dict)
        return attrs

    def create_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(**ingredient, recipe=recipe)
             for ingredient in ingredients]
        )

    def create(self, validated_data):
        ingredients = sorted(validated_data.pop('ingredients'),
                             key=lambda x: x.get('ingredient').name)
        recipe = super().create(validated_data)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        super().update(instance, validated_data)
        instance.ingredients.all().delete()
        self.create_ingredients(instance, ingredients)
        return instance


class FavoriteSerializer(FavoriteShoppingCartSerializer):
    class Meta(FavoriteShoppingCartSerializer.Meta):
        model = Favorite


class ShoppingCartSerializer(FavoriteShoppingCartSerializer):
    class Meta(FavoriteShoppingCartSerializer.Meta):
        model = ShoppingCart
