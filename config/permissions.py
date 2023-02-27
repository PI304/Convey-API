from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.users.services import UserService


class IsAdminOrReadOnly(BasePermission):
    message = "Permission denied"

    def has_permission(self, request: Request, view: APIView) -> bool:
        if request.method in SAFE_METHODS:
            if request.user:
                return True
        else:
            if request.user.role == 1:
                return True
            else:
                return False
