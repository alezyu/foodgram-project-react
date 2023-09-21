from django.contrib import admin

from .models import (FavouriteRecipes,
                     Ingredients,
                     IngredientsInRecipe,
                     Recipes,
                     Tags
                     )


"""
Как должна быть настроена админка
В интерфейс админ-зоны нужно вывести необходимые поля моделей и настроить фильтры:

    вывести все модели с возможностью редактирования и удаление записей;
    для модели пользователей добавить фильтр списка по email и имени пользователя;
    для модели рецептов:
      
        в списке рецептов вывести название и имя автора рецепта;
        добавить фильтры по автору, названию рецепта, тегам;
        на странице рецепта вывести общее число добавлений этого рецепта в избранное;
    для модели ингредиентов:
      
        в список вывести название ингредиента и единицы измерения;
        добавить фильтр по названию.
"""


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug', 'color')
    list_editable = ('name', 'slug', 'color')


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author')
    list_editable = ('name',)
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name', 'author')


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(IngredientsInRecipe)
class IngredientsInRecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingridient', 'amount')
    list_editable = ('recipe', 'ingridient', 'amount')


@admin.register(FavouriteRecipes)
class FavouriteRecipesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    list_editable = ('user', 'recipe')
    search_fields = ('name', 'recipe')
