from django_filters import rest_framework as filters

from .models import Recipe, Tag


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
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
            favorited_by_intermediate__user=self.request.user
        ) if value and self.request.user.is_authenticated else queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        return queryset.filter(
            in_shopping_cart_intermediate__user=self.request.user
        ) if value and self.request.user.is_authenticated else queryset
