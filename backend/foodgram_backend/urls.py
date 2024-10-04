from django.contrib import admin
from django.urls import include, path
from django.shortcuts import get_object_or_404, redirect
from recipes.models import Recipe


def recipe_redirect(request, short_link):
    recipe = get_object_or_404(Recipe, short_link=short_link)
    return redirect(f'/recipes/{recipe.id}/')


urlpatterns = [
    path('s/<str:short_link>/', recipe_redirect),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
