from rest_framework import status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from djoser.views import UserViewSet as BaseUserViewSet
from users.serializers import UserAvatarSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class UserViewSet(BaseUserViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @action(detail=False, methods=['PUT', 'DELETE'], url_path='me/avatar')
    def edit_avatar(self, request, *args, **kwargs):
        user = request.user
        if request.method == 'PUT':
            serializer = UserAvatarSerializer(instance=user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            user.avatar.delete()
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    # def get_serializer_class(self):
    #     super().get_serializer_class()
    #     if self.action in ('me', 'list', 'retrieve'):
    #         return UserSerializer
    #     if self.action == 'create':
    #         return UserCreateSerializer
    #     return self.serializer_class
