from rest_framework.permissions import SAFE_METHODS, BasePermission


class OwnerUserOrReadOnly(BasePermission):
    """ Пользователь является автором. """
    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user == obj.author
        )
