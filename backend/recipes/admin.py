from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from .forms import RecipeAdminForm
from .models import Ingredient, Recipe, RecipeIngredient, Tag


class RequiredInlineModelFormset(BaseInlineFormSet):
    '''
    Кастомный Formset с модифицированной валидацией для избежания случаев
    создания админом рецептов без ингредиентов, что противоречит ТЗ.
    '''
    def clean(self):
        super().clean()
        # Не при всех вызовах у RecipeIngredientFormFormSet
        # есть аттрибут cleaned_data.
        cleaned_data = getattr(self, 'cleaned_data', None)
        if cleaned_data is not None:
            if not cleaned_data:
                raise ValidationError('Ингредиенты - обязательное поле.')
            if not all(item.get('ingredient') and item.get('amount')
                       for item in cleaned_data):
                raise ValidationError(
                    'Отправлять пустые ингредиенты нельзя.')
            if all(item.get('DELETE') for item in cleaned_data):
                raise ValidationError(
                    'Вы не можете удалить все ингредиенты, '
                    'ингредиенты - обязательное поле.')


class IngredientInLine(admin.TabularInline):
    formset = RequiredInlineModelFormset
    model = RecipeIngredient
    extra = 0
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
