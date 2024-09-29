from django.contrib import admin
from .models import Recipe, Ingredient, Tag, RecipeIngredient


class IngredientInLine(admin.StackedInline):
    model = RecipeIngredient
    extra = 1
    verbose_name = 'Игредиент'
    verbose_name_plural = 'игредиенты'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientInLine,)
    list_display = ('name', 'get_short_text', 'cooking_time', 'author',
                    'get_tags')
    search_fields = ('name', 'author')

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
