from django_filters import rest_framework as filters

from recipes.models import Ingredients, Recipes, Tags, User


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
        queryset=Tags.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    author = filters.ModelChoiceFilter(queryset=User.objects.all())

    class Meta:
        model = Recipes
        fields = ('tags', 'author',)
