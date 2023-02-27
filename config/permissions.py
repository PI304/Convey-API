from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    message = "Permission denied"

    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            if request.user:
                return True
        else:
            if request.user.role == 1:
                return True
            else:
                return False
