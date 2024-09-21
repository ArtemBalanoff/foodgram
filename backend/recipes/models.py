from django.db import models
from django.contrib.auth import get_user_model

from foodgram_backend.constants import NAME_MAX_LENGTH

User = get_user_model()


class Ingredient(models.Model):
    class MeasureUnits(models.TextChoices):
        GRAM = 'gram', 'г'
        KILOGRAM = 'kilogram', 'кг'
        MILILITER = 'mililiter', 'мл'
        LITER = 'liter', 'л'
        TABLESPOON = 'tablespoon', 'ст.л.'
        TEASPOON = 'teaspoon', 'ч.л.'
        PINCH = 'pinch', 'щепотка'
        PIECE = 'piece', 'шт.'
        CLOVE = 'clove', 'долька'
        LEAF = 'leaf', 'лист'
        CUBE = 'cube', 'кубик'
        CUP = 'cup', 'стакан'
    name = models.CharField('Название', max_length=NAME_MAX_LENGTH)
    measure_unit = models.TextField(
        'Единица измерения', choices=MeasureUnits.choices,
        max_length=max(map(len, MeasureUnits.values)))


class Tag(models.Model):
    name = models.CharField('Название', max_length=NAME_MAX_LENGTH)
    slug = models.SlugField('Слаг', unique=True)


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes',
        verbose_name='Автор',)
    name = models.CharField('Название', max_length=NAME_MAX_LENGTH)
    image = models.ImageField('Изображение', upload_to='recipes/images/')
    description = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient', verbose_name='Ингредиенты')
    cook_duration = models.DurationField('Время приготовления')
    tags = models.ManyToManyField(Tag, related_name='recipes',
                                  verbose_name='Теги')


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField('Количество')
