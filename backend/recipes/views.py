from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.utils import convert_dict_to_text
from users.serializers import ShortRecipeSerializer
from .filters import RecipeFilter
from .models import Ingredient, Recipe, Tag
from .permissions import AuthorOrReadOnly
from .serializers import IngredientSerializer, RecipeSerializer, TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().prefetch_related(
        'favorited_by_intermediate', 'in_shopping_cart_intermediate',
        'tags', 'ingredients').select_related('author')
    permission_classes = (AuthorOrReadOnly,)
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(*args, **kwargs)

    @action(detail=True, methods=('POST',),
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, *args, **kwargs):
        recipe = self.get_object()
        user = request.user
        if not user.favorites.filter(pk=recipe.pk).exists():
            user.favorites.add(recipe)
            return Response(ShortRecipeSerializer(recipe).data,
                            status=status.HTTP_201_CREATED)
        return Response(
            {'error': 'Этот рецепт уже находится в ваших избранных'},
            status=status.HTTP_400_BAD_REQUEST)

    @favorite.mapping.delete
    def favorite_delete(self, request, *args, **kwargs):
        recipe = self.get_object()
        if not recipe.favorited_by_intermediate.filter(user=request.user):
            return Response(
                {'error': 'Вы еще не добавляли этот рецепт в избранное'},
                status=status.HTTP_400_BAD_REQUEST)
        request.user.favorites.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('POST',),
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, *args, **kwargs):
        recipe = self.get_object()
        user = request.user
        if recipe.in_shopping_cart_intermediate.filter(user=user).exists():
            return Response({'error': 'Вы уже добавили этот рецепт в корзину'},
                            status=status.HTTP_400_BAD_REQUEST)
        user.shopping_cart.add(recipe)
        return Response(ShortRecipeSerializer(recipe).data,
                        status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def shopping_cart_delete(self, request, *args, **kwargs):
        recipe = self.get_object()
        if not recipe.in_shopping_cart_intermediate.filter(user=request.user):
            return Response(
                {'error': 'Вы еще не добавляли этот рецепт список покупок'},
                status=status.HTTP_400_BAD_REQUEST)
        request.user.shopping_cart.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('GET',), url_path='get-link')
    def get_link(self, request, *args, **kwargs):
        protocol = 'https' if request.is_secure() else 'http'
        host = request.get_host()
        return Response(data={
            'short-link':
            f'{protocol}://{host}/s/{self.get_object().short_link}'})

    @action(detail=False, methods=('GET',))
    def download_shopping_cart(self, request, *args, **kwargs):
        measurement_unit_name_dict = {
            choice[0]: choice[1] for choice
            in Ingredient.MeasurementUnits.choices}
        aggregated_ingredients = request.user.shopping_cart.values(
            'ingredients__ingredient__name',
            'ingredients__ingredient__measurement_unit',
        ).annotate(total_amount=Sum('ingredients__amount'))
        ingredients_dict = {
            item['ingredients__ingredient__name']:
            (item['total_amount'],
             measurement_unit_name_dict.get(
                 item['ingredients__ingredient__measurement_unit']))
            for item in aggregated_ingredients}
        return Response(convert_dict_to_text(ingredients_dict))


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
