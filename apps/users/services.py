import string
import random

from datetime import datetime
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User


class UserService(object):
    def __init__(self, user: User):
        self.user = user

    def deactivate_user(self):
        self.user.is_deleted = True
        self.user.deleted_at = datetime.now()
        self.user.save(update_fields=["is_deleted", "deleted_at"])
        return self.user

    @staticmethod
    def generate_tokens(user: User):
        refresh = RefreshToken.for_user(user)

        return str(refresh.access_token), str(refresh)

    @staticmethod
    def authenticate_by_token(request: Request) -> User:
        authenticator = JWTAuthentication()
        try:
            user, _ = authenticator.authenticate(request)
        except InvalidToken:
            raise AuthenticationFailed("invalid access token")

        print(user)
        return user

    @staticmethod
    def generate_random_code(number_of_strings, length_of_string):
        for x in range(number_of_strings):
            return "".join(
                random.choice(string.ascii_letters + string.digits)
                for _ in range(length_of_string)
            )
