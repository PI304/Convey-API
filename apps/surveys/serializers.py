from rest_framework import serializers

from apps.surveys.models import (
    Survey,
    SurveySector,
    SectorQuestion,
    QuestionChoice,
    ChoicesSet,
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
    choices_set = QuestionChoiceSerializer(read_only=True, many=True)

    class Meta:
        model = SectorQuestion
        fields = "__all__"
        read_only_fields = ["id", "sector", "linked_sector", "created_at", "updated_at"]


class ChoicesSetSerializer(serializers.ModelSerializer):
    choice = QuestionChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = ChoicesSet
        fields = "__all__"
        read_only_fields = ["id", "question", "choice", "created_at", "updated_at"]


class SurveySectorSerializer(serializers.ModelSerializer):
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
