from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from virtualenv.app_data import read_only

from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "name", "role", "created_at", "updated_at"]
        read_only_fields = ["id", "email", "name", "role", "created_at", "updated_at"]

    def validate_role(self, value):
        choices = [k for (k, v) in User.UserType.choices]
        if value not in choices:
            raise ValidationError("role should be among " + str(choices))
