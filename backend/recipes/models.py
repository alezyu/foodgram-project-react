from django.contrib.auth import get_user_model
from django.db import models
from colorfield.fields import ColorField

User = get_user_model()

"""
Тег
Атрибуты модели:

    Название.
    Цветовой код, например, #49B64E.
    Slug.

Все поля обязательны для заполнения и уникальны.
"""


class Tags(models.Model):
    name = models.CharField(
        verbose_name='Название тега',
        max_length=100,
        unique=True,
    )
    color = ColorField(default='#FF0000')
    slug = models.SlugField(
        verbose_name='Уникальный слаг',
        max_length=100,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('id',)

    def __str__(self):
        return f'{self.name}'


"""
Ингредиент
Данные об ингредиентах должны храниться в нескольких связанных таблицах.
На стороне пользователя ингредиент должен содержать следующие атрибуты:

    Название.
    Количество.
    Единицы измерения.

Все поля обязательны для заполнения.
"""


class Ingredients(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=100,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=16,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


"""
Рецепт
Атрибуты модели:

    Автор публикации (пользователь).
    Название.
    Картинка.
    Текстовое описание.
    Ингредиенты — продукты для приготовления блюда по рецепту. Множественное поле с выбором из предустановленного списка и с указанием количества и единицы измерения.
    Тег. Можно установить несколько тегов на один рецепт.
    Время приготовления в минутах.

Все поля обязательны для заполнения.
"""


class Recipes(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=100,
    )
    image = models.ImageField(
        verbose_name='Изображение',
        blank=True,
        null=True,
        upload_to='images_recipes/',
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        through='IngredientsInRecipe',
        verbose_name='Список ингредиентов',
    )
    tags = models.ManyToManyField(
        Tags,
        verbose_name='Список тегов',
        related_name='recipes',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
    )
    pud_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pud_date',)

    def __str__(self):
        return f'{self.name}'


class IngredientsInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipes,
        verbose_name='Рецепт',
        related_name='ingredients_amount',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredients,
        verbose_name='Ингредиент',
        related_name='ingredients_amount',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveIntegerField(
        default=1,
        verbose_name='Количество в рецепте',
    )

    class Meta:
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецепта'
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_ingredient',
            )
        ]

    def __str__(self):
        return (
            f'{self.ingredient.name} - {self.amount},'
            f'{self.ingredient.measurement_unit}.')


class FavouriteRecipes(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='favourites',
    )
    recipe = models.ForeignKey(
        Recipes,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='favourites',
    )

    class Meta:
        verbose_name = 'Любимый рецепт'
        verbose_name_plural = 'Любимые рецепты'
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_recipe',
            )
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe.name}'


class ShoppingLists(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='list',
        verbose_name='Пользователь',
    )
    # related name namings
    recipe = models.ForeignKey(
        Recipes,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='list',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_list_user',
            )
        ]
    def __str__(self):
        return f'Рецепт {self.recipe.name}'
