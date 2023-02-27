from rest_framework import serializers

from apps.surveys.models import Survey, SurveySector, SectorChoice, SectorQuestion
from apps.users.serializers import UserSerializer


class SimpleSurveySerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Survey
        fields = "__all__"
        read_only_fields = ["id", "author", "created_at", "updated_at"]


class SectorChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectorChoice
        fields = "__all__"
        read_only_fields = ["id", "sector", "created_at", "updated_at"]


class SurveySectorSerializer(serializers.ModelSerializer):
    choices = SectorChoiceSerializer(read_only=True, many=True)

    class Meta:
        model = SurveySector
        fields = "__all__"
        read_only_fields = ["id", "survey", "created_at", "updated_at"]


class SectorQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectorQuestion
        fields = "__all__"
        read_only_fields = ["id", "sector", "linked_sector", "created_at", "updated_at"]


class SurveySerializer(serializers.ModelSerializer):
    sectors = SurveySectorSerializer(many=True)

    class Meta:
        model = Survey
        fields = "__all__"
