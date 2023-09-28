from django.core.validators import MaxLengthValidator, RegexValidator
from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from recipes.models import Recipes
from .models import CustomUser, Subscribe


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    def get_fields(self):
        fields = super().get_fields()
        if self.context['request'].method == 'POST':
            fields['password'] = serializers.CharField(write_only=True)
        else:
            fields.pop('password', None)
        return fields

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(
            user=request.user,
            author=obj.id
        ).exists()


class UserCreateCustomSerializer(UserSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            RegexValidator(
                regex='^[\\w.@+-]+\\z',
                message='Разрешены буквы, цифры и символы ., @, +, - '
            ),
            MaxLengthValidator(
                limit_value=150,
                message='Не более 150 символов!',
            ),
        ]
    )
    first_name = serializers.CharField(
        validators=[
            MaxLengthValidator(
                limit_value=150,
                message='Не более 150 символов!',
            ),
        ]
    )
    last_name = serializers.CharField(
        validators=[
            MaxLengthValidator(
                limit_value=150,
                message='Не более 150 символов!',
            ),
        ]
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
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
        #return Recipes.objects.filter(author=obj.author).count()
        return obj.author_recipes.count()


class SubscribeToUserSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Subscribe
        fields = (
            'user',
            'author'
        )

    def validate(self, data):
        request = self.context.get('request')
        author_id = data['author'].id
        subscribe_is_exists = Subscribe.objects.filter(
            user=request.user,
            author__id=author_id
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


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        user = self.context['request'].user
        #
        if not current_password or not new_password:
            raise serializers.ValidationError(
                'Введите оба пароля.'
            )
        #
        if not user.check_password(current_password):
            raise serializers.ValidationError('Неверный пароль.')

        return data
