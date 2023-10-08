from django.db.models import Exists, OuterRef, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from recipes.models import (
    Favourites,
    Ingredients,
    RecipeIngredients,
    Recipes,
    ShoppingCart,
    Tags, User,
)
from users.models import CustomUser, Subscribe
from .filters import RecipeFilter, IngredientsFilter
from .pagination import CustomPagination
from .serializers import (
    FavouriteSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    TagSerializer, RecipeCreateSerializer, UserSubscribeSerializer,
    UserSerializer, SubscribeToUserSerializer,
)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [IsAuthenticatedOrReadOnly]


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientSerializer
    search_fields = ('^name',)
    filter_backends = (IngredientsFilter,)
    pagination_class = None
    permission_classes = [IsAuthenticatedOrReadOnly]


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipeCreateSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return Recipes.objects.all()
        recipes = Recipes.objects.annotate(
            is_favorited=Exists(
                Favourites.objects.filter(
                    user=user,
                    recipe_id=OuterRef('pk'),
                ),
            ),
            is_in_shopping_cart=Exists(
                ShoppingCart.objects.filter(
                    user=user,
                    recipe_id=OuterRef('pk'),
                ),
            ),
        )
        if self.request.GET.get('is_favorited'):
            return recipes.filter(is_favorited=True)
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
    def favorite(self, request, pk):
        return self.create_obj(FavouriteSerializer, request, pk)

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        return self.create_obj(ShoppingCartSerializer, request, pk)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        return self.del_obj(ShoppingCart, request, pk)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.del_obj(Favourites, request, pk)

    @staticmethod
    def create_obj(serializer_class, request, recipe_id):
        recipe = get_object_or_404(Recipes, id=recipe_id)
        data = {
            'user': request.user.id,
            'recipe': recipe.id,
        }
        serializer = serializer_class(
            data=data, context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def del_obj(model, request, recipe_id):
        recipe = get_object_or_404(Recipes, id=recipe_id)
        obj = get_object_or_404(
            model,
            user=request.user,
            recipe=recipe,
        )
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def generate_list_for_shopping(user):
        ingredients = (
            RecipeIngredients.objects.filter(recipe__shoppingcarts__user=user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(amount=Sum('amount'))
            .order_by('ingredient__name')
        )
        shopping_list = []
        for ingredient in ingredients:
            shopping_list.append(
                f'{ingredient["ingredient__name"]} - '
                f'{ingredient["amount"]} '
                f'{ingredient["ingredient__measurement_unit"]} \n',
            )
        return shopping_list

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        user = request.user
        shopping_list = self.generate_list_for_shopping(user)
        response = HttpResponse(shopping_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="shoplist.txt"'
        return response


class CustomUserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = LimitOffsetPagination

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        data = {
            'user': request.user.id,
            'author': author.id,
        }
        serializer = SubscribeToUserSerializer(
            data=data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        subscribe = get_object_or_404(
            Subscribe,
            user=request.user,
            author=author,
        )
        subscribe.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(
        detail=False, methods=['GET'],
        permission_classes=[IsAuthenticated],
        serializer_class=UserSubscribeSerializer,
    )
    def subscriptions(self, request):
        subscriptions = User.objects.filter(
            author__user=request.user,
        )
        page = self.paginate_queryset(subscriptions)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
