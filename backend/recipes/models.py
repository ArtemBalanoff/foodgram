from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from nanoid import generate

from foodgram_backend.constants import (MAX_INGREDIENT_AMOUNT,
                                        MIN_INGREDIENT_AMOUNT, NAME_MAX_LENGTH)

User = get_user_model()


class Ingredient(models.Model):
    class MeasurementUnits(models.TextChoices):
        GRAM = 'gram', 'г'
        KILOGRAM = 'kilogram', 'кг'
        MILILITER = 'mililiter', 'мл'
        LITER = 'liter', 'л'
        TABLESPOON = 'tablespoon', 'ст. л.'
        TEASPOON = 'teaspoon', 'ч. л.'
        PINCH = 'pinch', 'щепотка'
        PIECE = 'piece', 'шт.'
        CLOVE = 'clove', 'долька'
        LEAF = 'leaf', 'лист'
        CUBE = 'cube', 'кубик'
        CUP = 'cup', 'стакан'
        CHUNK = 'chunk', 'кусок'
        BRANCH = 'branch', 'веточка'
        DROP = 'drop', 'капля'
        LOAF = 'loaf', 'батон'
        CAN = 'can', 'банка'
        HANDFUL = 'handful', 'горсть'
    name = models.CharField('Название', max_length=NAME_MAX_LENGTH)
    measurement_unit = models.TextField(
        'Единица измерения', choices=MeasurementUnits.choices,
        max_length=max(map(len, MeasurementUnits.values)))

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'ингредиенты'

    def __str__(self):
        return f'{self.name} - {self.get_measurement_unit_display()}'


class Tag(models.Model):
    name = models.CharField('Название', max_length=NAME_MAX_LENGTH)
    slug = models.SlugField('Слаг', unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes',
        verbose_name='Автор',)
    name = models.CharField('Название', max_length=NAME_MAX_LENGTH)
    image = models.ImageField('Изображение', upload_to='recipes/images/')
    text = models.TextField('Описание')
    cooking_time = models.PositiveSmallIntegerField('Время приготовления')
    tags = models.ManyToManyField(Tag, related_name='recipes',
                                  through='RecipeTag', verbose_name='Теги')
    short_link = models.CharField(max_length=5, unique=True,
                                  blank=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.short_link:
            while True:
                short_link = generate(size=5)
                if not Recipe.objects.filter(short_link=short_link).exists():
                    self.short_link = short_link
                    break
        super().save(*args, **kwargs)

    @property
    def favorited_count(self):
        return self.favorited_by.count()


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='ingredients', verbose_name='Рецепт')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   verbose_name='Ингредиент')
    amount = models.PositiveIntegerField(
        'Количество', validators=(MinValueValidator(MIN_INGREDIENT_AMOUNT),
                                  MaxValueValidator(MAX_INGREDIENT_AMOUNT)))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('recipe', 'ingredient'),
                                    name='unique_recipe_ingredient')]

    def __str__(self):
        return self.ingredient.name


class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               verbose_name='Рецепт')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE,
                            verbose_name='Тег')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('recipe', 'tag'),
                                    name='unique_recipe_tag')
        ]

    def __str__(self):
        return self.tag.name
