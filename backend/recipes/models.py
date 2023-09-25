from django.contrib.auth import get_user_model
from django.core.validators import validate_image_file_extension, validate_slug
from django.db import models
from rest_framework.fields import MinValueValidator

from .validators import validate_hex


User = get_user_model()


class Tags(models.Model):
    name = models.CharField(
        verbose_name='Название тега',
        max_length=100,
        unique=True,
        blank=True,
        null=True,
    )
    color = models.CharField(
        verbose_name='Цвет в формате #Hex',
        max_length=7,
        unique=True,
        validators=[validate_hex, ]
    )
    slug = models.SlugField(
        verbose_name='Уникальный слаг',
        max_length=100,
        unique=True,
        validators=[validate_slug, ]
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipes(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE
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
        validators=[validate_image_file_extension, ]
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    # можон лучше
    ingredients = models.ManyToManyField(
        'Ingredients',
        through='RecipeIngredients',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Список ингредиентов',
    )
    tags = models.ManyToManyField(
        Tags,
        verbose_name='Список тегов',
        blank=True,
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=(MinValueValidator(1),)
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
        max_length=100,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=12,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'
            )
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
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=(
                    'recipe',
                    'ingredient',
                ),
                name='recipe_ingredient_unique',
                # violation_error_message=
                # 'Такой ингредиент уже есть в рецепте!',
            )
        ]

    def __str__(self):
        return (
            f'{self.ingredient.name}'
            f'{self.amount}, {self.ingredient.measurement_unit}.'
        )


class Favourites(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='favourite_subscriber',
    )
    recipe = models.ForeignKey(
        Recipes,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='favourite_recipe',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.recipe} нравится {self.user}.'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='purchases',
    )
    recipe = models.ForeignKey(
        Recipes,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='customers',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        # не уверен
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_list_user',
            )
        ]

    def __str__(self):
        return (
            f'Рецепт {self.recipe.name} '
            f'из списка покупок'
        )
