from django.contrib import admin
from django.db import IntegrityError
from django.forms import BaseModelFormSet, ModelForm
from django.http import HttpRequest
from django.core.exceptions import ValidationError
from .forms import RecipeAdminForm
from .models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag


class IngredientInLine(admin.StackedInline):
    model = RecipeIngredient
    extra = 1
    verbose_name = 'Игредиент'
    verbose_name_plural = 'игредиенты*'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    form = RecipeAdminForm
    inlines = (IngredientInLine,)
    list_display = ('name', 'get_short_text', 'cooking_time', 'author',
                    'get_tags', 'get_favorited_count')
    search_fields = ('name', 'author')
    list_filter = ('tags',)

    @admin.display(description='В избранных у:')
    def get_favorited_count(self, obj):
        return obj.favorited_count

    @admin.display(description='Описание')
    def get_short_text(self, obj):
        return ' '.join(obj.text.split(' ')[:5]) + '...'

    @admin.display(description='Теги')
    def get_tags(self, obj):
        return list(obj.tags.values_list('name', flat=True))


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_editable = ('slug',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_editable = ('measurement_unit',)
    search_fields = ('name',)
    list_filter = ('measurement_unit',)
