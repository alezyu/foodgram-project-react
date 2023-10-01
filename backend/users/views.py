from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import (
    filters,
    generics,
    mixins,
    permissions,
    status,
    viewsets
)
from rest_framework.authentication import get_user_model
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from api.serializers import SubscribersSerializer, SubscribeToUserSerializer

from .models import CustomUser, Subscribe
from .serializers import CustomUserSerializer

User = get_user_model()


class CurrentUserView(generics.RetrieveAPIView):
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
            {'detail': 'Вы подписаны.'},
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


class SubscribeListViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = SubscribersSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ['author__username', 'subscriber__username', ]
    pagination_class = [LimitOffsetPagination, ]

    def get_queryset(self):
        return self.request.user.subscriber.all()
