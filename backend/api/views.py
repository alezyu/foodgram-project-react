from django.shortcuts import render
from rest_framework import mixins, viewsets

from .permissions import IsAdminOrReadOnlyObject, IsAdminOrReadOnly
from recipes.models import (
    Tags,
)
from .serializers import (
    TagsSerializer,
)


class ListRetrieveViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    permission_classes = (IsAdminOrReadOnly,)


class TagsViewSet(ListRetrieveViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None
