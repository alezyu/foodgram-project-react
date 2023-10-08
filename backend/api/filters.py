from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipes


class IngredientsFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
    )

    class Meta:
        model = Recipes
        fields = ('tags', 'author')
