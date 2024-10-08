# from django.contrib.auth import get_user_model
# from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
# from djoser.serializers import UserSerializer as BaseUserSerializer
# from rest_framework import serializers

# from foodgram_backend.fields import UserInstanceField
# from foodgram_backend.serializers import Base64ImageField
# from .models import Subscription

# User = get_user_model()


# class UserSerializer(BaseUserSerializer):
#     is_subscribed = serializers.SerializerMethodField()

#     class Meta(BaseUserSerializer.Meta):
#         model = User
#         fields = ('id', 'email', 'username', 'first_name',
#                   'last_name', 'is_subscribed', 'avatar')

#     def get_is_subscribed(self, obj):
#         cur_user = self.context.get('request').user
#         return bool(cur_user.is_authenticated
#                     and obj in cur_user.subscriptions.all())


# class UserSerializerWithRecipes(UserSerializer):
#     recipes = serializers.SerializerMethodField()

#     class Meta(UserSerializer.Meta):
#         fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

#     def get_recipes(self, obj):
#         from recipes.serializers import ShortRecipeSerializer
#         if recipes_limit := self.context.get('recipes_limit'):
#             recipes = obj.recipes.all()[:recipes_limit]
#         else:
#             recipes = obj.recipes.all()
#         return ShortRecipeSerializer(recipes, many=True).data


# class UserCreateSerializer(BaseUserCreateSerializer):
#     class Meta(BaseUserCreateSerializer.Meta):
#         model = User
#         fields = ('id', 'email', 'username', 'first_name',
#                   'last_name', 'password')
#         extra_kwargs = {
#             'first_name': {'required': True},
#             'last_name': {'required': True},
#         }
#         read_only_fields = ('id',)


# class UserAvatarSerializer(serializers.ModelSerializer):
#     avatar = Base64ImageField()

#     class Meta:
#         model = User
#         fields = ('avatar',)


# class SubscriptionSerializer(serializers.ModelSerializer):
#     subscriber = UserInstanceField()
#     author = UserInstanceField()

#     class Meta:
#         model = Subscription
#         fields = ('subscriber', 'author')

#     def validate(self, attrs):
#         subscriber = attrs.get('subscriber')
#         author = attrs.get('author')
#         if subscriber in author.subscribers.all():
#             raise serializers.ValidationError(
#                 'Вы уже подписаны на этого автора.')
#         if subscriber == author:
#             raise serializers.ValidationError(
#                 'Вы пытаетесь подписаться на себя.')
#         return attrs

#     def create(self, validated_data):
#         super().create(validated_data)
#         return validated_data.get('author')

#     def to_representation(self, instance):
#         return UserSerializerWithRecipes(
#             instance,
#             context={'request': self.context.get('request'),
#                      'recipes_limit': self.context.get('recipes_limit')}).data
