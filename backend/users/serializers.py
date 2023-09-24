from rest_framework import serializers
from rest_framework.authentication import get_user_model

from recipes.models import Recipes

from .models import CustomUser, Subscriber

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

    def get_is_subscribed(self, data):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscriber.objects.filter(
            user=request.user, author=data.id
        ).exists()


class SubscribeResipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(UserSerializer):
    email = serializers.EmailField(source='author.email')
    id = serializers.IntegerField(source='author.id')
    username = serializers.CharField(source='author.username')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
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

    def get_recipes(self, data):
        limit = self.context.get('request').query_params.get('recipes_limit')
        queryset = data.author.recipes.all()
        if limit:
            queryset = queryset[: int(limit)]
        return SubscribeResipeSerializer(queryset, many=True).data

    def get_recipes_count(self, data):
        return Recipes.objects.filter(author=data.author).count()


class CheckFollowSerializer(serializers.ModelSerializer):
    queryset = User.objects.all()
    user = serializers.PrimaryKeyRelatedField(queryset=queryset)
    subscribing = serializers.PrimaryKeyRelatedField(queryset=queryset)

    class Meta:
        model = Subscriber
        fields = ('user', 'author')

    def validate(self, data):
        user = data['user']
        author = data['author']
        subscribed = user.follower.filter(author=author).exists()

        if self.request.method == 'POST':
            if user == author:
                raise serializers.ValidationError(
                    'Подписка на себя не разрешена'
                )
            if subscribed:
                raise serializers.ValidationError('Вы уже подписались')
        if self.request.method == 'DELETE':
            if user == author:
                raise serializers.ValidationError(
                    'Отписка от самого себя не разрешена'
                )
            if not subscribed:
                raise serializers.ValidationError(
                    {'errors': 'Вы уже отписались'}
                )
        return data

