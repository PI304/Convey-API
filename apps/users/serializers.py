from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from virtualenv.app_data import read_only

from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "name",
            "social_provider",
            "role",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {"role": {"write_only": True}}
