from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    Favourites,
    Ingredients,
    Recipes,
    RecipeIngredients,
    ShoppingCart,
    Tags,
    User,
)
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
        read_only_fields = (
            'is_in_shopping_cart',
            'is_favourited',
        )

    def get_is_favourited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favourites.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        ingredients_set = set()
        for ingredient in ingredients:
            if int(ingredient.get('amount')) <= 0:
                raise serializers.ValidationError(
                    ('В рецепте должны быть ингредиенты.')
                )
            id = ingredient.get('id')
            if id in ingredients_set:
                raise serializers.ValidationError(
                    'Ингредиент можно добавить только один раз.'
                )
            ingredients_set.add(id)
        data['ingredients'] = ingredients
        return data
    
    # через bulk_create удобнее?
    def add_tags(self, instance):
        tags = self.initial_data.get('tags')
        for tag_id in tags:
            instance.tags.add(tag_id)
        return instance

    def add_ingredients(self, ingredients, instance):
        for ingredient in ingredients:
            ingredients_amounts = RecipeIngredients.objects.create(
                recipe=instance,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )
            ingredients_amounts.save()

    @transaction.atomic
    def create(self, validated_data):
        image = validated_data.pop('image')
        ingredients = validated_data.pop('ingredients')
        instance = Recipes.objects.create(image=image, **validated_data)
        instance = self.add_tags(instance)
        self.add_ingredients(ingredients, instance)
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        super().update(instance, validated_data)
        instance.tags.clear()
        instance = self.add_tags(instance)
        RecipeIngredients.objects.filter(recipe=instance).delete()
        self.add_ingredients(ingredients, instance)
        instance.save()
        return instance


class FavouriteSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipes.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Favourites
        fields = ('user', 'recipe')

    def validate(self, data):
        request = self.context.get('request')
        recipe_id = data['recipe'].id
        favourite_exists = Favourites.objects.filter(
            user=request.user,
            recipe__id=recipe_id,
        ).exists()
        if request.method == 'GET' and favourite_exists:
            raise serializers.ValidationError(
                'Рецепт уже добавлен.'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return FollowerRecipeSerializer(instance.recipe, context=context).data


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

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return FollowerRecipeSerializer(instance.recipe, context=context).data


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ['id', 'name', 'measurement_unit', ]
