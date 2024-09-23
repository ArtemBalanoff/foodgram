from rest_framework.routers import DefaultRouter
from django.urls import include, path
from users.views import CustomUserViewSet

users_router = DefaultRouter()
users_router.register('users', CustomUserViewSet)

djoser_urls = [
    path('', include(users_router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
router_v1 = DefaultRouter()

urls_v1 = []
urls_v1.extend(router_v1.urls)
urls_v1.extend(djoser_urls)


urlpatterns = [
    path('', include(urls_v1)),
]
