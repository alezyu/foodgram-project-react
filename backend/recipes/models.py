from django.contrib.auth import get_user_model
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    validate_image_file_extension,
    validate_slug
)
from django.db import models

from .constants import (
    COLOR_LENGTH,
    MEASUREMENT_LENGTH,
    NAME_LENGTH,
    SLUG_LENGTH,
)
from .validators import validate_hex

User = get_user_model()


class Tags(models.Model):
    name = models.CharField(
        verbose_name='Название тэга',
        max_length=NAME_LENGTH,
        unique=True,
    )
    color = models.CharField(
        verbose_name='Цвет в формате #Hex',
        max_length=COLOR_LENGTH,
        unique=True,
        validators=[validate_hex],
    )
    slug = models.SlugField(
        verbose_name='Уникальный слаг',
        max_length=SLUG_LENGTH,
        unique=True,
        validators=[validate_slug],
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name', )

    def __str__(self):
        return self.name


class Recipes(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='author_recipes',
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=254,
    )
    image = models.ImageField(
        verbose_name='Изображение',
        blank=True,
        null=True,
        upload_to='recipes/images/',
        validators=[validate_image_file_extension],
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    ingredients = models.ManyToManyField(
        'Ingredients',
        through='RecipeIngredients',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Список ингредиентов',
        blank=False,
        null=False,
    )
    tags = models.ManyToManyField(
        Tags,
        verbose_name='Список тегов',
        blank=True,
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=[
            MinValueValidator(
                1,
                message='Время приготовления должно быть от 1 минуты.',
            ),
            MaxValueValidator(
                1440,
                message=(
                    'Время приготовления должно быть меньше суток (1440 мин.)'
                ),
            ),
        ],
    )

    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.name}'


class Ingredients(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=NAME_LENGTH,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=MEASUREMENT_LENGTH,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient',
            ),
        ]

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipes,
        verbose_name='Рецепт',
        related_name='recipe_ingredients',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredients,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество в рецепте',
        default=1,
        validators=[
            MinValueValidator(
                1,
                message='Количество ингредиента должно быть больше 0.',
            ),
            MaxValueValidator(
                9999,
                message=(
                    'Максимум 9999 частей ингредиента.'
                ),
            ),
        ],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=(
                    'recipe',
                    'ingredient',
                ),
                name='recipe_ingredient_unique',
            )
        ]

    def __str__(self):
        return (
            f'{self.ingredient.name}'
            f'{self.amount}, {self.ingredient.measurement_unit}.'
        )


class BaseFavour(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='%(class)ss',
    )
    recipe = models.ForeignKey(
        Recipes,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='%(class)ss',
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=(
                    'user',
                    'recipe',
                ),
                name='%(class)ss_unique',
            )
        ]


class Favourites(BaseFavour):
    class Meta(BaseFavour.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.recipe} нравится {self.user}.'


class ShoppingCart(BaseFavour):
    class Meta(BaseFavour.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return (
            f'Рецепт {self.recipe.name} '
            f'из списка покупок {self.user}'
        )
