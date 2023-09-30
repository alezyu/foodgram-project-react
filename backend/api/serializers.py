from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, ValidationError

from recipes.models import (
    Favourites,
    Ingredients,
    RecipeIngredients,
    Recipes,
    ShoppingCart,
    Tags,
    User
)
from users.models import Subscribe
from users.serializers import UserSerializer


class FollowerRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredients
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=RecipeIngredients.objects.all(),
                fields=['ingredient', 'recipe']
            )
        ]

        def validate_amount(self, amount):
            if amount < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента не может быть меньше 1.'
                )
            return amount


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipes_ingredients',
        read_only=True
    )
    is_favourited = serializers.SerializerMethodField(
        method_name='get_is_favourited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipes
        fields = (
            'id',
            'author',
            'name',
            'image',
            'text',
            'ingredients',
            'tags',
            'cooking_time',
            'is_in_shopping_cart',
            'is_favourited',
        )

    def validate_cooking_time(self, cooking_time):
        if cooking_time <= 0:
            raise ValidationError(
                'Время приготовления должно быть больше 0.'
            )
        return cooking_time

    def get_is_favourited(self, obj):
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and Favourites.objects.filter(
                user=request.user,
                recipe=obj,
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and ShoppingCart.objects.filter(
                user=request.user,
                recipe=obj,
            ).exists()
        )

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        ingredients_temp_struct = set()
        for ingredient in ingredients:
            if int(ingredient.get('amount')) <= 0:
                raise serializers.ValidationError(
                    ('В рецепте должны быть ингредиенты.')
                )
            id = ingredient.get('id')
            if id in ingredients_temp_struct:
                raise serializers.ValidationError(
                    'Ингредиент можно добавить только один раз.'
                )
            ingredients_temp_struct.add(id)
        data['ingredients'] = ingredients
        cooking_time = self.initial_data.get('cooking_time')
        if cooking_time < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть от 1 минуты.'
            )
        return data

    @staticmethod
    def add_tags(tags, recipe):
        for tag_id in tags:
            recipe.tags.add(tag_id)

    @staticmethod
    def add_ingredients(ingredients, recipe):
        ingredients_in_recipe = [
            RecipeIngredients(
                recipe=recipe,
                ingredient=get_object_or_404(Ingredients, pk=ingredient['id']),
                amount=ingredient.get('amount'),
            )
            for ingredient in ingredients
        ]
        RecipeIngredients.objects.bulk_create(ingredients_in_recipe)

    @transaction.atomic
    def create(self, validated_data):
        image = validated_data.pop('image')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = Recipes.objects.create(image=image, **validated_data)
        self.add_tags(tags, instance)
        self.add_ingredients(ingredients, instance)
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        RecipeIngredients.objects.filter(recipe=instance).delete()
        self.add_tags(tags, instance)
        self.add_ingredients(ingredients, instance)
        return super().update(instance, validated_data)


class FavouriteSerializer(serializers.ModelSerializer): 
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipes.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Favourites
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favourites.objects.all(),
                fields=('user', 'recipe', ),
                message='Уже есть в избранном.',
            )
        ]

    def to_representation(self, instance):
        return FollowerRecipeSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class ShoppingCartSerializer(FavouriteSerializer):
    class Meta(FavouriteSerializer.Meta):
        model = ShoppingCart

        def validate(self, data):
            request = self.context.get('request')
            recipe_id = data['recipe'].id
            purchase_exists = ShoppingCart.objects.filter(
                user=request.user,
                recipe__id=recipe_id,
            ).exists()
            if request.method == 'POST' and purchase_exists:
                raise serializers.ValidationError(
                    'Рецепт уже есть в списке покупок.'
                )
            return data


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit', )


class CustomRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscribeToRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipes
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
        read_only_fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class SubscribersSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        limit = self.context.get('request').query_params.get('recipes_limit')

        if limit:
            queryset = obj.author_recipes.count().order_by(
                '-id'
            )[:int(limit)]
        else:
            queryset = obj.author_recipes.count()
        return SubscribeToRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.author_recipes.count()


class SubscribeToUserSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Subscribe
        fields = (
            'user',
            'author',
        )

    def validate(self, data):
        request = self.context.get('request')
        author_id = data['author'].id
        subscribe_is_exists = Subscribe.objects.filter(
            user=request.user,
            author__id=author_id,
        ).exists()

        if request.method == 'POST':
            if request.user.id == author_id:
                raise serializers.ValidationError(
                    'Нельзя подписаться на самого себя.'
                )
            if subscribe_is_exists:
                raise serializers.ValidationError(
                    'Вы уже подписаны.'
                )

        return data

