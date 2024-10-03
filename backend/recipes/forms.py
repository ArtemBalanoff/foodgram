from django import forms

from .models import Recipe, Tag


class RecipeAdminForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        label='Теги',
        queryset=Tag.objects.all(),
        required=True)

    class Meta:
        model = Recipe
        fields = '__all__'
