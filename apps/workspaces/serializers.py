from rest_framework import serializers
from virtualenv.app_data import read_only

from apps.workspaces.models import Workspace


class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = ["id", "owner", "name", "created_at", "updated_at"]
        read_only_fields = ["id", "owner", "name", "created_at", "updated_at"]
