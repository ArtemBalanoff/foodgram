from django_filters import rest_framework as filters
from .models import Recipe, Tag


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__name',
        to_field_name='name',
        queryset=Tag.objects.all(),
        conjoined=False
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags')
