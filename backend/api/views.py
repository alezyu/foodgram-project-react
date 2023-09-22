from django.shortcuts import render
from rest_framework import mixins, viewsets

from .permissions import IsAdminOrReadOnlyObject, IsAdminOrReadOnly
from recipes.models import (
    Tags,
    Ingredients,
)
from .serializers import (
    TagsSerializer,
    IngredientsSerializer,
)


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
