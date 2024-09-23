from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status


class CustomUserViewSet(UserViewSet):

    @action(methods=['PUT', 'DELETE'], url_path='me/avatar/', detail=True)
    def update_avatar(self, request, *args, **kwargs):
        if request.method == 'PUT':
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            request.user.avatar.delete()
            request.user.avatart = None
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
