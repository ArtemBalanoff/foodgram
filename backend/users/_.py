# from django.contrib.auth import get_user_model
# from djoser.views import UserViewSet as BaseUserViewSet
# from rest_framework import status
# from rest_framework.decorators import action
# from rest_framework.permissions import AllowAny, IsAuthenticated
# from rest_framework.response import Response

# from users.serializers import (SubscriptionSerializer, UserAvatarSerializer,
#                                UserSerializerWithRecipes)
# from .models import Subscription

# User = get_user_model()


# class UserViewSet(BaseUserViewSet):
#     queryset = User.objects.all().prefetch_related(
#         'subscriptions', 'favorite_recipes_related',
#         'shoppingcart_recipes_related')
#     permission_classes = (IsAuthenticated,)

#     def get_permissions(self):
#         if self.action in ('list', 'retrieve'):
#             return (AllowAny(),)
#         return super().get_permissions()

#     def get_recipes_limit(self):
#         recipes_limit = self.request.query_params.get('recipes_limit')
#         try:
#             return int(recipes_limit)
#         except (TypeError, ValueError):
#             pass

#     @action(detail=False, methods=('PUT',), url_path='me/avatar')
#     def avatar(self, request):
#         user = request.user
#         serializer = UserAvatarSerializer(instance=user, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)

#     @avatar.mapping.delete
#     def avatar_delete(self, request):
#         user = request.user
#         user.avatar.delete()
#         user.avatar = None
#         user.save()
#         return Response(status=status.HTTP_204_NO_CONTENT)

#     @action(detail=True, methods=('POST',), url_path='subscribe')
#     def subscribe(self, request, *args, **kwargs):
#         serializer = SubscriptionSerializer(
#             data={'subscriber': request.user,
#                   'author': self.get_object()},
#             context={'request': request,
#                      'recipes_limit': self.get_recipes_limit()})
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

#     @subscribe.mapping.delete
#     def subcribe_delete(self, request, *args, **kwargs):
#         subscriber = request.user
#         author = self.get_object()
#         try:
#             subscription = Subscription.objects.get(
#                 subscriber=subscriber, author=author)
#         except Subscription.DoesNotExist:
#             return Response(
#                 data={'error': 'Вы не подписаны на этого пользователя'},
#                 status=status.HTTP_400_BAD_REQUEST)
#         if author == request.user:
#             return Response(
#                 data={'error': 'Вы пытаетесь отписаться от самого себя'},
#                 status=status.HTTP_400_BAD_REQUEST)
#         subscription.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

#     @action(detail=False, methods=('GET',))
#     def subscriptions(self, request, *args, **kwargs):
#         subs = request.user.subscriptions.all()
#         paginated_subs = self.paginate_queryset(subs)
#         serializer_data = UserSerializerWithRecipes(
#             paginated_subs, many=True, context={
#                 'request': request,
#                 'recipes_limit': self.get_recipes_limit()}).data
#         return self.get_paginated_response(serializer_data)


# # class SubscriptionViewSet(viewsets.GenericViewSet,
# #                           mixins.CreateModelMixin,
# #                           mixins.DestroyModelMixin):
# #     serializer_class = SubscriptionSerializer

# #     def get_author(self):
# #         return get_object_or_404(User, pk=self.kwargs.get('user_id'))

# #     def get_object(self):
# #         try:
# #             return Subscription.objects.get(
# #                 subscriber=self.request.user, author=self.get_author())
# #         except Subscription.DoesNotExist:
# #             raise ValidationError('Вы не подписаны на этого пользователя')

# #     def get_serializer(self, *args, **kwargs):
# #         data = {
# #             'subscriber': self.request.user,
# #             'author': self.get_author()}
# #         return super().get_serializer(data)
