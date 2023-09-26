from rest_framework.permissions import SAFE_METHODS, BasePermission


class CustomBasePermissions(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_active
        )


class OwnerUserOrReadOnly(CustomBasePermissions):
    """ Пользователь является автором. """
    def has_object_permission(self, request, view, obj):
        return (
            request.user == obj.author
        )
