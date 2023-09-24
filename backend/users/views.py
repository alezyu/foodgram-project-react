from django.shortcuts import get_object_or_404
from django.db import transaction
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
from rest_framework.permissions import IsAuthenticated,
from rest_framework.response import Response

from .models import Subscriber
from .serializers import (
    ChangePasswordSerializer,
    FollowSerializer,
    CheckFollowSerializer,
    UserSerializer,
)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = LimitOffsetPagination

    @action(
        methods=['POST'],
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    @transaction.atomic()
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, pk=id)
        data = {
            'user': user.id,
            'subscribing': author.id,
        }

        serializer = CheckFollowSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            {"detail": "Подписка успешна."},
            status=status.HTTP_201_CREATED,
        )

    @subscribe.mapping.delete
    @transaction.atomic()
    def delete_subscribe(self, request, id=None):
        user = request.user
        subscribing = get_object_or_404(User, pk=id)
        subscribe = get_object_or_404(
            Subscriber,
            user=user,
            author=subscribing
        )
        subscribe.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class SubscribeListViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = FollowSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('author__username', 'subscriber__username')
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return self.request.user.subscriber.all()


class ChangePasswordView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_password = serializer.validated_data['new_password']
        user = request.user

        user.set_password(new_password)
        user.save()

        return Response(
            {'detail': 'Пароль успешно изменен.'},
            status=status.HTTP_200_OK,
        )
