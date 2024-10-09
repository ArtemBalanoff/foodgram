from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from users.models import Subscription
from .filters import RecipeFilter
from .permissions import AuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeReadSerializer,
                          ShoppingCartSerializer, SubscriptionSerializer,
                          TagSerializer, UserAvatarSerializer,
                          UserSerializerWithRecipes)
from .utils import create_shopping_cart_list

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.prefetch_related(
        'favorite_users_related', 'shoppingcart_users_related',
        'tags', 'ingredients').select_related('author')
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create_instance(self, request, serializer_class):
        recipe = self.get_object()
        user = request.user
        serializer = serializer_class(data={'recipe': recipe, 'user': user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_instance(self, request, model):
        recipe = self.get_object()
        user = request.user
        try:
            instance = model.objects.get(recipe=recipe, user=user)
        except model.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={
                'error': f'Такого {model._meta.verbose_name} не существует'})
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('POST',),
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, *args, **kwargs):
        return self.create_instance(request, FavoriteSerializer)

    @action(detail=True, methods=('POST',),
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, *args, **kwargs):
        return self.create_instance(request, ShoppingCartSerializer)

    @favorite.mapping.delete
    def favorite_delete(self, request, *args, **kwargs):
        return self.delete_instance(request, Favorite)

    @shopping_cart.mapping.delete
    def shopping_cart_delete(self, request, *args, **kwargs):
        return self.delete_instance(request, ShoppingCart)

    @action(detail=True, methods=('GET',), url_path='get-link')
    def get_link(self, request, *args, **kwargs):
        protocol = 'https' if request.is_secure() else 'http'
        host = request.get_host()
        return Response(data={
            'short-link':
            f'{protocol}://{host}/s/{self.get_object().short_link}'})

    @action(detail=False, methods=('GET',))
    def download_shopping_cart(self, request, *args, **kwargs):
        return create_shopping_cart_list(request)


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


class UserViewSet(BaseUserViewSet):
    queryset = User.objects.all().prefetch_related(
        'subscriptions', 'favorite_recipes_related',
        'shoppingcart_recipes_related')
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return (AllowAny(),)
        return super().get_permissions()

    def get_recipes_limit(self):
        recipes_limit = self.request.query_params.get('recipes_limit')
        try:
            return int(recipes_limit)
        except (TypeError, ValueError):
            pass

    @action(detail=False, methods=('PUT',), url_path='me/avatar')
    def avatar(self, request):
        user = request.user
        serializer = UserAvatarSerializer(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @avatar.mapping.delete
    def avatar_delete(self, request):
        user = request.user
        user.avatar.delete()
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('POST',), url_path='subscribe')
    def subscribe(self, request, *args, **kwargs):
        serializer = SubscriptionSerializer(
            data={'subscriber': request.user,
                  'author': self.get_object()},
            context={'request': request,
                     'recipes_limit': self.get_recipes_limit()})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def subcribe_delete(self, request, *args, **kwargs):
        subscriber = request.user
        author = self.get_object()
        try:
            subscription = Subscription.objects.get(
                subscriber=subscriber, author=author)
        except Subscription.DoesNotExist:
            return Response(
                data={'error': 'Вы не подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST)
        if author == request.user:
            return Response(
                data={'error': 'Вы пытаетесь отписаться от самого себя'},
                status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=('GET',))
    def subscriptions(self, request, *args, **kwargs):
        subs = request.user.subscriptions.all()
        paginated_subs = self.paginate_queryset(subs)
        serializer_data = UserSerializerWithRecipes(
            paginated_subs, many=True, context={
                'request': request,
                'recipes_limit': self.get_recipes_limit()}).data
        return self.get_paginated_response(serializer_data)
