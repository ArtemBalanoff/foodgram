from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.serializers import UserAvatarSerializer, UserSerializerWithRecipes

User = get_user_model()


class UserViewSet(BaseUserViewSet):
    queryset = User.objects.all().prefetch_related(
        'subscriptions', 'favorites_intermediate', 'shopping_cart_intermediate')
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return (AllowAny(),)
        return super().get_permissions()

    def get_recipes_limit(self, request):
        recipes_limit = request.query_params.get('recipes_limit')
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
        user = get_object_or_404(User, pk=kwargs.get('id'))
        if user in request.user.subscriptions.all():
            return Response(
                data={'error': 'Вы уже подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST)
        if user == request.user:
            return Response(
                data={'error': 'Вы не можете подписаться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST)
        request.user.subscriptions.add(user)
        recipes_limit = self.get_recipes_limit(request)
        return Response(data=UserSerializerWithRecipes(
            user, context={'request': request,
                           'recipes_limit': recipes_limit}
            ).data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def subcribe_delete(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs.get('id'))
        if user not in request.user.subscriptions.all():
            return Response(
                data={'error': 'Вы не подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST)
        if user == request.user:
            return Response(
                data={'error': 'Вы пытаетесь отписаться от самого себя'},
                status=status.HTTP_400_BAD_REQUEST)
        request.user.subscriptions.remove(user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=('GET',))
    def subscriptions(self, request, *args, **kwargs):
        recipes_limit = self.get_recipes_limit(request)
        subs = request.user.subscriptions.all()
        paginated_subs = self.paginate_queryset(subs)
        serializer_data = UserSerializerWithRecipes(
            paginated_subs, many=True, context={
                'request': request, 'recipes_limit': recipes_limit}).data
        return self.get_paginated_response(serializer_data)
