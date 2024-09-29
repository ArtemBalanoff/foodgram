from rest_framework import serializers
from foodgram_backend.constants import (
    MIN_INGREDIENT_AMOUNT, MAX_INGREDIENT_AMOUNT,
    MIN_COOKING_TIME, MAX_COOKING_TIME)
from users.serializers import UserSerializer
from foodgram_backend.serializers import Base64ImageField
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ('ingredient', 'amount')

    def to_internal_value(self, data):
        if 'id' in data.keys():
            data['ingredient'] = data.pop('id')
        return super().to_internal_value(data)

    def validate_amount(self, amount):
        if not MIN_INGREDIENT_AMOUNT <= amount <= MAX_INGREDIENT_AMOUNT:
            raise serializers.ValidationError(
                'Количество ингредиента должно быть в диапазоне от'
                f'{MIN_INGREDIENT_AMOUNT} до {MAX_INGREDIENT_AMOUNT}.')
        return amount

    def to_representation(self, instance):
        repr_dict = IngredientSerializer(instance.ingredient).data
        repr_dict['amount'] = instance.amount
        return repr_dict


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(
        many=True, source='ingredients_intermediate')
    image = Base64ImageField()
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

    def validate_cooking_time(self, cooking_time):
        if not MIN_COOKING_TIME <= cooking_time <= MAX_COOKING_TIME:
            raise serializers.ValidationError(
                'Время приготовления должно быть в диапазоне от '
                f'{MIN_COOKING_TIME} до {MAX_COOKING_TIME} минут.')
        return cooking_time

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                'Теги - обязательное поле')
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                'В вашем списке тегов есть повторяющиеся позиции')
        return tags

    def validate(self, attrs):
        # Из-за patch запроса, поля, которые нам нужны, пропускаются пустыми.
        # Остается вариант только проверять это вручную.
        required_fields = {'ingredients_intermediate', 'tags', 'name',
                           'text', 'cooking_time'}
        exc_dict = {}
        for required_field in required_fields:
            if not attrs.get(required_field):
                if required_field == 'ingredients_intermediate':
                    required_field = 'ingredients'
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
        ingredients = validated_data.pop('ingredients_intermediate')
        recipe = super().create(validated_data)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients_intermediate')
        super().update(instance, validated_data)
        instance.ingredients.clear()
        self.create_ingredients(instance, ingredients)
        return instance

    def to_representation(self, instance):
        repr_dict = super().to_representation(instance)
        tags = []
        for tag in instance.tags.all():
            tags.append(TagSerializer(tag).data)
        repr_dict['tags'] = tags
        return repr_dict

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return obj.favorited_by_intermediate.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return obj.in_shopping_cart_intermediate.filter(user=user).exists()
