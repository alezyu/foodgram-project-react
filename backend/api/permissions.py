# проверить на запросах!
from rest_framework.permissions import SAFE_METHODS, BasePermission


class CustomBasePermissions(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_active
        )


class AdminOrReadOnly(CustomBasePermissions):
    """ Безопасный запрос или пользователь авторизован или стафф. """
    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user.is_staff
        )


class OwnerUserOrReadOnly(CustomBasePermissions):
    """ Безопасный запрос или пользователь авторизован и автор или стафф. """
    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user == obj.author
            or request.user.is_staff
        )
