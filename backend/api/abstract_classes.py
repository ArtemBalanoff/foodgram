from django.contrib.auth import get_user_model
from rest_framework import serializers

from foodgram_backend.fields import RecipeInstanceField, UserInstanceField

User = get_user_model()


class FavoriteShoppingCartSerializer(serializers.ModelSerializer):
    user = UserInstanceField()
    recipe = RecipeInstanceField()

    class Meta:
        model = None
        fields = ('user', 'recipe')

    def validate(self, attrs):
        user = attrs.get('user')
        recipe = attrs.get('recipe')
        model = self.Meta.model
        verbose_name = model._meta.verbose_name.lower()
        if model.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                f'Такая запись {verbose_name} уже существует')
        return attrs

    def to_representation(self, instance):
        from .serializers import ShortRecipeSerializer
        return ShortRecipeSerializer(instance.recipe).data
