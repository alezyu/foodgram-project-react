from django.contrib import admin

from .models import Favourites, Ingredients, Recipes, ShoppingCart, Tags


@admin.register(Ingredients)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('^name',)
    list_filter = ('name',)


class RecipeIngredientInline(admin.TabularInline):
    model = Recipes.ingredients.through
    extra = 1
    min_num = 1


class RecipeTagsInline(admin.TabularInline):
    model = Recipes.tags.through
    min_num = 0


@admin.register(Recipes)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favourite', )
    list_filter = ('name', 'tags', 'author')
    inlines = (RecipeIngredientInline, RecipeTagsInline, )

    def favourite(self, obj):
        counter = Favourites.objects.filter(recipe=obj).count()
        return counter


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('^name', )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    search_fields = ('^user__username', )


@admin.register(Favourites)
class FavouritesAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', )
    search_fields = ('^user__username', )
