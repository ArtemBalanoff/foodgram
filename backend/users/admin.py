from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from recipes.models import Recipe

User = get_user_model()


admin.site.unregister(Group)


class RecipesInLine(admin.StackedInline):
    model = Recipe
    extra = 0
    verbose_name = 'Рецепт пользователя'
    verbose_name_plural = 'рецепты пользователя'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    inlines = (RecipesInLine,)
    list_display = ('email', 'username', 'first_name', 'last_name',
                    'get_recipes_count', 'get_subs_count', 'date_joined')
    search_fields = ('username', 'email')
    list_filter = ('is_staff',)

    @admin.display(description='Кол-во рецептов')
    def get_recipes_count(self, obj):
        return obj.recipes_count

    @admin.display(description='Кол-во подписчиков')
    def get_subs_count(self, obj):
        return obj.subs_count
