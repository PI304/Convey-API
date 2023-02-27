from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.users.services import UserService


class AdminPermission(permissions.BasePermission):
    message = "Permission denied"

    def has_permission(self, request: Request, view: APIView) -> bool:
        user = UserService.authenticate_by_token(request)
        if user.role == 0:
            return True
        else:
            return False


class AppUserPermission(permissions.BasePermission):
    message = "Permission denied"

    def has_permission(self, request: Request, view: APIView) -> bool:
        user = UserService.authenticate_by_token(request)
        if user.role == 1:
            return True
        else:
            return False
