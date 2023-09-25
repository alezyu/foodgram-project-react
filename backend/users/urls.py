from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ChangePasswordView,
    CurrentUserView,
    CustomUserViewSet,
    SubscribeListViewSet,
)

router_v1 = DefaultRouter()

router_v1.register(
    'users/subscriptions',
    SubscribeListViewSet,
    basename='subscribe',
)

router_v1.register(
    'users',
    CustomUserViewSet,
    basename='users',
)


urlpatterns = [
    path(
        'users/me/',
        CurrentUserView.as_view(),
        name='current-user',
    ),
    path(
        'users/set_password/',
        ChangePasswordView.as_view(),
        name='change-password',
    ),
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]