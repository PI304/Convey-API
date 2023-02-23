from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User


class UserService(object):
    def __init__(self, user: User):
        self.user = user

    def deactivate_user(self):
        self.user.is_deleted = True
        self.user.deleted_at = timezone.now()
        self.user.save(update_fields=["is_deleted", "deleted_at"])
        return self.user

    @staticmethod
    def generate_tokens(user: User):
        refresh = RefreshToken.for_user(user)

        return str(refresh.access_token), str(refresh)
