from rest_framework.routers import DefaultRouter
from django.urls import include, path
from users.views import UserViewSet
from recipes.views import IngredientViewSet, RecipeViewSet, TagViewSet

router_v1 = DefaultRouter()
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('users', UserViewSet, basename='users')

# urls_v1 = router_v1.urls

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
