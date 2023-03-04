from rest_framework import serializers

from apps.surveys.models import (
    Survey,
    SurveySector,
    SectorQuestion,
    QuestionChoice,
)
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


class QuestionChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionChoice
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class SectorQuestionSerializer(serializers.ModelSerializer):
    choices = QuestionChoiceSerializer(read_only=True, many=True)

    class Meta:
        model = SectorQuestion
        fields = [
            "id",
            "sector",
            "choices",
            "number",
            "content",
            "is_required",
            "linked_sector",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "sector", "linked_sector", "created_at", "updated_at"]


class SurveySectorSerializer(serializers.ModelSerializer):
    questions = SectorQuestionSerializer(read_only=True, many=True)
    common_choices = QuestionChoiceSerializer(read_only=True, many=True)

    class Meta:
        model = SurveySector
        fields = [
            "id",
            "survey",
            "title",
            "description",
            "question_type",
            "common_choices",
            "questions",
        ]
        read_only_fields = [
            "id",
            "survey",
            "created_at",
            "updated_at",
            "common_choices",
            "questions",
        ]


class SurveySerializer(serializers.ModelSerializer):
    sectors = SurveySectorSerializer(many=True, read_only=True)
    common_choices = QuestionChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Survey
        fields = [
            "id",
            "title",
            "description",
            "abbr",
            "author",
            "sectors",
            "common_choices",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "author",
            "sectors",
            "common_choices",
            "created_at",
            "updated_at",
        ]
