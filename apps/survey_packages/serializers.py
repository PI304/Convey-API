from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.survey_packages.models import (
    SurveyPackage,
    PackageContact,
    PackagePart,
    PackageSubject,
    PackageSubjectSurvey,
)
from apps.surveys.serializers import SurveySerializer
from apps.users.serializers import UserSerializer
from apps.workspaces.serializers import WorkspaceSerializer


class PackageContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageContact
        fields = "__all__"
        read_only_fields = ["id", "survey_package", "created_at", "updated_at"]

    def validate_type(self, value):
        if value not in PackageContact.ContactType.values:
            raise ValidationError("contact type must be either 'email' or 'phone'")


class SimpleSurveyPackageSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    logo = serializers.ImageField(required=False, use_url=True)
    workspace = WorkspaceSerializer(read_only=True, many=True)
    contact_info = PackageContactSerializer(many=True, read_only=True)

    class Meta:
        model = SurveyPackage
        fields = "__all__"
        read_only_fields = [
            "id",
            "author",
            "workspace",
            "created_at",
            "updated_at",
        ]


class PackageSubjectSurveySerializer(serializers.ModelSerializer):
    survey = SurveySerializer(read_only=True)

    class Meta:
        model = PackageSubjectSurvey
        fields = "__all__"
        read_only_fields = ["id", "subject", "survey", "created_at", "updated_at"]


class PackageSubjectSerializer(serializers.ModelSerializer):
    surveys = PackageSubjectSurveySerializer(read_only=True, many=True)

    class Meta:
        model = PackageSubject
        fields = "__all__"
        read_only_fields = ["id", "package_part", "created_at", "updated_at"]


class PackagePartSerializer(serializers.ModelSerializer):
    subjects = PackageSubjectSerializer(read_only=True, many=True)

    class Meta:
        model = PackagePart
        fields = "__all__"
        read_only_fields = ["id", "survey_package", "created_at", "updated_at"]


class SurveyPackageSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    logo = serializers.ImageField(required=False, use_url=True)
    workspace = WorkspaceSerializer(read_only=True, many=True)
    contact_info = PackageContactSerializer(many=True, read_only=True)
    parts = PackagePartSerializer()

    class Meta:
        model = SurveyPackage
        fields = "__all__"
        read_only_fields = [
            "id",
            "author",
            "workspace",
            "created_at",
            "updated_at",
        ]
