# from rest_framework import serializers

# from foodgram_backend.serializers import Base64ImageField
# from users.serializers import UserSerializer
# from .abstract_classes import FavoriteShoppingCartSerializer
# from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
#                      ShoppingCart, Tag)


# class ShortRecipeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Recipe
#         fields = ('id', 'name', 'image', 'cooking_time')


# class IngredientSerializer(serializers.ModelSerializer):
#     measurement_unit = serializers.SerializerMethodField()

#     class Meta:
#         model = Ingredient
#         fields = ('id', 'name', 'measurement_unit')

#     def get_measurement_unit(self, obj):
#         return obj.get_measurement_unit_display()


# class TagSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Tag
#         fields = ('id', 'name', 'slug')


# class RecipeIngredientSerializer(serializers.ModelSerializer):
#     ingredient = serializers.PrimaryKeyRelatedField(
#         queryset=Ingredient.objects.all())

#     class Meta:
#         model = RecipeIngredient
#         fields = ('ingredient', 'amount')

#     def to_internal_value(self, data):
#         if 'id' in data.keys():
#             data['ingredient'] = data.pop('id')
#         return super().to_internal_value(data)

#     def to_representation(self, instance):
#         repr_dict = IngredientSerializer(instance.ingredient).data
#         repr_dict['amount'] = instance.amount
#         return repr_dict


# class RecipeSerializer(serializers.ModelSerializer):
#     ingredients = RecipeIngredientSerializer(many=True)
#     image = Base64ImageField()
#     author = UserSerializer(read_only=True)
#     is_favorited = serializers.SerializerMethodField()
#     is_in_shopping_cart = serializers.SerializerMethodField()
#     tags = serializers.PrimaryKeyRelatedField(
#         queryset=Tag.objects.all(), many=True)

#     class Meta:
#         model = Recipe
#         fields = (
#             'id', 'name', 'text', 'image', 'ingredients', 'author',
#             'cooking_time', 'tags', 'is_favorited', 'is_in_shopping_cart')

#     def validate_ingredients(self, ingredients):
#         if not ingredients:
#             raise serializers.ValidationError(
#                 'Ингредиенты - обязательное поле')
#         ingredients_ids = [ingredient['ingredient'].id
#                            for ingredient in ingredients]
#         if len(ingredients_ids) != len(set(ingredients_ids)):
#             raise serializers.ValidationError(
#                 'В вашем списке ингредиентов есть повторяющиеся позиции')
#         return ingredients

#     def validate_tags(self, tags):
#         if not tags:
#             raise serializers.ValidationError(
#                 'Теги - обязательное поле')
#         if len(tags) != len(set(tags)):
#             raise serializers.ValidationError(
#                 'В вашем списке тегов есть повторяющиеся позиции')
#         return tags

#     def validate(self, attrs):
#         required_fields = {'ingredients', 'tags', 'name',
#                            'text', 'cooking_time'}
#         exc_dict = {}
#         for required_field in required_fields:
#             if not attrs.get(required_field):
#                 exc_dict[required_field] = 'Это обязательное поле.'
#         if exc_dict:
#             raise serializers.ValidationError(exc_dict)
#         return attrs

#     def create_ingredients(self, recipe, ingredients):
#         RecipeIngredient.objects.bulk_create(
#             [RecipeIngredient(**ingredient, recipe=recipe)
#              for ingredient in ingredients]
#         )

#     def create(self, validated_data):
#         ingredients = sorted(validated_data.pop('ingredients'),
#                              key=lambda x: x.get('ingredient').name)
#         recipe = super().create(validated_data)
#         self.create_ingredients(recipe, ingredients)
#         return recipe

#     def update(self, instance, validated_data):
#         ingredients = validated_data.pop('ingredients')
#         super().update(instance, validated_data)
#         instance.ingredients.all().delete()
#         self.create_ingredients(instance, ingredients)
#         return instance

#     def to_representation(self, instance):
#         repr_dict = super().to_representation(instance)
#         tags = []
#         for tag in instance.tags.all():
#             tags.append(TagSerializer(tag).data)
#         repr_dict['tags'] = tags
#         return repr_dict

#     def get_is_favorited(self, obj):
#         user = self.context['request'].user
#         if not user.is_authenticated:
#             return False
#         return obj.favorite_users_related.filter(user=user).exists()

#     def get_is_in_shopping_cart(self, obj):
#         user = self.context['request'].user
#         if not user.is_authenticated:
#             return False
#         return obj.shoppingcart_users_related.filter(user=user).exists()


# class FavoriteSerializer(FavoriteShoppingCartSerializer):
#     class Meta(FavoriteShoppingCartSerializer.Meta):
#         model = Favorite


# class ShoppingCartSerializer(FavoriteShoppingCartSerializer):
#     class Meta(FavoriteShoppingCartSerializer.Meta):
#         model = ShoppingCart
