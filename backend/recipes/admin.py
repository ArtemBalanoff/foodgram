from django.contrib import admin

from .models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag


class IngredientInLine(admin.StackedInline):
    model = RecipeIngredient
    extra = 1
    verbose_name = 'Игредиент'
    verbose_name_plural = 'игредиенты'


class TagInLine(admin.StackedInline):
    model = RecipeTag
    extra = 1
    verbose_name = 'Тег'
    verbose_name_plural = 'теги'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientInLine, TagInLine)
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
