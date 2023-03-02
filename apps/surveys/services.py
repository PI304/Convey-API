from typing import Union

from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from apps.surveys.models import (
    Survey,
    SurveySector,
    SectorQuestion,
)
from apps.surveys.serializers import (
    SurveySectorSerializer,
    SectorQuestionSerializer,
    QuestionChoiceSerializer,
)


class SurveyService(object):
    def __init__(self, survey: Union[Survey, int]):
        if type(survey) == int:
            self.survey = get_object_or_404(Survey, id=survey)
        else:
            self.survey = survey

    def create_sectors(self, sectors: list[dict]) -> list[SurveySector]:
        created_sectors: list[SurveySector] = []

        for data in sectors:
            sector = self._create_sector(data)
            created_sectors.append(sector)

        return created_sectors

    def _make_common_choices(
        self, common_choices_list: list[dict], sector_id: int
    ) -> None:
        print("making common choices")
        for c in common_choices_list:
            serializer = QuestionChoiceSerializer(data=c)
            if serializer.is_valid(raise_exception=True):
                serializer.save(related_sector_id=sector_id)

    def _make_question(self, question_data: dict, sector_id: int):
        # Create a question with empty choices
        question = None
        serializer = SectorQuestionSerializer(data=question_data)
        if serializer.is_valid(raise_exception=True):
            question: SectorQuestion = serializer.save(sector_id=sector_id)

        # Create choices for the question (if exists - non-common-choices)
        if "choices" in question_data and (question_data["choices"] is not None):
            self._make_choices(question_data["choices"], question.id)

        return question

    def _make_choices(self, choices_list_data: list[dict], question_id: int) -> None:
        for c_data in choices_list_data:
            serializer = QuestionChoiceSerializer(data=c_data)
            if serializer.is_valid(raise_exception=True):
                choice = serializer.save(related_question_id=question_id)

    def _create_sector(self, data: dict) -> SurveySector:
        # Create base SurveySector
        sector_data = dict(
            title=data.get("title", None),
            description=data.get("description", None),
            question_type=data.get("question_type", None),
        )

        sector = None

        serializer = SurveySectorSerializer(data=sector_data)
        if serializer.is_valid(raise_exception=True):
            sector = serializer.save(survey_id=self.survey.id)

        # Create common choices (if exists) and associate with the created sector
        if "common_choices" in data and data["common_choices"] is not None:
            self._make_common_choices(data["common_choices"], sector.id)

        # Create Questions and associate with survey sector
        questions_list_data: list[dict] = data.get("questions", None)
        if not questions_list_data:
            raise ValidationError("'questions' field is required")

        for q in questions_list_data:
            self._make_question(q, sector.id)

        return sector

    def delete_related_sectors(self) -> None:
        sectors: list[SurveySector] = SurveySector.objects.filter(
            survey_id=self.survey.id
        )
        if sectors:
            for s in sectors:
                s.delete()
