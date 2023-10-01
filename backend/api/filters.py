from django_filters import rest_framework as filters
from recipes.models import Ingredients, Recipes, User

from recipes.models import Tags


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith',
    )

    class Meta:
        model = Ingredients
        fields = ('name', 'measurement_unit',)


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tags.objects.all(),
        to_field_name='slug',
    )

    class Meta:
        model = Recipes
        fields = ('tags', 'author',)
