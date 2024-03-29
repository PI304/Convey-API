import json
import string
import random
import logging

from datetime import datetime
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User
from utils.body_encryption import AESCipher

logger = logging.getLogger("convey")


class UserService(object):
    def __init__(self, user: User):
        self.user = user

    def deactivate_user(self):
        self.user.is_deleted = True
        self.user.deleted_at = datetime.now()
        self.user.save(update_fields=["is_deleted", "deleted_at"])
        logger.info(f"User <{self.user.email}> is deactivated")
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

    @staticmethod
    def decrypt_body(bytes_data: bytes, total_len: int = 3) -> dict:
        cipher = AESCipher()
        data_json: str = cipher.decrypt(bytes_data)
        decrypted_data = json.loads(data_json)

        if total_len != len(decrypted_data):
            raise ValueError("invalid length of data")

        decrypted_data["social_provider"] = decrypted_data["socialProvider"]
        del decrypted_data["socialProvider"]

        if "privacyPolicyAgreed" in decrypted_data:
            decrypted_data["privacy_policy_agreed"] = decrypted_data[
                "privacyPolicyAgreed"
            ]
            del decrypted_data["privacyPolicyAgreed"]

        return decrypted_data

    @staticmethod
    def blacklist_token(token: str) -> None:
        token = RefreshToken(token)
        token.blacklist()
        return None
