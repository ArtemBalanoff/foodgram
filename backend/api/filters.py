from django_filters import rest_framework as filters

from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        conjoined=False
    )
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags')

    def filter_is_favorited(self, queryset, name, value):
        return queryset.filter(
            favorite_users_related__user=self.request.user
        ) if value and self.request.user.is_authenticated else queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        return queryset.filter(
            shoppingcart_users_related__user=self.request.user
        ) if value and self.request.user.is_authenticated else queryset
