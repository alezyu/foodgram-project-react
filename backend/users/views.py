from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import (
    permissions,
    status
)
from rest_framework.authentication import get_user_model
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from api.serializers import SubscribeToUserSerializer
from .models import CustomUser, Subscribe
from .serializers import CustomUserSerializer, UserSubscribeSerializer

User = get_user_model()


class CurrentUserView(UserViewSet):
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_object(self):
        return self.request.user


class CustomUserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]
    pagination_class = LimitOffsetPagination

    @action(
        detail=True,
        methods=['POST', ],
        permission_classes=[permissions.IsAuthenticated, ],
    )
    @transaction.atomic()
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
    @transaction.atomic()
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
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=UserSubscribeSerializer
    )
    def subscriptions(self, request):
        subscriptions = User.objects.filter(
            author__user=request.user
        )
        page = self.paginate_queryset(subscriptions)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
