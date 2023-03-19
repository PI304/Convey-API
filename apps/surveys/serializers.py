from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.surveys.models import (
    Survey,
    SurveySector,
    SectorQuestion,
    QuestionChoice,
    QuestionAnswer,
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

    def validate(self, obj):
        if obj.get("is_descriptive") and (obj.get("desc_form", None) is None):
            raise ValidationError(
                "desc_form must not be null if is_descriptive is set true"
            )
        return obj


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
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "sector", "created_at", "updated_at"]


class SurveySectorSerializer(serializers.ModelSerializer):
    questions = SectorQuestionSerializer(read_only=True, many=True)
    common_choices = QuestionChoiceSerializer(read_only=True, many=True)

    class Meta:
        model = SurveySector
        fields = [
            "id",
            "survey",
            "instruction",
            "description",
            "question_type",
            "common_choices",
            "questions",
            "is_linked",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "survey",
            "created_at",
            "updated_at",
            "common_choices",
            "questions",
            "created_at",
            "updated_at",
        ]


class SurveySerializer(serializers.ModelSerializer):
    sectors = SurveySectorSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = Survey
        fields = [
            "id",
            "title",
            "description",
            "abbr",
            "author",
            "sectors",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "author",
            "sectors",
            "created_at",
            "updated_at",
        ]


class QuestionAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionAnswer
        fields = "__all__"
        read_only_fields = [
            "id",
            "survey_package",
            "user",
            "question",
            "workspace",
            "created_at",
            "updated_at",
        ]
