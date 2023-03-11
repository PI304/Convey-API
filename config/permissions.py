from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    message = "Permission denied"

    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            if request.user:
                return True
        else:
            if request.user.role == 0:
                return True
            else:
                return False


class AdminOnly(BasePermission):
    message = "Permission denied"

    def has_permission(self, request, view) -> bool:
        if request.user and request.user.role == 0:
            return True
        return False


class IsAuthorOrReadOnly(BasePermission):
    message = "Only the author can write"

    def has_object_permission(self, request, view, obj) -> bool:
        if request.user and request.method in SAFE_METHODS:
            return True
        return obj.author_id == request.user.id


class IsOwnerOrReadOnly(BasePermission):
    message = "Only the owner can write"

    def has_object_permission(self, request, view, obj) -> bool:
        if request.user and request.method in SAFE_METHODS:
            return True
        return obj.owner_id == request.user.id
