from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import (
    filters,
    generics,
    mixins,
    permissions,
    status,
    viewsets,
)
from rest_framework.authentication import get_user_model
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from .models import Subscribe
from .serializers import (
    ChangePasswordSerializer,
    SubscribersSerializer,
    SubscribeToUserSerializer,
    UserSerializer,
)

User = get_user_model()


class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated,]

    def get_object(self):
        return self.request.user


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,]
    pagination_class = LimitOffsetPagination

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=[permissions.IsAuthenticated],
    )
    @transaction.atomic()
    def subscribe(self, request, id=None):
        subscribing = get_object_or_404(User, id=id)
        data = {
            'user': request.user.id,
            'subscribing': subscribing.id,
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

    #нужно ли тут это?
    @subscribe.mapping.delete
    @transaction.atomic()
    def delete_subscribe(self, request, id=None):
        subscribing = get_object_or_404(User, id=id)
        subscribe = get_object_or_404(
            Subscribe,
            user=request.user,
            subscribing=subscribing,
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
    search_fields = ('subscribing__username', 'subscriber__username')
    pagination_class = [LimitOffsetPagination, ]

    def get_queryset(self):
        return self.request.user.subscriber.all()


class ChangePasswordView(generics.CreateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    @transaction.atomic()
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_password = serializer.validated_data['new_password']
        user = request.user

        user.set_password(new_password)
        user.save()

        return Response(
            {'detail': 'Пароль изменен.'},
            status=status.HTTP_204_NO_CONTENT,
        )
