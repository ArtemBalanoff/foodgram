from rest_framework import status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from users.serializers import UserAvatarSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from djoser.views import UserViewSet as BaseUserViewSet


class UserViewSet(BaseUserViewSet):
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return (AllowAny(),)
        return super().get_permissions()

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
