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


@admin.register(Recipes)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favourite')
    inlines = (RecipeIngredientInline,)
    list_filter = ('name', 'tags', 'author')

    def favourite(self, obj):
        counter = Favourites.objects.filter(recipe=obj).count()
        return counter


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('^name',)


admin.site.register(ShoppingCart)
admin.site.register(Favourites)
