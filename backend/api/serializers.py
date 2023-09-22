from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.validators import UniqueValidator

from recipes.models import (
    FavouriteRecipes,
    Ingredients,
    IngredientsInRecipe,
    Recipes,
    ShoppingLists,
    Tags,
)

from rest_framework import serializers
from users.models import Follow

User = get_user_model()


class UserCreateSerializerCustom(UserCreateSerializer):
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
        )