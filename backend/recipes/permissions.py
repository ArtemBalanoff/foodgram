from rest_framework import permissions


class AuthorOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    def has_permission(self, request, view):
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        user = request.user
        return (obj.author == user or user.is_staff
                or request.method in permissions.SAFE_METHODS)
