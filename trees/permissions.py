from rest_framework import permissions

from trees.models import User


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Only allow the owner or admins to view/edit objects.
    """

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_superuser:
            return True

        return (
            obj == request.user
            if isinstance(obj, User)
            else obj.user == request.user
        )
