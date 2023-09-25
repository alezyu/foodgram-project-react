from django.db.models import Exists, OuterRef, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from recipes.models import (
    Favourites,
    Ingredients,
    Recipes,
    RecipeIngredients,
    ShoppingCart,
    Tags,
)
from api.permissions import AdminOrReadOnly
from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .serializers import (
    FavouriteSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    TagSerializer,
)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AdminOrReadOnly,)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    pagination_class = None
    filterset_class = IngredientFilter
    permission_classes = (AdminOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    filter_class = RecipeFilter

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return Recipes.objects.all()
        recipes = Recipes.objects.annotate(
            is_favourited=Exists(
                Favourites.objects.filter(
                    user=user,
                    recipe_id=OuterRef('pk'),
                )
            ),
            is_in_shopping_cart=Exists(
                ShoppingCart.objects.filter(
                    user=user,
                    recipe_id=OuterRef('pk'),
                )
            ),
        )
        if self.request.GET.get('is_favourited'):
            return recipes.filter(is_favourited=True)
        elif self.request.GET.get('is_in_shopping_cart'):
            return recipes.filter(is_in_shopping_cart=True)
        return recipes

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=[IsAuthenticated],
    )
    def favourite(self, request, pk):
        recipe = get_object_or_404(Recipes, id=pk)
        data = {
            'user': request.user.id,
            'recipe': recipe.id,
        }
        serializer = FavouriteSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favourite.mapping.delete
    def delete_favourite(self, request, pk):
        recipe = get_object_or_404(Recipes, id=pk)
        favourites = get_object_or_404(
            Favourites,
            user=request.user,
            recipe=recipe,
        )
        favourites.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipes, id=pk)
        data = {
            'user': request.user.id,
            'recipe': recipe.id,
        }
        serializer = ShoppingCartSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipes, id=pk)
        favourites = get_object_or_404(
            ShoppingCart,
            user=request.user,
            recipe=recipe,
        )
        favourites.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredients.objects.select_related('recipes')
            .filter(recipe__customers__user=request.user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(amount=Sum('amount'))
            .values_list(
                'ingredient__name', 'ingredient__measurement_unit', 'amount'
            )
        )
        shopping_list = []
        for name, measurement_unit, amount in ingredients:
            shopping_list.append(
                f'{name} - {amount} ' f'{measurement_unit} \n'
            )
        response = HttpResponse(shopping_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="shoplist.txt"'
        return response
