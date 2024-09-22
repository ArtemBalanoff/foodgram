from djoser.views import UserViewSet
from rest_framework.decorators import action


class UserViewSet(UserViewSet):
    action(methods=['PUT', 'DELETE'], url_path='me/avatar/')
    def update_avatar(self, request, *args, **kwargs):
        