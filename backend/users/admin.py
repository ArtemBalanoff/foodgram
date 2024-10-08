from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import TokenProxy

from recipes.models import Recipe
from .forms import UserCreationForm

User = get_user_model()


admin.site.unregister(Group)
admin.site.unregister(TokenProxy)


class RecipesInLine(admin.StackedInline):
    model = Recipe
    extra = 0
    verbose_name = 'Рецепт пользователя'
    verbose_name_plural = 'рецепты пользователя'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name',
                       'password1', 'password2', 'is_staff', 'is_superuser'),
        }),)
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


@admin.register(User.subscriptions.through)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'author')
    search_fields = ('subscriber__first_name', 'subscriber__last_name',
                     'subscriber__username', 'subscriber__email')
    list_filter = ('subscriber', 'author')
