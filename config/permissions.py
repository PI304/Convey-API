from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.users.services import UserService


class IsAdminOrReadOnly(BasePermission):
    message = "Permission denied"

    def has_permission(self, request: Request, view: APIView) -> bool:
        user = UserService.authenticate_by_token(request)
        if (
            request.method in SAFE_METHODS
            or request.user
            and request.user.is_authenticated
        ):
            return True
        return False
