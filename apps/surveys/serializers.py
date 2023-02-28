from rest_framework import serializers

from apps.surveys.models import Survey, SurveySector, SectorChoice, SectorQuestion
from apps.users.serializers import UserSerializer


class SimpleSurveySerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Survey
        fields = [
            "id",
            "author",
            "title",
            "description",
            "abbr",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "author", "created_at", "updated_at"]


class SectorChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectorChoice
        fields = "__all__"
        read_only_fields = ["id", "sector", "created_at", "updated_at"]


class SectorQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectorQuestion
        fields = "__all__"
        read_only_fields = ["id", "sector", "linked_sector", "created_at", "updated_at"]


class SurveySectorSerializer(serializers.ModelSerializer):
    choices = SectorChoiceSerializer(read_only=True, many=True)
    questions = SectorQuestionSerializer(read_only=True, many=True)

    class Meta:
        model = SurveySector
        fields = [
            "id",
            "survey",
            "title",
            "description",
            "question_type",
            "choices",
            "questions",
        ]
        read_only_fields = [
            "id",
            "survey",
            "created_at",
            "updated_at",
            "choices",
            "questions",
        ]


class SurveySerializer(serializers.ModelSerializer):
    sectors = SurveySectorSerializer(many=True, read_only=True)

    class Meta:
        model = Survey
        fields = ["id", "title", "description", "abbr", "author", "sectors"]
        read_only_fields = ["id", "author", "sectors", "created_at", "updated_at"]
