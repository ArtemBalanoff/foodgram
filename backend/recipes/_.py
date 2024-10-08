# from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework import filters, status, viewsets
# from rest_framework.decorators import action
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response

# from .filters import RecipeFilter
# from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
# from .permissions import AuthorOrReadOnly
# from .serializers import (FavoriteSerializer, IngredientSerializer,
#                           RecipeSerializer, ShoppingCartSerializer,
#                           TagSerializer)
# from .utils import create_shopping_cart_list


# class RecipeViewSet(viewsets.ModelViewSet):
#     queryset = Recipe.objects.prefetch_related(
#         'favorite_users_related', 'shoppingcart_users_related',
#         'tags', 'ingredients').select_related('author')
#     permission_classes = (AuthorOrReadOnly,)
#     serializer_class = RecipeSerializer
#     filter_backends = (DjangoFilterBackend,)
#     filterset_class = RecipeFilter

#     def perform_create(self, serializer):
#         serializer.save(author=self.request.user)

#     def create_instance(self, request, serializer_class):
#         recipe = self.get_object()
#         user = request.user
#         serializer = serializer_class(data={'recipe': recipe, 'user': user})
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

#     def delete_instance(self, request, model):
#         recipe = self.get_object()
#         user = request.user
#         try:
#             instance = model.objects.get(recipe=recipe, user=user)
#         except model.DoesNotExist:
#             return Response(status=status.HTTP_400_BAD_REQUEST, data={
#                 'error': f'Такого {model._meta.verbose_name} не существует'})
#         instance.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

#     @action(detail=True, methods=('POST',),
#             permission_classes=(IsAuthenticated,))
#     def favorite(self, request, *args, **kwargs):
#         return self.create_instance(request, FavoriteSerializer)

#     @action(detail=True, methods=('POST',),
#             permission_classes=(IsAuthenticated,))
#     def shopping_cart(self, request, *args, **kwargs):
#         return self.create_instance(request, ShoppingCartSerializer)

#     @favorite.mapping.delete
#     def favorite_delete(self, request, *args, **kwargs):
#         return self.delete_instance(request, Favorite)

#     @shopping_cart.mapping.delete
#     def shopping_cart_delete(self, request, *args, **kwargs):
#         return self.delete_instance(request, ShoppingCart)

#     @action(detail=True, methods=('GET',), url_path='get-link')
#     def get_link(self, request, *args, **kwargs):
#         protocol = 'https' if request.is_secure() else 'http'
#         host = request.get_host()
#         return Response(data={
#             'short-link':
#             f'{protocol}://{host}/s/{self.get_object().short_link}'})

#     @action(detail=False, methods=('GET',))
#     def download_shopping_cart(self, request, *args, **kwargs):
#         return create_shopping_cart_list(request)


# class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = Ingredient.objects.all()
#     serializer_class = IngredientSerializer
#     pagination_class = None
#     filter_backends = (filters.SearchFilter,)
#     search_fields = ('^name',)
#     filters.SearchFilter.search_param = 'name'


# class TagViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = Tag.objects.all()
#     serializer_class = TagSerializer
#     pagination_class = None
