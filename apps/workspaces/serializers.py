from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.survey_packages.serializers import (
    SurveyPackageSerializer,
    MiniSurveyPackageSerializer,
)
from apps.users.serializers import UserSerializer
from apps.workspaces.models import (
    Workspace,
    Routine,
    RoutineDetail,
    WorkspaceComposition,
)


class MiniWorkspaceCompositionSerializer(serializers.ModelSerializer):
    survey_package = MiniSurveyPackageSerializer(read_only=True)

    class Meta:
        model = WorkspaceComposition
        fields = ["survey_package", "workspace_id"]
        read_only_fields = ["survey_package", "workspace_id"]


class WorkspaceSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    survey_packages = MiniWorkspaceCompositionSerializer(many=True, read_only=True)

    class Meta:
        model = Workspace
        fields = [
            "id",
            "owner",
            "name",
            "uuid",
            "access_code",
            "survey_packages",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "owner",
            "uuid",
            "survey_packages",
            "created_at",
            "updated_at",
        ]

    def validate_access_code(self, value: str) -> str:
        if len(value) < 6:
            raise ValidationError("access code must be at least 6 characters long")
        return value

    def to_representation(self, obj):
        representation: dict = super().to_representation(obj)
        survey_packages_representation: list[dict] = representation.pop(
            "survey_packages"
        )

        for r in survey_packages_representation:
            survey_package_representation = r.pop("survey_package")
            for key, val in survey_package_representation.items():
                print(key, val)
                r[key] = val

        representation["survey_packages"] = survey_packages_representation

        return representation


class RoutineDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoutineDetail
        fields = [
            "id",
            "routine",
            "nth_day",
            "time",
            "survey_package",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "routine",
            "survey_package",
            "created_at",
            "updated_at",
        ]

    def validate_time(self, value: str) -> str:
        if len(value) != 5 or ":" not in value:
            raise ValidationError("time should be of 'HH:MM' format")

        hours = value.split(":")[0]
        minutes = value.split(":")[1]

        try:
            hours_int = int(hours)
            if hours_int < 0 or hours_int > 23:
                raise ValidationError(
                    "hours should be a valid number between 00 and 23"
                )
        except Exception:
            raise ValidationError("hours should be a valid number between 00 and 23")
        try:
            minutes_int = int(minutes)
            if minutes_int < 0 or minutes_int > 59:
                raise ValidationError(
                    "minutes should be a valid number between 00 and 59"
                )
        except Exception:
            raise ValidationError("minutes should be a valid number between 00 and 59")
        return value


class RoutineSerializer(serializers.ModelSerializer):
    workspace = WorkspaceSerializer(read_only=True)
    routines = RoutineDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Routine
        fields = [
            "id",
            "workspace",
            "duration",
            "routines",
            "kick_off",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "workspace", "routines", "created_at", "updated_at"]

    def validate_duration(self, value) -> int:
        if value <= 0:
            raise ValidationError("duration of the routine should exceed 0")
        return value


class WorkspaceCompositionSerializer(serializers.ModelSerializer):
    workspace = WorkspaceSerializer(read_only=True)
    survey_package = SurveyPackageSerializer(read_only=True)

    class Meta:
        model = WorkspaceComposition
        fields = ["id", "survey_package", "workspace", "created_at", "updated_at"]
        read_only_fields = [
            "id",
            "survey_package",
            "workspace",
            "created_at",
            "updated_at",
        ]
