from rest_framework import filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .permissions import AuthorOrReadOnly
from .models import Ingredient, Recipe, Tag
from .serializers import (
    IngredientSerializer, RecipeSerializer, TagSerializer)
from django_filters.rest_framework import DjangoFilterBackend
from .filters import RecipeFilter
from users.serializers import ShortRecipeSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().prefetch_related(
        'favorited_by_intermediate', 'in_shopping_cart_intermediate',
        'tags', 'ingredients').select_related('author')
    permission_classes = (AuthorOrReadOnly,)
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        filters = {}
        if self.request.query_params.get('is_favorited') == '1':
            filters['favorited_by_intermediate__user'] = user
        if self.request.query_params.get('is_in_shopping_cart') == '1':
            filters['in_shopping_cart_intermediate__user'] = user
        return queryset.filter(**filters)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=('POST',),
            # permission_classes=(IsAuthenticated,)
            )
    def favorite(self, request, *args, **kwargs):
        # recipe = get_object_or_404(Recipe, pk=kwargs.get('pk'))
        # self.check_object_permissions(request, recipe)
        recipe = self.get_object()
        user = request.user
        if not user.favorites.filter(pk=recipe.pk).exists():
            user.favorites.add(recipe)
            return Response(ShortRecipeSerializer(recipe).data,
                            status=status.HTTP_201_CREATED)
        return Response({'error': 'Этот рецепт уже находится в ваших избранных'},
                        status=status.HTTP_400_BAD_REQUEST)

    @favorite.mapping.delete
    def favorite_delete(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=kwargs.get('pk'))
        self.check_object_permissions(request, recipe)
        request.user.favorites.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # @action(detail=True, methods=('POST',),
    #         permission_classes=(IsAuthenticated,))
    # def shopping_cart(self, request, *args, **kwargs):
    #     recipe

    @action(detail=True, methods=('GET',), url_path='get-link')
    def get_link(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=kwargs.get('pk'))
        self.check_object_permissions(request, recipe)
        return Response(data={'short-link': recipe.short_link})


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    filters.SearchFilter.search_param = 'name'


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
