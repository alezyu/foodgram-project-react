from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import render, get_object_or_404
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import Follow

from .permissions import IsAdminOrReadOnlyObject, IsAdminOrReadOnly
from djoser.views import UserViewSet
from recipes.models import (
    Tags,
    Ingredients,
)
from .serializers import (
    CheckFollowSerializer,
    FollowSerializer,
    TagsSerializer,
    IngredientsSerializer,
)


User = get_user_model()


class ListRetrieveViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    permission_classes = (IsAdminOrReadOnly,)


class TagsViewSet(ListRetrieveViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None


class IngredientsViewSet(ListRetrieveViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None


class ViewUsersSet(UserViewSet):
    # нам не надо выводить пользователей???
    @action(
        methods=['POST'], detail=True, permission_classes=(IsAuthenticated,)
    )
    @transaction.atomic()
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, pk=id)
        data = {
            'user': user.id,
            'author': author.id,
        }
        serializer = CheckFollowSerializer(
            data=data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        result = Follow.objects.create(user=user, author=author)
        serializer = FollowSerializer(result, context={'request': request})
        return Response(serializer.data, status=HTTPStatus.CREATED)

    @subscribe.mapping.delete
    @transaction.atomic()
    def unsubscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, pk=id)
        data = {
            'user': user.id,
            'author': author.id,
        }
        serializer = CheckFollowSerializer(
            data=data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        user.follower.filter(author=author).delete()
        return Response(status=HTTPStatus.NO_CONTENT)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        user = request.user
        queryset = user.follower.all()
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)